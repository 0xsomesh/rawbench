"""
Results management and reporting.
"""

"""Result handling and reporting components."""

# Import core result classes
from .result import Result, ResultCollector

# # Lazy load transformer to avoid circular imports
# MarkdownTransformer = None
# def get_transformer():
#     global MarkdownTransformer
#     if MarkdownTransformer is None:
#         from .markdown_transformer import MarkdownTransformer as MT
#         MarkdownTransformer = MT
#     return MarkdownTransformer

__all__ = ['Result', 'ResultCollector']
