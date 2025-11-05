# Human Evaluation Guide

This guide explains how to conduct systematic human evaluation of LLM answers using the pre-filled forms generated from your rubrics.

## Overview

The human evaluation workflow has three simple steps:

1. **Generate Forms** - Create pre-filled evaluation forms
2. **Evaluate** - Humans complete the forms following the rubrics
3. **Collect Scores** - Compile scores into structured data

## Prerequisites

```bash
pip install -r requirements.txt
```

No API keys needed for human evaluation!

---

## Step 1: Generate Evaluation Forms

### Generate All Forms (Recommended)

```bash
python3 src/generate_evaluation_forms.py \
  --output-dir evaluations/human/forms \
  --evaluator-name "YOUR-NAME"
```

This creates **50 forms** (5 questions × 2 conditions × 5 criteria).

### Generate Specific Forms

**One criterion:**
```bash
python3 src/generate_evaluation_forms.py \
  --criterion evidence_quality \
  --evaluator-name "Rater1"
```

**One condition:**
```bash
python3 src/generate_evaluation_forms.py \
  --condition with-protocol \
  --evaluator-name "Rater1"
```

**One question:**
```bash
python3 src/generate_evaluation_forms.py \
  --question-id Q1 \
  --evaluator-name "Rater1"
```

### Command-Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `--qa-file` | Questions and answers file | `docs/questions_and_answers.md` |
| `--rubrics-dir` | Directory with rubrics | `docs/rubrics` |
| `--output-dir` | Where to save forms | `evaluations/human/forms` |
| `--criterion` | Specific criterion or `all` | `all` |
| `--condition` | `with-protocol`, `without-protocol`, or `both` | `both` |
| `--evaluator-name` | Name to pre-fill in forms | `RATER` |
| `--question-id` | Specific question or `all` | `all` |

### Output Structure

```
evaluations/human/forms/
├── INDEX.md                                    # Navigation index
├── Q1_without-protocol_evidence_quality_RATER.md
├── Q1_without-protocol_transparency_RATER.md
├── Q1_with-protocol_evidence_quality_RATER.md
├── ...
└── Q5_with-protocol_uncertainty_disclosure_RATER.md
```

---

## Step 2: Complete the Evaluation Forms

### Opening Forms

**Option A: Markdown Viewer**
- Use VS Code, Typora, or any markdown editor
- Forms render with nice formatting

**Option B: Print to PDF**
```bash
# Using pandoc (if installed)
pandoc Q1_without-protocol_evidence_quality_RATER.md -o Q1_evidence.pdf
```

**Option C: Plain Text Editor**
- Any text editor works
- Fill in tables and checkboxes manually

### Form Structure

Each form contains:

1. **Metadata** - Question ID, condition, criterion, evaluator info
2. **Question** - The original question being answered
3. **Answer to Evaluate** - Full LLM response (expandable section)
4. **Rubric Worksheet** - Complete rubric with tables to fill
5. **Final Score Entry** - Where you enter your 0-5 score

### Evaluation Workflow (per form)

**Time estimate:** 12-18 minutes per form

1. **Read the question** to understand context
2. **Expand and read the full answer** carefully
3. **Follow the rubric step-by-step:**
   - Complete all tables (citation inventory, checklists, etc.)
   - Make notes as you go
   - Reference the scoring guide
4. **Determine your final score** (0-5)
5. **Enter the score** in the designated box at the end
6. **Rate your confidence** (1-5)
7. **Add any justification notes**
8. **Save the file**

### Scoring Tips

- **Be systematic**: Complete every rubric section
- **Use the anchors**: Reference the 0-5 scale descriptions
- **When uncertain**: Choose the lower score (conservative)
- **Document reasoning**: Add notes explaining edge cases
- **Take breaks**: Don't evaluate more than 3-4 forms in one sitting

### Example Score Entry

At the end of each form, you'll see:

```markdown
## FINAL SCORE ENTRY

**Evidence Quality Score (0-5):** [ __3__ ]

**Confidence in this score (1-5):** [ __4__ ]

**Additional notes:**
Score of 3 because answer had 2 peer-reviewed sources but lacked
DOIs and some claims were uncited. Strong reasoning but incomplete
attribution.
```

---

## Step 3: Collect Scores from Completed Forms

After completing forms, extract scores automatically:

### Basic Collection

```bash
python3 src/collect_human_scores.py \
  --forms-dir evaluations/human/forms
```

This outputs:
- `evaluations/human/human_scores.jsonl` (structured data)
- `evaluations/human/human_scores.csv` (spreadsheet-friendly)
- `evaluations/human/collection_summary.txt` (overview)

### Options

| Option | Description | Default |
|--------|-------------|---------|
| `--forms-dir` | Directory containing forms | `evaluations/human/forms` |
| `--output-dir` | Where to save results | `evaluations/human` |
| `--format` | `jsonl`, `csv`, or `both` | `both` |
| `--include-incomplete` | Include forms without scores | `false` |

### Output Format

**JSONL (for analysis):**
```json
{
  "question_id": "Q1",
  "condition": "without-protocol",
  "criterion": "evidence_quality",
  "score": 3,
  "confidence": 4,
  "notes": "Score of 3 because...",
  "evaluator": "Rater1",
  "evaluation_date": "2025-11-05",
  "form_file": "Q1_without-protocol_evidence_quality_Rater1.md",
  "timestamp": "2025-11-05T20:30:00Z"
}
```

**CSV (for spreadsheets):**
```csv
question_id,condition,criterion,score,confidence,evaluator,date
Q1,without-protocol,evidence_quality,3,4,Rater1,2025-11-05
Q1,with-protocol,evidence_quality,5,5,Rater1,2025-11-05
...
```

---

## Multi-Rater Workflows

### Scenario: Two Independent Raters

**Generate forms for each rater:**
```bash
python3 src/generate_evaluation_forms.py \
  --evaluator-name "Alice" \
  --output-dir evaluations/human/forms_alice

python3 src/generate_evaluation_forms.py \
  --evaluator-name "Bob" \
  --output-dir evaluations/human/forms_bob
```

**Each rater completes their forms independently.**

**Collect scores separately:**
```bash
python3 src/collect_human_scores.py \
  --forms-dir evaluations/human/forms_alice \
  --output-dir evaluations/human/alice_results

python3 src/collect_human_scores.py \
  --forms-dir evaluations/human/forms_bob \
  --output-dir evaluations/human/bob_results
```

**Combine for inter-rater reliability analysis:**
```python
import json
import pandas as pd

# Load both raters' scores
alice = pd.read_json('evaluations/human/alice_results/human_scores.jsonl', lines=True)
bob = pd.read_json('evaluations/human/bob_results/human_scores.jsonl', lines=True)

# Merge on question_id, condition, criterion
merged = alice.merge(bob, on=['question_id', 'condition', 'criterion'],
                     suffixes=('_alice', '_bob'))

# Calculate inter-rater reliability
from scipy.stats import spearmanr
correlation, p_value = spearmanr(merged['score_alice'], merged['score_bob'])
print(f"Inter-rater correlation: {correlation:.3f} (p={p_value:.3f})")
```

### Scenario: Consensus Rating

1. **Both raters evaluate independently** (as above)
2. **Identify disagreements:**
   ```python
   disagreements = merged[abs(merged['score_alice'] - merged['score_bob']) >= 2]
   ```
3. **Discuss and re-evaluate** discrepant cases
4. **Create consensus scores file**

---

## Quality Control

### Before Starting

- [ ] Read all rubrics in `docs/rubrics/`
- [ ] Practice on 1-2 sample forms
- [ ] Calibrate with another rater (if doing inter-rater study)
- [ ] Set up comfortable evaluation environment

### During Evaluation

- [ ] Limit sessions to 60-90 minutes
- [ ] Take 5-minute breaks between forms
- [ ] Check that scores are entered in the correct format
- [ ] Keep notes on edge cases or questions

### After Completing Forms

- [ ] Run collection script to verify all scores extracted
- [ ] Check summary report for any missing forms
- [ ] Review any low-confidence scores
- [ ] Back up completed forms

---

## Troubleshooting

### Q: The collection script says "No score found"

**Solution:** Check that you entered the score in the correct format:

✅ **Correct:**
```markdown
**Evidence Quality Score (0-5):** [ 4 ]
```

❌ **Incorrect:**
```markdown
**Evidence Quality Score (0-5):** [ four ]
**Evidence Quality Score (0-5):** [4]  (no spaces)
**Evidence Quality Score (0-5):** 4     (no brackets)
```

### Q: How do I handle answers with NO citations?

Follow the rubric's "Score 0-1" guidance. Document what the answer claims vs. what it cites.

### Q: What if I disagree with the rubric anchor descriptions?

Note your concern in the form but apply the rubric as written to maintain consistency. Document disagreements for discussion.

### Q: Can I modify the rubrics?

Yes, but do it BEFORE generating forms. Edit files in `docs/rubrics/`, then regenerate all forms.

### Q: How do I evaluate if I'm not a domain expert?

Focus on evaluable aspects:
- **Evidence Quality**: Check if sources are cited (you don't need to verify every claim)
- **Transparency**: Look for limitation statements
- **Uncertainty**: Check for confidence language

For technical accuracy, consider recruiting domain experts.

---

## Comparison with AI Evaluation

### Advantages of Human Evaluation

- ✅ Nuanced judgment
- ✅ Domain expertise
- ✅ Can assess subjective qualities
- ✅ Doesn't require API costs

### Advantages of AI Evaluation

- ✅ Faster (minutes vs. hours)
- ✅ Consistent (no fatigue)
- ✅ Detailed justifications
- ✅ Scalable

### Recommended Approach: Both

1. **AI evaluates all 50 cases** (fast, comprehensive)
2. **Humans evaluate subset** (20-30 cases for reliability check)
3. **Compare AI vs. human scores** (inter-rater agreement)
4. **Use both in paper** (methodological rigor)

---

## Time Estimates

| Task | Time |
|------|------|
| Generate all 50 forms | 2 minutes |
| Evaluate 1 form | 12-18 minutes |
| Evaluate all 50 forms (1 rater) | 10-15 hours |
| Collect scores | 1 minute |
| **Total for single rater** | **10-15 hours** |

**Tips for efficiency:**
- Batch by criterion (all evidence_quality forms together)
- Use split-screen: rubric on left, answer on right
- Take organized notes for quick score decisions

---

## Support

For issues:
- Check forms are in correct directory
- Verify score format in forms
- Review collection script output
- Examine `collection_summary.txt` for diagnostic info

---

**Thank you for your rigorous evaluation work! Your careful assessments contribute to understanding how the Scientific Grounding Protocol affects LLM reliability.**
