import boto3
import json
import os
from botocore.exceptions import ClientError
from ..config import S3_BUCKET_NAME, ENABLE_FILE_LOGGING
from .logging_utils import configure_logger, add_file_handler

# Configure logger
logger = configure_logger('s3_utils')
if ENABLE_FILE_LOGGING:
    add_file_handler(logger)

# S3 client
s3 = boto3.client("s3")

def get_s3_object(key):
    """Get an object from S3"""
    try:
        response = s3.get_object(Bucket=S3_BUCKET_NAME, Key=key)
        return response['Body'].read()
    except Exception as e:
        logger.error(f"Error getting S3 object {key}: {str(e)}")
        return None

def put_s3_object(key, data, content_type="application/json"):
    """Put an object to S3"""
    try:
        s3.put_object(
            Bucket=S3_BUCKET_NAME,
            Key=key,
            Body=data,
            ContentType=content_type
        )
        logger.info(f"Uploaded to s3://{S3_BUCKET_NAME}/{key}")
        return True
    except Exception as e:
        logger.error(f"Error uploading to S3 {key}: {str(e)}")
        return False

def upload_json_to_s3(key, data):
    """Upload JSON data to S3"""
    try:
        json_data = json.dumps(data).encode("utf-8")
        return put_s3_object(key, json_data, "application/json")
    except Exception as e:
        logger.error(f"Error serializing JSON for {key}: {str(e)}")
        return False

def download_json_from_s3(key):
    """Download and parse JSON data from S3"""
    try:
        data = get_s3_object(key)
        if data:
            return json.loads(data)
        return None
    except json.JSONDecodeError as e:
        logger.error(f"Error parsing JSON from {key}: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error downloading JSON from {key}: {str(e)}")
        return None

def upload_file_to_s3(local_path, s3_key):
    """Upload a local file to S3"""
    try:
        with open(local_path, "rb") as f:
            s3.upload_fileobj(f, S3_BUCKET_NAME, s3_key)
        logger.info(f"Uploaded file from {local_path} to s3://{S3_BUCKET_NAME}/{s3_key}")
        return True
    except (IOError, ClientError) as e:
        logger.error(f"Failed to upload file to S3: {str(e)}")
        return False

def download_file_from_s3(s3_key, local_path):
    """Download a file from S3 to local path"""
    try:
        # Ensure directory exists
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        s3.download_file(S3_BUCKET_NAME, s3_key, local_path)
        logger.info(f"Downloaded s3://{S3_BUCKET_NAME}/{s3_key} to {local_path}")
        return True
    except ClientError as e:
        logger.error(f"Failed to download file from S3: {str(e)}")
        return False

def list_objects(prefix=""):
    """List objects in S3 bucket with given prefix"""
    try:
        response = s3.list_objects_v2(Bucket=S3_BUCKET_NAME, Prefix=prefix)
        if 'Contents' in response:
            return [item['Key'] for item in response['Contents']]
        return []
    except ClientError as e:
        logger.error(f"Failed to list objects in S3: {str(e)}")
        return []

def object_exists(key):
    """Check if an object exists in S3"""
    try:
        s3.head_object(Bucket=S3_BUCKET_NAME, Key=key)
        return True
    except ClientError:
        return False