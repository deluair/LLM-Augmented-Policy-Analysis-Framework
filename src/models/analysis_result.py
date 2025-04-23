"""
Defines the data model for storing the output of a specific analysis component.
"""

from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
from datetime import datetime
import uuid

class AnalysisResult(BaseModel):
    """Represents the output of a single analysis step on a document."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique identifier for this specific analysis result.")
    document_id: str = Field(..., description="Identifier of the Document object this analysis pertains to.")
    analysis_type: str = Field(..., description="Identifier for the type of analysis performed (e.g., 'sentiment', 'topic_modeling', 'ner', 'dissent_detection').")
    results: Dict[str, Any] = Field(..., description="The structured results of the analysis (e.g., {'score': 0.8, 'label': 'positive'}, {'topics': [...]}, {'entities': [...]}).")
    analyzer_name: Optional[str] = Field(None, description="Name or identifier of the specific analyzer class/module used.")
    model_info: Optional[Dict[str, Any]] = Field(None, description="Information about the model used for the analysis (e.g., name, version, parameters).")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Timestamp when the analysis was performed.")
    version: int = Field(default=1, description="Version of the analysis result structure or the analyzer.")

    class Config:
        schema_extra = {
            "example": {
                "id": "ar_789xyz",
                "document_id": "doc_123",
                "analysis_type": "sentiment_analysis",
                "results": {
                    "score": 0.92,
                    "label": "very positive",
                    "sentences": [
                        {"text": "Sentence 1...", "score": 0.8},
                        {"text": "Sentence 2...", "score": 0.95}
                    ]
                },
                "analyzer_name": "VaderSentimentAnalyzer",
                "model_info": {"model_type": "lexicon-based"},
                "timestamp": "2024-03-21T10:30:00Z",
                "version": 1
            },
            "example_topic": {
                "id": "ar_abc456",
                "document_id": "doc_456",
                "analysis_type": "topic_modeling",
                "results": {
                    "topics": [
                        {"id": 0, "keywords": ["inflation", "price", "economy"], "score": 0.65},
                        {"id": 1, "keywords": ["rates", "policy", "bank"], "score": 0.25}
                    ],
                    "dominant_topic": 0,
                    "summary": "Primary focus on inflation and economic prices."
                },
                "analyzer_name": "LatentDirichletAllocationAnalyzer",
                "model_info": {"num_topics": 5, "library": "gensim"},
                "timestamp": "2024-03-21T11:00:00Z",
                "version": 1
            }
        }

# Example Usage:
# if __name__ == "__main__":
#     sentiment_data = {
#         "document_id": "doc_xyz",
#         "analysis_type": "sentiment",
#         "results": {"score": -0.5, "label": "negative"},
#         "analyzer_name": "BasicSentiment",
#         "model_info": {"version": "1.1"}
#     }
#     analysis_res = AnalysisResult(**sentiment_data)
#     
#     print(analysis_res.json(indent=2))
