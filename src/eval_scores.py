#!/usr/bin/env python3
"""
Score LLM responses using an external evaluator API.

Supports two modes:
1. Single-answer scoring: Score each response individually against rubric criteria
2. Pairwise comparison: Compare two responses (with/without protocol)

Usage Examples:

Single-answer scoring:
    python3 src/eval_scores.py \
      --answers runs/raw/2025-10-05_with_proto_llama3.jsonl \
      --out runs/evals/2025-10-05_with_proto_llama3.eval.jsonl \
      --rubric protocol/evaluation_scoring_rubric.md \
      --eval-endpoint https://api.openai.com/v1/chat/completions \
      --eval-model gpt-4o-mini

Pairwise scoring:
    python3 src/eval_scores.py \
      --answers runs/raw/2025-10-05_without_proto_llama3.jsonl \
      --answers-b runs/raw/2025-10-05_with_proto_llama3.jsonl \
      --out runs/evals/2025-10-05_pairwise_llama3.eval.jsonl \
      --rubric protocol/evaluation_scoring_rubric.md \
      --pairwise \
      --eval-endpoint https://api.openai.com/v1/chat/completions \
      --eval-model gpt-4o-mini

Author: Monica Guimaraes
Created: 2025-10-05
"""

import argparse
import hashlib
import json
import os
import pathlib
import re
import requests

EVAL_HEADER = """You are an expert evaluator. Use the rubric below to score the model’s answer.
Return STRICT JSON only (no prose), with the keys and numeric ranges indicated.
"""

# Default JSON spec we expect back
JSON_SPEC = """Return strict JSON:
{
  "scores": {
    "evidence_quality": <0-5>,
    "transparency": <0-5>,
    "reasoning_depth": <0-5>,
    "actionability": <0-5>,
    "uncertainty_disclosure": <0-5>,
    "total": <0-25>
  },
  "justifications": {
    "evidence_quality": "...",
    "transparency": "...",
    "reasoning_depth": "...",
    "actionability": "...",
    "uncertainty_disclosure": "..."
  }
}"""

SINGLE_ANSWER_BLOCK = """
QUESTION: {qid} — {question}
CONDITION: {condition}
MODEL: {model_name}  temp={temperature}  seed={seed}

ANSWER:
<<<
{answer_text}
>>>
"""

PAIRWISE_BLOCK = """
PAIRWISE COMPARISON (A vs. B)
Focus on Evidence Quality, Transparency, Reasoning Depth, Actionability, and Uncertainty Disclosure.

Return strict JSON:
{
  "preference": "A" | "B" | "no-preference",
  "reason": "brief explanation focusing on rubric criteria"
}

ANSWER A (usually WITHOUT protocol):
<<<
{a_text}
>>>

ANSWER B (usually WITH protocol):
<<<
{b_text}
>>>
"""

def iter_jsonl(path):
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                yield json.loads(line)

def load_qmap(path):
    qmap = {}
    if not path or not os.path.exists(path):
        return qmap
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                o = json.loads(line)
                qmap[o["qid"]] = o["prompt"]
    return qmap

def load_rubric(path):
    with open(path, "r", encoding="utf-8") as f:
        text = f.read().strip()
    # Fingerprint for comparability
    fp = hashlib.sha256(text.encode("utf-8")).hexdigest()
    return text, fp

def call_eval_api(endpoint, api_key, model, prompt, max_tokens=1000):
    headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.0,
        "max_tokens": max_tokens
    }
    r = requests.post(endpoint, json=payload, headers=headers, timeout=600)
    r.raise_for_status()
    data = r.json()
    text = data["choices"][0]["message"]["content"]
    return text

def parse_json_strict(text):
    """Try to parse JSON, handle code fences and minor wrappers gracefully."""
    # Direct parse
    try:
        return json.loads(text)
    except Exception:
        pass
    # Extract first JSON object within fences or raw text
    m = re.search(r"\{.*\}", text, re.S)
    if m:
        return json.loads(m.group(0))
    raise ValueError(f"Evaluator did not return JSON:\n{text}")

def build_single_prompt(rubric_text, qid, question, row):
    prompt = (
        EVAL_HEADER
        + "\n\n[RUBRIC]\n"
        + rubric_text
        + "\n\n[OUTPUT FORMAT]\n"
        + JSON_SPEC
        + "\n\n[INSTANCE]\n"
        + SINGLE_ANSWER_BLOCK.format(
            qid=qid,
            question=question,
            condition=row["condition"],
            model_name=row["model"]["name"],
            temperature=row["gen_params"]["temperature"],
            seed=row["gen_params"]["seed"],
            answer_text=row["response"]["text"],
        )
    )
    return prompt

def build_pairwise_prompt(rubric_text, a_row, b_row, qid, question):
    prompt = (
        EVAL_HEADER
        + "\n\n[RUBRIC]\n"
        + rubric_text
        + "\n\n[PAIRWISE TASK]\n"
        + PAIRWISE_BLOCK.format(
            a_text=a_row["response"]["text"],
            b_text=b_row["response"]["text"],
        )
    )
    return prompt

def index_runs_by_key(rows):
    """Index by (qid, model_name, seed, condition) to make pairwise lookup easy."""
    idx = {}
    for r in rows:
        key = (r["qid"], r["model"]["name"], r["gen_params"]["seed"], r["condition"])
        idx[key] = r
    return idx

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--answers", required=True, help="JSONL from run_lmstudio.py (single-condition or both)")
    ap.add_argument("--out", required=True)
    ap.add_argument("--rubric", required=True, help="Path to evaluation_scoring_rubric.md")
    ap.add_argument("--questions", default="data/questions.jsonl")
    ap.add_argument("--eval-endpoint", default="https://api.openai.com/v1/chat/completions")
    ap.add_argument("--eval-model", default="gpt-4o-mini")
    ap.add_argument("--eval-api-key", default=os.getenv("EVAL_API_KEY"))
    ap.add_argument("--pairwise", action="store_true", help="If set, attempt A/B comparison for matching with/without runs")
    ap.add_argument("--answers-b", default=None, help="Optional second JSONL for pairwise (e.g., with_protocol). If omitted, will infer from --answers by pairing within the same file.")
    args = ap.parse_args()

    rubric_text, rubric_fp = load_rubric(args.rubric)
    qmap = load_qmap(args.questions)

    pathlib.Path(os.path.dirname(args.out) or ".").mkdir(parents=True, exist_ok=True)

    rows_a = list(iter_jsonl(args.answers))
    rows_b = list(iter_jsonl(args.answers_b)) if args.answers_b else rows_a

    # For pairwise, index to find matching A/B by (qid, model, seed)
    idx_a = index_runs_by_key(rows_a)
    idx_b = index_runs_by_key(rows_b)

    with open(args.out, "w", encoding="utf-8") as fout:
        if args.pairwise:
            # Pair WITHOUT vs WITH (or any two conditions), matching by qid+model+seed
            # We try A=without-protocol, B=with-protocol if present; otherwise any two distinct conditions.
            for key, a_row in idx_a.items():
                qid, model_name, seed, cond_a = key
                # Prefer the complementary condition
                desired = "with-protocol" if cond_a == "without-protocol" else "without-protocol"
                b_key = (qid, model_name, seed, desired)
                b_row = idx_b.get(b_key)
                if b_row is None:
                    # Fallback: any other condition for same (qid, model, seed)
                    candidates = [k for k in idx_b.keys() if k[:3] == key[:3] and k[3] != cond_a]
                    if candidates:
                        b_row = idx_b[candidates[0]]
                if b_row is None:
                    continue  # no pair found

                question = qmap.get(qid, qid)
                prompt = build_pairwise_prompt(rubric_text, a_row, b_row, qid, question)
                raw = call_eval_api(args.eval_endpoint, args.eval_api_key, args.eval_model, prompt)
                result = parse_json_strict(raw)

                out = {
                    "pairwise_of": [a_row["run_id"], b_row["run_id"]],
                    "qid": qid,
                    "model": model_name,
                    "seed": seed,
                    "conditions": [cond_a, b_row["condition"]],
                    "evaluator_model": args.eval_model,
                    "rubric_fingerprint": rubric_fp,
                    "pairwise": {
                        "preference": result.get("preference"),
                        "reason": result.get("reason", "")
                    }
                }
                json.dump(out, fout); fout.write("\n")
                print(f"[eval_scores] Pairwise {qid} {model_name} seed={seed} -> pref={out['pairwise']['preference']}")
        else:
            # Single-answer scoring for every row
            for row in rows_a:
                qid = row["qid"]
                question = qmap.get(qid, qid)
                prompt = build_single_prompt(rubric_text, qid, question, row)
                raw = call_eval_api(args.eval_endpoint, args.eval_api_key, args.eval_model, prompt)
                result = parse_json_strict(raw)

                scores = result.get("scores", {})
                if "total" not in scores and scores:
                    scores["total"] = sum(scores.get(k, 0) for k in [
                        "evidence_quality", "transparency", "reasoning_depth", "actionability", "uncertainty_disclosure"
                    ])

                out = {
                    "run_id": row["run_id"],
                    "qid": qid,
                    "condition": row["condition"],
                    "model": row["model"]["name"],
                    "seed": row["gen_params"]["seed"],
                    "evaluator_model": args.eval_model,
                    "rubric_fingerprint": rubric_fp,
                    "scores": scores,
                    "justifications": result.get("justifications", {})
                }
                json.dump(out, fout); fout.write("\n")
                print(f"[eval_scores] Scored {qid} ({row['condition']}) -> total={scores.get('total')}")

if __name__ == "__main__":
    main()
