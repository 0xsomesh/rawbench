"""
Results management and reporting.
"""

"""Result handling and reporting components."""

# Import core result classes
from .result import Result, ResultCollector
from .html_export import export_results_to_html

__all__ = ['Result', 'ResultCollector', 'export_results_to_html']
