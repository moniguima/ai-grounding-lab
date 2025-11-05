#!/usr/bin/env python3
"""
Aggregate evaluation results and compute summary statistics.

Reads JSONL evaluation files and groups results by specified keys
(model, qid, condition, etc.), computing mean and standard deviation
for each scoring criterion.

Author: Monica Guimaraes
Created: 2025-10-05
"""

import argparse
import glob
import json
import os
import statistics as stats
from collections import defaultdict

def load_evals(path_or_dir):
    files = []
    if os.path.isdir(path_or_dir):
        files = sorted(glob.glob(os.path.join(path_or_dir, "*.jsonl")))
    else:
        files = [path_or_dir]
    for fp in files:
        with open(fp, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    yield json.loads(line)

def summarize(rows, group_keys):
    groups = defaultdict(list)
    for r in rows:
        key = tuple(r.get(k) for k in group_keys)
        groups[key].append(r)
    table = []
    for key, items in groups.items():
        totals = [it["scores"].get("total", 0) for it in items]
        row = {k:v for k,v in zip(group_keys, key)}
        row.update({
            "n": len(items),
            "total_mean": round(stats.mean(totals), 2) if totals else None,
            "total_std": round(stats.pstdev(totals), 2) if len(totals) > 1 else 0.0,
        })
        # Optional: per-criterion means
        for crit in ["evidence_quality","transparency","reasoning_depth","actionability","uncertainty_disclosure"]:
            vals = [it["scores"].get(crit, 0) for it in items]
            row[f"{crit}_mean"] = round(stats.mean(vals), 2) if vals else None
        table.append(row)
    return table

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--evals", required=True, help="JSONL file or directory")
    ap.add_argument("--by", default="model,qid,condition", help="Comma-separated grouping keys")
    args = ap.parse_args()

    rows = list(load_evals(args.evals))
    keys = [k.strip() for k in args.by.split(",") if k.strip()]
    summary = summarize(rows, keys)

    # Pretty print as TSV
    cols = keys + ["n","total_mean","total_std",
                   "evidence_quality_mean","transparency_mean","reasoning_depth_mean","actionability_mean","uncertainty_disclosure_mean"]
    print("\t".join(cols))
    for r in summary:
        print("\t".join(str(r.get(c,"")) for c in cols))

if __name__ == "__main__":
    main()
