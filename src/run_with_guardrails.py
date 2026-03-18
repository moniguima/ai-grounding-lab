#!/usr/bin/env python3
"""
Run prompts through NeMo Guardrails as Condition C (with-guardrails).

The guardrails layer sits between the prompt composer and the LM runner,
enforcing Scientific Grounding Protocol constraints programmatically:

    Input rail  : domain boundary enforcement (blocks out-of-scope questions)
    Output rail : SGP compliance check (evidence, uncertainty, transparency)

Output schema is identical to run_lm_studio.py with one additional field:

    guardrails_trace : {
        input_rail_triggered  (bool)    — True if domain check blocked
        output_rail_triggered (bool)    — True if an SGP output check blocked
        rail_violated         (str|None)— "domain", "sgp", or None
    }

This schema extension is ignored by eval_scores.py and aggregate.py, so the
full downstream evaluation pipeline requires no modification.

Usage:
    python3 src/run_with_guardrails.py \\
        --model "llama-3.1-8b" \\
        --prompts data/prompts/with_guardrails.jsonl \\
        --out runs/raw/with_guardrails_llama3.jsonl \\
        --temperature 0.2 \\
        --max-tokens 1024 \\
        --seed 42

Author: Monica Guimaraes
"""

import argparse
import asyncio
import datetime
import json
import time
from pathlib import Path
from typing import Any, Dict, Iterator, Optional

from nemoguardrails import LLMRails, RailsConfig


# ---------------------------------------------------------------------------
# GuardrailsConfigLoader
# ---------------------------------------------------------------------------

class GuardrailsConfigLoader:
    """
    Loads NeMo Guardrails configuration and patches runtime model parameters.

    Follows Single Responsibility Principle: handles only config loading and
    CLI-driven parameter injection. Does not execute inference.
    """

    def __init__(self, config_dir: Path) -> None:
        """
        Args:
            config_dir: Path to the guardrails/ config directory containing
                        config.yml, rails.co, and actions.py.

        Raises:
            FileNotFoundError: If config_dir does not exist.
        """
        if not config_dir.exists():
            raise FileNotFoundError(
                f"Guardrails config directory not found: {config_dir}"
            )
        self.config_dir = config_dir

    def load(
        self,
        model_name: str,
        base_url: str,
        temperature: float,
        max_tokens: int,
    ) -> LLMRails:
        """
        Load RailsConfig from directory and patch model/endpoint parameters.

        RailsConfig.from_path auto-discovers config.yml, rails.co, and
        actions.py from the config directory. Model parameters are then
        overridden with the values supplied from the CLI.

        Args:
            model_name: LLM model identifier (e.g., "llama-3.1-8b").
            base_url:   LM Studio OpenAI-compatible API base URL.
            temperature: Sampling temperature.
            max_tokens:  Maximum tokens to generate per response.

        Returns:
            Fully configured LLMRails instance ready for async generation.
        """
        config = RailsConfig.from_path(str(self.config_dir))

        for model_config in config.models:
            if model_config.type == "main":
                model_config.model = model_name
                params: Dict[str, Any] = dict(model_config.parameters or {})
                params.update(
                    {
                        "base_url": base_url,
                        "openai_api_base": base_url,
                        "temperature": temperature,
                        "max_tokens": max_tokens,
                    }
                )
                model_config.parameters = params

        return LLMRails(config)


# ---------------------------------------------------------------------------
# PromptLoader
# ---------------------------------------------------------------------------

class PromptLoader:
    """
    Loads prompts from a JSONL file produced by compose_prompts.py.

    Follows Single Responsibility Principle: handles only prompt iteration.
    """

    @staticmethod
    def iter_prompts(path: Path) -> Iterator[Dict[str, Any]]:
        """
        Yield prompt dictionaries from a JSONL file.

        Args:
            path: Path to the JSONL prompt file (e.g., with_guardrails.jsonl).

        Yields:
            Prompt dicts with keys: qid, condition, wrapper, prompt_text.

        Raises:
            FileNotFoundError: If the prompt file does not exist.
            json.JSONDecodeError: If a line contains invalid JSON.
        """
        if not path.exists():
            raise FileNotFoundError(f"Prompt file not found: {path}")

        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    yield json.loads(line)


# ---------------------------------------------------------------------------
# GuardrailsRunner
# ---------------------------------------------------------------------------

class GuardrailsRunner:
    """
    Runs prompts through a configured LLMRails instance and captures rail traces.

    Follows Single Responsibility Principle: handles only prompt execution and
    result assembly. Does not handle I/O or config loading.
    """

    # Sentinel strings emitted by Colang bot utterances on rail violation.
    # Detected here to populate guardrails_trace without parsing NeMo internals.
    _OUT_OF_DOMAIN_MARKER: str = "outside the ai grounding lab"
    _SGP_RAIL_MARKER: str = "[sgp_rail_triggered]"

    def __init__(
        self,
        rails: LLMRails,
        model_name: str,
        gen_params: Dict[str, Any],
        seed: int,
    ) -> None:
        """
        Args:
            rails:       Configured LLMRails instance from GuardrailsConfigLoader.
            model_name:  Model identifier used in run_id and model metadata.
            gen_params:  Generation parameters dict (temperature, max_tokens, seed).
            seed:        Random seed value used in run_id label for reproducibility.
        """
        self.rails = rails
        self.model_name = model_name
        self.gen_params = gen_params
        self.seed = seed

    async def run_prompt(self, prompt_row: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run a single prompt through NeMo Guardrails and return a result dict.

        The result schema matches run_lm_studio.py output exactly, with the
        addition of a guardrails_trace field.

        Args:
            prompt_row: Prompt dict with keys: qid, condition, wrapper, prompt_text.

        Returns:
            Result dict with keys: run_id, timestamp_utc, qid, condition, model,
            gen_params, prompt, response, guardrails_trace.
        """
        qid: str = prompt_row["qid"]
        condition: str = prompt_row["condition"]
        prompt_text: str = prompt_row["prompt_text"]

        t0 = time.time()
        response_text: str
        latency_ms: Optional[int]
        guardrails_trace: Dict[str, Any]

        try:
            response_text = await self.rails.generate_async(
                messages=[{"role": "user", "content": prompt_text}]
            )
            latency_ms = int((time.time() - t0) * 1000)
            guardrails_trace = self._build_trace(response_text)
        except Exception as exc:
            response_text = f"[ERROR] {exc}"
            latency_ms = None
            guardrails_trace = {"error": str(exc)}

        run_id = (
            f"{datetime.datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')}"
            f"_{qid}_{self.model_name}_{condition}_seed{self.seed}"
        )

        return {
            "run_id": run_id,
            "timestamp_utc": datetime.datetime.utcnow().isoformat(),
            "qid": qid,
            "condition": condition,
            "model": {"name": self.model_name, "source": "LMStudio_NeMo"},
            "gen_params": self.gen_params,
            "prompt": {
                "wrapper": prompt_row.get("wrapper"),
                "full_prompt_text": prompt_text,
            },
            "response": {
                "text": response_text,
                "tokens_out": None,   # NeMo does not expose token counts directly
                "latency_ms": latency_ms,
            },
            "guardrails_trace": guardrails_trace,
        }

    def _build_trace(self, response_text: str) -> Dict[str, Any]:
        """
        Build a guardrails trace dict from sentinel strings in the response.

        Colang bot utterances embed distinct marker strings when rails trigger
        (see rails.co). This method detects those markers without coupling to
        NeMo internals.

        Args:
            response_text: Final response text returned by LLMRails.generate_async.

        Returns:
            Dict with keys:
                input_rail_triggered  (bool): True if domain check blocked.
                output_rail_triggered (bool): True if SGP output check blocked.
                rail_violated (str|None): "domain", "sgp", or None.
        """
        text_lower = response_text.lower()
        input_triggered = self._OUT_OF_DOMAIN_MARKER in text_lower
        output_triggered = self._SGP_RAIL_MARKER in text_lower

        return {
            "input_rail_triggered": input_triggered,
            "output_rail_triggered": output_triggered,
            "rail_violated": (
                "domain" if input_triggered
                else "sgp" if output_triggered
                else None
            ),
        }


# ---------------------------------------------------------------------------
# ResponseWriter
# ---------------------------------------------------------------------------

class ResponseWriter:
    """
    Writes GuardrailsRunner result dicts to a JSONL output file.

    Follows Single Responsibility Principle: handles only file I/O.
    Implements the context manager protocol for safe resource management.
    """

    def __init__(self, output_path: Path) -> None:
        """
        Args:
            output_path: Path to the output JSONL file. Parent directories
                         are created automatically.
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)
        self._file = open(output_path, "w", encoding="utf-8")

    def write(self, result: Dict[str, Any]) -> None:
        """
        Write a single result dict as a JSONL line and flush immediately.

        Args:
            result: Result dictionary from GuardrailsRunner.run_prompt.
        """
        json.dump(result, self._file)
        self._file.write("\n")
        self._file.flush()

    def close(self) -> None:
        """Close the underlying file handle."""
        self._file.close()

    def __enter__(self) -> "ResponseWriter":
        return self

    def __exit__(self, *_: Any) -> None:
        self.close()


# ---------------------------------------------------------------------------
# Async main and CLI entry point
# ---------------------------------------------------------------------------

async def _main_async() -> None:
    """Async orchestration: load config, iterate prompts, run rails, write output."""
    parser = argparse.ArgumentParser(
        description="Run prompts through NeMo Guardrails (SGP enforcement layer)"
    )
    parser.add_argument(
        "--guardrails-config",
        type=Path,
        default=Path("guardrails"),
        help="Path to guardrails config directory (default: guardrails/)",
    )
    parser.add_argument(
        "--base-url",
        default="http://localhost:1234/v1",
        help="LM Studio API base URL",
    )
    parser.add_argument("--model", required=True, help="Model identifier")
    parser.add_argument(
        "--prompts", type=Path, required=True, help="Path to with_guardrails.jsonl"
    )
    parser.add_argument(
        "--out", type=Path, required=True, help="Output JSONL path"
    )
    parser.add_argument("--temperature", type=float, default=0.2)
    parser.add_argument("--max-tokens", type=int, default=1024)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    gen_params: Dict[str, Any] = {
        "temperature": args.temperature,
        "max_tokens": args.max_tokens,
        "seed": args.seed,
    }

    config_loader = GuardrailsConfigLoader(args.guardrails_config)
    rails = config_loader.load(
        model_name=args.model,
        base_url=args.base_url,
        temperature=args.temperature,
        max_tokens=args.max_tokens,
    )

    runner = GuardrailsRunner(
        rails=rails,
        model_name=args.model,
        gen_params=gen_params,
        seed=args.seed,
    )

    with ResponseWriter(args.out) as writer:
        for prompt_row in PromptLoader.iter_prompts(args.prompts):
            result = await runner.run_prompt(prompt_row)
            writer.write(result)

            trace = result["guardrails_trace"]
            blocked = trace.get("input_rail_triggered") or trace.get("output_rail_triggered")
            status = f"BLOCKED:{trace.get('rail_violated')}" if blocked else "OK"
            chars = len(result["response"]["text"])
            ms = result["response"]["latency_ms"]
            print(
                f"[guardrails] {result['qid']} {result['condition']} "
                f"-> {chars} chars, {ms} ms, rails={status}"
            )

    print(f"\n✓ Guardrails run complete -> {args.out}")


def main() -> None:
    """Synchronous CLI entry point. Delegates to async main via asyncio.run."""
    asyncio.run(_main_async())


if __name__ == "__main__":
    main()
