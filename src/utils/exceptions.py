# src/utils/exceptions.py

"""Custom exception classes for the application."""

class PolicyAnalysisError(Exception):
    """Base exception class for the policy analysis framework."""
    pass

class DataCollectionError(PolicyAnalysisError):
    """Exception raised during data collection.
    
    Attributes:
        source (str): The source where the error occurred.
        message (str): Explanation of the error.
    """
    def __init__(self, source: str, message: str):
        self.source = source
        self.message = f"Error collecting data from {source}: {message}"
        super().__init__(self.message)

class DataProcessingError(PolicyAnalysisError):
    """Exception raised during data processing.
    
    Attributes:
        stage (str): The processing stage where the error occurred.
        message (str): Explanation of the error.
    """
    def __init__(self, stage: str, message: str):
        self.stage = stage
        self.message = f"Error during processing stage '{stage}': {message}"
        super().__init__(self.message)

class LLMInteractionError(PolicyAnalysisError):
    """Exception raised during interaction with LLMs.
    
    Attributes:
        model_name (str): The name of the LLM involved.
        message (str): Explanation of the error.
    """
    def __init__(self, model_name: str, message: str):
        self.model_name = model_name
        self.message = f"Error interacting with LLM '{model_name}': {message}"
        super().__init__(self.message)

class RetrievalError(PolicyAnalysisError):
    """Exception raised during data retrieval (e.g., from vector store)."""
    pass

class AnalysisError(PolicyAnalysisError):
    """Exception raised during the analysis phase."""
    pass

class ConfigurationError(PolicyAnalysisError):
    """Exception raised for configuration issues."""
    pass

# Example Usage:
# from src.utils.exceptions import DataCollectionError
# raise DataCollectionError(source="some_website", message="HTTP 404 Not Found")
