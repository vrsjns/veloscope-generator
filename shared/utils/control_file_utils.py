from ..config import CONTROL_KEY, STATUS_SUBMITTED, STATUS_PREPARED, STATUS_COMPLETED, STATUS_FAILED
from .s3_utils import download_json_from_s3, upload_json_to_s3
from .logging_utils import configure_logger
import datetime

# Configure logger
logger = configure_logger('control_file_utils')

def get_control_data():
    """Get the control data from S3"""
    control_data = download_json_from_s3(CONTROL_KEY)
    if control_data is None:
        logger.warning(f"No control data found at {CONTROL_KEY}, returning empty list")
        return []
    logger.debug(f"Retrieved control data with {len(control_data)} entries")
    return control_data

def update_control_data(control_data):
    """Update the control data in S3"""
    success = upload_json_to_s3(CONTROL_KEY, control_data)
    if success:
        logger.info(f"Updated control file with {len(control_data)} entries")
    else:
        logger.error(f"Failed to update control file")
    return success

def get_batches_by_status(status):
    """Get batches with specified status"""
    control_data = get_control_data()
    filtered_batches = [batch for batch in control_data if batch.get("status") == status]
    logger.debug(f"Found {len(filtered_batches)} batches with status '{status}'")
    return filtered_batches

def get_pending_batches():
    """Get batches with 'submitted' status"""
    return get_batches_by_status(STATUS_SUBMITTED)

def get_prepared_batches():
    """Get batches with 'prepared' status"""
    return get_batches_by_status(STATUS_PREPARED)

def get_completed_batches():
    """Get batches with 'completed' status"""
    return get_batches_by_status(STATUS_COMPLETED)

def get_failed_batches():
    """Get batches with 'failed' status"""
    return get_batches_by_status(STATUS_FAILED)

def update_batch_status(batch_id=None, s3_key=None, new_status=None, additional_data=None):
    """
    Update a batch's status and additional data in the control file
    
    Args:
        batch_id: The batch ID to find (optional if s3_key is provided)
        s3_key: The S3 key to find (optional if batch_id is provided)
        new_status: The new status to set
        additional_data: Dictionary of additional fields to update
    
    Returns:
        bool: True if successful, False otherwise
    """
    if not (batch_id or s3_key):
        logger.error("Either batch_id or s3_key must be provided")
        return False

    if not new_status:
        logger.error("New status must be provided")
        return False

    control_data = get_control_data()
    if not control_data:
        logger.error("Failed to retrieve control data")
        return False

    updated = False
    for i, item in enumerate(control_data):
        # Check if we're matching by batch_id or s3_key
        if (batch_id and item.get("batch_id") == batch_id) or (s3_key and item.get("input_file") == s3_key):
            # Update status
            control_data[i]["status"] = new_status
            control_data[i]["updated_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()

            # If we're updating with a new batch_id (when it was previously None)
            if batch_id and item.get("batch_id") is None:
                control_data[i]["batch_id"] = batch_id

            # Add additional data if provided
            if additional_data and isinstance(additional_data, dict):
                for key, value in additional_data.items():
                    control_data[i][key] = value

            updated = True
            logger.debug(f"Updated batch in control data: {control_data[i]}")
            break

    if not updated:
        logger.warning(f"No matching batch found to update status to {new_status}")
        return False

    return update_control_data(control_data)