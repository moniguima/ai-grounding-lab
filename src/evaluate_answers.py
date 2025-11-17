#!/usr/bin/env python3
"""
Automate AI evaluation of answers using criterion-specific prompts.

This script evaluates answers from data/answers.jsonl using detailed
evaluation prompts from docs/prompts/ and an external AI evaluator API.

Author: Monica Guimaraes
Created: 2025-11-05
Updated: 2025-11-17 - Refactored to use JSONL input files
"""

import argparse
import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import requests


class PromptLoader:
    """
    Loads evaluation prompts from the docs/prompts/ directory.

    Follows Single Responsibility Principle: only handles prompt loading.
    """

    CRITERION_FILES = {
        "evidence_quality": "Evidence Quality Assessment Prompt.md",
        "transparency": "Transparency Assessment Prompt.md",
        "reasoning_depth": "Reasoning Depth Assessment Prompt.md",
        "actionability": "Actionability Assessment Prompt.md",
        "uncertainty_disclosure": "Hallucination Detection Prompt.md"  # Maps to uncertainty
    }

    def __init__(self, prompts_dir: Path):
        """
        Initialize with path to prompts directory.

        Args:
            prompts_dir: Path to directory containing evaluation prompts.
        """
        self.prompts_dir = prompts_dir

    def load_prompt(self, criterion: str) -> str:
        """
        Load an evaluation prompt for a specific criterion.

        Args:
            criterion: The criterion name (e.g., "evidence_quality").

        Returns:
            The prompt text content.

        Raises:
            FileNotFoundError: If the prompt file doesn't exist.
            KeyError: If the criterion is not recognized.
        """
        if criterion not in self.CRITERION_FILES:
            raise KeyError(f"Unknown criterion: {criterion}")

        filename = self.CRITERION_FILES[criterion]
        filepath = self.prompts_dir / filename

        if not filepath.exists():
            raise FileNotFoundError(f"Prompt file not found: {filepath}")

        with open(filepath, "r", encoding="utf-8") as f:
            return f.read().strip()

    def load_all_prompts(self) -> Dict[str, str]:
        """
        Load all evaluation prompts.

        Returns:
            Dictionary mapping criterion names to prompt texts.
        """
        prompts = {}
        for criterion in self.CRITERION_FILES.keys():
            prompts[criterion] = self.load_prompt(criterion)
        return prompts


class AnswerParser:
    """
    Parses answers from JSONL file.

    Follows Single Responsibility Principle: only handles answer extraction.
    """

    def __init__(self, answers_file: Path):
        """
        Initialize with path to answers JSONL file.

        Args:
            answers_file: Path to answers.jsonl file.
        """
        self.answers_file = answers_file

    def parse_answers(self) -> List[Dict[str, str]]:
        """
        Parse all question-answer pairs from the JSONL file.

        Returns:
            List of dictionaries containing:
                - question_id: e.g., "Q1"
                - question_text: The question
                - answer_without_protocol: Answer text
                - answer_with_protocol: Answer text
        """
        answers = []

        with open(self.answers_file, "r", encoding="utf-8") as f:
            for line_num, line in enumerate(f, start=1):
                line = line.strip()
                if not line or line.startswith("#"):
                    continue

                try:
                    data = json.loads(line)
                    answers.append({
                        "question_id": data["question_id"],
                        "question_text": data["question"],
                        "answer_without_protocol": data["answer_without_protocol"],
                        "answer_with_protocol": data["answer_with_protocol"]
                    })
                except json.JSONDecodeError as e:
                    raise json.JSONDecodeError(
                        f"Invalid JSON on line {line_num}",
                        e.doc,
                        e.pos
                    )
                except KeyError as e:
                    raise KeyError(
                        f"Missing required field {e} on line {line_num}"
                    )

        return answers


class EvaluationComposer:
    """
    Composes evaluation requests by combining prompts and answers.

    Follows Single Responsibility Principle: only handles composition.
    """

    @staticmethod
    def compose_evaluation_request(
        evaluation_prompt: str,
        question_text: str,
        answer_text: str
    ) -> str:
        """
        Compose a complete evaluation request.

        Args:
            evaluation_prompt: The criterion-specific evaluation prompt.
            question_text: The original question.
            answer_text: The answer to evaluate.

        Returns:
            Complete evaluation request text.
        """
        # Replace the placeholder in the prompt with the actual answer
        request = evaluation_prompt.replace(
            "[Paste response here]",
            answer_text
        )

        # Add question context if not already included
        if "QUESTION:" not in request and "**Question:**" not in request:
            request = f"**Question being answered:** {question_text}\n\n{request}"

        return request


class APIClient:
    """
    Handles API calls to the AI evaluator service.

    Follows Single Responsibility Principle: only handles API communication.
    Follows Dependency Inversion: depends on abstract API interface.
    """

    def __init__(
        self,
        endpoint: str,
        api_key: str,
        model: str,
        temperature: float = 0.0,
        max_tokens: int = 4000
    ):
        """
        Initialize API client.

        Args:
            endpoint: API endpoint URL.
            api_key: API authentication key.
            model: Model name to use.
            temperature: Sampling temperature.
            max_tokens: Maximum tokens in response.
        """
        self.endpoint = endpoint
        self.api_key = api_key
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens

    def call_evaluator(self, prompt: str) -> str:
        """
        Call the AI evaluator API.

        Args:
            prompt: The evaluation request prompt.

        Returns:
            The evaluator's response text.

        Raises:
            requests.RequestException: If the API call fails.
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": self.temperature,
            "max_tokens": self.max_tokens
        }

        response = requests.post(
            self.endpoint,
            headers=headers,
            json=payload,
            timeout=600
        )
        response.raise_for_status()

        data = response.json()
        return data["choices"][0]["message"]["content"]


class ResultWriter:
    """
    Writes evaluation results to JSON files.

    Follows Single Responsibility Principle: only handles output writing.
    """

    def __init__(self, output_dir: Path):
        """
        Initialize with output directory.

        Args:
            output_dir: Directory to write results to.
        """
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def write_result(
        self,
        question_id: str,
        condition: str,
        criterion: str,
        evaluation_text: str,
        score: Optional[int],
        evaluator_model: str
    ) -> None:
        """
        Write a single evaluation result to a JSONL file.

        Args:
            question_id: Question identifier (e.g., "Q1").
            condition: "with-protocol" or "without-protocol".
            criterion: Evaluation criterion name.
            evaluation_text: Full evaluation response from AI.
            score: Extracted score (0-5), if found.
            evaluator_model: Name of the evaluator model used.
        """
        result = {
            "question_id": question_id,
            "condition": condition,
            "criterion": criterion,
            "score": score,
            "evaluation_text": evaluation_text,
            "evaluator_model": evaluator_model,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }

        # Write to criterion-specific file
        output_file = self.output_dir / f"{criterion}_evaluations.jsonl"
        with open(output_file, "a", encoding="utf-8") as f:
            json.dump(result, f)
            f.write("\n")

    def write_summary(self, summary_data: Dict) -> None:
        """
        Write a summary report.

        Args:
            summary_data: Dictionary containing summary statistics.
        """
        summary_file = self.output_dir / "evaluation_summary.json"
        with open(summary_file, "w", encoding="utf-8") as f:
            json.dump(summary_data, f, indent=2)


class ScoreExtractor:
    """
    Extracts numerical scores from evaluation text.

    Follows Single Responsibility Principle: only handles score extraction.
    """

    @staticmethod
    def extract_score(evaluation_text: str) -> Optional[int]:
        """
        Extract a 0-5 score from the evaluation text.

        Args:
            evaluation_text: The full evaluation response.

        Returns:
            The extracted score (0-5), or None if not found.
        """
        # Look for patterns like "Score: 4" or "**Score: 4/5**"
        patterns = [
            r'\*\*Score:\s*(\d)\s*/\s*5\*\*',
            r'Score:\s*(\d)\s*/\s*5',
            r'\*\*.*?Score:\s*\[?(\d)\]?\*\*',
            r'Score:\s*\[?(\d)\]?',
            r'Final Score:\s*(\d)',
        ]

        for pattern in patterns:
            match = re.search(pattern, evaluation_text, re.IGNORECASE)
            if match:
                score = int(match.group(1))
                if 0 <= score <= 5:
                    return score

        return None


def main() -> None:
    """Main execution function."""
    parser = argparse.ArgumentParser(
        description="Automate AI evaluation of answers using criterion-specific prompts"
    )
    parser.add_argument(
        "--answers-file",
        type=Path,
        default=Path("data/answers.jsonl"),
        help="Path to answers JSONL file (with protocol and non-protocol answers)"
    )
    parser.add_argument(
        "--prompts-dir",
        type=Path,
        default=Path("docs/prompts"),
        help="Directory containing evaluation prompts"
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("evaluations/ai"),
        help="Output directory for evaluation results"
    )
    parser.add_argument(
        "--criterion",
        type=str,
        choices=["evidence_quality", "transparency", "reasoning_depth",
                 "actionability", "uncertainty_disclosure", "all"],
        default="all",
        help="Which criterion to evaluate (default: all)"
    )
    parser.add_argument(
        "--evaluator-endpoint",
        type=str,
        required=True,
        help="API endpoint for evaluator (e.g., https://api.openai.com/v1/chat/completions)"
    )
    parser.add_argument(
        "--evaluator-model",
        type=str,
        required=True,
        help="Model to use for evaluation (e.g., claude-3-5-sonnet, gpt-4)"
    )
    parser.add_argument(
        "--api-key",
        type=str,
        default=os.getenv("EVALUATOR_API_KEY"),
        help="API key for evaluator (or set EVALUATOR_API_KEY env var)"
    )
    parser.add_argument(
        "--condition",
        type=str,
        choices=["with-protocol", "without-protocol", "both"],
        default="both",
        help="Which condition to evaluate (default: both)"
    )

    args = parser.parse_args()

    if not args.api_key:
        print("Error: API key required. Set --api-key or EVALUATOR_API_KEY environment variable.")
        exit(1)

    # Initialize components
    prompt_loader = PromptLoader(args.prompts_dir)
    answer_parser = AnswerParser(args.answers_file)
    composer = EvaluationComposer()
    api_client = APIClient(
        endpoint=args.evaluator_endpoint,
        api_key=args.api_key,
        model=args.evaluator_model
    )
    result_writer = ResultWriter(args.output_dir)
    score_extractor = ScoreExtractor()

    # Load answers
    print(f"Loading answers from {args.answers_file}...")
    answers = answer_parser.parse_answers()
    print(f"Found {len(answers)} question-answer pairs")

    # Determine which criteria to evaluate
    criteria = (
        list(PromptLoader.CRITERION_FILES.keys())
        if args.criterion == "all"
        else [args.criterion]
    )

    # Evaluate each answer
    total_evaluations = 0
    for answer_data in answers:
        question_id = answer_data["question_id"]
        question_text = answer_data["question_text"]

        # Determine which conditions to evaluate
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
                print(f"\n{'='*60}")
                print(f"Evaluating {question_id} | {condition} | {criterion}")
                print(f"{'='*60}")

                try:
                    # Load evaluation prompt
                    eval_prompt = prompt_loader.load_prompt(criterion)

                    # Compose evaluation request
                    request = composer.compose_evaluation_request(
                        eval_prompt,
                        question_text,
                        answer_text
                    )

                    # Call evaluator API
                    print(f"Calling {args.evaluator_model}...")
                    evaluation_text = api_client.call_evaluator(request)

                    # Extract score
                    score = score_extractor.extract_score(evaluation_text)

                    # Write result
                    result_writer.write_result(
                        question_id=question_id,
                        condition=condition,
                        criterion=criterion,
                        evaluation_text=evaluation_text,
                        score=score,
                        evaluator_model=args.evaluator_model
                    )

                    print(f"✓ Score: {score if score is not None else 'N/A'}")
                    total_evaluations += 1

                except Exception as e:
                    print(f"✗ Error: {e}")
                    continue

    print(f"\n{'='*60}")
    print(f"Completed {total_evaluations} evaluations")
    print(f"Results saved to: {args.output_dir}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
