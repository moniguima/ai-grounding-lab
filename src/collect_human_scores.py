#!/usr/bin/env python3
"""
Collect human evaluation scores from completed forms.

Scans evaluation forms for filled-in scores and compiles them into
a structured JSONL format compatible with AI evaluation results.

Author: Monica Guimaraes
Created: 2025-11-05
"""

import argparse
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


class FormScanner:
    """
    Scans evaluation form files for completed scores.

    Follows Single Responsibility Principle: only handles file scanning.
    """

    def __init__(self, forms_dir: Path):
        """
        Initialize with forms directory.

        Args:
            forms_dir: Directory containing evaluation forms.
        """
        self.forms_dir = forms_dir

    def find_forms(self) -> List[Path]:
        """
        Find all evaluation form markdown files.

        Returns:
            List of paths to form files.
        """
        return sorted(self.forms_dir.glob("Q*_*.md"))


class ScoreExtractor:
    """
    Extracts scores and metadata from form files.

    Follows Single Responsibility Principle: only handles score extraction.
    """

    @staticmethod
    def extract_metadata(form_text: str, filename: str) -> Dict[str, str]:
        """
        Extract metadata from form filename and content.

        Args:
            form_text: The form file content.
            filename: The form filename.

        Returns:
            Dictionary with metadata fields.
        """
        # Parse filename: Q1_with-protocol_evidence_quality_RATER.md
        parts = filename.replace(".md", "").split("_")

        metadata = {
            "question_id": parts[0] if len(parts) > 0 else "unknown",
            "condition": parts[1] if len(parts) > 1 else "unknown",
            "criterion": "_".join(parts[2:-1]) if len(parts) > 3 else "unknown",
            "evaluator": parts[-1] if len(parts) > 0 else "unknown"
        }

        # Try to extract evaluator name from content
        evaluator_match = re.search(
            r'\*\*Evaluator Name:\*\*\s+([^\n\*_]+)',
            form_text
        )
        if evaluator_match:
            name = evaluator_match.group(1).strip()
            if name and name != "______" and not name.startswith("___"):
                metadata["evaluator"] = name

        # Try to extract date
        date_match = re.search(
            r'\*\*Evaluation Date:\*\*\s+(\d{4}-\d{2}-\d{2})',
            form_text
        )
        if date_match:
            metadata["date"] = date_match.group(1)
        else:
            # Try other date formats
            date_match = re.search(
                r'\*\*Date:\*\*\s+(\d{4}-\d{2}-\d{2})',
                form_text
            )
            if date_match:
                metadata["date"] = date_match.group(1)
            else:
                metadata["date"] = datetime.now().strftime('%Y-%m-%d')

        return metadata

    @staticmethod
    def extract_score(form_text: str) -> Optional[int]:
        """
        Extract the final score from form.

        Args:
            form_text: The form file content.

        Returns:
            Score (0-5), or None if not found.
        """
        # Look for filled-in score in various formats
        patterns = [
            r'\*\*.*?Score.*?\(0-5\):\*\*\s*\[\s*(\d)\s*\]',
            r'Score \(0-5\):\s*\[\s*(\d)\s*\]',
            r'Final Score:\s*\[\s*(\d)\s*\]',
            r'Score:\s*(\d)\s*/\s*5',
        ]

        for pattern in patterns:
            match = re.search(pattern, form_text, re.IGNORECASE)
            if match:
                score = int(match.group(1))
                if 0 <= score <= 5:
                    return score

        return None

    @staticmethod
    def extract_confidence(form_text: str) -> Optional[int]:
        """
        Extract confidence rating from form.

        Args:
            form_text: The form file content.

        Returns:
            Confidence (1-5), or None if not found.
        """
        # Look for confidence rating
        patterns = [
            r'\*\*Confidence in this score.*?\*\*.*?\n.*?\[\s*(\d)\s*\]',
            r'Confidence.*?\(1-5\).*?\[\s*(\d)\s*\]',
        ]

        for pattern in patterns:
            match = re.search(pattern, form_text, re.IGNORECASE | re.DOTALL)
            if match:
                conf = int(match.group(1))
                if 1 <= conf <= 5:
                    return conf

        return None

    @staticmethod
    def extract_notes(form_text: str) -> Optional[str]:
        """
        Extract additional notes from form.

        Args:
            form_text: The form file content.

        Returns:
            Notes text, or None if not found.
        """
        # Look for notes section
        match = re.search(
            r'\*\*Additional notes.*?\*\*.*?\n\n(.*?)(?:\n\n---|\Z)',
            form_text,
            re.IGNORECASE | re.DOTALL
        )

        if match:
            notes = match.group(1).strip()
            # Filter out empty underscores
            notes = re.sub(r'_+', '', notes).strip()
            if notes:
                return notes

        return None


class ResultCompiler:
    """
    Compiles extracted scores into structured output.

    Follows Single Responsibility Principle: only handles compilation.
    """

    @staticmethod
    def compile_result(
        metadata: Dict[str, str],
        score: Optional[int],
        confidence: Optional[int],
        notes: Optional[str],
        form_file: Path
    ) -> Dict:
        """
        Compile a result record.

        Args:
            metadata: Metadata dict.
            score: Extracted score.
            confidence: Confidence rating.
            notes: Additional notes.
            form_file: Path to the form file.

        Returns:
            Complete result dictionary.
        """
        return {
            "question_id": metadata["question_id"],
            "condition": metadata["condition"],
            "criterion": metadata["criterion"],
            "score": score,
            "confidence": confidence,
            "notes": notes,
            "evaluator": metadata["evaluator"],
            "evaluation_date": metadata.get("date"),
            "form_file": str(form_file),
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }


class ResultWriter:
    """
    Writes compiled results to files.

    Follows Single Responsibility Principle: only handles output.
    """

    def __init__(self, output_dir: Path):
        """
        Initialize with output directory.

        Args:
            output_dir: Directory to write results to.
        """
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def write_jsonl(self, results: List[Dict], filename: str = "human_scores.jsonl") -> Path:
        """
        Write results to JSONL file.

        Args:
            results: List of result dictionaries.
            filename: Output filename.

        Returns:
            Path to written file.
        """
        output_path = self.output_dir / filename

        with open(output_path, "w", encoding="utf-8") as f:
            for result in results:
                json.dump(result, f)
                f.write("\n")

        return output_path

    def write_csv(self, results: List[Dict], filename: str = "human_scores.csv") -> Path:
        """
        Write results to CSV file.

        Args:
            results: List of result dictionaries.
            filename: Output filename.

        Returns:
            Path to written file.
        """
        output_path = self.output_dir / filename

        with open(output_path, "w", encoding="utf-8") as f:
            # Header
            f.write("question_id,condition,criterion,score,confidence,evaluator,date\n")

            # Data rows
            for result in results:
                f.write(f"{result['question_id']},")
                f.write(f"{result['condition']},")
                f.write(f"{result['criterion']},")
                f.write(f"{result['score'] if result['score'] is not None else ''},")
                f.write(f"{result['confidence'] if result['confidence'] is not None else ''},")
                f.write(f"{result['evaluator']},")
                f.write(f"{result['evaluation_date']}\n")

        return output_path

    def write_summary(self, results: List[Dict]) -> Path:
        """
        Write a summary report.

        Args:
            results: List of result dictionaries.

        Returns:
            Path to summary file.
        """
        output_path = self.output_dir / "collection_summary.txt"

        total = len(results)
        completed = len([r for r in results if r["score"] is not None])
        incomplete = total - completed

        # Calculate statistics
        scores_by_criterion = {}
        for result in results:
            if result["score"] is not None:
                crit = result["criterion"]
                if crit not in scores_by_criterion:
                    scores_by_criterion[crit] = []
                scores_by_criterion[crit].append(result["score"])

        with open(output_path, "w", encoding="utf-8") as f:
            f.write("HUMAN EVALUATION SCORE COLLECTION SUMMARY\n")
            f.write("=" * 60 + "\n\n")
            f.write(f"Collection Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

            f.write("OVERVIEW\n")
            f.write("-" * 60 + "\n")
            f.write(f"Total forms scanned: {total}\n")
            f.write(f"Forms with scores: {completed}\n")
            f.write(f"Forms incomplete: {incomplete}\n\n")

            if scores_by_criterion:
                f.write("SCORES BY CRITERION\n")
                f.write("-" * 60 + "\n")
                for criterion, scores in sorted(scores_by_criterion.items()):
                    avg = sum(scores) / len(scores) if scores else 0
                    f.write(f"\n{criterion}:\n")
                    f.write(f"  Count: {len(scores)}\n")
                    f.write(f"  Mean: {avg:.2f}\n")
                    f.write(f"  Range: {min(scores)}-{max(scores)}\n")

            if incomplete > 0:
                f.write("\n\nINCOMPLETE FORMS\n")
                f.write("-" * 60 + "\n")
                for result in results:
                    if result["score"] is None:
                        f.write(f"- {Path(result['form_file']).name}\n")

        return output_path


def main() -> None:
    """Main execution function."""
    parser = argparse.ArgumentParser(
        description="Collect human evaluation scores from completed forms"
    )
    parser.add_argument(
        "--forms-dir",
        type=Path,
        default=Path("evaluations/human/forms"),
        help="Directory containing evaluation forms"
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("evaluations/human"),
        help="Output directory for compiled scores"
    )
    parser.add_argument(
        "--format",
        type=str,
        choices=["jsonl", "csv", "both"],
        default="both",
        help="Output format (default: both)"
    )
    parser.add_argument(
        "--include-incomplete",
        action="store_true",
        help="Include forms without scores in output"
    )

    args = parser.parse_args()

    # Initialize components
    scanner = FormScanner(args.forms_dir)
    extractor = ScoreExtractor()
    compiler = ResultCompiler()
    writer = ResultWriter(args.output_dir)

    # Find forms
    print(f"Scanning forms in {args.forms_dir}...")
    form_files = scanner.find_forms()
    print(f"Found {len(form_files)} forms")

    # Extract scores
    results = []
    completed_count = 0
    incomplete_count = 0

    for form_file in form_files:
        print(f"Processing {form_file.name}...", end=" ")

        try:
            with open(form_file, "r", encoding="utf-8") as f:
                form_text = f.read()

            # Extract information
            metadata = extractor.extract_metadata(form_text, form_file.name)
            score = extractor.extract_score(form_text)
            confidence = extractor.extract_confidence(form_text)
            notes = extractor.extract_notes(form_text)

            # Compile result
            result = compiler.compile_result(
                metadata=metadata,
                score=score,
                confidence=confidence,
                notes=notes,
                form_file=form_file
            )

            if score is not None:
                print(f"✓ Score: {score}")
                completed_count += 1
                results.append(result)
            else:
                print("⚠ No score found")
                incomplete_count += 1
                if args.include_incomplete:
                    results.append(result)

        except Exception as e:
            print(f"✗ Error: {e}")
            continue

    # Write outputs
    print(f"\n{'='*60}")

    if args.format in ["jsonl", "both"]:
        jsonl_path = writer.write_jsonl(results)
        print(f"✓ JSONL: {jsonl_path}")

    if args.format in ["csv", "both"]:
        csv_path = writer.write_csv(results)
        print(f"✓ CSV: {csv_path}")

    summary_path = writer.write_summary(results)
    print(f"✓ Summary: {summary_path}")

    print(f"\n{'='*60}")
    print(f"Completed forms: {completed_count}")
    print(f"Incomplete forms: {incomplete_count}")
    print(f"Total collected: {len(results)}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
