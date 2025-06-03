import json
import sys
import uuid
from datetime import date, timedelta
from shared.config import (
    RIDERS_FILE, 
    OUTPUT_PREFIX, 
    OPENAI_INPUT_FILE,
    ENABLE_FILE_LOGGING
)
from shared.utils.logging_utils import configure_logger, add_file_handler
from shared.utils.control_file_utils import create_batch
from shared.utils.s3_utils import download_json_from_s3, upload_file_to_s3

# Configure logger
logger = configure_logger('batch_prepare')
if ENABLE_FILE_LOGGING:
    add_file_handler(logger)

# ---- Helpers ----
def get_zodiac_sign(birthdate):
    try:
        month, day = int(birthdate[0:2]), int(birthdate[3:5])
        zodiac = [
            ((1, 20), "Aquarius"), ((2, 19), "Pisces"), ((3, 21), "Aries"),
            ((4, 20), "Taurus"), ((5, 21), "Gemini"), ((6, 21), "Cancer"),
            ((7, 23), "Leo"), ((8, 23), "Virgo"), ((9, 23), "Libra"),
            ((10, 23), "Scorpio"), ((11, 22), "Sagittarius"), ((12, 22), "Capricorn")
        ]
        for (m, d), sign in reversed(zodiac):
            if (month, day) >= (m, d):
                return sign
        return "Capricorn"
    except (ValueError, IndexError) as e:
        logger.error(f"Error parsing birthdate '{birthdate}': {str(e)}")
        return "Unknown"

# ---- Main Logic ----
def generate_jsonl():
    try:
        # Step 1: Load riders list from S3
        logger.info("Loading riders list from S3...")
        riders = download_json_from_s3(RIDERS_FILE)
        if riders is None:
            logger.error("Failed to load riders list")
            return None, None

        logger.info(f"Successfully loaded {len(riders)} riders from S3")

        # Step 2: Build prompt entries
        target_date = (date.today() + timedelta(days=1)).isoformat()
        # Generate a unique identifier for this batch
        batch_uuid = str(uuid.uuid4())[:8]  # Use first 8 characters of UUID for brevity
        jsonl_key = f"{OUTPUT_PREFIX}/{target_date}-{batch_uuid}.jsonl"
        logger.info(f"Preparing JSONL for target date: {target_date} with ID: {batch_uuid}")

        try:
            with open(OPENAI_INPUT_FILE, "w", encoding="utf-8") as f:
                rider_count = 0
                for rider in riders:
                    name = rider["name"].title()
                    birthdate = rider["birth_date"]
                    sign = get_zodiac_sign(birthdate)

                    prompt = (
                    "Generate a daily horoscope for {name}, whose zodiac sign is {sign}, for the date {target_date}. "
                    "Make it friendly, encouraging, personalized and a little bit mystical. Do not include astrological terms. "
                    "Keep it under 3 sentences and feel free to use some cycling jargon, but not too much. "
                    "Don't forget some advice for personal life or for race recovery, "
                    "maybe some some improvement in technical setup or strategic planning or nutrition. "
                    ).format(name=name, sign=sign, target_date=target_date)

                    request = {
                        "custom_id": f"{name}",
                        "method": "POST",
                        "url": "/v1/chat/completions",
                        "body": {
                            "model": "gpt-4.1-nano",
                            "messages": [
                                {"role": "system", "content": "You are a friendly, creative and professional horoscope writer."},
                                {"role": "user", "content": prompt}
                            ],
                            "temperature": 0.8
                        }
                    }

                    f.write(json.dumps(request) + "\n")
                    rider_count += 1

                logger.info(f"Created JSONL with {rider_count} rider prompts")
        except IOError as e:
            logger.error(f"Failed to create JSONL file: {str(e)}")
            return None, None

        # Step 3: Upload to S3
        logger.info(f"Uploading JSONL to S3: {jsonl_key}")
        if not upload_file_to_s3(OPENAI_INPUT_FILE, jsonl_key):
            logger.error("Failed to upload JSONL to S3")
            return None, None

        # Step 4: Update control file with new batch info using the new create_batch function
        success, batch_uuid = create_batch(
            input_file=jsonl_key,
            target_date=target_date,
            additional_data={
                "rider_count": rider_count
            }
        )
        
        if not success:
            logger.error("Failed to create batch in control file")
            return None, None
            
        logger.info(f"Successfully created batch for {target_date} (UUID: {batch_uuid})")
        return jsonl_key, target_date

    except Exception as e:
        logger.error(f"Unexpected error in generate_jsonl: {str(e)}")
        return None, None

if __name__ == "__main__":
    jsonl_key, target_date = generate_jsonl()
    if jsonl_key and target_date:
        logger.info("Batch preparation completed successfully")
        sys.exit(0)
    else:
        logger.error("Batch preparation failed")
        sys.exit(1)