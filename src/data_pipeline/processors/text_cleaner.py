import re
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class TextCleaner:
    """Cleans raw extracted text data."""

    def __init__(self, remove_patterns: Optional[list[str]] = None, to_lowercase: bool = False):
        """Initializes the text cleaner.

        Args:
            remove_patterns (Optional[list[str]]): List of regex patterns to remove.
            to_lowercase (bool): Whether to convert text to lowercase.
        """
        self.remove_patterns = [re.compile(p) for p in remove_patterns] if remove_patterns else []
        self.to_lowercase = to_lowercase
        logger.info(f"TextCleaner initialized. Lowercase: {self.to_lowercase}, Remove Patterns: {len(self.remove_patterns)}")

    def clean(self, text: str) -> str:
        """Applies cleaning steps to the input text.

        Args:
            text (str): The text to clean.

        Returns:
            str: The cleaned text.
        """
        if not isinstance(text, str):
            logger.warning(f"Input to TextCleaner is not a string (type: {type(text)}). Returning as is.")
            return text # Or raise an error, depending on desired strictness

        cleaned_text = text

        # Apply custom removal patterns first
        for pattern in self.remove_patterns:
            cleaned_text = pattern.sub('', cleaned_text)

        # Normalize whitespace: replace multiple spaces/newlines with a single space/newline
        # Replace multiple spaces with a single space
        cleaned_text = re.sub(r' +', ' ', cleaned_text)
        # Replace multiple newlines with a single newline (or double for paragraph breaks)
        # This keeps paragraph structure better than collapsing all whitespace
        cleaned_text = re.sub(r'\n\s*\n', '\n\n', cleaned_text) 
        # Remove leading/trailing whitespace from each line
        cleaned_text = "\n".join([line.strip() for line in cleaned_text.split('\n')])
        # Finally, strip leading/trailing whitespace from the whole text
        cleaned_text = cleaned_text.strip()

        # Convert to lowercase if specified
        if self.to_lowercase:
            cleaned_text = cleaned_text.lower()

        # Optional: Add other common cleaning steps like removing specific control characters
        # cleaned_text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', cleaned_text)

        logger.debug(f"Cleaned text length: {len(cleaned_text)} (original: {len(text)})")
        return cleaned_text

# Example Usage:
# if __name__ == "__main__":
#     from src.utils.logging_config import setup_logging
#     setup_logging(log_level='DEBUG') # Set to DEBUG to see cleaner logs
#
#     cleaner = TextCleaner(to_lowercase=True, remove_patterns=[r'Advertisement'])
#     
#     dirty_text = "  \n\n   This is an example   text with    extra spaces\nand\n\n\nmultiple newlines. Advertisement should be removed.   \n  "
#     cleaned = cleaner.clean(dirty_text)
#     
#     print("--- Original Text ---")
#     print(repr(dirty_text))
#     print("\n--- Cleaned Text ---")
#     print(repr(cleaned))
