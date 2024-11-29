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
LOCAL_BASIC_DICTIONARY_PATH = os.getenv("LOCAL_BASIC_DICTIONARY_PATH", "./dictionaries/{language}/basic.txt")

# Initialize S3 client if needed
s3 = boto3.client("s3") if DICTIONARY_SOURCE == "s3" else None


def get_dictionary(language: str = DEFAULT_LANGUAGE) -> list[str]:
    """
    Load the (full) dictionary for the specified language from the appropriate source (local or S3).
    Falls back to the default language if the specified language is not provided.

    Args:
        language (str): The language code (e.g., 'en', 'es').

    Returns:
        list[str]: A list of words from the dictionary.
    """
    return _load_dictionary(language, "dictionary")


def get_basic_dictionary(language: str = DEFAULT_LANGUAGE) -> list[str]:
    """
    Load the (basic) dictionary for the specified language from the appropriate source (local or S3).
    Falls back to the default language if the specified language is not provided.

    Args:
        language (str): The language code (e.g., 'en', 'es').

    Returns:
        list[str]: A list of words from the basic dictionary.
    """
    return _load_dictionary(language, "basic")


def _load_dictionary(language: str, dictionary_type: str) -> list[str]:
    """
    Generic function to load a dictionary of a specified type.

    Args:
        language (str): The language code (e.g., 'en', 'es').
        dictionary_type (str): The type of dictionary to load ('dictionary', 'basic', etc.).

    Returns:
        list[str]: A list of words from the specified dictionary.
    """
    if DICTIONARY_SOURCE == "s3":
        print(f"Fetching dictionary from S3: {language}:{dictionary_type}")
        dictionary = _fetch_dictionary_from_s3(language, dictionary_type)
    else:
        print(f"Loading local dictionary for {language}:{dictionary_type}")
        dictionary = _load_local_dictionary(language, dictionary_type)
     
    return dictionary


def _fetch_dictionary_from_s3(language: str, dictionary_type: str) -> list[str]:
    """
    Fetch a dictionary of a specified type for the given language from S3.

    Args:
        language (str): The language code.
        dictionary_type (str): The type of dictionary to fetch ('dictionary', 'basic', etc.).

    Returns:
        list[str]: A list of words from the dictionary.
    """
    s3_bucket_name = os.getenv("S3_BUCKET_NAME")
    s3_base_path = os.getenv("DICTIONARY_BASE_S3_PATH", "")

    if not s3_bucket_name:
        raise ValueError("S3_BUCKET_NAME is not set in the environment.")

    if not s3:
        raise RuntimeError("boto3 failed to initialize S3 client.")

    s3_key = f"{s3_base_path}{language}/{dictionary_type}.txt"
    try:
        response = s3.get_object(Bucket=s3_bucket_name, Key=s3_key)
        body = response["Body"].read()
        if not isinstance(body, bytes):
            raise TypeError("Unexpected response type: 'Body.read()' did not return bytes.")
        dictionary_content = body.decode("utf-8")
        if not isinstance(dictionary_content, str):
            raise TypeError("Unexpected response type: Decoded content is not a string.")
        return [line.strip().upper() for line in dictionary_content.splitlines()]
    except ClientError as e:
        if e.response["Error"]["Code"] == "NoSuchKey":
            raise ValueError(f"Dictionary '{dictionary_type}.txt' for language '{language}' not found in S3.") from e
        raise RuntimeError(f"Error fetching dictionary from S3: {e}") from e
    except KeyError as e:
        raise ValueError(f"Unexpected response structure from S3: {e}") from e


def _load_local_dictionary(language: str, dictionary_type: str) -> list[str]:
    """
    Load a dictionary of a specified type for the given language from a local file.

    Args:
        language (str): The language code.
        dictionary_type (str): The type of dictionary to load ('dictionary', 'basic', etc.).

    Returns:
        list[str]: A list of words from the dictionary.
    """
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Construct the path relative to the script directory
    dictionary_path = os.path.join(script_dir, '..', '..', 'dictionaries', language, f'{dictionary_type}.txt')

    # Normalize the path
    dictionary_path = os.path.normpath(dictionary_path)

    if not os.path.exists(dictionary_path):
        raise ValueError(f"Dictionary '{dictionary_type}' for language '{language}' not found at '{dictionary_path}'.")
    
    with open(dictionary_path, "r") as file:
        return [word.strip().upper() for word in file.readlines()]
