"""
Cleans raw text content by removing unwanted elements like HTML tags, extra whitespace, etc.
"""

import logging
import re
# from bs4 import BeautifulSoup # Potential library for HTML cleaning

logger = logging.getLogger(__name__)

class TextCleaner:
    """Provides methods to clean text data."""

    def __init__(self, remove_html: bool = True, normalize_whitespace: bool = True):
        """Initializes the text cleaner.

        Args:
            remove_html (bool): Whether to attempt HTML tag removal.
            normalize_whitespace (bool): Whether to normalize whitespace (remove extra spaces/newlines).
        """
        self.remove_html = remove_html
        self.normalize_whitespace = normalize_whitespace
        logger.info(f"TextCleaner initialized (Remove HTML: {self.remove_html}, Normalize Whitespace: {self.normalize_whitespace})")

    def clean_text(self, text: str) -> str:
        """Applies the configured cleaning steps to the input text.

        Args:
            text (str): The raw text to clean.

        Returns:
            str: The cleaned text.
        """
        if not isinstance(text, str):
            logger.warning(f"Input to clean_text is not a string (type: {type(text)}). Returning as is.")
            return text # Or raise error?

        cleaned_text = text
        try:
            # 1. Remove HTML (if enabled)
            if self.remove_html:
                # Basic regex approach (less robust than libraries like BeautifulSoup)
                cleaned_text = re.sub(r'<[^>]+>', ' ', cleaned_text)
                # Example using BeautifulSoup (requires installation):
                # soup = BeautifulSoup(cleaned_text, 'html.parser')
                # cleaned_text = soup.get_text(separator=' ')
                logger.debug("Applied HTML tag removal (basic regex).")

            # 2. Normalize Whitespace (if enabled)
            if self.normalize_whitespace:
                cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()
                logger.debug("Applied whitespace normalization.")

            # Add other cleaning steps as needed (e.g., remove specific patterns, lowercasing)

            return cleaned_text

        except Exception as e:
            logger.error(f"Error during text cleaning: {e}", exc_info=True)
            # Return original text or raise? Returning original for now.
            return text

# Example Usage
# if __name__ == "__main__":
#     cleaner = TextCleaner()
#     raw = "  <p>This is <b>bold</b> text. </p> \n Extra   spaces.  "
#     cleaned = cleaner.clean_text(raw)
#     print(f"Raw: '{raw}'")
#     print(f"Cleaned: '{cleaned}'") # Expected: 'This is bold text. Extra spaces.'
