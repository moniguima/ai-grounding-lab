# Configs Directory

This directory is reserved for future configuration files that may control experimental parameters, model settings, or batch processing workflows.

## Planned Features

### run.yaml (Future)

Example configuration for batch experiments:

```yaml
experiment:
  name: "llama3-sgp-evaluation"
  timestamp: "2025-11-05"

models:
  - name: "llama-3.1-8b"
    source: "LMStudio"
    base_url: "http://localhost:1234/v1"

generation:
  temperature: 0.2
  max_tokens: 1024
  seed: 42

questions:
  source: "data/questions.jsonl"
  filter: null  # or list of qids: ["Q1", "Q2"]

protocol:
  enabled: true
  path: "protocol/SGP_compact.md"

evaluation:
  enabled: true
  evaluator_model: "gpt-4o-mini"
  endpoint: "https://api.openai.com/v1/chat/completions"
  rubric: "protocol/evaluation_scoring_rubric.md"
  modes:
    - single-answer
    - pairwise

output:
  raw_dir: "runs/raw"
  eval_dir: "runs/evals"
```

### model_configs/ (Future)

Model-specific parameter overrides:
- `llama3.yaml`
- `gpt4.yaml`
- `claude.yaml`

### Custom Configurations

You can create your own configuration files here for:
- Multi-model comparison experiments
- Domain-specific question sets
- Alternative protocol variants
- Custom evaluation rubrics

## Usage

Currently, this directory serves as a placeholder for future enhancements.
All configuration is done via command-line arguments to the individual scripts.

To use custom configs in your workflow:
1. Create your YAML/JSON config file here
2. Load it in your orchestration script
3. Pass parameters to the Python scripts programmatically

Example:
```python
import yaml
from pathlib import Path

config = yaml.safe_load(Path("configs/run.yaml").read_text())
# Use config values to construct CLI commands or call scripts directly
```
