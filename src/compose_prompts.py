#!/usr/bin/env python3
"""
Compose prompt variants from questions across all three experimental conditions.

This module creates up to three JSONL files:
- without_protocol.jsonl : Baseline questions (no protocol wrapper)
- with_protocol.jsonl    : Questions wrapped with SGP text (Condition B)
- with_guardrails.jsonl  : Plain questions routed through NeMo Guardrails
                           (Condition C — SGP enforced at runtime, not in prompt)

Author: Monica Guimaraes
"""

import argparse
import json
import os
from pathlib import Path
from typing import Dict, Iterator, List, Optional


class PromptComposer:
    """
    Composes prompts with or without a scientific grounding protocol wrapper.

    Follows Single Responsibility Principle: handles only prompt composition logic.
    """

    def __init__(self, protocol_text: Optional[str] = None):
        """
        Initialize the composer with optional protocol text.

        Args:
            protocol_text: The protocol wrapper text to prepend to prompts.
        """
        self.protocol_text = protocol_text

    def compose_with_protocol(self, question: str) -> str:
        """
        Compose a prompt with the protocol wrapper.

        Args:
            question: The question text to wrap.

        Returns:
            The composed prompt with protocol prepended.

        Raises:
            ValueError: If protocol_text is not set.
        """
        if self.protocol_text is None:
            raise ValueError("Protocol text is required for with-protocol composition")

        return f"{self.protocol_text}\n\n---\n\n{question}"

    def compose_without_protocol(self, question: str) -> str:
        """
        Compose a prompt without any protocol wrapper.

        Args:
            question: The question text.

        Returns:
            The question as-is.
        """
        return question

    def compose_with_guardrails(self, question: str) -> str:
        """
        Compose a prompt for the NeMo Guardrails condition (Condition C).

        The question is passed through unchanged. SGP constraints are enforced
        at runtime by the guardrails layer (guardrails/rails.co + actions.py)
        rather than embedded as prompt text. This isolates the architectural
        effect of programmatic enforcement from the effect of in-context
        instructions used in the with-protocol condition.

        Args:
            question: The question text.

        Returns:
            The question as-is.
        """
        return question


class QuestionLoader:
    """
    Loads questions from JSONL files.

    Follows Single Responsibility Principle: handles only question loading.
    """

    @staticmethod
    def load_questions(filepath: Path) -> Iterator[Dict[str, str]]:
        """
        Load questions from a JSONL file.

        Args:
            filepath: Path to the JSONL file.

        Yields:
            Dictionary containing question metadata (qid, domain, prompt).

        Raises:
            FileNotFoundError: If the questions file does not exist.
            json.JSONDecodeError: If a line contains invalid JSON.
        """
        if not filepath.exists():
            raise FileNotFoundError(f"Questions file not found: {filepath}")

        with open(filepath, "r", encoding="utf-8") as f:
            for line_num, line in enumerate(f, start=1):
                line = line.strip()
                # Skip empty lines and comments
                if not line or line.startswith("#"):
                    continue
                try:
                    yield json.loads(line)
                except json.JSONDecodeError as e:
                    raise json.JSONDecodeError(
                        f"Invalid JSON on line {line_num}",
                        e.doc,
                        e.pos
                    )


class ProtocolLoader:
    """
    Loads protocol text from markdown files.

    Follows Single Responsibility Principle: handles only protocol loading.
    """

    @staticmethod
    def load_protocol(filepath: Path) -> str:
        """
        Load protocol text from a markdown file.

        Args:
            filepath: Path to the protocol markdown file.

        Returns:
            The protocol text content.

        Raises:
            FileNotFoundError: If the protocol file does not exist.
        """
        if not filepath.exists():
            raise FileNotFoundError(f"Protocol file not found: {filepath}")

        with open(filepath, "r", encoding="utf-8") as f:
            return f.read().strip()


class PromptWriter:
    """
    Writes composed prompts to JSONL files.

    Follows Single Responsibility Principle: handles only output writing.
    """

    @staticmethod
    def write_prompts(
        prompts: List[Dict[str, str]],
        output_path: Path
    ) -> None:
        """
        Write prompts to a JSONL file.

        Args:
            prompts: List of prompt dictionaries to write.
            output_path: Path to the output JSONL file.
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            for prompt in prompts:
                json.dump(prompt, f)
                f.write("\n")


def compose_all_prompts(
    questions_path: Path,
    protocol_path: Optional[Path],
    output_dir: Path,
    include_guardrails: bool = False,
) -> None:
    """
    Main orchestration function to compose all prompt variants.

    Follows Open/Closed Principle: New composition strategies can be added
    without modifying existing code.

    Args:
        questions_path: Path to the questions JSONL file.
        protocol_path: Path to the protocol markdown file (None for without-protocol only).
        output_dir: Directory where output files will be written.
        include_guardrails: If True, also emit with_guardrails.jsonl (Condition C).
    """
    # Load questions
    loader = QuestionLoader()
    questions = list(loader.load_questions(questions_path))

    # Prepare output lists
    with_protocol_prompts: List[Dict[str, str]] = []
    without_protocol_prompts: List[Dict[str, str]] = []
    with_guardrails_prompts: List[Dict[str, str]] = []

    # Load protocol if provided
    protocol_text = None
    if protocol_path:
        protocol_loader = ProtocolLoader()
        protocol_text = protocol_loader.load_protocol(protocol_path)

    # Compose prompts
    composer = PromptComposer(protocol_text)

    for question in questions:
        qid = question["qid"]
        base_prompt = question["prompt"]

        # Without protocol variant
        without_prompt = {
            "qid": qid,
            "condition": "without-protocol",
            "wrapper": None,
            "prompt_text": composer.compose_without_protocol(base_prompt)
        }
        without_protocol_prompts.append(without_prompt)

        # With protocol variant (if protocol provided)
        if protocol_text:
            with_prompt = {
                "qid": qid,
                "condition": "with-protocol",
                "wrapper": "SGP_compact",
                "prompt_text": composer.compose_with_protocol(base_prompt)
            }
            with_protocol_prompts.append(with_prompt)

        # With guardrails variant (Condition C — SGP enforced at runtime)
        if include_guardrails:
            guardrails_prompt = {
                "qid": qid,
                "condition": "with-guardrails",
                "wrapper": "NeMo_SGP",
                "prompt_text": composer.compose_with_guardrails(base_prompt)
            }
            with_guardrails_prompts.append(guardrails_prompt)

    # Write outputs
    writer = PromptWriter()
    writer.write_prompts(
        without_protocol_prompts,
        output_dir / "without_protocol.jsonl"
    )
    print(f"✓ Wrote {len(without_protocol_prompts)} without-protocol prompts")

    if with_protocol_prompts:
        writer.write_prompts(
            with_protocol_prompts,
            output_dir / "with_protocol.jsonl"
        )
        print(f"✓ Wrote {len(with_protocol_prompts)} with-protocol prompts")

    if with_guardrails_prompts:
        writer.write_prompts(
            with_guardrails_prompts,
            output_dir / "with_guardrails.jsonl"
        )
        print(f"✓ Wrote {len(with_guardrails_prompts)} with-guardrails prompts")


def main() -> None:
    """Command-line interface for composing prompts."""
    parser = argparse.ArgumentParser(
        description="Compose prompt variants from questions with/without protocol"
    )
    parser.add_argument(
        "--questions",
        type=Path,
        required=True,
        help="Path to questions.jsonl file"
    )
    parser.add_argument(
        "--protocol",
        type=Path,
        default=None,
        help="Path to protocol markdown file (e.g., SGP_compact.md)"
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        required=True,
        help="Output directory for generated prompt files"
    )
    parser.add_argument(
        "--guardrails",
        action="store_true",
        default=False,
        help="Also emit with_guardrails.jsonl for Condition C (NeMo Guardrails)"
    )

    args = parser.parse_args()

    try:
        compose_all_prompts(
            questions_path=args.questions,
            protocol_path=args.protocol,
            output_dir=args.out_dir,
            include_guardrails=args.guardrails,
        )
        print("\n✓ Prompt composition complete!")
    except (FileNotFoundError, json.JSONDecodeError, ValueError) as e:
        print(f"Error: {e}")
        exit(1)


if __name__ == "__main__":
    main()
