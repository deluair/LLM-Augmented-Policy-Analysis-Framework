"""
Manages the storage and retrieval of raw/original documents.
"""

import logging
import os
import json
from pathlib import Path
from typing import Optional, Dict, Any, Union
from urllib.parse import urlparse, quote, unquote 

from src.config import settings # Assuming storage path might be in settings
from src.utils.exceptions import DataStorageError, ConfigurationError

logger = logging.getLogger(__name__)

class FileSystemDocumentStore:
    """Stores and retrieves original documents using the file system."""

    def __init__(self, base_path: Optional[str] = None):
        """Initializes the document store.
        
        Args:
            base_path (Optional[str]): The root directory for storing documents. 
                                       Defaults to a path from settings or a local default.
        """
        _path = base_path or settings.storage.get("document_store_path", "./document_store")
        self.base_path = Path(_path)
        try:
            self.base_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"FileSystemDocumentStore initialized at: {self.base_path.resolve()}")
        except OSError as e:
             logger.error(f"Failed to create document store directory at {self.base_path}: {e}")
             raise ConfigurationError(f"Failed to create document store directory: {e}")

    def _get_storage_path(self, document_id: str) -> Path:
        """Determines the file path for a given document ID (e.g., URL).
           Creates a file-system-safe path from the ID.
        Args:
            document_id (str): The unique identifier for the document (e.g., URL).
        Returns:
            Path: The full path where the document should be stored.
        """
        # Sanitize the ID to make it filesystem-friendly
        # URLs can be long and contain special characters
        parsed_id = urlparse(document_id)
        domain = parsed_id.netloc.replace(':', '_') # Replace port separator
        # URL-encode the path part to handle slashes and special chars, then truncate
        path_part = quote(parsed_id.path.strip('/'), safe='').replace('%', '_')[:100] 
        # Use a simplified approach: domain/encoded_path_prefix
        # More robust might involve hashing the ID
        sanitized_id = f"{domain}/{path_part}"
        
        # Determine extension based on assumed content (or add metadata?)
        # For now, assume binary or text based on some heuristic or default
        # A better approach might store metadata alongside content
        # Example: If ID looks like a PDF URL
        if document_id.lower().endswith('.pdf'):
             ext = '.pdf'
        elif document_id.lower().endswith(('.htm', '.html')):
             ext = '.html'
        else:
             ext = '.bin' # Default to binary/unknown
             
        return self.base_path / f"{sanitized_id}{ext}"

    def save_document(self, document_id: str, content: Union[str, bytes], metadata: Optional[Dict[str, Any]] = None) -> None:
        """Saves a document's content to the file system.

        Args:
            document_id (str): Unique ID for the document (e.g., URL).
            content (Union[str, bytes]): The document content (text or binary).
            metadata (Optional[Dict[str, Any]]): Optional metadata to save alongside (e.g., content_type, headers).
        
        Raises:
            DataStorageError: If saving fails.
        """
        storage_path = self._get_storage_path(document_id)
        try:
            storage_path.parent.mkdir(parents=True, exist_ok=True)
            mode = 'wb' if isinstance(content, bytes) else 'w'
            encoding = None if isinstance(content, bytes) else 'utf-8'
            
            with open(storage_path, mode, encoding=encoding) as f:
                f.write(content)
            logger.debug(f"Saved document '{document_id}' to {storage_path}")
            
            # Optionally save metadata as a separate .meta.json file
            if metadata:
                 meta_path = storage_path.with_suffix(storage_path.suffix + '.meta.json')
                 with open(meta_path, 'w', encoding='utf-8') as mf:
                     json.dump(metadata, mf, indent=2)
                 logger.debug(f"Saved metadata for '{document_id}' to {meta_path}")

        except IOError as e:
            logger.error(f"Failed to save document '{document_id}' to {storage_path}: {e}")
            raise DataStorageError(f"Failed to write document file: {e}")
        except Exception as e:
             logger.error(f"An unexpected error occurred saving document '{document_id}': {e}")
             raise DataStorageError(f"Unexpected error saving document: {e}")

    def retrieve_document(self, document_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves a document's content and metadata from the file system.

        Args:
            document_id (str): Unique ID of the document to retrieve.

        Returns:
            Optional[Dict[str, Any]]: Dictionary with 'content' (str or bytes) and 
                                      'metadata' (dict), or None if not found.
        Raises:
            DataStorageError: If retrieval fails (other than not found).
        """
        storage_path = self._get_storage_path(document_id)
        if not storage_path.exists():
            logger.debug(f"Document '{document_id}' not found at {storage_path}")
            return None

        try:
            # Determine read mode based on assumed type (needs improvement)
            # A stored metadata file could specify 'binary' or 'text/encoding'
            is_binary = storage_path.suffix == '.bin' or storage_path.suffix == '.pdf' # Heuristic
            mode = 'rb' if is_binary else 'r'
            encoding = None if is_binary else 'utf-8'
            
            with open(storage_path, mode, encoding=encoding) as f:
                content = f.read()
                
            # Attempt to load metadata if it exists
            metadata = None
            meta_path = storage_path.with_suffix(storage_path.suffix + '.meta.json')
            if meta_path.exists():
                 with open(meta_path, 'r', encoding='utf-8') as mf:
                     metadata = json.load(mf)
                     
            logger.debug(f"Retrieved document '{document_id}' from {storage_path}")
            return {"content": content, "metadata": metadata}

        except IOError as e:
            logger.error(f"Failed to read document '{document_id}' from {storage_path}: {e}")
            raise DataStorageError(f"Failed to read document file: {e}")
        except json.JSONDecodeError as e:
             logger.error(f"Failed to parse metadata for '{document_id}' from {meta_path}: {e}")
             # Decide whether to return content without metadata or raise error
             return {"content": content, "metadata": None} # Example: return content anyway
             # raise DataStorageError(f"Failed to parse metadata file: {e}")
        except Exception as e:
             logger.error(f"An unexpected error occurred retrieving document '{document_id}': {e}")
             raise DataStorageError(f"Unexpected error retrieving document: {e}")

    def delete_document(self, document_id: str) -> bool:
        """Deletes a document and its metadata from the file system.

        Args:
            document_id (str): Unique ID of the document to delete.

        Returns:
            bool: True if deleted successfully or not found, False otherwise.
        """
        storage_path = self._get_storage_path(document_id)
        meta_path = storage_path.with_suffix(storage_path.suffix + '.meta.json')
        deleted = False
        try:
            if storage_path.exists():
                storage_path.unlink()
                logger.info(f"Deleted document '{document_id}' from {storage_path}")
                deleted = True
            else:
                 logger.debug(f"Document '{document_id}' not found at {storage_path}, cannot delete.")
                 # Consider returning True even if not found, as the state is 'deleted'
                 return True 
            
            if meta_path.exists():
                 meta_path.unlink()
                 logger.debug(f"Deleted metadata for '{document_id}' from {meta_path}")
                 
            return True
        except OSError as e:
            logger.error(f"Failed to delete document '{document_id}' or its metadata: {e}")
            return False
