import json
import os
import boto3
import requests
from lambdas.prefetch_todays_game.prefetch_service import fetch_todays_game

s3 = boto3.client("s3")
sns = boto3.client("sns")

S3_SOURCE_BUCKET = "chazwinter.com"
S3_DICT_KEY = "LetterBoxed/Dictionaries/en/dictionary.txt"
S3_UPLOAD_TARGETS = [
    {"bucket": "chazwinter.com", "key": "LetterBoxed/Dictionaries/en/dictionary.txt"},
    {"bucket": "test-dictionary-bucket", "key": "Dictionaries/en/dictionary.txt"},
]

PREFETCH_API_URL = "https://9q2qk2fao1.execute-api.us-east-1.amazonaws.com/prod/prefetch"
SNS_TOPIC_ARN = os.environ.get("SNS_TOPIC_ARN", "")
TEMP_DICT_PATH = "/tmp/dictionary.txt"


def _clean_word(word):
    return word.strip().upper()


def _merge_nyt_words_into_dictionary(nyt_words):
    """
    Reads the downloaded dictionary from TEMP_DICT_PATH, merges in the NYT words,
    and writes the result back to the same path.
    Returns the total word count after merging.
    """
    unique_words = set()
    with open(TEMP_DICT_PATH, "r") as f:
        for line in f:
            word = _clean_word(line)
            if len(word) >= 3 and word.isalpha():
                unique_words.add(word)

    for word in nyt_words:
        word = _clean_word(word)
        if len(word) >= 3 and word.isalpha():
            unique_words.add(word)

    with open(TEMP_DICT_PATH, "w") as f:
        for word in sorted(unique_words):
            f.write(word + "\n")

    return len(unique_words)


def _notify(subject, body):
    print(body)
    if SNS_TOPIC_ARN:
        try:
            sns.publish(TopicArn=SNS_TOPIC_ARN, Subject=subject, Message=body)
        except Exception as e:
            print(f"SNS publish failed: {e}")


def handler(event, context):
    messages = []

    try:
        # Step 1: Fetch today's NYT game
        todays_game = fetch_todays_game()
        nyt_dictionary = todays_game.get("dictionary", [])
        game_id = todays_game["gameId"]
        messages.append(f"Fetched NYT game: {game_id} ({len(nyt_dictionary)} words in NYT dictionary)")

        # Step 2: Download the existing dictionary from S3
        s3.download_file(S3_SOURCE_BUCKET, S3_DICT_KEY, TEMP_DICT_PATH)
        messages.append(f"Downloaded s3://{S3_SOURCE_BUCKET}/{S3_DICT_KEY}")

        # Step 3: Merge NYT words into the dictionary
        word_count = _merge_nyt_words_into_dictionary(nyt_dictionary)
        messages.append(f"Merged dictionary has {word_count} unique words")

        # Step 4: Upload merged dictionary to all target buckets
        for target in S3_UPLOAD_TARGETS:
            s3.upload_file(TEMP_DICT_PATH, target["bucket"], target["key"])
            messages.append(f"Uploaded to s3://{target['bucket']}/{target['key']}")

        # Step 5: Trigger the prefetch endpoint to load today's game into DynamoDB
        prefetch_response = requests.get(PREFETCH_API_URL, timeout=30)
        prefetch_response.raise_for_status()
        prefetch_result = prefetch_response.json()
        messages.append(f"Prefetch result: {prefetch_result}")

        summary = "\n".join(messages)
        _notify(f"Daily LetterBoxed Update Complete: {game_id}", summary)

        return {
            "statusCode": 200,
            "body": json.dumps({"message": "Daily update complete", "gameId": game_id})
        }

    except Exception as e:
        error_body = f"Daily update FAILED: {str(e)}\n\nCompleted steps:\n" + "\n".join(messages)
        _notify("Daily LetterBoxed Update FAILED", error_body)
        raise
