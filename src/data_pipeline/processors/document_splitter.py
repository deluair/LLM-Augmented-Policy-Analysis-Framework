"""
Defines strategies for splitting documents into smaller chunks.
"""

import logging
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

from src.models.document import Document # Assuming Document model exists

logger = logging.getLogger(__name__)

class BaseDocumentSplitter(ABC):
    """Abstract base class for document splitting strategies."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initializes the splitter.

        Args:
            config (Optional[Dict[str, Any]]): Configuration parameters specific to the splitter.
                                                 Defaults to None.
        """
        self.config = config if config else {}
        logger.info(f"{self.__class__.__name__} initialized with config: {self.config}")

    @abstractmethod
    def split_document(self, document: Document) -> List[Document]:
        """
        Splits a single document into multiple smaller documents (chunks).

        Args:
            document (Document): The input document to split.

        Returns:
            List[Document]: A list of new Document objects, each representing a chunk.
                           Metadata should ideally be preserved or updated.
        """
        pass

    def split_documents(self, documents: List[Document]) -> List[Document]:
        """
        Splits a list of documents into chunks.

        Args:
            documents (List[Document]): The list of documents to split.

        Returns:
            List[Document]: A list containing chunks from all input documents.
        """
        all_chunks = []
        logger.info(f"Splitting {len(documents)} documents using {self.__class__.__name__}...")
        for i, doc in enumerate(documents):
            try:
                chunks = self.split_document(doc)
                all_chunks.extend(chunks)
                if (i + 1) % 10 == 0:
                     logger.debug(f"Processed {i+1}/{len(documents)} documents for splitting.")
            except Exception as e:
                logger.error(f"Failed to split document {doc.id or f'(index {i})'}: {e}", exc_info=True)
        logger.info(f"Finished splitting. Total chunks generated: {len(all_chunks)}")
        return all_chunks

# --- Concrete Implementations --- 

class CharacterSplitter(BaseDocumentSplitter):
    """Splits documents based on a fixed number of characters with optional overlap."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initializes the character splitter.
        Requires 'chunk_size' in config. Optional 'chunk_overlap'.
        """
        super().__init__(config)
        self.chunk_size = self.config.get('chunk_size', 1000)
        self.chunk_overlap = self.config.get('chunk_overlap', 100)

        if not isinstance(self.chunk_size, int) or self.chunk_size <= 0:
            raise ValueError("'chunk_size' must be a positive integer.")
        if not isinstance(self.chunk_overlap, int) or self.chunk_overlap < 0:
            raise ValueError("'chunk_overlap' must be a non-negative integer.")
        if self.chunk_overlap >= self.chunk_size:
             raise ValueError("'chunk_overlap' must be smaller than 'chunk_size'.")

    def split_document(self, document: Document) -> List[Document]:
        """Splits the document content by character count."""
        chunks = []
        content = document.content
        if not content:
            logger.warning(f"Document {document.id} has no content to split.")
            return []

        start_index = 0
        chunk_seq = 0
        while start_index < len(content):
            end_index = min(start_index + self.chunk_size, len(content))
            chunk_content = content[start_index:end_index]
            
            # Create new metadata for the chunk
            chunk_metadata = document.metadata.copy()
            chunk_metadata['original_doc_id'] = document.id
            chunk_metadata['chunk_sequence'] = chunk_seq
            chunk_metadata['chunk_start_index'] = start_index
            chunk_metadata['chunk_end_index'] = end_index

            # Create a new Document object for the chunk
            # Note: Generating new UUIDs for chunks
            chunk_doc = Document(
                content=chunk_content,
                metadata=chunk_metadata,
                source=f"{document.source or 'unknown'}_chunk_{chunk_seq}",
                tags=document.tags.copy() # Copy tags
                # Embeddings usually calculated *after* chunking
            )
            chunks.append(chunk_doc)
            
            chunk_seq += 1
            # Move start index for the next chunk, considering overlap
            start_index += self.chunk_size - self.chunk_overlap
            
            # Handle edge case: if overlap pushes start_index past the end
            if start_index >= len(content) and len(chunks) > 0 and end_index < len(content):
                 # If the last chunk didn't reach the very end due to overlap calculation, break
                 # This can happen if len(content) is slightly more than start_index + chunk_overlap
                 break
            # Handle case where overlap makes it skip content (shouldn't happen with check)
            if start_index >= end_index and end_index < len(content):
                 logger.warning("Potential issue with overlap calculation, advancing index.")
                 start_index = end_index # Prevent infinite loop

        logger.debug(f"Split document {document.id} into {len(chunks)} chunks.")
        return chunks

# Add other splitter types as needed (e.g., RecursiveCharacterTextSplitter, TokenSplitter)

# Example Usage:
# if __name__ == "__main__":
#     from src.utils.logging_config import setup_logging
#     setup_logging()
#     
#     splitter_config = {'chunk_size': 100, 'chunk_overlap': 10}
#     splitter = CharacterSplitter(config=splitter_config)
# 
#     doc1 = Document(id="doc1", content="This is the first document. It is relatively short.", source="file1.txt")
#     doc2 = Document(id="doc2", content="This is a much longer document. It contains many sentences and words. We need to split it into smaller chunks to process effectively. Character splitting is one way to do this, though token splitting or semantic chunking might be better depending on the downstream task.", metadata={'author': 'Test'}, tags=['test', 'nlp'])
# 
#     all_docs = [doc1, doc2]
#     chunked_docs = splitter.split_documents(all_docs)
# 
#     print(f"Total chunks created: {len(chunked_docs)}\n")
#     for i, chunk in enumerate(chunked_docs):
#         print(f"--- Chunk {i+1} ---")
#         print(f"ID: {chunk.id}")
#         print(f"Source: {chunk.source}")
#         print(f"Metadata: {chunk.metadata}")
#         print(f"Content: '{chunk.content}'")
#         print()
