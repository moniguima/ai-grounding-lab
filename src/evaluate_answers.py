#!/usr/bin/env python3
"""
Automate AI evaluation of answers using criterion-specific prompts.

This script evaluates answers from questions_and_answers.md using detailed
evaluation prompts from docs/prompts/ and an external AI evaluator API.

Author: Monica Guimaraes
Created: 2025-11-05
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

sys.path.insert(0, str(Path(__file__).parent))
from configuration import (
    DEFAULT_MODEL,
    _load_environment_variables,
    _configure_langsmith_tracing,
    _check_langsmith_status,
    _get_openai_api_key,
)
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage


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


class JsonlAnswerParser:
    """
    Parses answers from a JSONL file (data/answers.jsonl).

    Follows Single Responsibility Principle: only handles JSONL answer loading.
    """

    def __init__(self, answers_file: Path):
        """
        Initialize with path to answers JSONL file.

        Args:
            answers_file: Path to the answers.jsonl file.
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
            for line in f:
                line = line.strip()
                if not line:
                    continue
                record = json.loads(line)
                answers.append({
                    "question_id": record.get("question_id", ""),
                    "question_text": record.get("question", ""),
                    "answer_without_protocol": record.get("answer_without_protocol", ""),
                    "answer_with_protocol": record.get("answer_with_protocol", ""),
                })
        return answers


class AnswerParser:
    """
    Parses answers from questions_and_answers.md file.

    Follows Single Responsibility Principle: only handles answer extraction.
    """

    def __init__(self, qa_file: Path):
        """
        Initialize with path to questions and answers file.

        Args:
            qa_file: Path to questions_and_answers.md file.
        """
        self.qa_file = qa_file

    def parse_answers(self) -> List[Dict[str, str]]:
        """
        Parse all question-answer pairs from the file.

        Returns:
            List of dictionaries containing:
                - question_id: e.g., "Q1"
                - question_text: The question
                - answer_without_protocol: Answer text
                - answer_with_protocol: Answer text
        """
        with open(self.qa_file, "r", encoding="utf-8") as f:
            content = f.read()

        # Split by main sections (## 1., ## 2., etc.)
        # Handle first section specially since it starts with ## without newline
        if content.startswith("## "):
            content = "\n" + content

        sections = re.split(r'\n(## \d+\.)', content)

        # Reconstruct sections by pairing headers with content
        # sections will be: ['before_content', '## 1.', 'content1', '## 2.', 'content2', ...]
        reconstructed = []
        for i in range(1, len(sections), 2):
            if i + 1 < len(sections):
                reconstructed.append(sections[i] + sections[i + 1])
            else:
                reconstructed.append(sections[i])

        answers = []
        for section in reconstructed:
            qa_pair = self._parse_section(section)
            if qa_pair:
                answers.append(qa_pair)

        return answers

    def _parse_section(self, section: str) -> Optional[Dict[str, str]]:
        """
        Parse a single section containing Q&A.

        Args:
            section: Text of one section.

        Returns:
            Dictionary with question and answers, or None if parsing fails.
        """
        # Extract question ID and text
        q_match = re.search(r'### (Q\d+):\s*(.+?)(?=\n---|\n###)', section, re.DOTALL)
        if not q_match:
            return None

        question_id = q_match.group(1)
        question_text = q_match.group(2).strip()

        # Extract answer without protocol
        # Pattern: ### A1-NP: Answer without protocol:\n[content]\n---\n### A1-WP:
        anp_match = re.search(
            r'### A\d+-NP:[^\n]*\n\n(.*?)(?=\n---\n### A\d+-WP:|$)',
            section,
            re.DOTALL
        )
        answer_np = anp_match.group(1).strip() if anp_match else ""

        # Extract answer with protocol
        # Pattern: ### A1-WP: Answer with protocol:\n[content]
        awp_match = re.search(
            r'### A\d+-WP:[^\n]*\n\n(.*?)(?=\n\n## \d+\.|$)',
            section,
            re.DOTALL
        )
        answer_wp = awp_match.group(1).strip() if awp_match else ""

        return {
            "question_id": question_id,
            "question_text": question_text,
            "answer_without_protocol": answer_np,
            "answer_with_protocol": answer_wp
        }


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
    Handles API calls to the AI evaluator service via LangChain ChatOpenAI.

    Using ChatOpenAI enables automatic LangSmith tracing of all evaluator calls.

    Follows Single Responsibility Principle: only handles API communication.
    Follows Dependency Inversion: depends on abstract API interface.
    """

    def __init__(
        self,
        api_key: str,
        model: str,
        temperature: float = 0.0,
        max_tokens: int = 4000
    ):
        """
        Initialize API client.

        Args:
            api_key: OpenAI API authentication key.
            model: Model name to use.
            temperature: Sampling temperature.
            max_tokens: Maximum tokens in response.
        """
        self.model = model
        self._llm = ChatOpenAI(
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            api_key=api_key,
        )

    def call_evaluator(self, prompt: str) -> str:
        """
        Call the AI evaluator via LangChain (traced automatically by LangSmith).

        Args:
            prompt: The evaluation request prompt.

        Returns:
            The evaluator's response text.
        """
        response = self._llm.invoke([HumanMessage(content=prompt)])
        return response.content


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
        help="Path to answers JSONL file (default: data/answers.jsonl)"
    )
    parser.add_argument(
        "--qa-file",
        type=Path,
        default=None,
        help="Path to questions and answers markdown file (legacy; overrides --answers-file)"
    )
    parser.add_argument(
        "--prompts-dir",
        type=Path,
        default=Path("docs/AI_prompts"),
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
        "--evaluator-model",
        type=str,
        default=DEFAULT_MODEL,
        help=f"Model to use for evaluation (default: {DEFAULT_MODEL})"
    )
    parser.add_argument(
        "--condition",
        type=str,
        choices=["with-protocol", "without-protocol", "both"],
        default="both",
        help="Which condition to evaluate (default: both)"
    )
    parser.add_argument(
        "--question-id",
        type=str,
        default=None,
        help="Evaluate only this question ID (e.g., Q1). Omit to evaluate all."
    )

    args = parser.parse_args()

    # Environment setup: loads .env, configures LangSmith tracing, validates API key
    _load_environment_variables()
    _configure_langsmith_tracing()
    _check_langsmith_status()
    try:
        api_key = _get_openai_api_key()
    except ValueError as e:
        print(f"Error: {e}")
        exit(1)

    # Initialize components
    prompt_loader = PromptLoader(args.prompts_dir)
    composer = EvaluationComposer()
    api_client = APIClient(
        api_key=api_key,
        model=args.evaluator_model,
    )
    result_writer = ResultWriter(args.output_dir)
    score_extractor = ScoreExtractor()

    # Load answers — JSONL by default, markdown if --qa-file is given
    if args.qa_file is not None:
        print(f"Loading answers from {args.qa_file}...")
        answers = AnswerParser(args.qa_file).parse_answers()
    else:
        print(f"Loading answers from {args.answers_file}...")
        answers = JsonlAnswerParser(args.answers_file).parse_answers()
    print(f"Found {len(answers)} question-answer pairs")

    # Filter by question ID if specified
    if args.question_id is not None:
        answers = [a for a in answers if a["question_id"] == args.question_id]
        if not answers:
            print(f"Error: No answer found for question ID '{args.question_id}'")
            exit(1)
        print(f"Filtered to question: {args.question_id}")

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
