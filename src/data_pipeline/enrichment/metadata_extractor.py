# src/data_pipeline/enrichment/metadata_extractor.py

import logging
import re
from typing import Dict, Any, Optional
from urllib.parse import urlparse
from datetime import datetime

logger = logging.getLogger(__name__)

class MetadataExtractor:
    """Extracts metadata like publication date and source from documents."""

    def __init__(self):
        # Common date patterns (add more as needed, be wary of ambiguity)
        # Example: YYYY-MM-DD, MM/DD/YYYY, Month DD, YYYY
        self.date_patterns = [
            re.compile(r'\b(\d{4}-\d{1,2}-\d{1,2})\b'), # YYYY-MM-DD
            re.compile(r'\b(\d{1,2}/\d{1,2}/\d{4})\b'), # MM/DD/YYYY or D/M/YYYY (ambiguous)
            re.compile(r'\b(Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\s+(\d{1,2}),?\s+(\d{4})\b', re.IGNORECASE), # Month DD, YYYY
            # Add patterns for specific source formats if known
        ]
        logger.info("MetadataExtractor initialized.")

    def _extract_date(self, text: str) -> Optional[str]:
        """Attempts to find the most likely publication date using regex."""
        found_date_str = None
        for pattern in self.date_patterns:
            match = pattern.search(text)
            if match:
                # Basic implementation takes the first match found.
                # More sophisticated logic could prioritize patterns or positions.
                date_str = match.group(0) # Get the full matched string
                # Attempt to parse for validation/standardization (optional but recommended)
                try:
                    # This part needs refinement based on matched pattern
                    # Example for YYYY-MM-DD
                    if pattern.pattern == r'\b(\d{4}-\d{1,2}-\d{1,2})\b':
                         dt = datetime.strptime(match.group(1), '%Y-%m-%d')
                         found_date_str = dt.strftime('%Y-%m-%d') # Standardize format
                    # Add parsing logic for other patterns...
                    # For now, just return the matched string if pattern matches
                    if not found_date_str: # If not parsed by specific logic
                         found_date_str = date_str 
                    
                    logger.debug(f"Found potential date: {found_date_str}")
                    return found_date_str 
                except ValueError:
                    logger.warning(f"Could not parse potential date string: {date_str}")
                    # Continue searching with other patterns
                    pass
        
        logger.debug("No date pattern matched.")
        return None

    def _extract_source_domain(self, url: Optional[str]) -> Optional[str]:
        """Extracts the domain name from the URL."""
        if not url:
            return None
        try:
            parsed_url = urlparse(url)
            # Use netloc which includes domain and potentially port
            domain = parsed_url.netloc
            # Simple cleaning (e.g., remove www.)
            if domain.startswith('www.'):
                domain = domain[4:]
            logger.debug(f"Extracted domain: {domain} from URL: {url}")
            return domain
        except Exception as e:
            logger.error(f"Error parsing URL {url}: {e}")
            return None

    def extract_metadata(self, document_data: Dict[str, Any], text_content: Optional[str] = None) -> Dict[str, Any]:
        """Extracts metadata and adds it to the document data dictionary.

        Args:
            document_data (Dict[str, Any]): Dictionary containing document info (e.g., 'url').
            text_content (Optional[str]): The text content of the document, used for date extraction.

        Returns:
            Dict[str, Any]: The input dictionary updated with 'publication_date' and 'source_domain' keys.
        """
        metadata = {}
        
        # Extract Source Domain
        metadata['source_domain'] = self._extract_source_domain(document_data.get('url'))

        # Extract Publication Date (requires text content)
        if text_content:
            metadata['publication_date'] = self._extract_date(text_content)
        else:
            metadata['publication_date'] = None
            logger.debug("No text content provided, skipping date extraction.")

        logger.info(f"Extracted metadata: {metadata}")
        # Update the original dictionary
        document_data.update(metadata)
        return document_data

# Example Usage:
# if __name__ == "__main__":
#     from src.utils.logging_config import setup_logging
#     setup_logging(log_level='DEBUG')
#
#     extractor = MetadataExtractor()
#
#     sample_doc = {
#         'url': 'https://www.example-gov.org/news/policy-update-march-15-2023',
#         'raw_content': '...' 
#     }
#     sample_text = """
#     Policy Update - March 15, 2023
#     Washington D.C. – Today, the agency announced new guidelines... 
#     Published on 2023-03-15. 
#     For release 03/15/2023.
#     """
#
#     updated_doc = extractor.extract_metadata(sample_doc, text_content=sample_text)
#
#     print("\n--- Original Document Data ---")
#     print(sample_doc) # Note: This will show the updated dict directly
#     print("\n--- Extracted Metadata ---")
#     print(f"Source Domain: {updated_doc.get('source_domain')}")
#     print(f"Publication Date: {updated_doc.get('publication_date')}") # Should be '2023-03-15' or similar