"""
Synthesis sub-package for combining analysis results.
"""

from .recommendation_generator import generate_recommendations
from .summary_builder import build_summary
from .insight_generator import generate_insights

__all__ = [
    'generate_recommendations',
    'build_summary',
    'generate_insights',
]
