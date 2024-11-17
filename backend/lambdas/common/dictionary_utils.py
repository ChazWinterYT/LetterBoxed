import os
import boto3
from dotenv import load_dotenv

load_dotenv()

S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
DICTIONARY_BASE_PATH = os.getenv("DICTIONARY_BASE_PATH")
DEFAULT_LANGUAGE = os.getenv("DEFAULT_LANGUAGE", "en")

s3 = boto3.client("s3")


def get_dictionary(language: str = None) -> list:
    """
    Fetch the dictionary for the specified language from S3.
    Falls back to the default language if the specified language is not provided.

    Args:
        language (str): The language code (e.g., 'en', 'es').

    Returns:
        list: A list of words from the dictionary.
    """
    if not language:
        language = DEFAULT_LANGUAGE

    s3_key = f"{DICTIONARY_BASE_PATH}{language}/dictionary.txt"

    try:
        response = s3.get_object(Bucket=S3_BUCKET_NAME, Key=s3_key)
        dictionary_content = response["Body"].read().decode("utf-8")
        return dictionary_content.splitlines()
    except s3.exceptions.NoSuchKey:
        raise ValueError(f"Dictionary for language '{language}' not found in S3.")
    

def fetch_dictionary_from_s3(bucket_name, object_key):
    """
    Get the specified dictionary file from the specified S3 bucket
    """
    response = s3.get_object(Bucket=bucket_name, Key=object_key)
    return response['Body'].read().decode('utf-8').splitlines()


def load_dictionary():
    """
    Loads the dictionary file from S3 (production) or local file (development/testing).
    """
    dictionary_source = os.getenv("DICTIONARY_SOURCE", "local") # Default to local

    if dictionary_source == "s3":
        bucket_name = os.getenv("S3_BUCKET_NAME")
        object_key = os.getenv("DICTIONARY_S3_KEY")
        return fetch_dictionary_from_s3(bucket_name, object_key)
    else:
        local_path = os.getenv("LOCAL_DICTIONARY_PATH")
        with open(local_path, "r") as file:
            return file.read().splitlines()
        