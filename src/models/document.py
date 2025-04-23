"""
Defines the core data model for a generic document.
"""

from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
import uuid
from datetime import datetime

class Document(BaseModel):
    """Represents a single text document processed by the system."""
    
    # Use Field default_factory for mutable defaults like uuid
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique identifier for the document.")
    content: str = Field(..., description="The main text content of the document.")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Arbitrary metadata associated with the document (e.g., author, source URL, publication date).")
    source: Optional[str] = Field(None, description="Identifier for the origin of the document (e.g., filename, database ID).")
    tags: List[str] = Field(default_factory=list, description="List of tags or keywords associated with the document.")
    embedding: Optional[List[float]] = Field(None, description="Optional vector embedding of the document content.")
    processed_at: Optional[datetime] = Field(None, description="Timestamp when the document was last processed or ingested.")

    class Config:
        # Example configuration: allows extra fields if needed, though often stricter is better
        # extra = 'allow' 
        # Or configure schema examples
        schema_extra = {
            "example": {
                "id": "a1b2c3d4-e5f6-7890-1234-567890abcdef",
                "content": "The central bank announced new measures today...",
                "metadata": {
                    "source_url": "http://example.com/news/123",
                    "publication_date": "2024-01-15T10:00:00Z",
                    "author": "Jane Doe",
                    "sentiment_score": 0.75
                },
                "source": "example.com news feed",
                "tags": ["central bank", "monetary policy", "interest rates"],
                "processed_at": "2024-01-15T11:30:00Z"
            }
        }

# Example Usage:
# if __name__ == "__main__":
#     doc_data = {
#         "content": "Interest rates were held steady following the committee meeting.",
#         "metadata": {"publication_date": "2024-02-10", "source_type": "press release"},
#         "source": "Central Bank Website"
#     }
#     doc = Document(**doc_data)
#     doc.tags.extend(["interest rates", "monetary policy", "central bank"])
#     doc.processed_at = datetime.now()
#     
#     print(doc.id)
#     print(doc.json(indent=2))
#
#     # Example with default ID generation
#     doc2 = Document(content="Another document content.")
#     print(f"\nDocument 2 ID: {doc2.id}")
