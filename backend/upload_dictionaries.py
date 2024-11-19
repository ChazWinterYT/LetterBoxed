import boto3
import glob
import os

s3 = boto3.client("s3")

bucket_name = "chazwinter.com"
s3_key_prefix = "LetterBoxed/Dictionaries/"
dictionaries_dir = os.path.join(os.getcwd(), "dictionaries")

for file_path in glob.glob(f"{dictionaries_dir}/**/*", recursive=True):
    if os.path.isfile(file_path):
        s3_key = f"{s3_key_prefix}{file_path.replace(dictionaries_dir, '').lstrip('/')}"
        print(f"Uploading {file_path} to s3://{bucket_name}/{s3_key}")
        s3.upload_file(file_path, bucket_name, s3_key)

# Upload to test bucket too
bucket_name = "test-dictionary-bucket"
s3_key_prefix = "Dictionaries/"

for file_path in glob.glob(f"{dictionaries_dir}/**/*", recursive=True):
    if os.path.isfile(file_path):
        s3_key = f"{s3_key_prefix}{file_path.replace(dictionaries_dir, '').lstrip('/')}"
        print(f"Uploading {file_path} to s3://{bucket_name}/{s3_key}")
        s3.upload_file(file_path, bucket_name, s3_key)
        