import sys
from openai import OpenAI, OpenAIError
from shared.config import (
    OPENAI_INPUT_FILE,
    OPENAI_API_KEY,
    OPENAI_COMPLETION_WINDOW,
    STATUS_PREPARED,
    STATUS_SUBMITTED,
    STATUS_FAILED,
    ENABLE_FILE_LOGGING
)
from shared.utils.logging_utils import configure_logger, add_file_handler
from shared.utils.control_file_utils import get_control_data, update_batch_status
from shared.utils.s3_utils import download_file_from_s3

# Configure logger
logger = configure_logger('batch_upload')
if ENABLE_FILE_LOGGING:
    add_file_handler(logger)

# ---- Clients ----
try:
    client = OpenAI(
        api_key=OPENAI_API_KEY,
    )
except Exception as e:
    logger.error(f"Failed to initialize clients: {str(e)}")
    sys.exit(1)

def upload_jsonl_to_openai():
    try:
        # Get control data
        control_data = get_control_data()
        if control_data is None:
            logger.error("Failed to retrieve control data")
            return False

        # Find all prepared batches
        prepared_batches = [batch for batch in control_data if batch["status"] == STATUS_PREPARED]
        if not prepared_batches:
            logger.info("No prepared batches found in control file.")
            return False

        logger.info(f"Found {len(prepared_batches)} prepared batches to process")

        success_count = 0
        for batch in prepared_batches:
            s3_key = batch["input_file"]
            target_date = batch["target_date"]

            logger.info(f"Processing batch for target date: {target_date}")

            # Download the JSONL file from S3
            if not download_file_from_s3(s3_key, OPENAI_INPUT_FILE):
                logger.error(f"Failed to download file from S3: {s3_key}")
                update_batch_status(batch_id=batch.get("batch_id"), s3_key=s3_key, new_status=STATUS_FAILED, additional_data={"error": "Failed to download file from S3"})
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
                update_batch_status(batch_id=batch.get("batch_id"), s3_key=s3_key, new_status=STATUS_FAILED, additional_data={"error": str(e)})
                continue

            # Submit batch job
            try:
                logger.info("Submitting batch job...")
                batch_resp = client.batches.create(
                    input_file_id=file_id,
                    endpoint="/v1/chat/completions",
                    completion_window=OPENAI_COMPLETION_WINDOW
                )
                batch_id = batch_resp.id
                logger.info(f"Submitted batch job. Batch ID: {batch_id}")
            except OpenAIError as e:
                logger.error(f"Failed to submit batch job: {str(e)}")
                update_batch_status(batch_id=batch.get("batch_id"), s3_key=s3_key, new_status=STATUS_FAILED, additional_data={"error": str(e), "file_id": file_id})
                continue

            # Update batch info in control data
            update_batch_status(batch_id=batch_id, s3_key=s3_key, new_status=STATUS_SUBMITTED, additional_data={"file_id": file_id})
            success_count += 1

        logger.info(f"Successfully processed {success_count} out of {len(prepared_batches)} batches")
        return success_count > 0

    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return False

if __name__ == "__main__":
    success = upload_jsonl_to_openai()
    sys.exit(0 if success else 1)