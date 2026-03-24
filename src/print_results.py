#!/usr/bin/env python3
"""
Pretty-print AI evaluation results to the terminal.

Usage:
    python src/print_results.py
    python src/print_results.py --verbose
    python src/print_results.py --dir evaluations/ai --questions data/questions.jsonl
"""

import argparse
import json
from pathlib import Path
from typing import Dict, List, Optional


# ============================================================================
# CONSTANTS
# ============================================================================

CRITERIA_KEYS = [
    "evidence_quality",
    "transparency",
    "reasoning_depth",
    "actionability",
    "uncertainty_disclosure",
]

CRITERIA_ABBREV = {
    "evidence_quality":       "Ev.Q",
    "transparency":           "Trns",
    "reasoning_depth":        "Rs.D",
    "actionability":          "Actn",
    "uncertainty_disclosure": "Un.D",
}

CRITERIA_LABELS = {
    "evidence_quality":       "Evidence Quality",
    "transparency":           "Transparency",
    "reasoning_depth":        "Reasoning Depth",
    "actionability":          "Actionability",
    "uncertainty_disclosure": "Uncertainty Disclosure",
}

CONDITIONS = ["without-protocol", "with-protocol"]
CONDITION_LABELS = {
    "without-protocol": "Without Protocol",
    "with-protocol":    "With Protocol",
}

COL_W = 6
LABEL_W = 18
LINE_W = LABEL_W + COL_W * len(CRITERIA_KEYS) + 8


# ============================================================================
# DATA LOADING
# ============================================================================

def _load_records(evaluations_dir: Path) -> List[Dict]:
    """
    Load all evaluation records from JSONL files in the given directory.

    Args:
        evaluations_dir: Directory containing criterion JSONL files.

    Returns:
        List of record dicts with non-null scores.
    """
    records = []
    for key in CRITERIA_KEYS:
        filepath = evaluations_dir / f"{key}_evaluations.jsonl"
        if not filepath.exists():
            continue
        with open(filepath, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    record = json.loads(line)
                    if record.get("score") is not None:
                        records.append(record)
    return records


def _load_questions(questions_path: Path) -> List[Dict]:
    """
    Load questions from a JSONL file.

    Args:
        questions_path: Path to the questions JSONL file.

    Returns:
        List of question dicts with keys qid, domain, prompt.
    """
    questions = []
    if not questions_path.exists():
        return questions
    with open(questions_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                questions.append(json.loads(line))
    return questions


# ============================================================================
# DATA ORGANIZATION
# ============================================================================

def _organize(records: List[Dict]) -> Dict[str, Dict[str, Dict[str, Dict]]]:
    """
    Organize records by question, condition, and criterion.

    Args:
        records: List of raw evaluation record dicts.

    Returns:
        {question_id: {condition: {criterion: {"score": int, "text": str}}}}
    """
    result: Dict[str, Dict[str, Dict[str, Dict]]] = {}
    for r in records:
        qid = r["question_id"]
        cond = r["condition"]
        crit = r["criterion"]
        result.setdefault(qid, {}).setdefault(cond, {})[crit] = {
            "score": r["score"],
            "text": r.get("evaluation_text", ""),
        }
    return result


# ============================================================================
# FORMATTING HELPERS
# ============================================================================

def _fmt_score(score: Optional[float], is_gain: bool = False) -> str:
    """Format a score value into a fixed-width string."""
    if score is None:
        return "—".center(COL_W)
    if is_gain:
        s = f"+{score:.1f}" if score >= 0 else f"{score:.1f}"
    else:
        s = f"{score:.1f}" if isinstance(score, float) else str(int(score))
    return s.rjust(COL_W)


def _header_row() -> str:
    """Return the column header row string."""
    abbrevs = "".join(a.rjust(COL_W) for a in CRITERIA_ABBREV.values())
    return " " * LABEL_W + abbrevs + "  │" + "  Avg"


def _separator() -> str:
    """Return a horizontal separator line."""
    return "─" * LINE_W


def _score_row(label: str, scores: Dict[str, float], is_gain: bool = False) -> str:
    """
    Format a single score row with label, per-criterion scores, and row average.

    Args:
        label:    Row label (e.g. condition name or "Gain").
        scores:   {criterion_key: score} mapping.
        is_gain:  If True, prefix positive values with '+'.

    Returns:
        Formatted row string.
    """
    cells = "".join(_fmt_score(scores.get(k), is_gain) for k in CRITERIA_KEYS)
    avg = sum(scores.values()) / len(scores) if scores else 0.0
    avg_str = _fmt_score(avg, is_gain).rjust(6)
    return label.ljust(LABEL_W) + cells + "  │" + avg_str


# ============================================================================
# MAIN FUNCTION
# ============================================================================

def print_evaluation_results(
    evaluations_dir: Path = Path("evaluations/ai"),
    questions_path: Path = Path("data/questions.jsonl"),
    verbose: bool = False,
) -> None:
    """
    Pretty-print AI evaluation scores to stdout.

    Displays a score table per question (per-criterion scores for each condition
    and their gain), followed by a summary of averages across all questions.
    When verbose=True, the full evaluation text for each condition and criterion
    is printed after each question's score table.

    Args:
        evaluations_dir: Directory containing criterion JSONL files.
        questions_path:  Path to the questions JSONL file.
        verbose:         If True, print full evaluation texts after each question block.
    """
    records = _load_records(evaluations_dir)
    questions = _load_questions(questions_path)
    data = _organize(records)

    question_map = {q["qid"]: q for q in questions}
    question_ids = sorted(data.keys())
    border = "═" * LINE_W
    evaluator = records[0].get("evaluator_model", "unknown") if records else "unknown"

    print()
    print(border)
    print("  AI Grounding Lab — Evaluation Results".center(LINE_W))
    subtitle = (
        f"Evaluator: {evaluator}  |  {len(question_ids)} questions"
        f"  |  {len(CONDITIONS)} conditions"
    )
    print(subtitle.center(LINE_W))
    print(border)

    # ── Per-question blocks ──────────────────────────────────────────────────
    for qid in question_ids:
        q = question_map.get(qid, {})
        domain = q.get("domain", "")
        prompt = q.get("prompt", "")
        truncated = (prompt[:70] + "…") if len(prompt) > 70 else prompt

        print()
        print(f"  {qid}  [{domain}]")
        print(f"  \"{truncated}\"")
        print()
        print("  " + _header_row())
        print("  " + _separator())

        cond_scores: Dict[str, Dict[str, float]] = {}
        for condition in CONDITIONS:
            scores = {
                k: v["score"]
                for k, v in data[qid].get(condition, {}).items()
            }
            print("  " + _score_row(CONDITION_LABELS[condition], scores))
            cond_scores[condition] = scores

        gain_scores = {
            k: cond_scores.get("with-protocol", {}).get(k, 0)
               - cond_scores.get("without-protocol", {}).get(k, 0)
            for k in CRITERIA_KEYS
        }
        print("  " + _separator())
        print("  " + _score_row("Gain", gain_scores, is_gain=True))

        # ── Verbose: full evaluation texts ───────────────────────────────────
        if verbose:
            for condition in CONDITIONS:
                cond_label = CONDITION_LABELS[condition]
                divider = "─" * (LINE_W - 6 - len(cond_label))
                print()
                print(f"  ── {cond_label} {divider}")
                for crit_key in CRITERIA_KEYS:
                    entry = data[qid].get(condition, {}).get(crit_key)
                    if not entry:
                        continue
                    print()
                    print(f"  [{CRITERIA_LABELS[crit_key]}]")
                    print()
                    for text_line in entry["text"].splitlines():
                        print(f"    {text_line}")

    # ── Summary averages ─────────────────────────────────────────────────────
    print()
    print(border)
    print("  SUMMARY — Average Scores Across All Questions".center(LINE_W))
    print(border)
    print()
    print("  " + _header_row())
    print("  " + _separator())

    for condition in CONDITIONS:
        avg_scores: Dict[str, float] = {}
        for k in CRITERIA_KEYS:
            vals = [
                data[qid][condition][k]["score"]
                for qid in question_ids
                if condition in data[qid] and k in data[qid][condition]
            ]
            avg_scores[k] = sum(vals) / len(vals) if vals else 0.0
        print("  " + _score_row(CONDITION_LABELS[condition], avg_scores))

    summary_gain: Dict[str, float] = {}
    for k in CRITERIA_KEYS:
        n_with = sum(
            1 for qid in question_ids
            if "with-protocol" in data[qid] and k in data[qid]["with-protocol"]
        )
        n_without = sum(
            1 for qid in question_ids
            if "without-protocol" in data[qid] and k in data[qid]["without-protocol"]
        )
        with_avg = sum(
            data[qid]["with-protocol"][k]["score"]
            for qid in question_ids
            if "with-protocol" in data[qid] and k in data[qid]["with-protocol"]
        ) / max(n_with, 1)
        without_avg = sum(
            data[qid]["without-protocol"][k]["score"]
            for qid in question_ids
            if "without-protocol" in data[qid] and k in data[qid]["without-protocol"]
        ) / max(n_without, 1)
        summary_gain[k] = with_avg - without_avg

    print("  " + _separator())
    print("  " + _score_row("Gain", summary_gain, is_gain=True))
    print()
    print(border)
    print()


# ============================================================================
# CLI ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Pretty-print AI evaluation results.")
    parser.add_argument(
        "--dir", default="evaluations/ai",
        help="Directory containing evaluation JSONL files (default: evaluations/ai)",
    )
    parser.add_argument(
        "--questions", default="data/questions.jsonl",
        help="Path to questions JSONL file (default: data/questions.jsonl)",
    )
    parser.add_argument(
        "--verbose", action="store_true",
        help="Print full evaluation texts after each question block",
    )
    args = parser.parse_args()
    print_evaluation_results(
        evaluations_dir=Path(args.dir),
        questions_path=Path(args.questions),
        verbose=args.verbose,
    )
