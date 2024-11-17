import os
import boto3
from dotenv import load_dotenv
from botocore.exceptions import ClientError

load_dotenv()

# Environment variables
DICTIONARY_SOURCE = os.getenv("DICTIONARY_SOURCE", "local").lower()
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
DICTIONARY_BASE_S3_PATH = os.getenv("DICTIONARY_BASE_S3_PATH", "")
DEFAULT_LANGUAGE = os.getenv("DEFAULT_LANGUAGE", "en")
LOCAL_DICTIONARY_PATH = os.getenv("LOCAL_DICTIONARY_PATH", "./dictionaries/{language}/dictionary.txt")

# Initialize S3 client if needed
s3 = boto3.client("s3") if DICTIONARY_SOURCE == "s3" else None


def get_dictionary(language: str = None) -> list:
    """
    Load the dictionary for the specified language from the appropriate source (local or S3).
    Falls back to the default language if the specified language is not provided.

    Args:
        language (str): The language code (e.g., 'en', 'es').

    Returns:
        list: A list of words from the dictionary.
    """
    language = language or DEFAULT_LANGUAGE

    if DICTIONARY_SOURCE == "s3":
        return _fetch_dictionary_from_s3(language)
    else:
        return _load_local_dictionary(language)


def _fetch_dictionary_from_s3(language: str) -> list:
    """
    Fetch the dictionary for the specified language from S3.

    Args:
        language (str): The language code.

    Returns:
        list: A list of words from the dictionary.
    """
    if not S3_BUCKET_NAME:
        raise ValueError("S3_BUCKET_NAME is not set in the environment.")

    s3_key = f"{DICTIONARY_BASE_S3_PATH}{language}/dictionary.txt"
    try:
        response = s3.get_object(Bucket=S3_BUCKET_NAME, Key=s3_key)
        dictionary_content = response["Body"].read().decode("utf-8")
        return dictionary_content.splitlines()
    except ClientError as e:
        error_code = e.response["Error"]["Code"]
        if error_code == "NoSuchKey":
            raise ValueError(f"Dictionary for language '{language}' not found in S3.")
        else:
            raise RuntimeError(f"Failed to fetch dictionary from S3: {str(e)}")


def _load_local_dictionary(language: str) -> list:
    """
    Load the dictionary for the specified language from a local file.

    Args:
        language (str): The language code.

    Returns:
        list: A list of words from the dictionary.
    """
    # Construct an absolute path for the dictionary
    base_path = os.path.abspath(LOCAL_DICTIONARY_PATH.format(language=language))

    if not os.path.exists(base_path):
        raise ValueError(f"Dictionary for language '{language}' not found at '{base_path}'.")
    
    with open(base_path, "r") as file:
        return file.read().splitlines()
