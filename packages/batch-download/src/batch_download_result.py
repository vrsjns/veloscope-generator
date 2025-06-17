"""
Batch download module for retrieving and processing OpenAI batch results.

This module handles downloading completed batch results from OpenAI,
processing the responses, and uploading the generated horoscopes to S3.
It checks for pending batches, waits for their completion, and updates
their status in the control file.
"""

import datetime
import json
import os
import sys
from typing import Any, Dict, Optional

from openai import OpenAIError

from shared.config import (
    ENABLE_FILE_LOGGING,
    HOROSCOPE_PREFIX,
    RESULT_DIR,
    STATUS_COMPLETED,
    STATUS_FAILED,
)
from shared.utils.control_file_utils import (
    get_pending_batches,
    update_batch_status,
)
from shared.utils.logging_utils import add_file_handler, configure_logger
from shared.utils.openai_utils import initialize_openai_client
from shared.utils.s3_utils import upload_json_to_s3

# Configure logger
logger = configure_logger('batch_download')
if ENABLE_FILE_LOGGING:
    add_file_handler(logger)

# Ensure result directory exists
os.makedirs(RESULT_DIR, exist_ok=True)

# OpenAI batch status constants
BATCH_STATUS_COMPLETED = "completed"
BATCH_STATUS_FAILED = "failed"
BATCH_STATUS_IN_PROGRESS = "in_progress"
BATCH_POLL_INTERVAL = 60  # seconds

# ---- Clients ----
# Initialize OpenAI client
client = initialize_openai_client()


# ---- Helpers ----
def check_batch_completion(batch_id: str) -> Optional[Any]:
    """
    Check an OpenAI batch to complete or fail.

    Args:
        batch_id (str): The ID of the batch to check.

    Returns:
        object: The batch object if completed or failed, None otherwise.
    """
    try:
        batch = client.batches.retrieve(batch_id)

        if batch.status in [BATCH_STATUS_COMPLETED, BATCH_STATUS_FAILED]:
            logger.info(f"Batch {batch_id} status: {batch.status}")
            return batch

        logger.info(
            f"Batch {batch_id} is still {batch.status}. "
            f"Will check again later."
        )
        return None
    except OpenAIError as e:
        logger.error(f"Error retrieving batch {batch_id}: {str(e)}")
        return None


def download_and_upload_results(
        batch: Any, batch_info: Dict[str, Any]
) -> bool:
    """
    Download batch results from OpenAI and upload processed horoscopes to S3.

    Args:
        batch (object): The OpenAI batch object containing result information.
        batch_info (dict): Information about the batch from the control file.

    Returns:
        bool: True if processing was successful, False otherwise.
    """
    try:
        target_date = batch_info["target_date"]
        result_file_id = batch.output_file_id

        if not result_file_id:
            logger.error("No result file found in batch.")
            return False

        logger.info(f"Downloading result file: {result_file_id}")

        # Extract result text to a separate function to reduce local variables
        result_text = _download_result_file(result_file_id)
        if result_text is None:
            return False

        # Process results in a separate function
        return _process_results(result_text, target_date)

    except Exception as e:
        logger.error(
            f"Unexpected error in download_and_upload_results: {str(e)}"
        )
        return False


def _download_result_file(result_file_id: str) -> Optional[Any]:
    """Download the result file from OpenAI."""
    try:
        result = client.files.content(result_file_id)
        return result.text
    except OpenAIError as e:
        logger.error(f"Failed to download result file: {str(e)}")
        return None


def _process_results(result_text: str, target_date: str) -> bool:
    """Process the results and upload horoscopes to S3."""
    lines = result_text.splitlines()
    success_count = 0
    total_count = len(lines)

    for line in lines:
        try:
            item = json.loads(line)
            name = item.get("custom_id", "unknown").replace(" ", "_")

            # Extract output from nested structure
            choices = (
                item.get("response", {}).get("body", {}).get("choices", [{}])
            )
            output = (
                choices[0].get("message", {}).get("content", "")
                if choices
                else ""
            )

            if not output:
                logger.warning(f"Empty or invalid response for {name}")
                continue

            data = {
                "name": name,
                "sign": "",  # Could extract from prompt if needed
                "horoscope": output.strip()
            }

            key = f"{HOROSCOPE_PREFIX}/{target_date}/{name}.json".lower()

            # Upload to S3
            if upload_json_to_s3(key, data):
                logger.info(f"Uploaded horoscope for {name}")
                success_count += 1
            else:
                logger.error(f"Failed to upload horoscope for {name}")

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse result line: {str(e)}")

    logger.info(
        f"Successfully processed {success_count} "
        f"out of {total_count} results"
    )
    return success_count > 0


# ---- Main Logic ----
def process_pending_batches() -> bool:
    """
    Process all pending batches from the control file.

    Retrieves all batches with 'submitted' status, checks if they are
    completed, downloads and processes their results, and updates their
    status in the control file.

    Returns:
        bool: True if at least one batch was successfully processed or
              if there were no pending batches, False otherwise.
    """
    try:
        pending_batches = get_pending_batches()

        if not pending_batches:
            logger.info("No pending batches found.")
            return True

        logger.info(f"Found {len(pending_batches)} pending batches to process")

        success_count = 0
        for batch_info in pending_batches:
            batch_id = batch_info["batch_id"]
            logger.info(f"Processing batch: {batch_id}")

            batch = check_batch_completion(batch_id)
            if batch is None:
                logger.info(f"Batch {batch_id} not ready for processing yet")
                continue

            # Update batch status in control data
            if batch.status == BATCH_STATUS_COMPLETED:
                success = download_and_upload_results(batch, batch_info)
                new_status = STATUS_COMPLETED if success else STATUS_FAILED
                if success:
                    success_count += 1
            else:
                new_status = STATUS_FAILED

            # Use update_batch_status instead of direct update
            additional_data = {
                "completed_at": datetime.datetime.now(
                    datetime.timezone.utc
                ).isoformat()
            }
            update_success = update_batch_status(
                batch_id=batch_id,
                new_status=new_status,
                additional_data=additional_data
            )

            if not update_success:
                logger.warning(f"Failed to update status for batch {batch_id}")

        logger.info(
            f"Successfully processed {success_count} out of "
            f"{len(pending_batches)} batches"
        )
        return success_count > 0

    except Exception as e:
        logger.error(f"Unexpected error in process_pending_batches: {str(e)}")
        return False


if __name__ == "__main__":
    ready = process_pending_batches()
    sys.exit(0 if ready else 1)
