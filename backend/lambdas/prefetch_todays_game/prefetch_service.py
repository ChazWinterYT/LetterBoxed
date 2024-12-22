import os
import json
import requests
from typing import Any, Dict
from bs4 import BeautifulSoup
from boto3 import client
from lambdas.common.db_utils import fetch_game_by_id


# S3 configuration
s3 = client("s3")
s3_buckets = [
    {"bucket_name": "chazwinter.com", "prefix": "LetterBoxed/Dictionaries/en/"},
    {"bucket_name": "test-dictionary-bucket", "prefix": "Dictionaries/en/"}
]


def fetch_todays_game() -> Dict[str, Any]:
    """
    Fetches today's game data from the New York Times Letter Boxed page.

    Returns:
        dict: A dictionary containing today's game data.

    Raises:
        Exception: If game data cannot be found or parsed from the page.
    """
    url = "https://www.nytimes.com/puzzles/letter-boxed"
    response = requests.get(url)
    response.raise_for_status() # Raise an error for bad status codes

    soup = BeautifulSoup(response.text, 'html.parser')

    script_tag = soup.find("script", string=lambda s: s and "window.gameData" in s)
    if not script_tag:
        raise Exception("Could not find game data in the page.")
    
    # Extract game data from the JSON
    raw_game_data = script_tag.string.split("=", 1)[1].strip()

    # Strip the trailing semicolon from the end of a JavaScript object
    if raw_game_data.endswith(";"):
        raw_game_data = raw_game_data[:-1]

    game_data = json.loads(raw_game_data)

    todays_game = {
        "gameId": game_data["printDate"],
        "gameLayout": game_data["sides"],
        "nytSolution": game_data["ourSolution"],
        "dictionary": game_data["dictionary"],
        "par": str(game_data["par"]),
        "createdBy": game_data.get("editor", ""),
    }

    # Merge the NYT dictionary with the existing S3 dictionary
    for bucket in s3_buckets:
        merge_nyt_dictionary_to_final(
            nyt_dictionary=todays_game["dictionary"],
            s3_bucket=bucket["bucket_name"],
            s3_key=f"{bucket['prefix']}dictionary.txt"
        )

    return todays_game


def game_exists_in_db(game_id: str) -> bool:
    """
    Checks if a game with the given gameId exists in the database.

    Args:
        game_id (str): The unique identifier of the game.

    Returns:
        bool: True if the game exists, False otherwise.
    """
    return fetch_game_by_id(game_id) is not None


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


def merge_nyt_dictionary_to_final(nyt_dictionary: list, s3_bucket: str, s3_key: str):
    """
    Merge the NYT dictionary with the latest dictionary from S3, 
    and upload the updated dictionary back to S3.

    Args:
        nyt_dictionary (list): List of words from the NYT game.
        s3_bucket (str): Name of the S3 bucket.
        s3_key (str): Key for the dictionary file in S3.
    """
    # Step 1: Download the existing dictionary from S3 to a temporary file
    temp_local_path = "/tmp/temp_dictionary.txt"
    try:
        print(f"Downloading dictionary from s3://{s3_bucket}/{s3_key}...")
        s3.download_file(s3_bucket, s3_key, temp_local_path)
        print("Download complete.")
    except s3.exceptions.ClientError as e:
        if e.response["Error"]["Code"] == "NoSuchKey":
            print(f"No existing dictionary found at {s3_key}. Starting fresh.")
            open(temp_local_path, "w").close()  # Create an empty file
        else:
            raise

    # Step 2: Create a new temporary output file for the merged result
    merged_temp_path = "/tmp/merged_dictionary.txt"

    # Step 3: Merge the NYT dictionary with the S3 dictionary
    merge_word_lists(
        merged_temp_path,       # New merged file as output
        temp_local_path,        # Existing dictionary from S3
        nyt_dictionary          # NYT dictionary
    )

    # Step 4: Upload the merged dictionary back to S3
    print(f"Uploading merged dictionary to s3://{s3_bucket}/{s3_key}...")
    s3.upload_file(merged_temp_path, s3_bucket, s3_key)
    print("Upload complete.")

    # Step 5: Clean up temporary files
    os.remove(temp_local_path)
    os.remove(merged_temp_path)
    print(f"Temporary files cleaned up: {temp_local_path}, {merged_temp_path}")
