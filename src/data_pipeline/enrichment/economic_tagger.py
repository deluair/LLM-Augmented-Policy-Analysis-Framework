import logging
import re
from typing import List, Dict, Set
# import spacy # Import if using spaCy NER

logger = logging.getLogger(__name__)

class EconomicTagger:
    """Tags documents with relevant economic concepts based on keywords or NER."""

    def __init__(self, keyword_config: Dict[str, List[str]], use_spacy: bool = False, spacy_model: str = 'en_core_web_sm'):
        """Initializes the tagger.
        
        Args:
            keyword_config (Dict[str, List[str]]): Dictionary where keys are economic tags 
                                                  (e.g., 'inflation', 'unemployment') and 
                                                  values are lists of related keywords/phrases.
            use_spacy (bool): Whether to use spaCy for Named Entity Recognition (NER).
                              (Currently placeholder - implementation uses keywords).
            spacy_model (str): Name of the spaCy model to use if use_spacy is True.
        """
        self.keyword_config = {tag: [kw.lower() for kw in kws] for tag, kws in keyword_config.items()}
        self.use_spacy = use_spacy
        self.nlp = None

        if self.use_spacy:
            logger.warning("spaCy NER is selected but not fully implemented in this basic version. Falling back to keywords.")
            # try:
            #     self.nlp = spacy.load(spacy_model)
            #     logger.info(f"Loaded spaCy model: {spacy_model}")
            # except OSError:
            #     logger.error(f"spaCy model '{spacy_model}' not found. "
            #                  f"Please download it: python -m spacy download {spacy_model}")
            #     self.nlp = None # Fallback
            #     self.use_spacy = False
        
        logger.info(f"EconomicTagger initialized. Using keywords for {len(self.keyword_config)} tags. SpaCy enabled: {self.use_spacy}")

    def tag_document(self, text: str) -> Set[str]:
        """Applies tagging logic to the document text.

        Args:
            text (str): The cleaned text content of the document.

        Returns:
            Set[str]: A set of identified economic tags.
        """
        if not isinstance(text, str):
             logger.warning(f"Input to tag_document is not a string (type: {type(text)}). Returning empty set.")
             return set()

        found_tags = set()
        text_lower = text.lower() # Perform matching in lowercase for keywords

        # Keyword-based tagging (primary method in this basic version)
        for tag, keywords in self.keyword_config.items():
            for keyword in keywords:
                # Use word boundaries to avoid partial matches (e.g., 'rate' in 'operate')
                pattern = r'\b' + re.escape(keyword) + r'\b'
                if re.search(pattern, text_lower):
                    found_tags.add(tag)
                    break # Move to the next tag once one keyword is found for it

        # Placeholder for spaCy NER tagging
        # if self.use_spacy and self.nlp:
        #     doc = self.nlp(text)
        #     for ent in doc.ents:
        #         # Example: Map specific entity labels (ORG, GPE, MONEY) to tags
        #         # This requires defining a mapping based on your needs
        #         if ent.label_ == 'MONEY':
        #              found_tags.add('monetary_value')
        #         elif ent.label_ == 'ORG' and 'bank' in ent.text.lower():
        #              found_tags.add('banking')
        #         # ... add more sophisticated NER-based tagging rules

        logger.debug(f"Found tags: {found_tags}")
        return found_tags

# Example Usage:
# if __name__ == "__main__":
#     from src.utils.logging_config import setup_logging
#     setup_logging(log_level='DEBUG')
#
#     # Example keyword configuration
#     keywords = {
#         'inflation': ['inflation', 'consumer price index', 'cpi', 'rising prices'],
#         'unemployment': ['unemployment', 'jobless claims', 'job growth', 'labor market'],
#         'interest_rates': ['interest rate', 'federal funds rate', 'policy rate', 'discount rate'],
#         'gdp': ['gross domestic product', 'gdp', 'economic growth', 'output gap']
#     }
#
#     tagger = EconomicTagger(keyword_config=keywords)
#
#     sample_text = """
#     The latest report shows a slight decrease in unemployment, signaling a robust labor market. 
#     However, concerns about inflation persist as the consumer price index continues to climb. 
#     The central bank might consider raising the interest rate to combat rising prices. Economic growth remains steady.
#     """
#
#     tags = tagger.tag_document(sample_text)
#     print(f"--- Sample Text --- \n{sample_text}")
#     print(f"\n--- Identified Tags ---\n{tags}") # Should identify unemployment, inflation, interest_rates
