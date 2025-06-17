"""
Utility module for configuring and managing logging.

This module provides functions to set up logging with consistent formatting
across different components of the application, including console and file
logging options.
"""

import logging
import os
from datetime import datetime

from ..config import LOG_DIR, LOG_LEVEL


def configure_logger(name: str) -> logging.Logger:
    """
    Configure a logger with the specified name.

    Sets up a logger with consistent formatting for console output and
    returns it for use in the application.

    Args:
        name (str): The name of the logger, typically the module name.

    Returns:
        logging.Logger: A configured logger instance.
    """
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, LOG_LEVEL))

    # Clear existing handlers to avoid duplicates
    if logger.handlers:
        logger.handlers.clear()

    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, LOG_LEVEL))

    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Add formatter to console handler
    console_handler.setFormatter(formatter)

    # Add console handler to logger
    logger.addHandler(console_handler)

    return logger


def add_file_handler(logger: logging.Logger) -> None:
    """
    Add a file handler to an existing logger.

    Creates a log file in the configured directory with a timestamp in the
    filename and adds a handler to write log messages to this file.

    Args:
        logger (logging.Logger): The logger to add the file handler to.

    Returns:
        None
    """
    # Ensure log directory exists
    os.makedirs(LOG_DIR, exist_ok=True)

    # Create log filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    log_file = os.path.join(LOG_DIR, f"{logger.name}-{timestamp}.log")

    # Create file handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(getattr(logging, LOG_LEVEL))

    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Add formatter to file handler
    file_handler.setFormatter(formatter)

    # Add file handler to logger
    logger.addHandler(file_handler)
    logger.info(f"Logging to file: {log_file}")
