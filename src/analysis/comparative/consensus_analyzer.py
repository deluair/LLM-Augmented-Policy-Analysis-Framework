"""
Analyzes the level of consensus or disagreement among different sources or viewpoints.
"""
from typing import List, Dict, Any
from collections import Counter

def analyze_consensus(analysis_outputs: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analyzes consensus across multiple analysis outputs.

    Assumes each dictionary in analysis_outputs might contain keys like 
    'sentiment', 'key_themes', 'identified_stakeholders', etc.

    Args:
        analysis_outputs: A list of dictionaries, each representing an analysis result 
                          (e.g., from different stakeholder groups or documents).

    Returns:
        A dictionary summarizing the consensus level and key points of agreement/
        disagreement.
    """
    num_outputs = len(analysis_outputs)
    if num_outputs < 2:
        return {
            'overall_consensus_level': 'N/A (Insufficient data)',
            'points_of_agreement': [],
            'points_of_disagreement': [],
            'conflicting_views_details': {},
            'notes': 'Requires at least two analysis outputs to compare.'
        }

    # --- Placeholder Logic --- 
    # This needs refinement based on the actual structure of analysis_outputs
    # Example: Analyze consensus on 'key_themes'
    all_themes = [theme for output in analysis_outputs if 'key_themes' in output for theme in output['key_themes']]
    theme_counts = Counter(all_themes)
    
    points_of_agreement = []
    points_of_disagreement = []
    conflicting_views = {}

    # Identify themes mentioned in most/all outputs as agreement points
    # Identify themes mentioned only in a few as potential disagreement/niche points
    for theme, count in theme_counts.items():
        if count >= num_outputs * 0.8: # Arbitrary threshold for strong agreement
            points_of_agreement.append(f"General agreement on the importance of theme: '{theme}'.")
        elif count <= num_outputs * 0.2: # Arbitrary threshold for low consensus / niche topic
            points_of_disagreement.append(f"Limited consensus on the relevance of theme: '{theme}'.")
        else: # Moderate consensus or potential conflict
             # More sophisticated logic needed here to detect actual conflict vs. variance
             pass

    # Example: Analyze consensus on 'sentiment'
    sentiments = [output.get('sentiment') for output in analysis_outputs if 'sentiment' in output]
    sentiment_counts = Counter(sentiments)
    if len(sentiment_counts) == 1 and sentiments:
        points_of_agreement.append(f"Universal sentiment expressed: '{sentiments[0]}'.")
    elif len(sentiment_counts) > 1:
        points_of_disagreement.append("Diverging sentiments detected across outputs.")
        conflicting_views['sentiment'] = dict(sentiment_counts)
        
    # --- Determine Overall Consensus Level (Simple Example) --- 
    overall_consensus_level = 'Moderate' # Default
    if not points_of_disagreement and points_of_agreement:
        overall_consensus_level = 'High'
    elif points_of_disagreement and not points_of_agreement:
        overall_consensus_level = 'Low'
    elif not points_of_disagreement and not points_of_agreement:
         overall_consensus_level = 'Indeterminate'

    # TODO: Refine consensus level calculation based on the number and nature of agreements/disagreements

    return {
        'overall_consensus_level': overall_consensus_level,
        'points_of_agreement': points_of_agreement,
        'points_of_disagreement': points_of_disagreement,
        'conflicting_views_details': conflicting_views,
        'notes': f'Analysis based on {num_outputs} outputs.'
    }
