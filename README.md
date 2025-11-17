# AI Grounding Lab

A reproducible, open-source framework for testing how a **Scientific Grounding Protocol (SGP)** affects LLM answer quality across domains.
**Goal:** turn plausible outputs into **verifiable, transparent, and actionable** responses.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

## What's Inside

- **Protocol:** `protocol/SGP_compact.md` – compact prompt wrapper for models without system role
- **Questions:** `data/questions.jsonl` – canonical test prompts (Q1–Q5) across domains
- **Prompt composer:** `src/compose_prompts.py` – builds with/without protocol prompts
- **Runner:** `src/run_lm_studio.py` – queries local LM Studio (OpenAI-compatible API)
- **Evaluator:** `src/eval_scores.py` – scores answers with rubric using an external model (Claude/GPT)
- **Aggregator:** `src/aggregate.py` – merges scores, prints summary stats

## Repository Structure

```
ai-grounding-lab/
├── README.md
├── LICENSE (MIT)
├── requirements.txt
├── protocol/
│   ├── SGP_compact.md              # Compact protocol for any model
│   ├── evaluation_scoring_rubric.md
│   └── scientific_grounding_protocol.md
├── data/
│   ├── questions.jsonl             # Test questions (Q1-Q5)
│   └── prompts/                    # AI Prompts to evaluate resultscompose_prompts.py
├── docs/
│   └── rubrics/                    # Human rubrics to evaluate results
├── runs/
│   ├── raw/                        # Model responses (JSONL)
│   └── evals/                      # Evaluation scores (JSONL)
├── src/
│   ├── compose_prompts.py          # Generate prompt variants
│   ├── run_lm_studio.py            # Run model inference
│   ├── eval_scores.py              # Score responses
│   └── aggregate.py                # Aggregate results
└── docs/                           # Additional documentation
```

## Installation

### Prerequisites

- Python 3.8 or higher
- [LM Studio](https://lmstudio.ai/) (for local model inference) or any OpenAI-compatible API
- API key for evaluation model (OpenAI GPT-4, Anthropic Claude, etc.)

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

Run a complete experiment comparing responses with and without the Scientific Grounding Protocol:

**Step 1: Compose prompts**
```bash
python3 src/compose_prompts.py \
  --questions data/questions.jsonl \
  --protocol protocol/SGP_compact.md \
  --out-dir data/prompts
```
This creates `with_protocol.jsonl` and `without_protocol.jsonl` in `data/prompts/`.

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

**Step 5: Aggregate results**
```bash
python3 src/aggregate.py \
  --evals runs/evals/ \
  --by condition,qid
```

This will output a TSV table showing mean scores by condition (with/without protocol) and question.

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

## Evaluation Criteria

Responses are scored on five dimensions (0-5 scale each):

1. **Evidence Quality** – Citations, peer-reviewed sources, verifiability
2. **Transparency** – Limitations, boundary conditions, biases disclosed
3. **Reasoning Depth** – Causal explanations, mechanisms, alternative views
4. **Actionability** – Concrete, context-aware recommendations
5. **Uncertainty Disclosure** – Confidence levels, research gaps, unknowns

See `protocol/evaluation_scoring_rubric.md` for detailed scoring criteria.

## Configuration Options

### LM Studio Runner
- `--base-url`: API endpoint (default: `http://localhost:1234/v1`)
- `--temperature`: Sampling temperature (default: 0.2)
- `--max-tokens`: Maximum response length (default: 1024)
- `--seed`: Random seed for reproducibility (default: 42)

### Evaluator
- `--eval-endpoint`: Evaluator API endpoint
- `--eval-model`: Model to use for evaluation (e.g., `gpt-4o-mini`, `claude-3-5-sonnet`)
- `--eval-api-key`: API key (or use `EVAL_API_KEY` environment variable)
- `--pairwise`: Enable pairwise comparison mode

## Research Background

The **Scientific Grounding Protocol (SGP)** is a structured prompt template designed to enhance LLM outputs by:
- Requiring peer-reviewed evidence with recency guidelines
- Mandating transparency about limitations and uncertainties
- Enforcing actionability tied to evidence strength
- Promoting deep reasoning with alternative explanations

This framework allows researchers to empirically test whether such protocols improve answer quality across diverse domains (cognitive science, machine learning, HCI, health tech, policy).

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

## Contact

**Monica Guimaraes**
- GitHub: [@moniguima](https://github.com/moniguima)

For questions, issues, or collaboration inquiries, please open an issue on GitHub.

---

**Version:** 1.0.0
**Last Updated:** 2025-11-05
