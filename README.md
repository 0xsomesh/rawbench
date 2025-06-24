# RawBench Prompt Evaluation

Powerful, minimal framework for LLM prompt evaluation with YAML configuration, tool execution support, and comprehensive result tracking.

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

## 🚀 Features

- Multi-model testing with simultaneous evaluation
- YAML configuration with Docker-compose style anchors
- Variable substitution and template system
- Metrics for latency, tokens, and costs
- CLI and Python API interfaces

### Coming soon 🔜

- markdown reports
- tool mocking
- UI
- anthoric, openrouter support
- documentation
- pypi release

## 💻 Installation

```bash
git clone https://github.com/0xsomesh/rawbench.git
cd rawbench
make install

```

## 🧹 Usage

```bash
# make a new directory
mkdir prompts-eval
cd prompts-eval

# initiate rawbench
rawbench init

# configure openai api key in .env

# Run evaluation
rawbench run evaluations/template.yaml
```

## 🔖 Requirements

- Python ≥ 3.8

## 🪪 License

MIT