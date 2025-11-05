#!/usr/bin/env python3
"""
Generate pre-filled evaluation forms for human raters.

Creates markdown forms combining rubrics with answers for systematic
human evaluation of LLM responses.

Author: Monica Guimaraes
Created: 2025-11-05
"""

import argparse
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List

# Import AnswerParser from evaluate_answers.py
import sys
sys.path.insert(0, str(Path(__file__).parent))
from evaluate_answers import AnswerParser


class RubricLoader:
    """
    Loads evaluation rubrics from the docs/rubrics/ directory.

    Follows Single Responsibility Principle: only handles rubric loading.
    """

    RUBRIC_FILES = {
        "evidence_quality": "Evidence Quality Assessment Rubric.md",
        "transparency": "Transparency Assessment Rubric.md",
        "reasoning_depth": "Reasoning Depth Assessment Rubric.md",
        "actionability": "Actionability Assessment Rubric.md",
        "uncertainty_disclosure": "Hallucination Detection Rubric.md"
    }

    def __init__(self, rubrics_dir: Path):
        """
        Initialize with path to rubrics directory.

        Args:
            rubrics_dir: Path to directory containing evaluation rubrics.
        """
        self.rubrics_dir = rubrics_dir

    def load_rubric(self, criterion: str) -> str:
        """
        Load an evaluation rubric for a specific criterion.

        Args:
            criterion: The criterion name (e.g., "evidence_quality").

        Returns:
            The rubric text content.

        Raises:
            FileNotFoundError: If the rubric file doesn't exist.
            KeyError: If the criterion is not recognized.
        """
        if criterion not in self.RUBRIC_FILES:
            raise KeyError(f"Unknown criterion: {criterion}")

        filename = self.RUBRIC_FILES[criterion]
        filepath = self.rubrics_dir / filename

        if not filepath.exists():
            raise FileNotFoundError(f"Rubric file not found: {filepath}")

        with open(filepath, "r", encoding="utf-8") as f:
            return f.read().strip()

    def load_all_rubrics(self) -> Dict[str, str]:
        """
        Load all evaluation rubrics.

        Returns:
            Dictionary mapping criterion names to rubric texts.
        """
        rubrics = {}
        for criterion in self.RUBRIC_FILES.keys():
            rubrics[criterion] = self.load_rubric(criterion)
        return rubrics


class FormComposer:
    """
    Composes evaluation forms by combining rubrics and answers.

    Follows Single Responsibility Principle: only handles composition.
    """

    @staticmethod
    def compose_evaluation_form(
        rubric_text: str,
        question_id: str,
        question_text: str,
        answer_text: str,
        condition: str,
        criterion: str,
        evaluator_name: str = "______"
    ) -> str:
        """
        Compose a complete evaluation form.

        Args:
            rubric_text: The criterion-specific rubric worksheet.
            question_id: Question identifier (e.g., "Q1").
            question_text: The original question.
            answer_text: The answer to evaluate.
            condition: "with-protocol" or "without-protocol".
            criterion: Criterion being evaluated.
            evaluator_name: Name of the evaluator (default: blank).

        Returns:
            Complete evaluation form text in markdown.
        """
        # Extract the criterion title from rubric
        criterion_title = criterion.replace("_", " ").title()

        # Build header
        header = f"""# Human Evaluation Form

## Question {question_id} | {condition.title()} | {criterion_title}

---

### Metadata

**Response ID:** {question_id}_{condition}
**Condition:** {'☑' if condition == 'with-protocol' else '☐'} With Protocol | {'☑' if condition == 'without-protocol' else '☐'} Without Protocol
**Criterion:** {criterion_title}
**Evaluator Name:** {evaluator_name}
**Evaluation Date:** _______________
**Time Started:** _______  **Time Completed:** _______

---

## QUESTION BEING ANSWERED

**Question {question_id}:**

> {question_text}

---

## ANSWER TO EVALUATE

<details>
<summary><strong>Click to expand full answer (scroll down after reading)</strong></summary>

{answer_text}

</details>

---

"""

        # Update rubric header fields if they exist
        rubric_filled = rubric_text

        # Replace header placeholders if present
        rubric_filled = rubric_filled.replace(
            "**Response ID:** __________",
            f"**Response ID:** {question_id}_{condition}"
        )
        rubric_filled = rubric_filled.replace(
            "**Condition:** ☐ Baseline ☐ Protocol",
            f"**Condition:** {'☐ Without Protocol ☑ With Protocol' if condition == 'with-protocol' else '☑ Without Protocol ☐ With Protocol'}"
        )
        rubric_filled = rubric_filled.replace(
            "**Rater:** __________",
            f"**Rater:** {evaluator_name}"
        )
        rubric_filled = rubric_filled.replace(
            "**Date:** __________",
            f"**Date:** {datetime.now().strftime('%Y-%m-%d')}"
        )

        # Footer for score entry
        footer = f"""

---

## FINAL SCORE ENTRY

After completing all sections of the rubric above, enter your final score here:

**{criterion_title} Score (0-5):** [ _____ ]

**Confidence in this score (1-5):**
1 = Very uncertain | 2 = Somewhat uncertain | 3 = Moderately confident | 4 = Confident | 5 = Very confident

[ _____ ]

**Additional notes or justification (optional):**

_________________________________________________________________

_________________________________________________________________

_________________________________________________________________

---

## INSTRUCTIONS FOR SCORE ENTRY

After completing this evaluation form:

1. **Enter your score** in the box above (0-5)
2. **Rate your confidence** in this score (1-5)
3. **Add any notes** that help explain your reasoning
4. **Save this file** with your score
5. **Report your score** using one of these methods:

   **Method A: Add to scores CSV**
   ```csv
   question_id,condition,criterion,score,confidence,evaluator,date
   {question_id},{condition},{criterion},YOUR_SCORE,YOUR_CONFIDENCE,{evaluator_name},{datetime.now().strftime('%Y-%m-%d')}
   ```

   **Method B: Use the score collection script**
   ```bash
   python3 src/collect_human_scores.py --forms-dir evaluations/human/forms
   ```

---

**Thank you for your careful evaluation!**

*Evaluation form generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""

        return header + rubric_filled + footer


class FormWriter:
    """
    Writes evaluation forms to files.

    Follows Single Responsibility Principle: only handles file output.
    """

    def __init__(self, output_dir: Path):
        """
        Initialize with output directory.

        Args:
            output_dir: Directory to write forms to.
        """
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def write_form(
        self,
        form_text: str,
        question_id: str,
        condition: str,
        criterion: str,
        evaluator_name: str = "RATER"
    ) -> Path:
        """
        Write an evaluation form to a file.

        Args:
            form_text: The complete form text.
            question_id: Question identifier.
            condition: "with-protocol" or "without-protocol".
            criterion: Criterion name.
            evaluator_name: Name to include in filename.

        Returns:
            Path to the written file.
        """
        # Clean evaluator name for filename
        safe_name = "".join(c if c.isalnum() else "-" for c in evaluator_name)
        if safe_name == "" or safe_name == "------":
            safe_name = "RATER"

        filename = f"{question_id}_{condition}_{criterion}_{safe_name}.md"
        filepath = self.output_dir / filename

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(form_text)

        return filepath

    def write_index(self, forms_info: List[Dict]) -> Path:
        """
        Write an index file listing all generated forms.

        Args:
            forms_info: List of form metadata dicts.

        Returns:
            Path to the index file.
        """
        index_path = self.output_dir / "INDEX.md"

        index_text = f"""# Human Evaluation Forms Index

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Total forms: {len(forms_info)}

## Forms by Question

"""

        # Group by question
        by_question = {}
        for form in forms_info:
            qid = form["question_id"]
            if qid not in by_question:
                by_question[qid] = []
            by_question[qid].append(form)

        for qid in sorted(by_question.keys()):
            forms = by_question[qid]
            index_text += f"### {qid}\n\n"
            for form in sorted(forms, key=lambda x: (x["condition"], x["criterion"])):
                index_text += f"- [{form['filename']}]({form['filename']}) - {form['condition']} | {form['criterion']}\n"
            index_text += "\n"

        # Instructions
        index_text += """
## How to Use These Forms

1. **Choose a form** from the list above
2. **Open it** in a markdown viewer or text editor
3. **Read the question and answer** carefully
4. **Follow the rubric** to evaluate systematically
5. **Enter your final score** at the end
6. **Save the form** when complete

## Collecting Scores

After completing forms, collect scores using:

```bash
python3 src/collect_human_scores.py --forms-dir evaluations/human/forms
```

This will scan all completed forms and extract scores into a JSONL file.

---

**Happy evaluating!**
"""

        with open(index_path, "w", encoding="utf-8") as f:
            f.write(index_text)

        return index_path


def main() -> None:
    """Main execution function."""
    parser = argparse.ArgumentParser(
        description="Generate pre-filled evaluation forms for human raters"
    )
    parser.add_argument(
        "--qa-file",
        type=Path,
        default=Path("docs/questions_and_answers.md"),
        help="Path to questions and answers file"
    )
    parser.add_argument(
        "--rubrics-dir",
        type=Path,
        default=Path("docs/rubrics"),
        help="Directory containing evaluation rubrics"
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("evaluations/human/forms"),
        help="Output directory for evaluation forms"
    )
    parser.add_argument(
        "--criterion",
        type=str,
        choices=["evidence_quality", "transparency", "reasoning_depth",
                 "actionability", "uncertainty_disclosure", "all"],
        default="all",
        help="Which criterion to generate forms for (default: all)"
    )
    parser.add_argument(
        "--condition",
        type=str,
        choices=["with-protocol", "without-protocol", "both"],
        default="both",
        help="Which condition to generate forms for (default: both)"
    )
    parser.add_argument(
        "--evaluator-name",
        type=str,
        default="RATER",
        help="Name to pre-fill in forms (default: RATER)"
    )
    parser.add_argument(
        "--question-id",
        type=str,
        default="all",
        help="Specific question to generate forms for (e.g., Q1) or 'all'"
    )

    args = parser.parse_args()

    # Initialize components
    rubric_loader = RubricLoader(args.rubrics_dir)
    answer_parser = AnswerParser(args.qa_file)
    composer = FormComposer()
    form_writer = FormWriter(args.output_dir)

    # Load answers
    print(f"Loading answers from {args.qa_file}...")
    answers = answer_parser.parse_answers()

    # Filter by question if specified
    if args.question_id != "all":
        answers = [a for a in answers if a["question_id"] == args.question_id.upper()]
        if not answers:
            print(f"Error: Question {args.question_id} not found")
            exit(1)

    print(f"Found {len(answers)} question-answer pairs")

    # Determine which criteria to generate
    criteria = (
        list(RubricLoader.RUBRIC_FILES.keys())
        if args.criterion == "all"
        else [args.criterion]
    )

    # Generate forms
    forms_info = []
    total_forms = 0

    for answer_data in answers:
        question_id = answer_data["question_id"]
        question_text = answer_data["question_text"]

        # Determine which conditions to generate
        conditions = []
        if args.condition in ["without-protocol", "both"]:
            conditions.append(("without-protocol", answer_data["answer_without_protocol"]))
        if args.condition in ["with-protocol", "both"]:
            conditions.append(("with-protocol", answer_data["answer_with_protocol"]))

        for condition, answer_text in conditions:
            if not answer_text:
                print(f"⚠ Skipping {question_id} ({condition}): No answer text")
                continue

            for criterion in criteria:
                print(f"Generating form: {question_id} | {condition} | {criterion}")

                try:
                    # Load rubric
                    rubric_text = rubric_loader.load_rubric(criterion)

                    # Compose form
                    form_text = composer.compose_evaluation_form(
                        rubric_text=rubric_text,
                        question_id=question_id,
                        question_text=question_text,
                        answer_text=answer_text,
                        condition=condition,
                        criterion=criterion,
                        evaluator_name=args.evaluator_name
                    )

                    # Write form
                    filepath = form_writer.write_form(
                        form_text=form_text,
                        question_id=question_id,
                        condition=condition,
                        criterion=criterion,
                        evaluator_name=args.evaluator_name
                    )

                    forms_info.append({
                        "filename": filepath.name,
                        "question_id": question_id,
                        "condition": condition,
                        "criterion": criterion
                    })

                    total_forms += 1

                except Exception as e:
                    print(f"✗ Error: {e}")
                    continue

    # Write index
    index_path = form_writer.write_index(forms_info)

    print(f"\n{'='*60}")
    print(f"✓ Generated {total_forms} evaluation forms")
    print(f"✓ Forms saved to: {args.output_dir}")
    print(f"✓ Index file: {index_path}")
    print(f"{'='*60}")
    print(f"\nNext steps:")
    print(f"1. Open forms in {args.output_dir}")
    print(f"2. Evaluate each answer using the rubric")
    print(f"3. Enter scores in the forms")
    print(f"4. Run: python3 src/collect_human_scores.py --forms-dir {args.output_dir}")


if __name__ == "__main__":
    main()
