"""
Utility module for OpenAI API interactions.

This module provides common functions for interacting with the OpenAI API,
including client initialization and error handling.
"""

import sys

from openai import OpenAI, OpenAIError

from ..config import OPENAI_API_KEY
from .logging_utils import configure_logger

# Configure logger
logger = configure_logger('openai_utils')


def initialize_openai_client() -> OpenAI:
    """
    Initialize and return an OpenAI client.

    Returns:
        OpenAI: An initialized OpenAI client.

    Exits:
        If client initialization fails, logs the error and exits with code 1.
    """
    try:
        client = OpenAI(
            api_key=OPENAI_API_KEY,
        )
        return client
    except OpenAIError as e:
        logger.error(f"Failed to initialize OpenAI client: {str(e)}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Failed to initialize OpenAI client: {str(e)}")
        sys.exit(1)
