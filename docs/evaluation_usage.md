# AI Evaluation System Usage Guide

## Overview

The refactored evaluation system automatically assesses answers using AI evaluators (Claude, GPT, etc.) across 5 key criteria based on the Scientific Grounding Protocol.

## Architecture

```
Input Files:
├── data/questions.jsonl          # Original questions (optional reference)
├── data/answers.jsonl            # Answers with/without protocol
└── docs/prompts/                 # 5 evaluation criteria prompts
    ├── Evidence Quality Assessment Prompt.md
    ├── Transparency Assessment Prompt.md
    ├── Reasoning Depth Assessment Prompt.md
    ├── Actionability Assessment Prompt.md
    └── Hallucination Detection Prompt.md

Processing:
└── src/evaluate_answers.py       # Main evaluation script

Output:
└── evaluations/                  # Results directory
    ├── evidence_quality_evaluations.jsonl
    ├── transparency_evaluations.jsonl
    ├── reasoning_depth_evaluations.jsonl
    ├── actionability_evaluations.jsonl
    └── uncertainty_disclosure_evaluations.jsonl
```

## Usage

### Basic Usage

Evaluate all answers using all criteria:

```bash
python3 src/evaluate_answers.py \
  --evaluator-endpoint https://api.anthropic.com/v1/messages \
  --evaluator-model claude-3-5-sonnet-20241022 \
  --api-key $ANTHROPIC_API_KEY
```

### Selective Evaluation

**Evaluate specific criterion only:**
```bash
python3 src/evaluate_answers.py \
  --criterion evidence_quality \
  --evaluator-endpoint https://api.anthropic.com/v1/messages \
  --evaluator-model claude-3-5-sonnet-20241022 \
  --api-key $ANTHROPIC_API_KEY
```

**Evaluate specific condition (with/without protocol):**
```bash
python3 src/evaluate_answers.py \
  --condition with-protocol \
  --evaluator-endpoint https://api.anthropic.com/v1/messages \
  --evaluator-model claude-3-5-sonnet-20241022 \
  --api-key $ANTHROPIC_API_KEY
```

### Using Environment Variables

Set your API key as an environment variable:

```bash
export EVALUATOR_API_KEY="your-api-key-here"

python3 src/evaluate_answers.py \
  --evaluator-endpoint https://api.anthropic.com/v1/messages \
  --evaluator-model claude-3-5-sonnet-20241022
```

### Custom File Paths

```bash
python3 src/evaluate_answers.py \
  --answers-file custom/path/answers.jsonl \
  --prompts-dir custom/prompts/ \
  --output-dir custom/output/ \
  --evaluator-endpoint https://api.anthropic.com/v1/messages \
  --evaluator-model claude-3-5-sonnet-20241022 \
  --api-key $ANTHROPIC_API_KEY
```

## API Endpoints

### Anthropic Claude
```bash
--evaluator-endpoint https://api.anthropic.com/v1/messages
--evaluator-model claude-3-5-sonnet-20241022
--api-key $ANTHROPIC_API_KEY
```

### OpenAI GPT
```bash
--evaluator-endpoint https://api.openai.com/v1/chat/completions
--evaluator-model gpt-4
--api-key $OPENAI_API_KEY
```

### Local LM Studio
```bash
--evaluator-endpoint http://localhost:1234/v1/chat/completions
--evaluator-model local-model
--api-key "not-needed"
```

## Output Format

Each evaluation is saved as a JSONL entry with the following structure:

```json
{
  "question_id": "Q1",
  "condition": "with-protocol",
  "criterion": "evidence_quality",
  "score": 5,
  "evaluation_text": "Detailed AI evaluation...",
  "evaluator_model": "claude-3-5-sonnet-20241022",
  "timestamp": "2025-11-17T12:34:56.789Z"
}
```

## Evaluation Criteria

| Criterion | Description | Score Range |
|-----------|-------------|-------------|
| **Evidence Quality** | Citations, empirical support, source reliability | 0-5 |
| **Transparency** | Clarity about limitations and uncertainties | 0-5 |
| **Reasoning Depth** | Logical coherence and analytical rigor | 0-5 |
| **Actionability** | Practical applicability of recommendations | 0-5 |
| **Uncertainty Disclosure** | Hallucination detection and confidence calibration | 0-5 |

## Example Workflow

### 1. Prepare Data
```bash
# Verify your data files exist
ls -lh data/answers.jsonl
ls -lh docs/prompts/
```

### 2. Run Evaluation
```bash
# Full evaluation (all criteria, both conditions)
export EVALUATOR_API_KEY="your-key"

python3 src/evaluate_answers.py \
  --evaluator-endpoint https://api.anthropic.com/v1/messages \
  --evaluator-model claude-3-5-sonnet-20241022
```

### 3. Review Results
```bash
# Check output files
ls -lh evaluations/

# View sample results
head -1 evaluations/evidence_quality_evaluations.jsonl | jq .
```

### 4. Analyze Scores
```bash
# Extract all scores for a specific criterion
cat evaluations/evidence_quality_evaluations.jsonl | jq '.score'

# Compare with-protocol vs without-protocol
cat evaluations/evidence_quality_evaluations.jsonl | \
  jq -r '[.question_id, .condition, .score] | @csv'
```

## Troubleshooting

### Missing API Key
```
Error: API key required. Set --api-key or EVALUATOR_API_KEY environment variable.
```
**Solution:** Set your API key using `--api-key` or export `EVALUATOR_API_KEY`

### Invalid JSON in answers.jsonl
```
json.JSONDecodeError: Invalid JSON on line 3
```
**Solution:** Validate your JSONL file - each line must be valid JSON

### Missing Required Field
```
KeyError: Missing required field 'question' on line 2
```
**Solution:** Ensure each line contains: `question_id`, `question`, `answer_without_protocol`, `answer_with_protocol`

### API Rate Limiting
If you encounter rate limits, consider:
- Evaluating one criterion at a time (`--criterion evidence_quality`)
- Evaluating one condition at a time (`--condition with-protocol`)
- Adding delays between requests (modify script if needed)

## Next Steps

After running evaluations, you can:

1. **Aggregate Results:** Use `src/aggregate.py` to compute summary statistics
2. **Compare Conditions:** Analyze score differences between with/without protocol
3. **Visualize:** Create charts showing performance across criteria
4. **Export:** Convert JSONL to CSV for spreadsheet analysis

## Notes

- The script automatically creates the `evaluations/` directory if it doesn't exist
- Each criterion generates a separate JSONL file for easier analysis
- Scores are extracted automatically using regex patterns; verify accuracy
- All timestamps are in UTC ISO 8601 format
