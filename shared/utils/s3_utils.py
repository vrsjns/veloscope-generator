"""
Utility module for Amazon S3 operations.

This module provides functions to interact with Amazon S3 for storing and
retrieving data, including JSON objects and files. It handles common S3
operations such as uploading, downloading, and checking for the existence
of objects.
"""

import json
import os
from typing import Any, Dict, List, Optional, Union

import boto3

from ..config import ENABLE_FILE_LOGGING, S3_BUCKET_NAME
from .logging_utils import add_file_handler, configure_logger

# Configure logger
logger = configure_logger('s3_utils')
if ENABLE_FILE_LOGGING:
    add_file_handler(logger)

# S3 client
s3 = boto3.client("s3")


def get_s3_object(key: str) -> Optional[bytes]:
    """
    Get an object from S3 bucket.

    Args:
        key (str): The S3 key of the object to retrieve.

    Returns:
        bytes: The content of the S3 object, or None if retrieval fails.
    """
    try:
        response = s3.get_object(Bucket=S3_BUCKET_NAME, Key=key)
        return bytes(response['Body'].read())
    except Exception as e:
        logger.error(f"Error getting object from S3: {str(e)}")
        return None


def put_s3_object(
    key: str, data: Union[str, bytes], content_type: str = "application/json"
) -> bool:
    """
    Put an object into S3 bucket.

    Args:
        key (str): The S3 key to store the object under.
        data (Union[str, bytes]): The data to store in S3.
        content_type (str): The content type of the data.

    Returns:
        bool: True if the operation was successful, False otherwise.
    """
    try:
        s3.put_object(
            Bucket=S3_BUCKET_NAME,
            Key=key,
            Body=data,
            ContentType=content_type
        )
        logger.info(f"Successfully uploaded object to S3: {key}")
        return True
    except Exception as e:
        logger.error(f"Error putting object to S3: {str(e)}")
        return False


def upload_json_to_s3(key: str, data: Dict[str, Any]) -> bool:
    """
    Upload JSON data to S3.

    Args:
        key (str): The S3 key to store the JSON under.
        data (dict): The Python dictionary to convert to JSON and upload.

    Returns:
        bool: True if the upload was successful, False otherwise.
    """
    try:
        json_data = json.dumps(data, indent=2)
        return put_s3_object(key, json_data, "application/json")
    except Exception as e:
        logger.error(f"Error uploading JSON to S3: {str(e)}")
        return False


def download_json_from_s3(key: str) -> Optional[Dict[str, Any]]:
    """
    Download and parse JSON data from S3.

    Args:
        key (str): The S3 key of the JSON object to download.

    Returns:
        dict: The parsed JSON data as a Python dictionary, or None if
              download or parsing fails.
    """
    try:
        data = get_s3_object(key)
        if data is None:
            return None
        parsed_data: Dict[str, Any] = json.loads(data)
        return parsed_data
    except json.JSONDecodeError as e:
        logger.error(f"Error parsing JSON from S3: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Error downloading JSON from S3: {str(e)}")
        return None


def upload_file_to_s3(local_path: str, s3_key: str) -> bool:
    """
    Upload a file to S3.

    Args:
        local_path (str): The local path of the file to upload.
        s3_key (str): The S3 key to store the file under.

    Returns:
        bool: True if the upload was successful, False otherwise.
    """
    try:
        s3.upload_file(
            Filename=local_path,
            Bucket=S3_BUCKET_NAME,
            Key=s3_key
        )
        logger.info(f"Successfully uploaded file to S3: {s3_key}")
        return True
    except Exception as e:
        logger.error(f"Error uploading file to S3: {str(e)}")
        return False


def download_file_from_s3(s3_key: str, local_path: str) -> bool:
    """
    Download a file from S3.

    Args:
        s3_key (str): The S3 key of the file to download.
        local_path (str): The local path to save the downloaded file.

    Returns:
        bool: True if the download was successful, False otherwise.
    """
    try:
        # Ensure directory exists
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        s3.download_file(
            Bucket=S3_BUCKET_NAME,
            Key=s3_key,
            Filename=local_path
        )
        logger.info(
            f"Successfully downloaded file from S3: {s3_key} to {local_path}"
        )
        return True
    except Exception as e:
        logger.error(f"Error downloading file from S3: {str(e)}")
        return False


def list_objects(prefix: str = "") -> List[str]:
    """
    List objects in the S3 bucket with the given prefix.

    Args:
        prefix (str): The prefix to filter objects by.

    Returns:
        list: A list of object keys matching the prefix.
    """
    try:
        response = s3.list_objects_v2(
            Bucket=S3_BUCKET_NAME,
            Prefix=prefix
        )
        if 'Contents' in response:
            return [obj['Key'] for obj in response['Contents']]
        return []
    except Exception as e:
        logger.error(f"Error listing objects in S3: {str(e)}")
        return []


def object_exists(key: str) -> bool:
    """
    Check if an object exists in the S3 bucket.

    Args:
        key (str): The S3 key to check for existence.

    Returns:
        bool: True if the object exists, False otherwise.
    """
    try:
        s3.head_object(Bucket=S3_BUCKET_NAME, Key=key)
        return True
    except Exception:
        return False
