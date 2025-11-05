# Runs Directory

This directory stores experiment outputs organized by processing stage.

## Structure

```
runs/
├── raw/       # Model responses from run_lm_studio.py
└── evals/     # Evaluation scores from eval_scores.py
```

## File Naming Convention

### Raw Responses (`runs/raw/`)

Format: `{condition}_{model}_{timestamp}.jsonl`

Examples:
- `without_protocol_llama3_20251105.jsonl`
- `with_protocol_llama3_20251105.jsonl`
- `without_protocol_gpt4_20251105.jsonl`

Each line contains:
```json
{
  "run_id": "unique-run-identifier",
  "timestamp_utc": "ISO-8601-timestamp",
  "qid": "Q1",
  "condition": "with-protocol" | "without-protocol",
  "model": {"name": "model-name", "source": "LMStudio"},
  "gen_params": {"temperature": 0.2, "max_tokens": 1024, "seed": 42},
  "prompt": {"wrapper": "SGP_compact" | null, "full_prompt_text": "..."},
  "response": {"text": "...", "tokens_out": 512, "latency_ms": 1234}
}
```

### Evaluation Scores (`runs/evals/`)

Format: `{condition}_{model}_{timestamp}.eval.jsonl`

Examples:
- `without_protocol_llama3_20251105.eval.jsonl`
- `with_protocol_llama3_20251105.eval.jsonl`
- `pairwise_llama3_20251105.eval.jsonl`

Each line contains:
```json
{
  "run_id": "matching-run-id-from-raw",
  "qid": "Q1",
  "condition": "with-protocol" | "without-protocol",
  "model": "model-name",
  "seed": 42,
  "evaluator_model": "gpt-4o-mini",
  "rubric_fingerprint": "sha256-hash",
  "scores": {
    "evidence_quality": 4,
    "transparency": 5,
    "reasoning_depth": 4,
    "actionability": 4,
    "uncertainty_disclosure": 5,
    "total": 22
  },
  "justifications": {
    "evidence_quality": "explanation...",
    "transparency": "explanation...",
    ...
  }
}
```

## Git Ignore

Note: This directory is excluded from git by default (see `.gitignore`).
Experiment results are local to each researcher's machine.

## Best Practices

1. **Timestamp your runs:** Use ISO-8601 format (YYYYMMDD or YYYYMMDDTHHMMSSZ)
2. **Keep raw and eval files paired:** Same naming prefix for easy matching
3. **Document experiments:** Consider keeping a `EXPERIMENTS.md` log file
4. **Archive important runs:** Move significant results to a versioned location
