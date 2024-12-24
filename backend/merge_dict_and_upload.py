import os
import glob
import shutil
import json
import requests
from typing import Any, Dict
from bs4 import BeautifulSoup
from datetime import date
import boto3

# AWS S3 client
s3 = boto3.client("s3")

# Paths and directories
script_dir = os.path.dirname(os.path.abspath(__file__))
temp_dictionary_path = os.path.join(script_dir, "utility", "temp_dictionary.txt")
final_dictionary_path = os.path.join(script_dir, "utility", "dictionary.txt")
dictionaries_dir = os.path.join(script_dir, "dictionaries")
target_directory = os.path.join(script_dir, "dictionaries", "en")

# S3 configuration
S3_SOURCE_BUCKET = {"bucket_name": "chazwinter.com", "prefix": "LetterBoxed/Dictionaries/en/dictionary.txt"}
S3_BUCKETS = [
    {"bucket_name": "chazwinter.com", "prefix": "LetterBoxed/Dictionaries/"},
    {"bucket_name": "test-dictionary-bucket", "prefix": "Dictionaries/"}
]


def clean_word(word):
    """Normalize and clean a word."""
    return word.strip().upper()


def merge_word_lists(output_file, *word_lists):
    """
    Merge multiple word lists into a single cleaned and deduplicated list.
    
    Args:
        output_file (str): Path to the output file.
        *word_lists (list): Lists of words to merge.
    """
    unique_words = set()
    word_count = 0

    for word_list in word_lists:
        if isinstance(word_list, str) and os.path.isfile(word_list):
            # If word_list is a file path, load it
            with open(word_list, 'r') as infile:
                for line in infile:
                    word_count += 1
                    word = clean_word(line)
                    if len(word) >= 3 and word.isalpha():
                        unique_words.add(word)
        elif isinstance(word_list, list):
            # If word_list is a Python list, process it directly
            for word in word_list:
                word_count += 1
                word = clean_word(word)
                if len(word) >= 3 and word.isalpha():
                    unique_words.add(word)
        print(f"Processed {word_count} words from current word list.")
        word_count = 0

    # Write sorted unique words to output file
    with open(output_file, 'w') as outfile:
        for word in sorted(unique_words):
            outfile.write(word + '\n')


def copy_file(source_file, target_file):
    """
    Copy a file to another location.

    Args:
        source_file (str): The path to the source file.
        target_file (str): The path to the target file.
    """
    shutil.copy(source_file, target_file)
    print(f"Copied {source_file} to {target_file}")


def download_s3_file(bucket_name: str, key: str, local_path: str):
    """Download a file from S3."""
    try:
        print(f"Downloading {key} from bucket {bucket_name} to {local_path}")
        s3.download_file(bucket_name, key, local_path)
    except Exception as e:
        print(f"Error downloading {key} from bucket {bucket_name}: {e}")
        raise
    

def upload_dictionaries_to_s3():
    """Upload dictionaries to S3."""
    for bucket in S3_BUCKETS:
        for file_path in glob.glob(f"{dictionaries_dir}/**/*", recursive=True):
            if os.path.isfile(file_path):
                s3_key = f"{bucket['prefix']}{file_path.replace(dictionaries_dir, '').lstrip('/')}"
                print(f"Uploading {file_path} to s3://{bucket['bucket_name']}/{s3_key}")
                s3.upload_file(file_path, bucket["bucket_name"], s3_key)


def fetch_todays_game() -> Dict[str, Any]:
    """
    Fetches today's game data from the New York Times Letter Boxed page.

    Returns:
        dict: A dictionary containing today's game data.

    Raises:
        Exception: If game data cannot be found or parsed from the page.
    """
    url = "https://www.nytimes.com/puzzles/letter-boxed"
    print(f"Getting data from {url}")
    response = requests.get(url)
    response.raise_for_status()  # Raise an error for bad status codes

    soup = BeautifulSoup(response.text, 'html.parser')

    script_tag = soup.find("script", string=lambda s: s and "window.gameData" in s)
    if not script_tag:
        raise Exception("Could not find game data in the page.")
    
    # Extract game data from the JSON
    raw_game_data = script_tag.string.split("=", 1)[1].strip()
    print("Raw game data fetched.")

    # Strip the trailing semicolon from the end of a JavaScript object
    if raw_game_data.endswith(";"):
        raw_game_data = raw_game_data[:-1]

    game_data = json.loads(raw_game_data)

    game_id = game_data["printDate"]
    game_layout = game_data["sides"]

    todays_game = {
        "gameId": game_data["printDate"],
        "gameLayout": game_data["sides"],
        "nytSolution": game_data["ourSolution"],
        "dictionary": game_data["dictionary"],
        "par": str(game_data["par"]),
        "createdBy": game_data.get("editor", ""),
    }
    print(f"Game for {game_id} fetched: {game_layout}")
    return todays_game


def prefetch_nyt_game_for_app():
    """
    Fetch the NYT game data from the specified API endpoint to use in our app.
    Returns the JSON response or raises an exception for errors.
    """
    url = "https://9q2qk2fao1.execute-api.us-east-1.amazonaws.com/prod/prefetch"
    print("Adding today's game to app...")
    try:
        response = requests.get(url)  # Set timeout to 10 seconds
        response.raise_for_status()  # Raise an exception for HTTP errors
        print(response.json())
        return response.json()  # Parse and return JSON response
    except requests.exceptions.RequestException as e:
        print(f"Error fetching NYT game: {e}")
        raise
    

def merge_s3_and_nyt_dictionaries(nyt_dictionary: list):
    """Merge the S3 dictionary and the NYT dictionary."""
    # Step 1: Download the S3 dictionary from the source bucket
    download_s3_file(S3_SOURCE_BUCKET["bucket_name"], S3_SOURCE_BUCKET["prefix"], temp_dictionary_path)

    # Step 2: Merge dictionaries
    merged_temp_path = temp_dictionary_path + ".merged"
    merge_word_lists(
        merged_temp_path,  # New temp file as output
        temp_dictionary_path,  # S3 dictionary
        nyt_dictionary  # NYT dictionary
    )

    # Step 3: Replace the final utility dictionary with the merged result
    shutil.move(merged_temp_path, final_dictionary_path)
    print(f"Merged dictionary saved to {final_dictionary_path}")

    # Step 4: Copy the merged dictionary to the language-specific target directory
    en_target_path = os.path.join(target_directory, "dictionary.txt")
    shutil.copy(final_dictionary_path, en_target_path)
    print(f"Copied merged dictionary to {en_target_path}")


def merge_nyt_dictionary_to_final(nyt_dictionary, temp_dictionary_path, final_dictionary_path):
    """
    Merge the NYT dictionary with the latest dictionary, updating the final dictionary.

    Args:
        nyt_dictionary (list): List of words from the NYT game.
        temp_dictionary_path (str): Path to the temporary dictionary file.
        final_dictionary_path (str): Path to the final dictionary file.
    """
    # Step 1: Copy the final dictionary to the temp dictionary
    copy_file(final_dictionary_path, temp_dictionary_path)

    # Step 2: Create a new temporary output file for the merged result
    merged_temp_path = temp_dictionary_path + ".merged"

    # Step 3: Merge the NYT dictionary with the temp dictionary
    merge_word_lists(
        merged_temp_path,       # New temp file as output
        temp_dictionary_path,   # Existing dictionary words
        nyt_dictionary          # NYT dictionary
    )

    # Step 4: Replace the final dictionary with the merged result
    print(f"Merge complete! Copying merged dictionary to {final_dictionary_path}")
    copy_file(merged_temp_path, final_dictionary_path)

    # Step 5: Clean up temporary merged file
    os.remove(merged_temp_path)
    print(f"Cleaned up temporary file: {merged_temp_path}")


def main():
    """
    Main function to fetch the NYT game, merge its dictionary with the local dictionary,
    and upload all dictionaries to S3.
    """
    # Fetch today's NYT game data
    todays_game = fetch_todays_game()
    nyt_dictionary = todays_game.get("dictionary", [])

    # Merge the S3 dictionary and the NYT dictionary
    merge_s3_and_nyt_dictionaries(nyt_dictionary)

    # Upload the updated dictionaries to all configured S3 buckets
    upload_dictionaries_to_s3()

    # Add the game to the app
    prefetch_nyt_game_for_app()

    print("All tasks completed successfully.")


if __name__ == "__main__":
    main()
