import os
import json
import sys
import datetime
from openai import OpenAI, OpenAIError
from shared.config import (
    RESULT_DIR,
    OPENAI_API_KEY,
    STATUS_COMPLETED,
    STATUS_FAILED,
    HOROSCOPE_PREFIX,
    ENABLE_FILE_LOGGING
)
from shared.utils.logging_utils import configure_logger, add_file_handler
from shared.utils.control_file_utils import get_pending_batches, update_batch_status
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
try:
    client = OpenAI(
        api_key=OPENAI_API_KEY,
    )
except Exception as e:
    logger.error(f"Failed to initialize clients: {str(e)}")
    sys.exit(1)

# ---- Helpers ----
def wait_for_batch_completion(batch_id):
    """Wait for batch to complete or fail"""
    try:
        batch = client.batches.retrieve(batch_id)
        
        if batch.status in [BATCH_STATUS_COMPLETED, BATCH_STATUS_FAILED]:
            logger.info(f"Batch {batch_id} status: {batch.status}")
            return batch
        
        logger.info(f"Batch {batch_id} is still {batch.status}. Will check again later.")
        return None
    except OpenAIError as e:
        logger.error(f"Error retrieving batch {batch_id}: {str(e)}")
        return None

def download_and_upload_results(batch, batch_info):
    try:
        target_date = batch_info["target_date"]
        
        result_file_id = batch.output_file_id
        if not result_file_id:
            logger.error("No result file found in batch.")
            return False
        
        logger.info(f"Downloading result file: {result_file_id}")
        try:
            # Using the recommended .content() method
            result = client.files.content(result_file_id)
            result_text = result.text
        except OpenAIError as e:
            logger.error(f"Failed to download result file: {str(e)}")
            return False
            
        lines = result_text.splitlines()
        success_count = 0
        total_count = len(lines)
        
        for line in lines:
            try:
                item = json.loads(line)
                
                name = item.get("custom_id", "unknown").replace(" ", "_")
                output = item.get("response", {}).get("body", {}).get("choices", [{}])[0].get("message", {}).get("content", "")
                
                if not output:
                    logger.warning(f"Empty or invalid response for {name}")
                    continue
                
                data = {
                    "name": name,
                    "sign": "",  # Could extract from prompt if needed
                    "horoscope": output.strip()
                }
                
                key = f"{HOROSCOPE_PREFIX}/{target_date}/{name}.json".lower()
                
                # Use the s3_utils function instead of direct S3 client
                if upload_json_to_s3(key, data):
                    logger.info(f"Uploaded horoscope for {name}")
                    success_count += 1
                else:
                    logger.error(f"Failed to upload horoscope for {name}")
                
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse result line: {str(e)}")
        
        logger.info(f"Successfully processed {success_count} out of {total_count} results")
        return success_count > 0
        
    except Exception as e:
        logger.error(f"Unexpected error in download_and_upload_results: {str(e)}")
        return False

# ---- Main Logic ----
def process_pending_batches():
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
            
            batch = wait_for_batch_completion(batch_id)
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
            additional_data = {"completed_at": datetime.datetime.now(datetime.timezone.utc).isoformat()}
            update_success = update_batch_status(batch_id=batch_id, new_status=new_status, additional_data=additional_data)
            
            if not update_success:
                logger.warning(f"Failed to update status for batch {batch_id}")

        logger.info(f"Successfully processed {success_count} out of {len(pending_batches)} batches")
        return success_count > 0
        
    except Exception as e:
        logger.error(f"Unexpected error in process_pending_batches: {str(e)}")
        return False

if __name__ == "__main__":
    success = process_pending_batches()
    sys.exit(0 if success else 1)