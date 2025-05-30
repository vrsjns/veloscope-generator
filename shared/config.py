import os
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
TEMP_DIR = "/tmp"
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
LOG_DIR = os.getenv("LOG_DIR", "/tmp/logs")
ENABLE_FILE_LOGGING = os.getenv("ENABLE_FILE_LOGGING", "false").lower() == "true"