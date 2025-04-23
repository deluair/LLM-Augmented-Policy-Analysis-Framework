import requests
from bs4 import BeautifulSoup
import logging
from typing import List, Dict, Any, Optional
from urllib.parse import urljoin

from src.utils.exceptions import DataCollectionError

logger = logging.getLogger(__name__)

class PolicyCollector:
    """Collects policy documents from specified web sources."""

    def __init__(self, base_url: str, headers: Optional[Dict[str, str]] = None):
        """Initializes the collector.
        
        Args:
            base_url (str): The starting URL for scraping policy documents.
            headers (Optional[Dict[str, str]]): Optional HTTP headers for requests.
        """
        self.base_url = base_url
        self.headers = headers or {'User-Agent': 'PolicyAnalysisBot/1.0'}
        logger.info(f"PolicyCollector initialized for base URL: {self.base_url}")

    def _fetch_page(self, url: str) -> Optional[str]:
        """Fetches the content of a given URL.

        Args:
            url (str): The URL to fetch.
        
        Returns:
            Optional[str]: The HTML content of the page, or None if fetch fails.
        """
        try:
            response = requests.get(url, headers=self.headers, timeout=15)
            response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
            logger.debug(f"Successfully fetched page: {url}")
            return response.text
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch page {url}: {e}")
            # Optionally raise a custom exception here or let it return None
            # raise DataCollectionError(source=url, message=str(e))
            return None

    def find_policy_links(self, page_url: str, link_selector: str) -> List[str]:
        """Finds links to policy documents on a given page.

        Args:
            page_url (str): The URL of the page to search for links.
            link_selector (str): CSS selector to identify the links.

        Returns:
            List[str]: A list of absolute URLs to potential policy documents.
        """
        html_content = self._fetch_page(page_url)
        if not html_content:
            return []

        soup = BeautifulSoup(html_content, 'html.parser')
        links = []
        try:
            link_elements = soup.select(link_selector)
            for link in link_elements:
                href = link.get('href')
                if href:
                    # Construct absolute URL
                    absolute_url = urljoin(page_url, href)
                    links.append(absolute_url)
            logger.info(f"Found {len(links)} potential policy links on {page_url} using selector '{link_selector}'")
        except Exception as e:
            logger.error(f"Error parsing links on {page_url} with selector '{link_selector}': {e}")
            raise DataCollectionError(source=page_url, message=f"Error parsing links: {e}")
            
        return links

    def fetch_document_content(self, doc_url: str) -> Optional[Dict[str, Any]]:
        """Fetches the content of a specific policy document.
        
        This is a basic implementation assuming the document is directly downloadable
        or its content is within the page.
        More specific logic (e.g., handling PDFs, Word docs) would go in the parsers.

        Args:
            doc_url (str): The URL of the policy document.

        Returns:
            Optional[Dict[str, Any]]: A dictionary containing document URL and content,
                                     or None if fetching fails.
        """
        logger.debug(f"Attempting to fetch document content from: {doc_url}")
        # This basic version assumes the content is HTML
        # More complex logic needed for binary files (PDF, DOCX) which should be
        # handled by downloading the file and passing it to a specific parser.
        content = self._fetch_page(doc_url)
        if content:
            # Basic extraction - might need refinement based on actual site structure
            soup = BeautifulSoup(content, 'html.parser')
            # Try to find a main content area (common practice)
            main_content = soup.find('main') or soup.find('article') or soup.find('div', {'role': 'main'}) or soup.body
            text_content = main_content.get_text(separator='\n', strip=True) if main_content else ""
            
            logger.info(f"Successfully fetched and extracted text content from: {doc_url}")
            return {
                "url": doc_url,
                "content_type": "text/html", # Placeholder
                "raw_content": text_content # Or 'content' if directly usable
            }
        else:
            logger.warning(f"Failed to fetch document content from: {doc_url}")
            return None

    def collect(self, index_page_selector: str) -> List[Dict[str, Any]]:
        """Runs the collection process.
        
        Fetches the base URL, finds policy links, and fetches their content.

        Args:
            index_page_selector (str): The CSS selector to find links on the index page.

        Returns:
            List[Dict[str, Any]]: A list of dictionaries, each representing a fetched document.
        """
        logger.info(f"Starting policy collection from base URL: {self.base_url}")
        policy_links = self.find_policy_links(self.base_url, index_page_selector)
        
        collected_documents = []
        for link in policy_links:
            doc_data = self.fetch_document_content(link)
            if doc_data:
                collected_documents.append(doc_data)
            else:
                # Optionally retry or log failure more prominently
                pass 
                
        logger.info(f"Collection finished. Fetched {len(collected_documents)} documents.")
        return collected_documents

# Example Usage (Illustrative - requires actual URL and selector):
# if __name__ == "__main__":
#     # Configure logging (assuming setup_logging is callable)
#     from src.utils.logging_config import setup_logging
#     setup_logging()
#
#     # Example: Federal Reserve Press Releases (selector needs inspection)
#     fed_url = "https://www.federalreserve.gov/newsevents/pressreleases.htm"
#     # This selector is hypothetical and needs to be determined by inspecting the page
#     # It might target <a> tags within a specific list or div
#     link_selector = "div.panel-default ul.list-unstyled li a" 
#
#     collector = PolicyCollector(base_url=fed_url)
#     try:
#         documents = collector.collect(index_page_selector=link_selector)
#         print(f"Collected {len(documents)} documents.")
#         # Further processing would happen here (e.g., passing to parsers)
#         # for doc in documents:
#         #     print(f" - {doc['url']}")
#     except DataCollectionError as e:
#         logger.critical(f"Data collection failed: {e}")
