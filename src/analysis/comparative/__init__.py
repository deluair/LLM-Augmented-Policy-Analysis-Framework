"""
Comparative Analysis sub-package.

Modules for comparing different documents, policies, time periods, or narratives.
"""

from .consensus_analyzer import analyze_consensus 
from .cross_policy_analyzer import CrossPolicyAnalyzer 
from .historical_comparator import HistoricalComparator 
from .narrative_tracker import NarrativeTracker 

__all__ = [
    'analyze_consensus',
    'CrossPolicyAnalyzer', 
    'HistoricalComparator',
    'NarrativeTracker',
]
