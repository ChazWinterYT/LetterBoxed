import boto3
import glob
import os
import hashlib

s3 = boto3.client("s3")

def calculate_md5(file_path):
    """Calculate the MD5 hash of a local file."""
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def file_needs_upload(file_path, bucket_name, s3_key):
    """
    Check if the file in the local directory needs to be uploaded to S3.
    Compare MD5 checksum of the local file and the S3 object ETag.
    """
    try:
        response = s3.head_object(Bucket=bucket_name, Key=s3_key)
        s3_etag = response["ETag"].strip('"')  # S3 ETag includes quotes
        local_md5 = calculate_md5(file_path)
        return local_md5 != s3_etag
    except s3.exceptions.ClientError:
        # File does not exist in S3
        return True

bucket_names = ["chazwinter.com", "test-dictionary-bucket"]
s3_key_prefixes = ["LetterBoxed/Dictionaries/", "Dictionaries/"]
dictionaries_dir = os.path.join(os.getcwd(), "dictionaries")

for bucket_name, s3_key_prefix in zip(bucket_names, s3_key_prefixes):
    for file_path in glob.glob(f"{dictionaries_dir}/**/*", recursive=True):
        if os.path.isfile(file_path):
            s3_key = f"{s3_key_prefix}{file_path.replace(dictionaries_dir, '').lstrip('/')}"
            if file_needs_upload(file_path, bucket_name, s3_key):
                print(f"Uploading {file_path} \nto s3://{bucket_name}/{s3_key}")
                s3.upload_file(file_path, bucket_name, s3_key)
            else:
                print(f"Skipping {file_path} \nas it is identical to the S3 object.")
