"""
Manages the storage and retrieval of pre-computed embeddings.

Note: May be less critical if the vector database handles embedding storage internally,
      but can be useful for caching or managing embeddings independently.
"""

import logging
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Union
import numpy as np # Embeddings are often numpy arrays

from src.utils.exceptions import DataStorageError

logger = logging.getLogger(__name__)

class BaseEmbeddingStore(ABC):
    """Abstract base class for storing and retrieving document embeddings."""

    @abstractmethod
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initializes the embedding store.

        Args:
            config (Optional[Dict[str, Any]]): Configuration options specific to the implementation 
                                                (e.g., file path, database connection).
        """
        pass

    @abstractmethod
    def save_embeddings(self, document_id: str, embeddings: Union[np.ndarray, List[List[float]]], metadata: Optional[Dict[str, Any]] = None) -> None:
        """Saves embeddings for a specific document.

        Args:
            document_id (str): The unique identifier of the document.
            embeddings (Union[np.ndarray, List[List[float]]]): The embedding vectors.
            metadata (Optional[Dict[str, Any]]): Optional metadata (e.g., model used, text chunks).
        
        Raises:
            DataStorageError: If saving fails.
        """
        pass

    @abstractmethod
    def retrieve_embeddings(self, document_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves embeddings for a specific document.

        Args:
            document_id (str): The unique identifier of the document.

        Returns:
            Optional[Dict[str, Any]]: Dictionary containing 'embeddings' and 'metadata', 
                                      or None if not found.
            
        Raises:
            DataStorageError: If retrieval fails (other than not found).
        """
        pass
        
    @abstractmethod
    def delete_embeddings(self, document_id: str) -> bool:
        """Deletes embeddings for a specific document.

        Args:
            document_id (str): The unique identifier of the document.

        Returns:
            bool: True if deleted successfully or not found, False otherwise.
            
        Raises:
            DataStorageError: If deletion fails.
        """
        pass

    # Optional: Method to check if embeddings exist
    def embeddings_exist(self, document_id: str) -> bool:
        """Checks if embeddings exist for a given document ID."""
        try:
            return self.retrieve_embeddings(document_id) is not None
        except DataStorageError:
            # Depending on desired behavior, log and return False or re-raise
            logger.warning(f"Error checking existence for embeddings of '{document_id}'", exc_info=True)
            return False 

# Example concrete implementation (e.g., saving as .npy files)
# class FileSystemEmbeddingStore(BaseEmbeddingStore):
#     def __init__(self, config: Optional[Dict[str, Any]] = None):
#         # Implementation details: base path, file structure...
#         pass 
#     # ... implement abstract methods using np.save/np.load and file operations ...
