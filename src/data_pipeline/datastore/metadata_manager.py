"""
Manages metadata associated with documents and the data pipeline process.
"""

import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List

from src.utils.exceptions import DataStorageError

logger = logging.getLogger(__name__)

class BaseMetadataManager(ABC):
    """Abstract base class for managing document and process metadata."""

    @abstractmethod
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initializes the metadata manager.

        Args:
            config (Optional[Dict[str, Any]]): Configuration options specific to the implementation 
                                                (e.g., database connection string, file path).
        """
        pass

    @abstractmethod
    def save_metadata(self, document_id: str, metadata: Dict[str, Any]) -> None:
        """Saves or updates metadata for a specific document.

        Args:
            document_id (str): The unique identifier of the document.
            metadata (Dict[str, Any]): The metadata dictionary to save.
        
        Raises:
            DataStorageError: If saving fails.
        """
        pass

    @abstractmethod
    def retrieve_metadata(self, document_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves metadata for a specific document.

        Args:
            document_id (str): The unique identifier of the document.

        Returns:
            Optional[Dict[str, Any]]: The metadata dictionary, or None if not found.
            
        Raises:
            DataStorageError: If retrieval fails (other than not found).
        """
        pass
        
    @abstractmethod
    def update_metadata_field(self, document_id: str, field: str, value: Any) -> None:
        """Updates a specific field within the metadata for a document.

        Args:
            document_id (str): The unique identifier of the document.
            field (str): The metadata field key to update.
            value (Any): The new value for the field.
        
        Raises:
            DataStorageError: If update fails or document/field doesn't exist (depending on implementation).
        """
        pass

    @abstractmethod
    def query_metadata(self, query_criteria: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Queries metadata based on specified criteria.

        Args:
            query_criteria (Dict[str, Any]): Criteria to filter metadata (e.g., {'source': 'SEC', 'processed_status': 'pending'}).

        Returns:
            List[Dict[str, Any]]: A list of metadata dictionaries matching the criteria.
            
        Raises:
            DataStorageError: If querying fails.
        """
        pass

    @abstractmethod
    def delete_metadata(self, document_id: str) -> bool:
        """Deletes metadata for a specific document.

        Args:
            document_id (str): The unique identifier of the document.

        Returns:
            bool: True if deleted successfully or not found, False otherwise.
            
        Raises:
            DataStorageError: If deletion fails.
        """
        pass

# Example concrete implementation (could be in a separate file or below)
# class JsonFileMetadataManager(BaseMetadataManager):
#     """ VERY basic implementation using a single JSON file (NOT suitable for production!). """
#     def __init__(self, config: Optional[Dict[str, Any]] = None):
#         self.filepath = Path(config.get('filepath', './metadata_store.json'))
#         self._load_data()
#         logger.info(f"JsonFileMetadataManager initialized with file: {self.filepath}")
# 
#     def _load_data(self):
#         try:
#             if self.filepath.exists():
#                 with open(self.filepath, 'r') as f:
#                     self.data = json.load(f)
#             else:
#                 self.data = {}
#         except (IOError, json.JSONDecodeError) as e:
#             logger.error(f"Failed to load metadata from {self.filepath}: {e}")
#             self.data = {} # Start fresh or raise error?
# 
#     def _save_data(self):
#         try:
#             with open(self.filepath, 'w') as f:
#                 json.dump(self.data, f, indent=2)
#         except IOError as e:
#             logger.error(f"Failed to save metadata to {self.filepath}: {e}")
#             raise DataStorageError(f"Failed to write metadata file: {e}")
# 
#     def save_metadata(self, document_id: str, metadata: Dict[str, Any]) -> None:
#         self.data[document_id] = metadata
#         self._save_data()
# 
#     def retrieve_metadata(self, document_id: str) -> Optional[Dict[str, Any]]:
#         return self.data.get(document_id)
#         
#     def update_metadata_field(self, document_id: str, field: str, value: Any) -> None:
#         if document_id in self.data:
#             self.data[document_id][field] = value
#             self._save_data()
#         else:
#              logger.warning(f"Document ID '{document_id}' not found for metadata update.")
#             # Optionally raise an error
# 
#     def query_metadata(self, query_criteria: Dict[str, Any]) -> List[Dict[str, Any]]:
#         results = []
#         for doc_id, meta in self.data.items():
#             match = True
#             for key, value in query_criteria.items():
#                 if meta.get(key) != value:
#                     match = False
#                     break
#             if match:
#                 results.append({**meta, '_document_id': doc_id}) # Add id back for context
#         return results
# 
#     def delete_metadata(self, document_id: str) -> bool:
#         if document_id in self.data:
#             del self.data[document_id]
#             self._save_data()
#             return True
#         return False
