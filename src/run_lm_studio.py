#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Oct  5 15:38:07 2025

@author: Monica Guimaraes
"""
#!/usr/bin/env python3
"""
Run prompts through a local LM Studio server using the OpenAI-compatible SDK.
Generates a JSONL file with responses for downstream evaluation.
"""

import argparse, json, os, pathlib, time, datetime
from openai import OpenAI

def iter_prompts(path):
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                yield json.loads(line)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base-url", default="http://localhost:1234/v1", help="LM Studio API base URL")
    ap.add_argument("--model", required=True)
    ap.add_argument("--prompts", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--temperature", type=float, default=0.2)
    ap.add_argument("--max-tokens", type=int, default=1024)
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()

    client = OpenAI(base_url=args.base_url, api_key="not-needed")
    pathlib.Path(os.path.dirname(args.out) or ".").mkdir(parents=True, exist_ok=True)

    with open(args.out, "w", encoding="utf-8") as fout:
        for row in iter_prompts(args.prompts):
            qid, condition = row["qid"], row["condition"]
            t0 = time.time()
            try:
                response = client.chat.completions.create(
                    model=args.model,
                    messages=[{"role": "user", "content": row["prompt_text"]}],
                    temperature=args.temperature,
                    max_tokens=args.max_tokens,
                    seed=args.seed
                )
                text = response.choices[0].message.content
                latency_ms = int((time.time() - t0) * 1000)
                tokens_out = getattr(response, "usage", {}).get("completion_tokens", None)
            except Exception as e:
                text = f"[ERROR] {e}"
                latency_ms, tokens_out = None, None

            outrow = {
                "run_id": f"{datetime.datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')}_{qid}_{args.model}_{condition}_seed{args.seed}",
                "timestamp_utc": datetime.datetime.utcnow().isoformat(),
                "qid": qid,
                "condition": condition,
                "model": {"name": args.model, "source": "LMStudio"},
                "gen_params": {
                    "temperature": args.temperature,
                    "max_tokens": args.max_tokens,
                    "seed": args.seed
                },
                "prompt": {
                    "wrapper": row.get("wrapper"),
                    "full_prompt_text": row["prompt_text"]
                },
                "response": {
                    "text": text,
                    "tokens_out": tokens_out,
                    "latency_ms": latency_ms
                }
            }
            json.dump(outrow, fout)
            fout.write("\n")
            print(f"[run_lmstudio] {qid} {condition} -> {len(text)} chars, {latency_ms} ms")

if __name__ == "__main__":
    main()

