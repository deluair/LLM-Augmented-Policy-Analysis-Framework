"""
Defines Pydantic models for application configuration validation.

Ensures that configuration files or environment variables conform to expected structures.
"""

from typing import Dict, Any, Optional, List, Literal
from pydantic import BaseModel, Field, HttpUrl, validator, SecretStr

# --- Database Configuration --- 

class DatabaseConfig(BaseModel):
    """Configuration for database connection."""
    db_type: Literal['sqlite', 'postgresql', 'mysql'] = Field(..., description="Type of the database.")
    db_path: Optional[str] = Field(None, description="Path to the database file (for SQLite).")
    host: Optional[str] = Field(None, description="Database host address.")
    port: Optional[int] = Field(None, description="Database port.")
    username: Optional[str] = Field(None, description="Database username.")
    password: Optional[SecretStr] = Field(None, description="Database password.")
    db_name: Optional[str] = Field(None, description="Database name.")

    @validator('db_path', always=True)
    def check_db_path_for_sqlite(cls, v, values):
        if values.get('db_type') == 'sqlite' and not v:
            raise ValueError("'db_path' must be provided for SQLite database type")
        return v

    @validator('host', 'port', 'username', 'password', 'db_name', always=True)
    def check_fields_for_networked_db(cls, v, field, values):
        if values.get('db_type') in ['postgresql', 'mysql'] and v is None:
            # Allow password to be optional sometimes, but others are usually required
            if field.name != 'password': 
                 raise ValueError(f"'{field.name}' must be provided for {values.get('db_type')} database type")
        return v

# --- LLM Provider Configuration --- 

class LLMConfig(BaseModel):
    """Configuration for a specific LLM provider and model."""
    provider: Literal['openai', 'huggingface', 'anthropic', 'local'] = Field(..., description="LLM provider name.")
    model_name: str = Field(..., description="Specific model identifier (e.g., 'gpt-4', 'claude-3-opus-20240229', 'mistralai/Mistral-7B-Instruct-v0.1').")
    api_key: Optional[SecretStr] = Field(None, description="API key for the provider (if required).")
    api_base: Optional[HttpUrl] = Field(None, description="Base URL for the API endpoint (e.g., for local models or proxies).")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Additional parameters for the LLM (e.g., temperature, max_tokens).")

# --- Analysis Component Configuration --- 

class AnalyzerConfig(BaseModel):
    """Generic configuration for an analysis component."""
    analyzer_name: str = Field(..., description="Identifier for the analyzer.")
    enabled: bool = Field(True, description="Whether this analyzer is enabled.")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Specific parameters for this analyzer.")
    model_config: Optional[LLMConfig] = Field(None, description="LLM configuration if the analyzer uses one.")

# --- Pipeline Configuration --- 

class PipelineStepConfig(BaseModel):
    """Configuration for a single step in a processing pipeline."""
    step_name: str = Field(..., description="Name of the pipeline step.")
    component_type: Literal['data_loader', 'preprocessor', 'analyzer', 'synthesizer', 'exporter'] = Field(..., description="Type of component for this step.")
    config: Dict[str, Any] = Field(default_factory=dict, description="Configuration specific to the component used in this step.") # Could use specific models like AnalyzerConfig if needed

class PipelineConfig(BaseModel):
    """Configuration for a full data processing or analysis pipeline."""
    pipeline_name: str = Field(..., description="Name of the pipeline.")
    description: Optional[str] = Field(None, description="Description of the pipeline's purpose.")
    steps: List[PipelineStepConfig] = Field(..., description="Sequence of steps in the pipeline.")

# --- Main Application Configuration --- 

class AppConfig(BaseModel):
    """Root configuration model for the entire application."""
    app_name: str = Field("LLM Policy Analysis Framework", description="Name of the application.")
    log_level: str = Field("INFO", description="Logging level.")
    database: Optional[DatabaseConfig] = Field(None, description="Database configuration.")
    api_keys: Dict[str, SecretStr] = Field(default_factory=dict, description="Dictionary of API keys for external services.")
    llm_providers: List[LLMConfig] = Field(default_factory=list, description="List of configured LLM providers.")
    analyzers: List[AnalyzerConfig] = Field(default_factory=list, description="Configuration for individual analysis components.")
    pipelines: List[PipelineConfig] = Field(default_factory=list, description="Configuration for predefined pipelines.")
    # Add other top-level configurations as needed
    # e.g., api_server_port: int = 8000

    class Config:
        # Allow reading from environment variables (needs pydantic[dotenv] usually)
        # env_file = '.env'
        # env_file_encoding = 'utf-8'
        # case_sensitive = False # For environment variables
        pass

# Example Usage (typically loaded from YAML/JSON file or env vars)
# if __name__ == "__main__":
#     config_data = {
#         "database": {"db_type": "sqlite", "db_path": "./data/analysis.db"},
#         "llm_providers": [
#             {"provider": "openai", "model_name": "gpt-3.5-turbo", "api_key": "sk-..."},
#             {"provider": "local", "model_name": "llama3-8b", "api_base": "http://localhost:11434"}
#         ],
#         "analyzers": [
#             {"analyzer_name": "sentiment", "enabled": True, "parameters": {"threshold": 0.1}},
#             {"analyzer_name": "topic", "enabled": True, "parameters": {"num_topics": 10}}
#         ],
#         "pipelines": [
#             {
#                 "pipeline_name": "standard_analysis",
#                 "steps": [
#                     {"step_name": "load_data", "component_type": "data_loader", "config": {"source": "./input"}},
#                     {"step_name": "run_sentiment", "component_type": "analyzer", "config": {"analyzer_ref": "sentiment"}},
#                     {"step_name": "run_topics", "component_type": "analyzer", "config": {"analyzer_ref": "topic"}},
#                     {"step_name": "export_results", "component_type": "exporter", "config": {"target": "./output"}}
#                 ]
#             }
#         ]
#     }
# 
#     try:
#         app_config = AppConfig(**config_data)
#         print("Configuration loaded successfully!")
#         print(app_config.json(indent=2))
#     except ValidationError as e:
#         print(f"Configuration validation failed:\n{e}")
