"""
Utility module for managing batch control data.

This module provides functions to read, update, and manage the batch control
file stored in S3. It handles operations such as:
- Retrieving control data from S3
- Updating control data in S3
- Filtering batches by status
- Creating new batch entries
- Updating batch status
"""

import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from ..config import (
    CONTROL_KEY,
    STATUS_COMPLETED,
    STATUS_FAILED,
    STATUS_PREPARED,
    STATUS_SUBMITTED,
)
from .logging_utils import configure_logger
from .s3_utils import download_json_from_s3, upload_json_to_s3

# Configure logger
logger = configure_logger('control_file_utils')


def get_control_data() -> Dict[str, Any]:
    """
    Retrieve the batch control data from S3.

    Returns:
        dict: The control data as a dictionary, or an empty dictionary with
              'batches' key if the file doesn't exist or can't be read.
    """
    control_data = download_json_from_s3(CONTROL_KEY)
    if control_data is None:
        logger.info("Control file not found, creating new one")
        control_data = {"batches": []}
    elif not isinstance(control_data, dict):
        logger.error(f"Control data is not a dictionary: {type(control_data)}")
        control_data = {"batches": []}
    elif "batches" not in control_data:
        logger.info("'batches' key not found in control data, adding it")
        control_data["batches"] = []
    elif not isinstance(control_data["batches"], list):
        logger.error(
            f"'batches' is not a list: {type(control_data['batches'])}"
        )
        control_data["batches"] = []

    return control_data


def update_control_data(control_data: Dict[str, Any]) -> bool:
    """
    Update the batch control data in S3.

    Args:
        control_data (dict): The control data to upload.

    Returns:
        bool: True if the update was successful, False otherwise.
    """
    success = upload_json_to_s3(CONTROL_KEY, control_data)
    if not success:
        logger.error("Failed to update control data in S3")
    return success


def get_batches_by_status(status: str) -> List[Dict[str, Any]]:
    """
    Get all batches with a specific status from the control file.

    Args:
        status (str): The status to filter by (e.g., 'prepared', 'submitted').

    Returns:
        list: A list of batch dictionaries with the specified status.
    """
    control_data = get_control_data()
    filtered_batches = [
        batch for batch in control_data.get("batches", [])
        if batch.get("status") == status
    ]

    logger.info(
        f"Found {len(filtered_batches)} batches with status '{status}'"
    )
    return filtered_batches


def get_pending_batches() -> List[Dict[str, Any]]:
    """
    Get all batches with 'submitted' status from the control file.

    Returns:
        list: A list of batch dictionaries with 'submitted' status.
    """
    return get_batches_by_status(STATUS_SUBMITTED)


def get_prepared_batches() -> List[Dict[str, Any]]:
    """
    Get all batches with 'prepared' status from the control file.

    Returns:
        list: A list of batch dictionaries with 'prepared' status.
    """
    return get_batches_by_status(STATUS_PREPARED)


def get_completed_batches() -> List[Dict[str, Any]]:
    """
    Get all batches with 'completed' status from the control file.

    Returns:
        list: A list of batch dictionaries with 'completed' status.
    """
    return get_batches_by_status(STATUS_COMPLETED)


def get_failed_batches() -> List[Dict[str, Any]]:
    """
    Get all batches with 'failed' status from the control file.

    Returns:
        list: A list of batch dictionaries with 'failed' status.
    """
    return get_batches_by_status(STATUS_FAILED)


def create_batch(
    input_file: str,
    target_date: str,
    status: str = STATUS_PREPARED,
    additional_data: Optional[Dict[str, Any]] = None
) -> Tuple[bool, Optional[str]]:
    """
    Create a new batch entry in the control file.

    Args:
        input_file (str): The S3 key of the input file.
        target_date (str): The target date for the batch.
        status (str, optional): The initial status of the batch.
            Defaults to 'prepared'.
        additional_data (dict, optional): Additional data to include in the
            batch entry.

    Returns:
        tuple: (success, batch_id) where success is a boolean indicating if the
               operation was successful, and batch_id is the ID of the created
               batch.
    """
    try:
        control_data = get_control_data()

        # Generate a unique batch ID
        batch_id = str(uuid.uuid4())

        # Create the batch entry
        batch_entry = {
            "batch_id": batch_id,
            "input_file": input_file,
            "target_date": target_date,
            "status": status,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }

        # Add additional data if provided
        if additional_data:
            batch_entry.update(additional_data)

        # Add the batch to the control data
        control_data["batches"].append(batch_entry)

        # Update the control file
        # pylint: disable=R1705
        if update_control_data(control_data):
            logger.info(f"Created new batch with ID: {batch_id}")
            return True, batch_id
        else:
            logger.error("Failed to create batch")
            return False, None
        # pylint: enable=R1705

    except Exception as e:
        logger.error(f"Error creating batch: {str(e)}")
        return False, None


def update_batch_status(
    batch_id: Optional[str] = None,
    s3_key: Optional[str] = None,
    new_status: Optional[str] = None,
    additional_data: Optional[Dict[str, Any]] = None
) -> bool:
    """
    Update the status and/or additional data of a batch in the control file.

    Args:
        batch_id (str, optional): The ID of the batch to update.
        s3_key (str, optional): The S3 key of the batch's input file
            (alternative to batch_id).
        new_status (str, optional): The new status to set.
        additional_data (dict, optional): Additional data to update or add to
            the batch entry.

    Returns:
        bool: True if the update was successful, False otherwise.
    """
    if not batch_id and not s3_key:
        logger.error("Either batch_id or s3_key must be provided")
        return False

    control_data = get_control_data()

    # Find the batch to update
    for batch in control_data.get("batches", []):
        if (batch_id and batch.get("batch_id") == batch_id) or \
           (s3_key and batch.get("input_file") == s3_key):

            # Update status if provided
            if new_status:
                batch["status"] = new_status

            # Update additional data if provided
            if additional_data:
                batch.update(additional_data)

            # Update the timestamp
            batch["updated_at"] = datetime.now().isoformat()

            logger.info(
                f"Updated batch {batch.get('batch_id')} status to {new_status}"
            )

            # Save the updated control data
            return update_control_data(control_data)

    logger.error(f"Batch not found: ID={batch_id}, S3 Key={s3_key}")
    return False
