# AI Grounding Lab

A reproducible, open-source framework for testing how a **Scientific Grounding Protocol (SGP)** affects LLM answer quality across domains.
**Goal:** turn plausible outputs into **verifiable, transparent, and actionable** responses.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![NeMo Guardrails](https://img.shields.io/badge/NeMo%20Guardrails-%E2%89%A50.9.0-76b900.svg)](https://github.com/NVIDIA-NeMo/Guardrails)
[![Status: In Development](https://img.shields.io/badge/status-in%20development-orange.svg)]()

> **Note:** This project is actively under development. Features and documentation may change.

## What's Inside

- **Protocol:** `protocol/SGP_compact.md` – compact prompt wrapper for models without system role
- **Questions:** `data/questions.jsonl` – canonical test prompts (Q1–Q5) across domains
- **Prompt composer:** `src/compose_prompts.py` – builds prompts for all three experimental conditions
- **Runner:** `src/run_lm_studio.py` – queries local LM Studio (OpenAI-compatible API)
- **Guardrails Runner:** `src/run_with_guardrails.py` – runs Condition C through NeMo Guardrails (SGP enforced at runtime)
- **AI Evaluator:** `src/eval_scores.py` – scores answers using a rubric and an external model (Claude/GPT)
- **Criterion Evaluator:** `src/evaluate_answers.py` – AI evaluation using criterion-specific prompts
- **Human Forms Generator:** `src/generate_evaluation_forms.py` – creates pre-filled forms for human raters
- **Human Score Collector:** `src/collect_human_scores.py` – extracts scores from completed human forms
- **Aggregator:** `src/aggregate.py` – merges scores, prints summary stats

## Repository Structure

```
ai-grounding-lab/
├── README.md
├── LICENSE (MIT)
├── CONTRIBUTING.md
├── requirements.txt
├── protocol/
│   ├── SGP_compact.md              # Compact protocol for any model
│   └── scientific_grounding_protocol.md  # Full protocol specification
├── data/
│   ├── questions.jsonl             # Test questions (Q1-Q5)
│   └── answers.jsonl               # Sample answers (with/without protocol)
├── docs/
│   ├── AI_prompts/                 # Criterion-specific AI evaluation prompts
│   ├── human_rubrics/              # Rubrics for human evaluators
│   ├── EVALUATION_GUIDE.md         # Guide for automated AI evaluation
│   └── HUMAN_EVALUATION_GUIDE.md   # Guide for human validation
├── guardrails/
│   ├── config.yml                  # NeMo LLMRails config (model/endpoint patched at runtime)
│   ├── rails.co                    # Colang flows: domain boundary + SGP compliance rails
│   └── actions.py                  # Deterministic keyword/regex rail actions
├── runs/
│   ├── raw/                        # Model responses (JSONL)
│   └── evals/                      # Evaluation scores (JSONL)
└── src/
    ├── compose_prompts.py          # Generate prompt variants (all three conditions)
    ├── run_lm_studio.py            # Run model inference (Conditions A & B)
    ├── run_with_guardrails.py      # Run model inference via NeMo Guardrails (Condition C)
    ├── eval_scores.py              # Score responses (automated)
    ├── evaluate_answers.py         # AI evaluation with criterion prompts
    ├── generate_evaluation_forms.py # Generate human evaluation forms
    ├── collect_human_scores.py     # Collect human evaluation scores
    └── aggregate.py                # Aggregate and compare results
```

## Installation

### Prerequisites

- Python 3.10 or higher (required by NeMo Guardrails)
- [LM Studio](https://lmstudio.ai/) (for local model inference) or any OpenAI-compatible API
- API key for evaluation model (OpenAI GPT-4, Anthropic Claude, etc.)
- C++ compiler (required by NeMo Guardrails' `annoy` dependency — usually pre-installed on Linux/macOS)

### Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/moniguima/ai-grounding-lab.git
   cd ai-grounding-lab
   ```

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up your evaluation API key:**
   ```bash
   export EVAL_API_KEY="your-api-key-here"
   ```

## Quick Start

### Full Workflow Example

Run a complete experiment across all three conditions — baseline, in-context protocol, and programmatic guardrails:

**Step 1: Compose prompts**
```bash
python3 src/compose_prompts.py \
  --questions data/questions.jsonl \
  --protocol protocol/SGP_compact.md \
  --out-dir data/prompts \
  --guardrails
```
This creates three files in `data/prompts/`: `without_protocol.jsonl`, `with_protocol.jsonl`, and `with_guardrails.jsonl`.

**Step 2: Run model inference (without protocol)**
```bash
python3 src/run_lm_studio.py \
  --model "llama-3.1-8b" \
  --prompts data/prompts/without_protocol.jsonl \
  --out runs/raw/without_protocol_llama3.jsonl \
  --temperature 0.2 \
  --max-tokens 1024 \
  --seed 42
```

**Step 3: Run model inference (with protocol)**
```bash
python3 src/run_lm_studio.py \
  --model "llama-3.1-8b" \
  --prompts data/prompts/with_protocol.jsonl \
  --out runs/raw/with_protocol_llama3.jsonl \
  --temperature 0.2 \
  --max-tokens 1024 \
  --seed 42
```

**Step 3b: Run model inference (with guardrails — Condition C)**
```bash
python3 src/run_with_guardrails.py \
  --model "llama-3.1-8b" \
  --prompts data/prompts/with_guardrails.jsonl \
  --out runs/raw/with_guardrails_llama3.jsonl \
  --temperature 0.2 \
  --max-tokens 1024 \
  --seed 42
```
NeMo Guardrails enforces SGP constraints programmatically via an input rail (domain boundary check) and an output rail (evidence, uncertainty, and transparency check). The output JSONL includes a `guardrails_trace` field recording which rails, if any, were triggered.

**Step 4: Evaluate responses**
```bash
# Score without-protocol responses
python3 src/eval_scores.py \
  --answers runs/raw/without_protocol_llama3.jsonl \
  --out runs/evals/without_protocol_llama3.eval.jsonl \
  --rubric protocol/evaluation_scoring_rubric.md \
  --questions data/questions.jsonl \
  --eval-endpoint https://api.openai.com/v1/chat/completions \
  --eval-model gpt-4o-mini

# Score with-protocol responses
python3 src/eval_scores.py \
  --answers runs/raw/with_protocol_llama3.jsonl \
  --out runs/evals/with_protocol_llama3.eval.jsonl \
  --rubric protocol/evaluation_scoring_rubric.md \
  --questions data/questions.jsonl \
  --eval-endpoint https://api.openai.com/v1/chat/completions \
  --eval-model gpt-4o-mini
```

**Step 4b: Evaluate guardrails responses**
```bash
python3 src/eval_scores.py \
  --answers runs/raw/with_guardrails_llama3.jsonl \
  --out runs/evals/with_guardrails_llama3.eval.jsonl \
  --rubric protocol/evaluation_scoring_rubric.md \
  --questions data/questions.jsonl \
  --eval-endpoint https://api.openai.com/v1/chat/completions \
  --eval-model gpt-4o-mini
```

**Step 5: Aggregate results**
```bash
python3 src/aggregate.py \
  --evals runs/evals/ \
  --by condition,qid
```

This outputs a TSV table showing mean scores across all three conditions (`without-protocol`, `with-protocol`, `with-guardrails`) and question.

### Pairwise Comparison Mode

For direct A/B comparisons:

```bash
python3 src/eval_scores.py \
  --answers runs/raw/without_protocol_llama3.jsonl \
  --answers-b runs/raw/with_protocol_llama3.jsonl \
  --out runs/evals/pairwise_llama3.eval.jsonl \
  --rubric protocol/evaluation_scoring_rubric.md \
  --pairwise \
  --eval-endpoint https://api.openai.com/v1/chat/completions \
  --eval-model gpt-4o-mini
```

## Guardrails Layer — Condition C

Condition C uses [NVIDIA NeMo Guardrails](https://github.com/NVIDIA-NeMo/Guardrails) to enforce SGP constraints programmatically at runtime. The same plain question is sent to the model — no SGP text in the prompt — and compliance is enforced by the rail layer.

### Rails

**Input rail — Domain Boundary Enforcement**

Validates that each question falls within the five SGP domains: cognitive science, ML factuality, HCI, health tech, and EU policy. Questions outside these domains are rejected with a structured refusal before reaching the model. None of the five canonical lab questions trigger this rail — it acts as a safety boundary for open-ended use.

**Output rail — SGP Compliance**

Validates generated responses against three sub-checks, all of which must pass:

- **Evidence** — response contains at least one research marker (e.g. `study`, `findings`, `et al`, `doi:`, `peer-reviewed`)
- **Uncertainty** — response contains at least one hedging or limitation marker (e.g. `limitation`, `may`, `however`, `context-dependent`)
- **Transparency** — response does not match any absolute-claim pattern (e.g. `always`, `definitively proves`, `proven fact`)

When an output rail fires, the response is halted and a `[SGP_RAIL_TRIGGERED]` sentinel is recorded in the `guardrails_trace` field of the output JSONL.

### Design Decisions

**Deterministic actions, not LLM self-check.** The rails use keyword and regex matching rather than a secondary safety model. This ensures full reproducibility across experimental runs — LLM-based evaluation would introduce variability that confounds the scoring comparison across conditions.

**No NVIDIA API key required.** Models are served locally via LM Studio. No NVIDIA cloud authentication is involved.

**No downstream modifications.** The output schema is identical to `run_lm_studio.py` with one additional `guardrails_trace` field, so `eval_scores.py` and `aggregate.py` work unchanged.

### Output Schema

Identical to `run_lm_studio.py` with one additional field:

```json
{
  "run_id": "...",
  "qid": "Q1",
  "condition": "with-guardrails",
  "model": { "name": "llama-3.1-8b", "source": "LMStudio_NeMo" },
  "gen_params": { "temperature": 0.2, "max_tokens": 1024, "seed": 42 },
  "prompt": { "wrapper": "NeMo_SGP", "full_prompt_text": "..." },
  "response": { "text": "...", "tokens_out": null, "latency_ms": 1234 },
  "guardrails_trace": {
    "input_rail_triggered": false,
    "output_rail_triggered": false,
    "rail_violated": null
  }
}
```

## Human Validation Workflow

Human evaluation validates AI scores and provides an inter-rater reliability check. See [`docs/HUMAN_EVALUATION_GUIDE.md`](docs/HUMAN_EVALUATION_GUIDE.md) for full details.

**Step 1: Generate evaluation forms**
```bash
python3 src/generate_evaluation_forms.py \
  --output-dir evaluations/human/forms \
  --evaluator-name "YourName"
```
This creates 50 forms (5 questions × 2 conditions × 5 criteria).

**Step 2: Complete forms**

Open forms in any markdown editor and fill in scores following the rubrics in `docs/human_rubrics/`.

**Step 3: Collect scores**
```bash
python3 src/collect_human_scores.py \
  --forms-dir evaluations/human/forms \
  --output-dir evaluations/human
```

**Step 4: Compare with AI scores**

Compare `evaluations/human/human_scores.jsonl` against `runs/evals/` to calculate inter-rater agreement between human and AI evaluations.

## Evaluation Criteria

Responses are scored on five dimensions (0-5 scale each):

1. **Evidence Quality** – Citations, peer-reviewed sources, verifiability
2. **Transparency** – Limitations, boundary conditions, biases disclosed
3. **Reasoning Depth** – Causal explanations, mechanisms, alternative views
4. **Actionability** – Concrete, context-aware recommendations
5. **Uncertainty Disclosure** – Confidence levels, research gaps, unknowns

See `docs/human_rubrics/` for detailed scoring criteria per dimension.

## Configuration Options

### LM Studio Runner
- `--base-url`: API endpoint (default: `http://localhost:1234/v1`)
- `--temperature`: Sampling temperature (default: 0.2)
- `--max-tokens`: Maximum response length (default: 1024)
- `--seed`: Random seed for reproducibility (default: 42)

### Guardrails Runner
- `--guardrails-config`: Path to guardrails config directory (default: `guardrails/`)
- `--base-url`: LM Studio API endpoint (default: `http://localhost:1234/v1`)
- `--temperature`, `--max-tokens`, `--seed`: same as LM Studio runner

### Evaluator
- `--eval-endpoint`: Evaluator API endpoint
- `--eval-model`: Model to use for evaluation (e.g., `gpt-4o-mini`, `claude-3-5-sonnet`)
- `--eval-api-key`: API key (or use `EVAL_API_KEY` environment variable)
- `--pairwise`: Enable pairwise comparison mode

## Research Background

The **Scientific Grounding Protocol (SGP)** is a structured set of constraints designed to enhance LLM outputs by:
- Requiring peer-reviewed evidence with recency guidelines
- Mandating transparency about limitations and uncertainties
- Enforcing actionability tied to evidence strength
- Promoting deep reasoning with alternative explanations

This framework tests SGP enforcement across three experimental conditions:

| Condition | How SGP is enforced | Key question |
|-----------|--------------------|-|
| **A — without-protocol** | Not at all | Baseline quality |
| **B — with-protocol** | In-context prompt text (`SGP_compact.md`) | Does prompting help? |
| **C — with-guardrails** | Programmatically via NeMo Guardrails | Does architecture help? |

Comparing B and C isolates the effect of *where* enforcement happens — in the prompt versus in the inference pipeline — across diverse domains (cognitive science, machine learning, HCI, health tech, EU policy).

## Citation

If you use this framework in your research, please cite:

```bibtex
@software{ai_grounding_lab_2025,
  author = {Guimaraes, Monica},
  title = {AI Grounding Lab: A Framework for Testing Scientific Grounding Protocols in LLMs},
  year = {2025},
  url = {https://github.com/moniguima/ai-grounding-lab}
}
```

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

Areas of interest:
- Additional test questions across new domains
- Alternative protocol variants
- Evaluation rubric refinements
- Statistical analysis tools
- Integration with other LLM APIs

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Protocol design inspired by evidence-based medicine and scientific communication best practices
- Evaluation framework adapted from automated fact-checking and AI alignment research
- Guardrails layer built with [NVIDIA NeMo Guardrails](https://github.com/NVIDIA-NeMo/Guardrails)

## Contact

**Monica Guimaraes**
- GitHub: [@moniguima](https://github.com/moniguima)

For questions, issues, or collaboration inquiries, please open an issue on GitHub.

---

**Version:** 1.1.0
**Last Updated:** 2026-03-18
