import os
import time
import pysftp
import boto3
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# SFTP parameters
sftp_host = os.getenv("SFTP_HOST")
sftp_port = int(os.getenv("SFTP_PORT"))
sftp_username = os.getenv("SFTP_USERNAME")
sftp_password = os.getenv("SFTP_PASSWORD")
remote_directory = os.getenv("REMOTE_DIRECTORY")

# AWS parameters
aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")
s3_bucket_name = os.getenv("S3_BUCKET_NAME")

# Local directory for file processing
local_directory = "local_directory"

# Establish SFTP connection
def establish_sftp_connection():
    try:
        sftp = pysftp.Connection(host=sftp_host, port=sftp_port, username=sftp_username, password=sftp_password)
        logger.info("SFTP connection established successfully")
        return sftp
    except Exception as e:
        logger.error(f"Error establishing SFTP connection: {str(e)}")
        raise

# Download file from SFTP to local directory
def download_file(sftp, remote_file, local_file):
    try:
        sftp.get(remote_file, local_file)
        logger.info(f"Downloaded file '{remote_file}' to '{local_file}'")
    except Exception as e:
        logger.error(f"Error downloading file '{remote_file}': {str(e)}")
        raise

# Upload file to AWS S3 bucket
def upload_file_to_s3(local_file):
    try:
        s3 = boto3.client("s3", aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)
        s3.upload_file(local_file, s3_bucket_name, os.path.basename(local_file))
        logger.info(f"Uploaded file '{local_file}' to AWS S3 bucket '{s3_bucket_name}'")
    except Exception as e:
        logger.error(f"Error uploading file '{local_file}' to AWS S3: {str(e)}")
        raise

# Check for new files in SFTP directory
def check_for_new_files(sftp):
    try:
        sftp.chdir(remote_directory)
        remote_files = sftp.listdir()
        for remote_file in remote_files:
            local_file = os.path.join(local_directory, remote_file)
            if not os.path.exists(local_file):
                download_file(sftp, remote_file, local_file)
                upload_file_to_s3(local_file)
                mark_file_as_processed(remote_file)
    except Exception as e:
        logger.error(f"Error checking for new files: {str(e)}")
        raise

# Mark file as processed
def mark_file_as_processed(remote_file):
    try:
        with open(".processed_files.txt", "a") as file:
            file.write(remote_file + "\n")
        logger.info(f"Marked file '{remote_file}' as processed")
    except Exception as e:
        logger.error(f"Error processing file '{remote_file}' as processed: {str(e)}")
        raise

# Main execution
if __name__ == "__main__":
    # Create local directory if it doesn't exist
    if not os.path.exists(local_directory):
        os.makedirs(local_directory)
        logger.info(f"Created local directory '{local_directory}'")

    # Main loop to continuously check for new files
    while True:
        try:
            sftp = establish_sftp_connection()
            check_for_new_files(sftp)
            sftp.close()
        except Exception as e:
            logger.error(f"Error during main loop execution: {str(e)}")

        # Sleep for a specified interval before checking again
        time.sleep(60)
