# Contributing to AI Grounding Lab

Thank you for your interest in contributing to the AI Grounding Lab! This project aims to create a reproducible, scientifically rigorous framework for testing LLM grounding protocols.

## Table of Contents

- [How to Contribute](#how-to-contribute)
- [Code of Conduct](#code-of-conduct)
- [Development Guidelines](#development-guidelines)
- [Submitting Contributions](#submitting-contributions)
- [Testing](#testing)
- [Documentation Standards](#documentation-standards)

## How to Contribute

### Areas Where We Need Help

1. **Test Questions**: Additional questions across diverse domains
2. **Protocol Variants**: Alternative grounding protocol designs
3. **Evaluation**: Refinements to the scoring rubric
4. **Tooling**: Integration with other LLM APIs (OpenAI, Anthropic, HuggingFace)
5. **Analysis**: Statistical analysis tools and visualization
6. **Documentation**: Tutorials, examples, case studies

### Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR-USERNAME/ai-grounding-lab.git
   cd ai-grounding-lab
   ```
3. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```
4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Code of Conduct

### Our Standards

- **Be respectful and inclusive**: Welcome contributors of all backgrounds
- **Be collaborative**: Focus on what's best for the project
- **Be constructive**: Provide helpful feedback and accept criticism gracefully
- **Be rigorous**: Maintain scientific standards and reproducibility

### Unacceptable Behavior

- Harassment, discrimination, or personal attacks
- Publishing others' private information
- Trolling, insulting comments, or deliberate disruption
- Any conduct inappropriate in a professional setting

## Development Guidelines

### Code Style

#### Python Code Standards

All Python code must follow these principles:

1. **SOLID Principles** (mandatory):
   - **Single Responsibility**: Each class/function does one thing
   - **Open/Closed**: Design for extension without modification
   - **Liskov Substitution**: Subtypes must be substitutable for base types
   - **Interface Segregation**: Many specific interfaces over one general
   - **Dependency Inversion**: Depend on abstractions, not concretions

2. **PEP 8 Compliance**:
   - Use 4 spaces for indentation (no tabs)
   - Maximum line length: 88 characters (Black formatter standard)
   - Use meaningful variable and function names

3. **Type Hints** (required):
   ```python
   def compose_prompt(question: str, protocol: Optional[str] = None) -> str:
       """
       Compose a prompt with optional protocol wrapper.

       Args:
           question: The question text to wrap.
           protocol: Optional protocol text to prepend.

       Returns:
           The composed prompt string.
       """
       ...
   ```

4. **Docstrings** (required for all public functions/classes):
   - Use Google-style or NumPy-style docstrings
   - Include Args, Returns, Raises sections
   - Provide usage examples for complex functions

5. **Error Handling**:
   - Use specific exceptions, not bare `except:`
   - Provide informative error messages
   - Clean up resources properly (use context managers)

#### Example Good Code

```python
from typing import Iterator, Dict
from pathlib import Path

class QuestionLoader:
    """Loads questions from JSONL files following SRP."""

    @staticmethod
    def load_questions(filepath: Path) -> Iterator[Dict[str, str]]:
        """
        Load questions from a JSONL file.

        Args:
            filepath: Path to the JSONL file.

        Yields:
            Dictionary containing question metadata.

        Raises:
            FileNotFoundError: If the file does not exist.
            json.JSONDecodeError: If JSON is malformed.
        """
        if not filepath.exists():
            raise FileNotFoundError(f"Questions file not found: {filepath}")

        with open(filepath, "r", encoding="utf-8") as f:
            for line_num, line in enumerate(f, start=1):
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                try:
                    yield json.loads(line)
                except json.JSONDecodeError as e:
                    raise json.JSONDecodeError(
                        f"Invalid JSON on line {line_num}",
                        e.doc,
                        e.pos
                    )
```

### File Organization

- **Scripts**: All executable scripts in `src/`
- **Data**: Test data in `data/`
- **Protocols**: Protocol documents in `protocol/`
- **Docs**: Additional documentation in `docs/`
- **Tests**: Unit tests in `tests/` (if/when added)

### Git Commit Messages

Follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring without feature changes
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples:**
```
feat(eval): add support for Claude API evaluation
fix(compose): handle comments in JSONL input files
docs(readme): add installation troubleshooting section
refactor(runner): extract API client logic into separate class
```

## Submitting Contributions

### Pull Request Process

1. **Update documentation**: Ensure README and docstrings reflect your changes
2. **Add tests** (if applicable): Include test cases for new functionality
3. **Update CHANGELOG**: Add a brief description of your changes
4. **Run tests locally**: Verify everything works before submitting
5. **Create a pull request**:
   - Use a clear, descriptive title
   - Reference any related issues (#123)
   - Describe what changed and why
   - Include before/after examples if applicable

### Pull Request Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Code refactoring

## Testing
Describe how you tested your changes

## Checklist
- [ ] Code follows SOLID principles
- [ ] Added type hints to all functions
- [ ] Added/updated docstrings
- [ ] Updated relevant documentation
- [ ] Tested locally
```

### Code Review

All submissions require review. We review for:
- **Correctness**: Does the code work as intended?
- **Design**: Does it follow SOLID principles?
- **Clarity**: Is the code readable and well-documented?
- **Testing**: Are edge cases handled?
- **Performance**: Are there obvious bottlenecks?

## Testing

### Manual Testing

Before submitting, test your changes with the full workflow:

```bash
# 1. Compose prompts
python3 src/compose_prompts.py \
  --questions data/questions.jsonl \
  --protocol protocol/SGP_compact.md \
  --out-dir data/prompts

# 2. Test with a sample model (if applicable)
# 3. Verify outputs are well-formed JSONL
```

### Unit Tests (Future)

We're working on adding a test suite. Contributions welcome!

Planned structure:
```
tests/
├── test_compose_prompts.py
├── test_eval_scores.py
├── test_aggregate.py
└── fixtures/
    ├── sample_questions.jsonl
    └── sample_responses.jsonl
```

## Documentation Standards

### README Updates

When adding features, update the README with:
- Installation requirements (if new dependencies)
- Usage examples
- Configuration options
- Any breaking changes

### Code Comments

- **Use comments sparingly**: Good code is self-documenting
- **Explain WHY, not WHAT**: The code shows what; comments explain why
- **Keep comments up-to-date**: Outdated comments are worse than no comments

```python
# Good: Explains the reasoning
# Skip comments because JSONL files may have metadata headers
if line.startswith("#"):
    continue

# Bad: Just repeats what the code does
# Check if line starts with #
if line.startswith("#"):
    continue
```

## Questions or Need Help?

- **Open an issue**: For bugs, feature requests, or questions
- **Discussions**: For broader topics or brainstorming
- **LinkedIn**: https://www.linkedin.com/in/moniguima/ (for private inquiries)

## Recognition

Contributors will be acknowledged in:
- The project README
- Release notes for significant contributions
- Academic citations (if contributing to research results)

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for helping make AI systems more reliable and scientifically grounded!
