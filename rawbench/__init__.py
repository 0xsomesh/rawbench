"""
RawBench Prompt Evaluation - A tool for evaluating LLM prompts across models.
"""

# Core functionality
from .core.evaluation import Evaluation

# Configuration
from .config.loader import load_config, validate_config

# Results
from .results.result import Result, ResultCollector
# from .results.markdown_transformer import MarkdownTransformer

# Version info
__version__ = "0.1.0"

# Expose core classes and functions
__all__ = [
    # Core
    "Evaluation",
    
    # Config
    "load_config",
    "validate_config",
    "convert_json_to_yaml",

    # Results
    "Result",
    "ResultCollector",
    "MarkdownTransformer",
]