import sys
import os
import boto3
import json
import pytest
import constants as c

from lambdas.create_custom import handler as create_custom_handler
from lambdas.create_random import handler as create_random_handler, random_game_service
from lambdas.fetch_game import handler as fetch_game_handler
from lambdas.fetch_random import handler as fetch_random_handler
from lambdas.fetch_user_state import handler as fetch_user_state_handler
from lambdas.game_archive import handler as game_archive_handler
from lambdas.get_solutions import handler as get_solutions_handler
from lambdas.play_today import handler as play_today_handler
from lambdas.prefetch_todays_game import handler as prefetch_todays_game_handler, prefetch_service
from lambdas.save_user_state import handler as save_user_state_handler
from lambdas.validate_word import handler as validate_word_handler, word_validator_service
from lambdas.common import (
    db_utils,
    dictionary_utils,
    game_schema,
    game_utils
)
from lambdas.common.game_schema import create_game_schema


def create_custom_missing_layout(aws_clients):
    """
    Test create_custom flow with a missing game layout.
    This should return a 400 status code and ensure no game is added to the database.
    """
    dynamodb = aws_clients["dynamodb"]

    response = create_custom_handler.handler(c.CREATE_CUSTOM_EVENT_MISSING_LAYOUT, None)

    assert response["statusCode"] == 400, f"Expected 400, got {response['statusCode']}"
    assert "Game Layout is required" in response["body"], f"Unexpected body: {response['body']}"

    # Since there's no game ID, we check that the DB has not been updated at all.
    assert_table_is_empty(dynamodb, os.environ["GAMES_TABLE"])
    assert_table_is_empty(dynamodb, os.environ["VALID_WORDS_TABLE"])


def create_custom_invalid_layout(aws_clients):
    """
    Test create_custom flow with an invalid layout.
    This should return a 400 status code and ensure no game is added to the database.
    """
    dynamodb = aws_clients["dynamodb"]

    # Call the create_custom handler directly with the invalid payload
    from lambdas.create_custom.handler import handler  # Import the handler function
    try:
        response = handler(c.CREATE_CUSTOM_EVENT_INVALID_LAYOUT, None)
    except ValueError as e:
        print(f"ValueError raised as expected: {str(e)}")
        assert "Invalid game layout" in str(e), "Expected ValueError for invalid board layout"

    # Verify the response
    assert response["statusCode"] == 400, f"Expected 400 status code, got {response['statusCode']}"
    response_body = json.loads(response["body"])
    assert "message" in response_body, "Expected a 'message' key in the response body"
    print(f"Response message: {response_body['message']}")

    # Verify no game was added to the database
    assert_table_is_empty(dynamodb, os.environ["GAMES_TABLE"])
    assert_table_is_empty(dynamodb, os.environ["VALID_WORDS_TABLE"])


def create_custom_size_mismatch(aws_clients):
    """
    Test create_custom flow with a size mismatch between boardSize and gameLayout.
    This should return a 400 status code and ensure no game is added to the database.
    """
    dynamodb = aws_clients["dynamodb"]

    # Call the create_custom handler directly with the size mismatch payload
    from lambdas.create_custom.handler import handler  # Import the handler function
    try:
        response = handler(c.CREATE_CUSTOM_EVENT_SIZE_MISMATCH, None)
    except ValueError as e:
        print(f"ValueError raised as expected: {str(e)}")
        assert "Size mismatch" in str(e), "Expected ValueError for board size mismatch"

    # Verify the response
    assert response["statusCode"] == 400, f"Expected 400 status code, got {response['statusCode']}"
    response_body = json.loads(response["body"])
    assert "message" in response_body, "Expected a 'message' key in the response body"
    print(f"Response message: {response_body['message']}")

    # Verify no game was added to the database
    assert_table_is_empty(dynamodb, os.environ["GAMES_TABLE"])
    assert_table_is_empty(dynamodb, os.environ["VALID_WORDS_TABLE"])


def create_custom_unsupported_language(aws_clients):
    """
    Test create_custom flow with an unsupported language.
    This should return a 400 status code and ensure no game is added to the database.
    """
    dynamodb = aws_clients["dynamodb"]

    # Call the create_custom handler directly with the unsupported language payload
    from lambdas.create_custom.handler import handler  # Import the handler function
    try:
        response = handler(c.CREATE_CUSTOM_EVENT_UNSUPPORTED_LANGUAGE, None)
    except ValueError as e:
        print(f"ValueError raised as expected: {str(e)}")
        assert "Unsupported language" in str(e), "Expected ValueError for unsupported language"

    # Verify the response
    assert response["statusCode"] == 400, f"Expected 400 status code, got {response['statusCode']}"
    response_body = json.loads(response["body"])
    assert "message" in response_body, "Expected a 'message' key in the response body"
    print(f"Response message: {response_body['message']}")

    # Verify no game was added to the database
    assert_table_is_empty(dynamodb, os.environ["GAMES_TABLE"])
    assert_table_is_empty(dynamodb, os.environ["VALID_WORDS_TABLE"])


def create_custom_malformed_json(aws_clients):
    """
    Test create_custom flow with a malformed JSON payload.
    This should return a 400 status code and ensure no game is added to the database.
    """
    dynamodb = aws_clients["dynamodb"]

    # Call the create_custom handler directly with the malformed JSON payload
    from lambdas.create_custom.handler import handler  # Import the handler function
    try:
        response = handler(c.CREATE_CUSTOM_EVENT_MALFORMED_JSON, None)
    except json.JSONDecodeError as e:
        print(f"JSONDecodeError raised as expected: {str(e)}")
        assert "Expecting property name enclosed in double quotes" in str(e), "Expected JSONDecodeError for malformed JSON"

    # Verify the response
    assert response["statusCode"] == 400, f"Expected 400 status code, got {response['statusCode']}"
    response_body = json.loads(response["body"])
    assert "message" in response_body, "Expected a 'message' key in the response body"
    print(f"Response message: {response_body['message']}")

    # Verify no game was added to the database
    assert_table_is_empty(dynamodb, os.environ["GAMES_TABLE"])
    assert_table_is_empty(dynamodb, os.environ["VALID_WORDS_TABLE"])


def create_custom_english_game(aws_clients):
    """
    Test create_custom flow with a valid 3x3 layout in English.
    This should return a 200 status code, ensure the game is added to the database,
    and validate that the game can be fetched.
    """


def create_custom_spanish_game(aws_clients):
    """
    Test create_custom flow with a valid 3x3 layout in Spanish.
    This should return a 200 status code, ensure the game is added to the database,
    and validate that the game can be fetched.
    """


def create_custom_4x4_game(aws_clients):
    """
    Test create_custom flow with a valid 4x4 layout.
    This should return a 200 status code, ensure the game is added to the database,
    and validate that the game can be fetched.
    """




# ===================================================================
# Assertions related to DB Tables and specific function calls
# ===================================================================
def assert_game_not_in_db(game_id: str, dynamodb):
    """
    Verify that the game with the given ID does not exist in the database.
    """
    game = db_utils.fetch_game_by_id(game_id)
    assert game is None, f"Game with ID {game_id} should not exist in the DB."

def assert_game_in_db(game_id: str, dynamodb):
    """
    Verify that the game with the given ID exists in the database.
    """
    game = db_utils.fetch_game_by_id(game_id)
    assert game is not None, f"Game with ID {game_id} should exist in the DB."
    print(f"Verified game with ID {game_id} exists in the DB.")

def assert_valid_words_not_in_db(game_id: str, dynamodb):
    """
    Verify that valid words for the given game ID do not exist in the database.
    """
    words = db_utils.fetch_valid_words_by_game_id(game_id)
    assert words is None, f"Valid words for game ID {game_id} should not exist in the DB."


def assert_valid_words_in_db(game_id: str, dynamodb):
    """
    Verify that valid words for the given game ID exist in the database.
    """
    words = db_utils.fetch_valid_words_by_game_id(game_id)
    assert words is not None, f"Valid words for game ID {game_id} should exist in the DB."
    print(f"Verified valid words for game ID {game_id} exist in the DB.")


def assert_user_game_state_not_in_db(session_id: str, game_id: str, dynamodb):
    """
    Verify that the user game state for the given session and game ID does not exist in the database.
    """
    state = db_utils.get_user_game_state(session_id, game_id)
    assert state is None, f"User game state for session ID {session_id} and game ID {game_id} should not exist in the DB."


def assert_user_game_state_in_db(session_id: str, game_id: str, dynamodb):
    """
    Verify that the user game state for the given session and game ID exists in the database.
    """
    state = db_utils.get_user_game_state(session_id, game_id)
    assert state is not None, f"User game state for session ID {session_id} and game ID {game_id} should exist in the DB."
    print(f"Verified user game state for session ID {session_id} and game ID {game_id} exists in the DB.")


def assert_random_game_not_in_db(atomic_number: int, dynamodb):
    """
    Verify that a random game with the given atomic number does not exist in the random games table.
    """
    table = db_utils.get_random_games_table()
    response = table.get_item(Key={"atomicNumber": atomic_number})
    assert "Item" not in response, f"Random game with atomic number {atomic_number} should not exist in the DB."


def assert_random_game_in_db(atomic_number: int, dynamodb):
    """
    Verify that a random game with the given atomic number exists in the random games table.
    """
    table = db_utils.get_random_games_table()
    response = table.get_item(Key={"atomicNumber": atomic_number})
    assert "Item" in response, f"Random game with atomic number {atomic_number} should exist in the DB."
    print(f"Verified random game with atomic number {atomic_number} exists in the DB.")


def assert_archived_games_not_in_db(game_id: str, dynamodb):
    """
    Verify that the archived game with the given game ID does not exist in the archive table.
    """
    games = db_utils.fetch_archived_games(limit=1, last_key={"gameId": game_id})
    assert not any(game["gameId"] == game_id for game in games["items"]), f"Archived game with ID {game_id} should not exist in the DB."


def assert_archived_games_in_db(game_id: str, dynamodb):
    """
    Verify that the archived game with the given game ID exists in the archive table.
    """
    games = db_utils.fetch_archived_games(limit=1, last_key={"gameId": game_id})
    assert any(game["gameId"] == game_id for game in games["items"]), f"Archived game with ID {game_id} should exist in the DB."
    print(f"Verified archived game with ID {game_id} exists in the DB.")


def assert_random_game_count_equals(expected_count: int, dynamodb):
    """
    Verify that the random game count matches the expected value.
    """
    count = db_utils.fetch_random_game_count()
    assert count == expected_count, f"Random game count should be {expected_count} but is {count}."
    print(f"Verified random game count is {count}.")

def assert_table_is_empty(dynamodb, table_name):
    table = dynamodb.Table(table_name)
    print(f"Verifying {table_name} is empty...")
    scan = table.scan()
    assert scan["Count"] == 0, f"Table {table_name} is not empty. Found items: {scan['Items']}"
