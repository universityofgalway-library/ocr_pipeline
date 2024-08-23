import os
import boto3
import logging

# Setup basic logging
logging.basicConfig(level=logging.INFO)

def upload_folder_to_s3(folder_path, bucket_name, s3_folder=''):
    s3_client = boto3.client('s3')

    logging.info(f"Starting upload of {folder_path} to s3://{bucket_name}/{s3_folder}")

    for root, dirs, files in os.walk(folder_path):
        for file in files:
            file_path = os.path.join(root, file)
            s3_file_path = os.path.join(s3_folder, os.path.relpath(file_path, folder_path))

            try:
                logging.info(f"Uploading {file_path} to s3://{bucket_name}/{s3_file_path}")
                s3_client.upload_file(file_path, bucket_name, s3_file_path)
                logging.info(f"Successfully uploaded {file_path} to s3://{bucket_name}/{s3_file_path}")
            except Exception as e:
                logging.error(f"Failed to upload {file_path}: {e}")


folder_path = 'Z:\OCR outputs\p155_kerby_miller\Letters\ocr_test'
bucket_name = 'nuig-ocr'
s3_folder = 'test_folder'  # Leave this as an empty string if you don't want a folder in S3


upload_folder_to_s3(folder_path, bucket_name, s3_folder)
