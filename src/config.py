# src/config.py

import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

# Load environment variables from .env file
load_dotenv()

class APISettings(BaseSettings):
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    # Add other relevant API keys (e.g., for data sources)
    # example_data_api_key: str = os.getenv("EXAMPLE_DATA_API_KEY", "")

class DatabaseSettings(BaseSettings):
    vector_db_url: str = os.getenv("VECTOR_DB_URL", "sqlite:///./vector_store.db") # Example default
    # Add settings for relational DB if needed
    # relational_db_url: str = os.getenv("RELATIONAL_DB_URL", "")

class ModelSettings(BaseSettings):
    embedding_model_name: str = os.getenv("EMBEDDING_MODEL_NAME", "all-MiniLM-L6-v2")
    llm_model_name: str = os.getenv("LLM_MODEL_NAME", "gpt-3.5-turbo") # Example default
    # Add paths for local models if applicable
    # local_model_path: str = os.getenv("LOCAL_MODEL_PATH", "")

class LoggingSettings(BaseSettings):
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    log_file: str | None = os.getenv("LOG_FILE") # Optional log file path

class Settings(BaseSettings):
    api: APISettings = APISettings()
    database: DatabaseSettings = DatabaseSettings()
    models: ModelSettings = ModelSettings()
    logging: LoggingSettings = LoggingSettings()

    app_env: str = os.getenv("APP_ENV", "development") # e.g., development, production

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'
        # Allow nested structures
        env_nested_delimiter = '__'

# Instantiate settings
settings = Settings()

# You can now import 'settings' from this module elsewhere in your code
# from src.config import settings
# print(settings.api.openai_api_key)
