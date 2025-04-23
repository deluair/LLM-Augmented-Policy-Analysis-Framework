"""
Defines the data model for a Policy Brief, often a synthesized output.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
import uuid

from .document import Document # Assuming Document model is in the same directory

class PolicyBrief(BaseModel):
    """Represents a structured policy brief, potentially generated from analysis."""
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique identifier for the policy brief.")
    title: str = Field(..., description="The title of the policy brief.")
    summary: str = Field(..., description="A concise summary of the policy brief's content.")
    key_findings: List[str] = Field(default_factory=list, description="Bulleted list of key findings or insights.")
    recommendations: List[str] = Field(default_factory=list, description="Actionable recommendations derived from the analysis.")
    source_document_ids: List[str] = Field(default_factory=list, description="List of IDs of source documents used to generate this brief.")
    analysis_metadata: Dict[str, Any] = Field(default_factory=dict, description="Metadata about the analysis process that generated this brief (e.g., models used, parameters).")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Timestamp when the policy brief was created.")
    version: int = Field(default=1, description="Version number of the policy brief.")
    tags: List[str] = Field(default_factory=list, description="Tags relevant to the policy brief's content.")

    class Config:
        schema_extra = {
            "example": {
                "id": "pb_a1b2c3d4",
                "title": "Analysis of Recent Monetary Policy Statements",
                "summary": "The latest statements indicate a continued focus on inflation control, with potential for future rate adjustments based on upcoming economic data.",
                "key_findings": [
                    "Sentiment towards inflation remains high.",
                    "Forward guidance suggests data-dependency for future rate hikes.",
                    "Dissent among committee members noted on the pace of tightening."
                ],
                "recommendations": [
                    "Monitor upcoming CPI and employment reports closely.",
                    "Assess portfolio risk exposure to potential rate volatility."
                ],
                "source_document_ids": ["doc_123", "doc_456", "doc_789"],
                "analysis_metadata": {
                    "sentiment_model": "bert-base-uncased-finetuned",
                    "topic_model": "LDA-5topics",
                    "run_id": "run_xyz789"
                },
                "created_at": "2024-03-20T15:00:00Z",
                "version": 1,
                "tags": ["monetary policy", "inflation", "central bank", "interest rates"]
            }
        }

# Example Usage:
# if __name__ == "__main__":
#     brief_data = {
#         "title": "Impact Assessment of New Trade Regulations",
#         "summary": "The new regulations are expected to have a mixed impact on domestic industries.",
#         "key_findings": ["Sector A likely to benefit.", "Sector B faces challenges."],
#         "recommendations": ["Provide support for Sector B.", "Monitor import/export data."],
#         "source_document_ids": ["doc_abc", "doc_def"]
#     }
#     policy_brief = PolicyBrief(**brief_data)
#     policy_brief.tags.append("trade policy")
#     
#     print(policy_brief.json(indent=2))
