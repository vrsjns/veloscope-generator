"""
Batch upload module for submitting OpenAI batch processing jobs.

This module handles:
1. Retrieving prepared batches from the control file
2. Downloading JSONL files from S3
3. Uploading files to OpenAI
4. Creating batch processing jobs
5. Updating batch status in the control file
"""

import sys

from openai import OpenAIError

from shared.config import (
    ENABLE_FILE_LOGGING,
    OPENAI_COMPLETION_WINDOW,
    OPENAI_INPUT_FILE,
    STATUS_FAILED,
    STATUS_SUBMITTED,
)
from shared.utils.control_file_utils import (
    get_prepared_batches,
    update_batch_status,
)
from shared.utils.logging_utils import add_file_handler, configure_logger
from shared.utils.openai_utils import initialize_openai_client
from shared.utils.s3_utils import download_file_from_s3

# Configure logger
logger = configure_logger('batch_upload')
if ENABLE_FILE_LOGGING:
    add_file_handler(logger)


# ---- Clients ----
# Initialize OpenAI client
client = initialize_openai_client()


def upload_jsonl_to_openai() -> bool:
    """
    Upload prepared JSONL files to OpenAI and create batch processing jobs.

    Retrieves prepared batches from the control file, downloads the JSONL files
    from S3, uploads them to OpenAI, creates batch processing jobs, and updates
    the batch status in the control file.

    Returns:
        bool: True if at least one batch was successfully processed,
            False otherwise.
    """
    try:
        # Get prepared batches directly using the utility function
        prepared_batches = get_prepared_batches()
        if not prepared_batches:
            logger.info("No prepared batches found in control file.")
            return False

        logger.info(
            f"Found {len(prepared_batches)} prepared batches to process"
        )

        success_count = 0
        for batch in prepared_batches:
            s3_key = batch["input_file"]
            target_date = batch["target_date"]

            logger.info(f"Processing batch for target date: {target_date}")

            # Download the JSONL file from S3
            if not download_file_from_s3(s3_key, OPENAI_INPUT_FILE):
                logger.error(f"Failed to download file from S3: {s3_key}")
                update_batch_status(
                    batch_id=batch.get("batch_id"),
                    s3_key=s3_key,
                    new_status=STATUS_FAILED,
                    additional_data={
                        "error": "Failed to download file from S3"
                    }
                )
                continue

            # Upload the file to OpenAI
            try:
                logger.info("Uploading file to OpenAI...")
                with open(OPENAI_INPUT_FILE, "rb") as file:
                    file_resp = client.files.create(
                        file=file,
                        purpose="batch"
                    )
                file_id = file_resp.id
                logger.info(f"Uploaded file. File ID: {file_id}")
            except (OpenAIError, IOError) as e:
                logger.error(f"Failed to upload file to OpenAI: {str(e)}")
                update_batch_status(
                    batch_id=batch.get("batch_id"),
                    s3_key=s3_key,
                    new_status=STATUS_FAILED,
                    additional_data={"error": str(e)}
                )
                continue

            # Submit batch job
            try:
                logger.info("Submitting batch job...")
                batch_resp = client.batches.create(
                    input_file_id=file_id,
                    endpoint="/v1/chat/completions",
                    completion_window=OPENAI_COMPLETION_WINDOW
                )
                openai_batch_id = batch_resp.id
                logger.info(
                    f"Submitted batch job. Batch ID: {openai_batch_id}"
                )
            except OpenAIError as e:
                logger.error(f"Failed to submit batch job: {str(e)}")
                update_batch_status(
                    batch_id=batch.get("batch_id"),
                    s3_key=s3_key,
                    new_status=STATUS_FAILED,
                    additional_data={"error": str(e), "file_id": file_id}
                )
                continue

            # Update batch info in control data
            update_batch_status(
                batch_id=batch.get("batch_id"),
                s3_key=s3_key,
                new_status=STATUS_SUBMITTED,
                additional_data={
                    "file_id": file_id,
                    "openai_batch_id": openai_batch_id
                }
            )
            success_count += 1

        logger.info(
            f"Successfully processed {success_count} out of "
            f"{len(prepared_batches)} batches"
        )
        return success_count > 0

    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return False


if __name__ == "__main__":
    success = upload_jsonl_to_openai()
    sys.exit(0 if success else 1)
