"""
Evaluation Module
----------------
Model performance evaluation and comparison.
"""

from .core import CVEvaluator
from .runner import main as run_evaluation

__all__ = ["CVEvaluator", "run_evaluation"]
