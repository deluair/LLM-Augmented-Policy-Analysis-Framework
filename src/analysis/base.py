"""
Base classes and utilities for analysis modules.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict

class BaseAnalyzer(ABC):
    """Abstract base class for all analysis components."""

    def __init__(self, config: Dict[str, Any] = None):
        """Initialize the analyzer, potentially with configuration."""
        self.config = config or {}
        print(f"Initializing {self.__class__.__name__}")

    @abstractmethod
    def analyze(self, data: Any, **kwargs) -> Any:
        """Perform the analysis.
        
        Args:
            data: The input data for analysis.
            **kwargs: Additional parameters for the analysis.
            
        Returns:
            The results of the analysis.
        """
        pass

    def _preprocess(self, data: Any) -> Any:
        """Optional preprocessing step."""
        print(f"Preprocessing data in {self.__class__.__name__}...")
        # Default implementation: return data as is
        return data

    def _postprocess(self, results: Any) -> Any:
        """Optional postprocessing step."""
        print(f"Postprocessing results in {self.__class__.__name__}...")
        # Default implementation: return results as is
        return results

    def run(self, data: Any, **kwargs) -> Any:
        """Standard execution flow: preprocess, analyze, postprocess."""
        processed_data = self._preprocess(data)
        analysis_results = self.analyze(processed_data, **kwargs)
        final_results = self._postprocess(analysis_results)
        return final_results

# Example of how a specific analyzer might inherit:
# class SentimentAnalyzer(BaseAnalyzer):
#     def analyze(self, text_data: str, **kwargs) -> Dict[str, float]:
#         # Implementation using an NLP library
#         print(f"Analyzing sentiment for: {text_data[:50]}...")
#         # Placeholder logic
#         sentiment_score = 0.5 # Example score
#         return {'sentiment_score': sentiment_score}
