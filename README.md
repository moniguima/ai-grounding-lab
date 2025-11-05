# AI Grounding Lab

A reproducible, open-source framework for testing how a **Scientific Grounding Protocol (SGP)** affects LLM answer quality across domains.  
**Goal:** turn plausible outputs into **verifiable, transparent, and actionable** responses.

## What’s inside

- **Protocol:** `protocol/SGP_compact.md` – compact prompt wrapper for models without system role
- **Questions:** `data/questions.jsonl` – canonical test prompts (Q1–Q5)
- **Prompt composer:** `src/compose_prompts.py` – builds with/without protocol prompts
- **Runner:** `src/run_lmstudio.py` – queries local LMStudio (OpenAI-compatible API)
- **Evaluator:** `src/eval_scores.py` – scores answers with rubric using an external model (Claude/GPT)
- **Aggregator:** `src/aggregate.py` – merges scores, prints summary stats

## Repo layout

ai-grounding-lab/
├─ README.md
├─ protocol/
│ └─ SGP_compact.md
├─ data/
│ ├─ questions.jsonl
│ └─ prompts/
│ ├─ with_protocol.jsonl
│ └─ without_protocol.jsonl
├─ runs/
│ ├─ raw/
│ └─ evals/
├─ src/
│ ├─ compose_prompts.py
│ ├─ run_lmstudio.py
│ ├─ eval_scores.py
│ └─ aggregate.py
└─ configs/
└─ run.yaml (optional, future)


## Quick start

1) **Create prompts**
```bash
python3 src/compose_prompts.py \
  --questions data/questions.jsonl \
  --protocol protocol/SGP_compact.md \
  --out-dir data/prompts


