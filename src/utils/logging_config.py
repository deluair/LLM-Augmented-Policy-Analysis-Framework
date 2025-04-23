# src/utils/logging_config.py

import logging
import sys
from src.config import settings

def setup_logging():
    """Configures the logging system based on settings.

    Sets the log level and optionally configures file logging.
    """
    log_level = settings.logging.log_level.upper()
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    handlers = [logging.StreamHandler(sys.stdout)] # Log to console by default

    if settings.logging.log_file:
        file_handler = logging.FileHandler(settings.logging.log_file)
        file_handler.setFormatter(logging.Formatter(log_format))
        handlers.append(file_handler)

    logging.basicConfig(
        level=log_level,
        format=log_format,
        handlers=handlers,
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Example: Silence overly verbose libraries if needed
    # logging.getLogger("urllib3").setLevel(logging.WARNING)

    logger = logging.getLogger(__name__)
    logger.info(f"Logging configured with level {log_level}. Logging to file: {settings.logging.log_file or 'No'}")

# You can call setup_logging() early in your application entry point.
# Example usage:
# import logging
# from src.utils.logging_config import setup_logging
# setup_logging()
# logger = logging.getLogger(__name__)
# logger.info("This is an info message.")
# logger.debug("This is a debug message.") # Won't show if level is INFO
