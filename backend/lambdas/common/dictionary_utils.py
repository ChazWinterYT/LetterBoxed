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


def get_dictionary(language: str = DEFAULT_LANGUAGE) -> list[str]:
    """
    Load the dictionary for the specified language from the appropriate source (local or S3).
    Falls back to the default language if the specified language is not provided.

    Args:
        language (str): The language code (e.g., 'en', 'es').

    Returns:
        list[str]: A list of words from the dictionary.
    """
    if DICTIONARY_SOURCE == "s3":
        return _fetch_dictionary_from_s3(language)
    else:
        return _load_local_dictionary(language)


def _fetch_dictionary_from_s3(language: str) -> list[str]:
    """
    Fetch the dictionary for the specified language from S3.

    Args:
        language (str): The language code.

    Returns:
        list[str]: A list of words from the dictionary.
    """
    if not S3_BUCKET_NAME:
        raise ValueError("S3_BUCKET_NAME is not set in the environment.")

    if not s3:
        raise RuntimeError("boto3 failed to initialize s3 client.")

    s3_key = f"{DICTIONARY_BASE_S3_PATH}{language}/dictionary.txt"
    try:
        response = s3.get_object(Bucket=S3_BUCKET_NAME, Key=s3_key)
        body = response["Body"].read()
        if not isinstance(body, bytes):
            raise TypeError("Unexpected response type: 'Body.read()' did not return bytes.")
        dictionary_content = body.decode("utf-8")
        if not isinstance(dictionary_content, str):
            raise TypeError("Unexpected response type: Decoded content is not a string.")
        return dictionary_content.splitlines()
    except KeyError as e:
        raise ValueError(f"Unexpected response structure from S3: {e}") from e
    except Exception as e:
        raise RuntimeError(f"Error fetching dictionary from S3: {e}") from e


def _load_local_dictionary(language: str) -> list[str]:
    """
    Load the dictionary for the specified language from a local file.

    Args:
        language (str): The language code.

    Returns:
        list[str]: A list of words from the dictionary.
    """
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Construct the path relative to the script directory
    dictionary_path = os.path.join(script_dir, '..', '..', 'dictionaries', language, 'dictionary.txt')

    # Normalize the path
    dictionary_path = os.path.normpath(dictionary_path)

    if not os.path.exists(dictionary_path):
        raise ValueError(f"Dictionary for language '{language}' not found at '{dictionary_path}'.")
    
    with open(dictionary_path, "r") as file:
        return [word.strip().upper() for word in file.readlines()]
