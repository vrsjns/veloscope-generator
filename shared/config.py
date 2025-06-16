"""
Configuration module for the Veloscope Generator application.

This module loads environment variables and defines configuration constants
used throughout the application, including:
- Environment settings
- S3 configuration
- OpenAI API settings
- File paths and prefixes
- Batch status constants
- Logging configuration

The configuration is loaded from environment variables, with sensible defaults
provided for development environments.
"""

import os
import tempfile  # Add this import at the top of the file

from dotenv import load_dotenv

# Load environment variables once
load_dotenv()

# Environment
ENV = os.getenv("ENV", "development")

# S3 Configuration
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME", "default_bucket")
CONTROL_KEY = os.getenv("CONTROL_KEY", "batch_control.json")
RIDERS_FILE = os.getenv("RIDERS_FILE", "riders.json")

# OpenAI Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4.1-nano")
OPENAI_COMPLETION_WINDOW = "24h"

# AWS Configuration
AWS_REGION = os.getenv("AWS_REGION", "eu-central-1")

# File paths
TEMP_DIR = tempfile.gettempdir()
RESULT_DIR = os.path.join(TEMP_DIR, "batch_results")
OPENAI_INPUT_FILE = os.path.join(TEMP_DIR, "openai_input.jsonl")

# S3 Prefixes and paths
OUTPUT_PREFIX = "openai/input"
HOROSCOPE_PREFIX = "horoscope"

# Batch status constants
STATUS_PREPARED = "prepared"
STATUS_SUBMITTED = "submitted"
STATUS_COMPLETED = "completed"
STATUS_FAILED = "failed"

# Logging Configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_DIR = os.getenv("LOG_DIR", os.path.join(tempfile.gettempdir(), "logs"))
ENABLE_FILE_LOGGING = os.getenv(
    "ENABLE_FILE_LOGGING", "false"
).lower() == "true"
