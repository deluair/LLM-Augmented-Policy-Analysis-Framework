"""
API Logging Utilities.

Configures logging for the application.
"""

import logging
import sys
import os

# Mapping string log levels to logging constants
LOG_LEVELS = {
    'DEBUG': logging.DEBUG,
    'INFO': logging.INFO,
    'WARNING': logging.WARNING,
    'ERROR': logging.ERROR,
    'CRITICAL': logging.CRITICAL
}

def setup_logging(log_level: str = 'INFO', log_format: str = None):
    """
    Configures the root logger for the application.

    Args:
        log_level (str, optional): The desired logging level (e.g., 'DEBUG', 'INFO'). 
                                   Can be overridden by the LOG_LEVEL environment variable.
                                   Defaults to 'INFO'.
        log_format (str, optional): The logging format string. Defaults to a standard format.
    """
    # Determine log level (environment variable takes precedence)
    env_log_level = os.environ.get('LOG_LEVEL', log_level).upper()
    level = LOG_LEVELS.get(env_log_level, logging.INFO)

    if not log_format:
        log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # Get the root logger
    root_logger = logging.getLogger()
    
    # Remove existing handlers to avoid duplicates if called multiple times
    if root_logger.hasHandlers():
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
            handler.close() # Close handlers properly

    # Create formatter
    formatter = logging.Formatter(log_format)

    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout) # Use stdout for console logs
    console_handler.setFormatter(formatter)

    # Add handler to the root logger
    root_logger.addHandler(console_handler)
    
    # Set the logging level for the root logger
    root_logger.setLevel(level)

    # Optionally, set specific levels for noisy libraries
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING) # Quieten access logs unless needed
    logging.getLogger("faker").setLevel(logging.WARNING) # Quieten faker logs if used

    # Log that logging is configured
    # Use the root logger directly for this initial message
    logging.info(f"Logging configured with level: {logging.getLevelName(level)} ({env_log_level})")

# Example of how to use this in main.py or at the start of your app:
# from .utils.logging import setup_logging
# 
# setup_logging(log_level='DEBUG') # Set default level, env var can override
# 
# logger = logging.getLogger(__name__)
# logger.info("Application starting...")
