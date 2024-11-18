import json
import os
import boto3

dynamodb = boto3.resource('dynamodb')
valid_words_table_name = os.environ['VALID_WORDS_TABLE']
user_game_states_table_name = os.environ['USER_GAME_STATES_TABLE']

valid_words_table = dynamodb.Table(valid_words_table_name)
user_game_states_table = dynamodb.Table(user_game_states_table_name)

def handler(event, context):
    """
    Check the validity of a word
    """
    word = event.get("word")
    is_valid = True # Placeholder
    return {
        "statusCode": 200,
        "body": json.dumps({
            "word": word,
            "isValid": is_valid
        })
    }