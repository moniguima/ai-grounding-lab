# AI Evaluation Automation Guide

This guide explains how to use the `evaluate_answers.py` script to automatically evaluate answers using AI.

## Overview

The script evaluates answers from `docs/questions_and_answers.md` using the detailed evaluation prompts in `docs/prompts/` and an external AI API (Claude or GPT).

## Prerequisites

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Get an API key:**
   - For Anthropic Claude: https://console.anthropic.com/
   - For OpenAI GPT: https://platform.openai.com/api-keys

3. **Set your API key:**
   ```bash
   export EVALUATOR_API_KEY="your-api-key-here"
   ```

## Basic Usage

### Evaluate All Criteria (Both Conditions)

```bash
python3 src/evaluate_answers.py \
  --evaluator-endpoint https://api.anthropic.com/v1/messages \
  --evaluator-model claude-3-5-sonnet-20241022 \
  --api-key $EVALUATOR_API_KEY
```

### Evaluate Specific Criterion

```bash
python3 src/evaluate_answers.py \
  --evaluator-endpoint https://api.openai.com/v1/chat/completions \
  --evaluator-model gpt-4 \
  --api-key $EVALUATOR_API_KEY \
  --criterion evidence_quality
```

### Evaluate Only One Condition

```bash
python3 src/evaluate_answers.py \
  --evaluator-endpoint https://api.anthropic.com/v1/messages \
  --evaluator-model claude-3-5-sonnet-20241022 \
  --api-key $EVALUATOR_API_KEY \
  --condition with-protocol
```

## Command-Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `--qa-file` | Path to questions and answers file | `docs/questions_and_answers.md` |
| `--prompts-dir` | Directory with evaluation prompts | `docs/prompts` |
| `--output-dir` | Output directory for results | `evaluations/ai` |
| `--criterion` | Which criterion to evaluate | `all` |
| `--evaluator-endpoint` | API endpoint URL | *Required* |
| `--evaluator-model` | Model name | *Required* |
| `--api-key` | API key (or use `EVALUATOR_API_KEY` env var) | `$EVALUATOR_API_KEY` |
| `--condition` | Which condition: `with-protocol`, `without-protocol`, or `both` | `both` |

## Available Criteria

1. **evidence_quality** - Citation quality, peer-review, verifiability
2. **transparency** - Limitations, boundary conditions, biases
3. **reasoning_depth** - Causal explanations, mechanisms
4. **actionability** - Practical recommendations, implementation
5. **uncertainty_disclosure** - Confidence levels, research gaps

## API Endpoints

### Anthropic Claude
```bash
--evaluator-endpoint https://api.anthropic.com/v1/messages \
--evaluator-model claude-3-5-sonnet-20241022
```

### OpenAI GPT
```bash
--evaluator-endpoint https://api.openai.com/v1/chat/completions \
--evaluator-model gpt-4
```

## Output Format

Results are saved in `evaluations/ai/` (or your specified `--output-dir`):

### Per-Criterion Files
Each criterion generates a JSONL file: `{criterion}_evaluations.jsonl`

Example entry:
```json
{
  "question_id": "Q1",
  "condition": "without-protocol",
  "criterion": "evidence_quality",
  "score": 2,
  "evaluation_text": "### EVIDENCE QUALITY EVALUATION...",
  "evaluator_model": "claude-3-5-sonnet-20241022",
  "timestamp": "2025-11-05T20:45:00Z"
}
```

### Summary File
`evaluation_summary.json` (if generated)

## Example Workflow

### Step 1: Evaluate with Claude

```bash
export EVALUATOR_API_KEY="sk-ant-..."

python3 src/evaluate_answers.py \
  --evaluator-endpoint https://api.anthropic.com/v1/messages \
  --evaluator-model claude-3-5-sonnet-20241022 \
  --output-dir evaluations/ai/claude
```

### Step 2: Review Results

```bash
# View all evidence quality scores
cat evaluations/ai/claude/evidence_quality_evaluations.jsonl | \
  jq '{qid: .question_id, condition: .condition, score: .score}'

# Count evaluations
wc -l evaluations/ai/claude/*.jsonl
```

### Step 3: Extract Scores for Analysis

```python
import json

scores = []
with open('evaluations/ai/claude/evidence_quality_evaluations.jsonl') as f:
    for line in f:
        data = json.loads(line)
        scores.append({
            'qid': data['question_id'],
            'condition': data['condition'],
            'score': data['score']
        })

# Average by condition
import pandas as pd
df = pd.DataFrame(scores)
print(df.groupby('condition')['score'].mean())
```

## Troubleshooting

### API Rate Limits

If you hit rate limits, add delays:
```python
import time
time.sleep(2)  # Add between API calls
```

### Missing Scores

If scores aren't extracted, check the evaluation text:
```bash
cat evaluations/ai/evidence_quality_evaluations.jsonl | \
  jq '.evaluation_text' | less
```

The script looks for patterns like:
- `**Score: 4/5**`
- `Score: [4]`
- `Final Score: 4`

### API Errors

Common issues:
- **401 Unauthorized**: Check your API key
- **429 Too Many Requests**: Rate limited, wait and retry
- **500 Server Error**: API service issue, retry later

## Cost Estimation

Rough estimates (as of 2025):

**Per evaluation:**
- Input: ~2,000-4,000 tokens (prompt + answer)
- Output: ~1,000-2,000 tokens (evaluation)
- Total: ~3,000-6,000 tokens

**Full evaluation (5 questions × 2 conditions × 5 criteria = 50 evaluations):**
- Total tokens: ~150,000-300,000
- Claude Sonnet cost: ~$0.45-$0.90
- GPT-4 cost: ~$4.50-$9.00

## Advanced Usage

### Parallel Execution

For faster evaluation (if API allows):
```bash
# Evaluate different criteria in parallel
python3 src/evaluate_answers.py --criterion evidence_quality &
python3 src/evaluate_answers.py --criterion transparency &
python3 src/evaluate_answers.py --criterion reasoning_depth &
wait
```

### Custom Output Location

```bash
python3 src/evaluate_answers.py \
  --output-dir "paper_results/round1" \
  --evaluator-model claude-3-5-sonnet-20241022
```

## Next Steps

After AI evaluation:
1. Review the detailed evaluation texts in the JSONL files
2. Use the scores to populate your paper tables
3. Compare with human evaluation scores (from rubrics in `docs/rubrics/`)
4. Calculate inter-rater reliability (AI vs. human)

## Support

For issues or questions:
- Check the script's inline documentation
- Review error messages carefully
- Verify API credentials and endpoints
- Ensure input files are properly formatted
