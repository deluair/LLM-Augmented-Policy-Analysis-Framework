import logging
from typing import Dict, Any, Optional
from io import BytesIO

from bs4 import BeautifulSoup
from pypdf import PdfReader
from docx import Document
import requests # Needed for fetching binary content

from src.utils.exceptions import DataProcessingError

logger = logging.getLogger(__name__)

class DocumentParser:
    """Parses raw document content into structured text based on content type."""

    def __init__(self):
        logger.info("DocumentParser initialized.")

    def _parse_html(self, html_content: str) -> str:
        """Extracts text from HTML content."""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            # Attempt to find main content, fallback to body
            main_content = soup.find('main') or soup.find('article') or soup.find('div', {'role': 'main'}) or soup.body
            if main_content:
                return main_content.get_text(separator='\n', strip=True)
            else:
                logger.warning("Could not find main content area in HTML, extracting from body.")
                return soup.get_text(separator='\n', strip=True)
        except Exception as e:
            logger.error(f"Error parsing HTML: {e}")
            raise DataProcessingError(stage="HTML Parsing", message=str(e))

    def _parse_pdf(self, pdf_content: bytes) -> str:
        """Extracts text from PDF content."""
        try:
            reader = PdfReader(BytesIO(pdf_content))
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text.strip()
        except Exception as e:
            logger.error(f"Error parsing PDF: {e}")
            # pypdf can raise various errors, including PasswordError
            raise DataProcessingError(stage="PDF Parsing", message=str(e))

    def _parse_docx(self, docx_content: bytes) -> str:
        """Extracts text from DOCX content."""
        try:
            document = Document(BytesIO(docx_content))
            text = "\n".join([para.text for para in document.paragraphs])
            return text.strip()
        except Exception as e:
            logger.error(f"Error parsing DOCX: {e}")
            raise DataProcessingError(stage="DOCX Parsing", message=str(e))

    def _fetch_binary_content(self, url: str) -> Optional[bytes]:
        """Fetches binary content (like PDF, DOCX) from a URL."""
        try:
            response = requests.get(url, timeout=30) # Longer timeout for potential large files
            response.raise_for_status()
            logger.debug(f"Successfully fetched binary content from: {url}")
            return response.content
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch binary content from {url}: {e}")
            return None

    def parse(self, document_data: Dict[str, Any]) -> Optional[str]:
        """Parses the document based on its URL or content type.

        Args:
            document_data (Dict[str, Any]): A dictionary possibly containing:
                'url': The URL of the document.
                'raw_content': The raw content (e.g., HTML string).
                'content_type': (Optional) Hint about the content type.

        Returns:
            Optional[str]: The extracted text content, or None if parsing fails.
        """
        url = document_data.get('url')
        raw_content = document_data.get('raw_content')
        content_type = document_data.get('content_type', '').lower()

        if not url and not raw_content:
            logger.error("Parsing requires either 'url' or 'raw_content'.")
            return None
        
        logger.info(f"Parsing document: {url or 'from raw content'}")

        # --- Strategy 1: Use provided raw_content if available and type hints match --- 
        if raw_content and 'html' in content_type:
             try:
                logger.debug(f"Parsing HTML content provided directly for {url}")
                return self._parse_html(str(raw_content)) # Ensure it's string
             except DataProcessingError as e:
                 logger.error(f"Failed to parse provided HTML content: {e}")
                 # Fall through to fetch/guess if needed

        # --- Strategy 2: Determine type from URL and fetch if necessary --- 
        if url:
            # Determine content type from URL extension or HEAD request (more robust)
            # Simple check for now:
            if url.endswith('.pdf') or 'application/pdf' in content_type:
                logger.debug(f"Identified as PDF: {url}. Fetching binary content.")
                binary_content = self._fetch_binary_content(url)
                if binary_content:
                    try:
                        return self._parse_pdf(binary_content)
                    except DataProcessingError as e:
                         logger.error(f"Failed to parse PDF from {url}: {e}") 
                         return None # Failed to parse fetched PDF
                else:
                     return None # Failed to fetch

            elif url.endswith('.docx') or 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' in content_type:
                logger.debug(f"Identified as DOCX: {url}. Fetching binary content.")
                binary_content = self._fetch_binary_content(url)
                if binary_content:
                    try:
                        return self._parse_docx(binary_content)
                    except DataProcessingError as e:
                         logger.error(f"Failed to parse DOCX from {url}: {e}") 
                         return None
                else:
                    return None # Failed to fetch
            
            # Assume HTML if not PDF/DOCX and no raw content was successfully parsed before
            elif not raw_content or 'html' in content_type:
                logger.debug(f"Assuming HTML or fetching HTML content for: {url}")
                html_content = raw_content if raw_content else self._fetch_page_content(url)
                if html_content:
                    try:
                        return self._parse_html(html_content)
                    except DataProcessingError as e:
                        logger.error(f"Failed to parse HTML from {url}: {e}")
                        return None
                else:
                    # Handle case where fetching HTML page failed
                    if not raw_content: # Only log if we attempted fetching
                        logger.warning(f"Failed to fetch page content for HTML parsing: {url}")
                    return None

        # Fallback if only raw_content was provided without a clear type hint
        if raw_content and not url: 
             logger.warning("Parsing raw content without URL or clear type hint. Assuming HTML.")
             try:
                 return self._parse_html(str(raw_content))
             except DataProcessingError as e:
                 logger.error(f"Failed to parse raw content assumed as HTML: {e}")
                 return None

        logger.warning(f"Could not determine how to parse document: {url or 'raw content'}")
        return None

    # Helper to fetch page content, similar to collector but maybe simpler
    def _fetch_page_content(self, url: str) -> Optional[str]:
        try:
            response = requests.get(url, headers={'User-Agent': 'PolicyAnalysisParser/1.0'}, timeout=15)
            response.raise_for_status()
            # Basic check for HTML content type
            if 'text/html' in response.headers.get('Content-Type', ''):
                return response.text
            else:
                logger.warning(f"Content type for {url} is not text/html: {response.headers.get('Content-Type')}")
                return None 
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch page content {url} for parsing: {e}")
            return None

# Example Usage:
# if __name__ == "__main__":
#     from src.utils.logging_config import setup_logging
#     setup_logging()
#
#     parser = DocumentParser()
#
#     # Example 1: Parse from URL (assuming it's HTML)
#     html_doc = {'url': 'https://www.example.com'}
#     text = parser.parse(html_doc)
#     if text:
#         print("--- HTML Example ---")
#         print(text[:500] + "...")
#
#     # Example 2: Parse from URL (PDF - requires a real PDF link)
#     # pdf_doc = {'url': 'https://www.federalreserve.gov/releases/z1/current/z1.pdf'}
#     # text = parser.parse(pdf_doc)
#     # if text:
#     #     print("\n--- PDF Example ---")
#     #     print(text[:500] + "...")
#
#     # Example 3: Parse from raw HTML content
#     raw_html = {'raw_content': '<html><body><h1>Title</h1><p>Paragraph 1.</p><main><p>Main content.</p></main></body></html>', 'content_type': 'text/html'}
#     text = parser.parse(raw_html)
#     if text:
#         print("\n--- Raw HTML Example ---")
#         print(text)
