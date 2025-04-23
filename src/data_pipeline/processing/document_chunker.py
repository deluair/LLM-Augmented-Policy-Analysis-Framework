"""
Splits large documents into smaller chunks suitable for processing by LLMs or embedding models.
"""

import logging
from typing import List, Optional
# from langchain.text_splitter import RecursiveCharacterTextSplitter # Example using LangChain

logger = logging.getLogger(__name__)

class DocumentChunker:
    """Splits text into chunks based on specified strategy and size."""

    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 100, method: str = 'simple'):
        """Initializes the document chunker.

        Args:
            chunk_size (int): The target size of each chunk (e.g., in characters or tokens).
            chunk_overlap (int): The number of characters/tokens to overlap between chunks.
            method (str): The chunking method ('simple', 'recursive_char', 'sentence', etc.).
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.method = method
        self.splitter = None # For library-based splitters

        if self.chunk_overlap >= self.chunk_size:
             logger.warning(f"Chunk overlap ({self.chunk_overlap}) is >= chunk size ({self.chunk_size}). Setting overlap to 0.")
             self.chunk_overlap = 0

        try:
             if self.method == 'recursive_char':
                 # self.splitter = RecursiveCharacterTextSplitter(
                 #     chunk_size=self.chunk_size,
                 #     chunk_overlap=self.chunk_overlap,
                 #     length_function=len # Use character length
                 # )
                 logger.info(f"Initialized RecursiveCharacterTextSplitter (placeholder) with size {self.chunk_size}, overlap {self.chunk_overlap}")
                 pass # Placeholder for actual initialization
             elif self.method == 'simple':
                 logger.info(f"Using simple character chunking with size {self.chunk_size}, overlap {self.chunk_overlap}")
             # Add other methods like sentence splitting (e.g., using NLTK)
             else:
                 logger.error(f"Unsupported chunking method: {self.method}")
                 raise ValueError(f"Unsupported chunking method: {self.method}")
        except Exception as e:
             logger.error(f"Failed to initialize chunker (method: {self.method}): {e}")
             raise

    def split_text(self, text: str) -> List[str]:
        """Splits the input text into chunks.

        Args:
            text (str): The text to split.

        Returns:
            List[str]: A list of text chunks.
        """
        if not isinstance(text, str):
             logger.warning("Input text is not a string. Returning empty list.")
             return []

        if len(text) <= self.chunk_size:
             logger.debug("Text length is <= chunk size. Returning as single chunk.")
             return [text]

        chunks = []
        try:
            if self.method == 'recursive_char' and self.splitter:
                 # chunks = self.splitter.split_text(text)
                 logger.warning("RecursiveCharacterTextSplitter not fully implemented. Falling back to simple chunking.")
                 # Fallback to simple if placeholder
                 chunks = self._simple_chunking(text)
                 
            elif self.method == 'simple':
                 chunks = self._simple_chunking(text)
            # Add other methods
            else:
                 logger.error(f"Chunker method '{self.method}' not supported or not initialized.")
                 return [] # Or raise error

            logger.info(f"Split text into {len(chunks)} chunks (Method: {self.method}, Size: {self.chunk_size}, Overlap: {self.chunk_overlap})")
            return chunks
            
        except Exception as e:
             logger.error(f"Error during text splitting: {e}", exc_info=True)
             return [] # Return empty list on error

    def _simple_chunking(self, text: str) -> List[str]:
        """Performs basic character-based chunking with overlap."""
        chunks = []
        start_index = 0
        text_len = len(text)

        while start_index < text_len:
            end_index = min(start_index + self.chunk_size, text_len)
            chunks.append(text[start_index:end_index])
            
            # Move start index for the next chunk
            next_start = start_index + self.chunk_size - self.chunk_overlap
            
            # If overlap pushes us back or keeps us at the same spot, just move by chunk size
            if next_start <= start_index:
                 next_start = start_index + self.chunk_size 
            
            start_index = next_start
            
            # Safety break if something goes wrong (shouldn't be needed with logic above)
            if start_index >= text_len and len(chunks[-1]) < self.chunk_size and end_index == text_len:
                 break 

        return chunks

# Example Usage
# if __name__ == "__main__":
#     chunker_simple = DocumentChunker(chunk_size=20, chunk_overlap=5, method='simple')
#     sample = "This is a sample text that needs to be split into smaller chunks for processing."
#     chunks = chunker_simple.split_text(sample)
#     print(f"--- Simple Chunking (Size=20, Overlap=5) ---")
#     for i, chunk in enumerate(chunks):
#         print(f"Chunk {i}: '{chunk}' (Length: {len(chunk)})")
# 
#     # Example with LangChain (requires installation)
#     # chunker_lc = DocumentChunker(chunk_size=20, chunk_overlap=5, method='recursive_char')
#     # chunks_lc = chunker_lc.split_text(sample) 
#     # print(f"\n--- LangChain Recursive Char Chunking (Placeholder Fallback) ---")
#     # for i, chunk in enumerate(chunks_lc):
#     #     print(f"Chunk {i}: '{chunk}' (Length: {len(chunk)})")
