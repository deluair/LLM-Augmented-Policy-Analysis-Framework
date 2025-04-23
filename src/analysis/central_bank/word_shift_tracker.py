"""
Tracks changes in word usage or frequency between different central bank 
communications or time periods.

Useful for identifying shifts in focus, tone, or key topics.
"""

from typing import Any, Dict, List, Tuple
from collections import Counter
import re # For basic text cleaning

from ..base import BaseAnalyzer

class WordShiftTracker(BaseAnalyzer):
    """Analyzes shifts in word frequencies between texts."""

    def _get_word_frequencies(self, text: str) -> Counter:
        """Helper method to count word frequencies in cleaned text."""
        words = re.findall(r'\b\w+\b', text.lower()) # Simple word extraction
        # TODO: Add more sophisticated text cleaning (stopwords, stemming/lemmatization)
        return Counter(words)

    def analyze(self, text_data_1: str, text_data_2: str, **kwargs) -> Dict[str, Any]:
        """Compares word frequencies between two texts to identify shifts.

        Args:
            text_data_1: The first text document (e.g., earlier period).
            text_data_2: The second text document (e.g., later period).
            **kwargs: Additional parameters (e.g., min_frequency, significance_threshold).

        Returns:
            A dictionary highlighting significant word shifts, e.g.,
            {'increased_frequency': List[Tuple[str, float]], 
             'decreased_frequency': List[Tuple[str, float]], 
             'relative_shift_scores': Dict[str, float]}.
        """
        print(f"Analyzing word shifts in {self.__class__.__name__}...")
        
        freq1 = self._get_word_frequencies(self._preprocess(text_data_1))
        freq2 = self._get_word_frequencies(self._preprocess(text_data_2))

        # Placeholder Logic for comparing frequencies
        increased_frequency = []
        decreased_frequency = []
        relative_shift_scores = {}
        min_freq_threshold = kwargs.get('min_frequency', 5) # Ignore infrequent words

        all_words = set(freq1.keys()) | set(freq2.keys())

        total_words1 = sum(freq1.values()) or 1 # Avoid division by zero
        total_words2 = sum(freq2.values()) or 1

        for word in all_words:
            count1 = freq1.get(word, 0)
            count2 = freq2.get(word, 0)

            if count1 < min_freq_threshold and count2 < min_freq_threshold:
                continue # Skip words infrequent in both texts

            # Calculate relative frequencies
            rel_freq1 = count1 / total_words1
            rel_freq2 = count2 / total_words2

            # Simple relative change (could use more robust metrics like log odds ratio)
            if rel_freq1 == 0: # Avoid division by zero if word is new
                relative_change = float('inf') if rel_freq2 > 0 else 0
            else:
                relative_change = (rel_freq2 - rel_freq1) / rel_freq1

            relative_shift_scores[word] = relative_change

            # TODO: Add statistical significance testing (e.g., chi-squared, log-likelihood ratio)
            # to identify truly significant shifts, not just random fluctuations.

            # Example threshold for significant change (needs proper statistical basis)
            if relative_change > 0.5: # Arbitrary threshold for increase
                increased_frequency.append((word, relative_change))
            elif relative_change < -0.33: # Arbitrary threshold for decrease
                decreased_frequency.append((word, relative_change))

        # Sort by magnitude of shift
        increased_frequency.sort(key=lambda item: item[1], reverse=True)
        decreased_frequency.sort(key=lambda item: item[1])

        results = {
            'increased_frequency': increased_frequency[:20], # Limit output size
            'decreased_frequency': decreased_frequency[:20], # Limit output size
            'relative_shift_scores': {k: v for k, v in sorted(relative_shift_scores.items(), key=lambda item: abs(item[1]), reverse=True)[:50]} # Top 50 absolute shifts
        }

        final_results = self._postprocess(results)
        return final_results
