import sys
import os
import time
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


# ===================================================================
# Create Custom Lambda Tests
# ===================================================================
def create_custom_missing_layout(aws_clients):
    """
    Test create_custom flow with a missing game layout.
    This should return a 400 status code and ensure no game is added to the database.
    """
    dynamodb = aws_clients["dynamodb"]

    from lambdas.create_custom.handler import handler  # Import the handler function
    response = handler(c.CREATE_CUSTOM_EVENT_MISSING_LAYOUT, None)

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
    try:
        from lambdas.create_custom.handler import handler  # Import the handler function
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
    try:
        from lambdas.create_custom.handler import handler  # Import the handler function
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
    try:
        from lambdas.create_custom.handler import handler  # Import the handler function
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
    try:
        from lambdas.create_custom.handler import handler  # Import the handler function
        response = handler(c.CREATE_CUSTOM_EVENT_MALFORMED_JSON, None)
    except json.JSONDecodeError as e:
        print(f"JSONDecodeError raised as expected: {str(e)}")
        assert (
            "Expecting property name enclosed in double quotes" in str(e)
        ), "Expected JSONDecodeError for malformed JSON"
        
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
    Return the game_id so it can be used for further integration tests.
    This should return a 200 status code, ensure the game is added to the database,
    and validate that the game can be fetched.
    """
    dynamodb = aws_clients["dynamodb"]

    # Call the create_custom handler directly with the valid English payload
    from lambdas.create_custom.handler import handler  # Import the handler function
    response = handler(c.CREATE_CUSTOM_EVENT_VALID_EN, None)

    # Verify the response
    assert response["statusCode"] == 201, f"Expected 200 status code, got {response['statusCode']}"
    response_body = json.loads(response["body"])
    assert "gameId" in response_body, "Expected a 'gameId' key in the response body"
    assert response_body["message"] == "Game created successfully.", "Expected success message in the response body"
    game_id = response_body["gameId"]
    print(f"Successfully created game with ID {game_id}")

    # Verify the game exists in the database
    assert_game_in_db(game_id, dynamodb)
    assert_valid_words_in_db(game_id, dynamodb)

    # Fetch the game and verify its details
    fetched_game = db_utils.fetch_game_by_id(game_id)
    assert fetched_game is not None, "Game should exist in the database"
    assert fetched_game["twoWordSolutions"] is not None, "Two-word solutions should be calculated"
    assert fetched_game["gameLayout"] == c.VALID_GAME_LAYOUT_EN, "Game layout does not match expected layout"
    assert fetched_game["language"] == "en", "Game language does not match expected language"
    assert fetched_game["boardSize"] == "3x3", "Game board size does not match expected size"

    # Return the gameId for further tests
    print(f"Successfully created English game with ID {game_id}.")
    return game_id


def create_custom_spanish_game(aws_clients):
    """
    Test create_custom flow with a valid 3x3 layout in Spanish.
    This should return a 200 status code, ensure the game is added to the database,
    and validate that the game can be fetched.
    """
    dynamodb = aws_clients["dynamodb"]

    # Call the create_custom handler directly with the valid Spanish payload
    from lambdas.create_custom.handler import handler  # Import the handler function
    response = handler(c.CREATE_CUSTOM_EVENT_VALID_ES, None)

    # Verify the response
    assert response["statusCode"] == 201, f"Expected 200 status code, got {response['statusCode']}"
    response_body = json.loads(response["body"])
    assert "gameId" in response_body, "Expected 'gameId' in the response body"
    game_id = response_body["gameId"]
    print(f"Response gameId: {game_id}")

    # Verify the game was added to the database
    assert_game_in_db(game_id, dynamodb)
    assert_valid_words_in_db(game_id, dynamodb)

    # Fetch the game and validate the details
    fetched_game = db_utils.fetch_game_by_id(game_id)
    assert fetched_game is not None, f"Game with ID {game_id} should exist in the database"
    assert fetched_game["twoWordSolutions"] is not None, "Two-word solutions should be calculated"
    assert fetched_game["gameLayout"] == c.VALID_GAME_LAYOUT_ES, "Game layout does not match expected layout"
    assert fetched_game["language"] == "es", "Expected game language to be Spanish ('es')"
    assert fetched_game["boardSize"] == "3x3", "Expected game board size to be '3x3'"

    print(f"Successfully created and verified Spanish game with ID {game_id}.")


def create_custom_4x4_game_english(aws_clients):
    """
    Test create_custom flow with a valid 4x4 layout.
    This should return a 200 status code, ensure the game is added to the database,
    and validate that the game can be fetched.
    """
    dynamodb = aws_clients["dynamodb"]

    # Call the create_custom handler directly with the valid 4x4 payload
    from lambdas.create_custom.handler import handler  # Import the handler function
    response = handler(c.CREATE_CUSTOM_EVENT_VALID_LARGE_EN, None)

    # Verify the response
    assert response["statusCode"] == 201, f"Expected 200 status code, got {response['statusCode']}"
    response_body = json.loads(response["body"])
    assert "gameId" in response_body, "Expected 'gameId' in the response body"
    game_id = response_body["gameId"]
    print(f"Response gameId: {game_id}")

    # Verify the game was added to the database
    assert_game_in_db(game_id, dynamodb)
    assert_valid_words_in_db(game_id, dynamodb)

    # Fetch the game and validate the details
    fetched_game = db_utils.fetch_game_by_id(game_id)
    assert fetched_game is not None, f"Game with ID {game_id} should exist in the database"
    assert fetched_game["twoWordSolutions"] is not None, "Two-word solutions should be calculated"
    assert fetched_game["gameLayout"] == c.VALID_GAME_LAYOUT_4x4_EN, "Game layout does not match expected layout"
    assert fetched_game["language"] == "en", "Expected game language to be English ('en')"
    assert fetched_game["boardSize"] == "4x4", "Expected game board size to be '4x4'"

    print(f"Successfully created and verified 4x4 game with ID {game_id}.")


def create_custom_4x4_game_spanish(aws_clients):
    """
    Test create_custom flow with a valid 4x4 layout.
    This should return a 200 status code, ensure the game is added to the database,
    and validate that the game can be fetched.
    """
    dynamodb = aws_clients["dynamodb"]

    # Call the create_custom handler directly with the valid 4x4 payload
    from lambdas.create_custom.handler import handler  # Import the handler function
    response = handler(c.CREATE_CUSTOM_EVENT_VALID_LARGE_ES, None)

    # Verify the response
    assert response["statusCode"] == 201, f"Expected 200 status code, got {response['statusCode']}"
    response_body = json.loads(response["body"])
    assert "gameId" in response_body, "Expected 'gameId' in the response body"
    game_id = response_body["gameId"]
    print(f"Response gameId: {game_id}")

    # Verify the game was added to the database
    assert_game_in_db(game_id, dynamodb)
    assert_valid_words_in_db(game_id, dynamodb)

    # Fetch the game and validate the details
    fetched_game = db_utils.fetch_game_by_id(game_id)
    assert fetched_game is not None, f"Game with ID {game_id} should exist in the database"
    assert fetched_game["twoWordSolutions"] is not None, "Two-word solutions should be calculated"
    assert fetched_game["gameLayout"] == c.VALID_GAME_LAYOUT_4x4_ES, "Game layout does not match expected layout"
    assert fetched_game["language"] == "es", "Expected game language to be Spanish ('es')"
    assert fetched_game["boardSize"] == "4x4", "Expected game board size to be '4x4'"

    print(f"Successfully created and verified 4x4 game with ID {game_id}.")


# ===================================================================
# Create Random lambda tests
# ===================================================================
def create_random_valid_en(aws_clients):
    """
    Test create_random flow with a valid 3x3 English game without seed words.
    This should return a 201 status code and validate the game is stored in the DB.
    """
    dynamodb = aws_clients["dynamodb"]

    # Import the handler
    from lambdas.create_random.handler import handler

    # Call the handler with the valid payload
    response = handler(c.CREATE_RANDOM_EVENT_VALID_EN, None)

    # Verify the response
    assert response["statusCode"] == 201, f"Expected 201 status code, got {response['statusCode']}"
    response_body = json.loads(response["body"])
    assert "gameId" in response_body, "Expected 'gameId' in the response body"
    assert "gameLayout" in response_body, "Expected 'gameLayout' in the response body"
    game_id = response_body["gameId"]
    print(response_body)

    # Verify the game was added to the database
    assert_game_in_db(game_id, dynamodb)
    assert_valid_words_in_db(game_id, dynamodb)
    
    # Verify that an atomic number was generated, and that the random game is
    # present in the random games DB under that number
    atomic_number = db_utils.fetch_random_game_count("en")
    assert_random_game_in_db(atomic_number, dynamodb)
    assert_random_game_count_equals(1, dynamodb)

    # Fetch the game and validate the details
    fetched_game = db_utils.fetch_game_by_id(game_id)
    assert fetched_game is not None, f"Game with ID {game_id} should exist in the database"
    assert fetched_game["gameLayout"] == response_body["gameLayout"], "Game layout does not match the expected layout"
    assert fetched_game["language"] == "en", "Expected game language to be English ('en')"
    assert fetched_game["boardSize"] == "3x3", "Expected game board size to be '3x3'"

    print(f"Successfully created and verified English game with ID {game_id}.")


def create_random_valid_es(aws_clients):
    """
    Test create_random flow with a valid 3x3 Spanish game without seed words.
    This should return a 201 status code and validate the game is stored in the DB.
    """
    dynamodb = aws_clients["dynamodb"]

    # Import the handler
    from lambdas.create_random.handler import handler

    # Call the handler with the valid Spanish payload
    response = handler(c.CREATE_RANDOM_EVENT_VALID_ES, None)

    # Verify the response
    assert response["statusCode"] == 201, f"Expected 201 status code, got {response['statusCode']}"
    response_body = json.loads(response["body"])
    assert "gameId" in response_body, "Expected 'gameId' in the response body"
    assert "gameLayout" in response_body, "Expected 'gameLayout' in the response body"
    game_id = response_body["gameId"]

    # Verify the game was added to the database
    assert_game_in_db(game_id, dynamodb)
    assert_valid_words_in_db(game_id, dynamodb)

    # Verify that an atomic number was generated, and that the random game is
    # present in the random games DB under that number
    atomic_number = db_utils.fetch_random_game_count("es")
    assert_random_game_in_db(atomic_number, dynamodb)
    assert_random_game_count_equals(1, dynamodb)

    # Fetch the game and validate the details
    fetched_game = db_utils.fetch_game_by_id(game_id)
    assert fetched_game is not None, f"Game with ID {game_id} should exist in the database"
    assert fetched_game["gameLayout"] == response_body["gameLayout"], "Game layout does not match the expected layout"
    assert fetched_game["language"] == "es", "Expected game language to be Spanish ('es')"
    assert fetched_game["boardSize"] == "3x3", "Expected game board size to be '3x3'"

    print(f"Successfully created and verified Spanish game with ID {game_id}.")


def create_random_valid_en_with_seed(aws_clients):
    """
    Test create_random flow with a valid 3x3 English game with seed words.
    This should return a 201 status code and validate the game is stored in the DB.
    """
    dynamodb = aws_clients["dynamodb"]

    # Import the handler
    from lambdas.create_random.handler import handler

    # Call the handler with the valid English payload including seed words
    response = handler(c.CREATE_RANDOM_EVENT_VALID_SEED_WORDS_EN, None)

    # Verify the response
    assert response["statusCode"] == 201, f"Expected 201 status code, got {response['statusCode']}"
    response_body = json.loads(response["body"])
    assert "gameId" in response_body, "Expected 'gameId' in the response body"
    assert "gameLayout" in response_body, "Expected 'gameLayout' in the response body"
    game_id = response_body["gameId"]

    # Verify the game was added to the database
    assert_game_in_db(game_id, dynamodb)
    assert_valid_words_in_db(game_id, dynamodb)

    # Verify that an atomic number was generated, and that the random game is
    # present in the random games DB under that number
    atomic_number = db_utils.fetch_random_game_count("en")
    assert_random_game_in_db(atomic_number, dynamodb)
    assert_random_game_count_equals(2, dynamodb) # Should be two English games in the DB now

    # Fetch the game and validate the details
    fetched_game = db_utils.fetch_game_by_id(game_id)
    assert fetched_game is not None, f"Game with ID {game_id} should exist in the database"
    assert fetched_game["gameLayout"] == response_body["gameLayout"], "Game layout does not match the expected layout"
    assert fetched_game["language"] == "en", "Expected game language to be English ('en')"
    assert fetched_game["boardSize"] == "3x3", "Expected game board size to be '3x3'"
    assert fetched_game["randomSeedWords"] == ["VAPORIZE", "ELEMENT"], "Seed words do not match the expected seed words"

    print(f"Successfully created and verified English game with seed words and ID {game_id}.")


def create_random_valid_es_with_seed(aws_clients):
    """
    Test create_random flow with a valid 3x3 Spanish game with seed words.
    This should return a 201 status code and validate the game is stored in the DB.
    """
    dynamodb = aws_clients["dynamodb"]

    # Import the handler
    from lambdas.create_random.handler import handler

    print("Calling the create_random handler with Spanish seed words...")
    # Call the handler with the valid Spanish payload including seed words
    response = handler(c.CREATE_RANDOM_EVENT_VALID_SEED_WORDS_ES, None)
    print(f"Handler response: {response}")

    # Verify the response
    print("Verifying response status code...")
    assert response["statusCode"] == 201, f"Expected 201 status code, got {response['statusCode']}"

    print("Parsing response body...")
    response_body = json.loads(response["body"])
    assert "gameId" in response_body, "Expected 'gameId' in the response body"
    assert "gameLayout" in response_body, "Expected 'gameLayout' in the response body"
    game_id = response_body["gameId"]
    print(f"Game ID from response: {game_id}")

    # Verify the game was added to the database
    print("Verifying game was added to the database...")
    assert_game_in_db(game_id, dynamodb)
    assert_valid_words_in_db(game_id, dynamodb)

    # Verify that an atomic number was generated, and that the random game is
    # present in the random games DB under that number
    print("Fetching random game count for Spanish games...")
    atomic_number = db_utils.fetch_random_game_count("es")
    print(f"Atomic number for Spanish game: {atomic_number}")
    assert_random_game_in_db(atomic_number, dynamodb)

    print("Verifying random game count equals expected...")
    assert_random_game_count_equals(2, dynamodb)  # Should be two Spanish games now

    # Fetch the game and validate the details
    print(f"Fetching game by ID {game_id}...")
    fetched_game = db_utils.fetch_game_by_id(game_id)
    assert fetched_game is not None, f"Game with ID {game_id} should exist in the database"
    assert fetched_game["gameLayout"] == response_body["gameLayout"], "Game layout does not match the expected layout"
    assert fetched_game["language"] == "es", "Expected game language to be Spanish ('es')"
    assert fetched_game["boardSize"] == "3x3", "Expected game board size to be '3x3'"
    assert fetched_game["randomSeedWords"] == ["ÚNICAMENTE", "ELECTRICOS"], "Seed words do not match the expected seed words"

    print(f"Successfully created and verified Spanish game with seed words and ID {game_id}.")


def create_random_valid_4x4_with_seed_en(aws_clients):
    """
    Test create_random flow with a valid 4x4 English game with seed words.
    This should return a 201 status code and validate the game is stored in the DB.
    """
    dynamodb = aws_clients["dynamodb"]

    # Import the handler
    from lambdas.create_random.handler import handler

    # Call the handler with the valid 4x4 English payload including seed words
    response = handler(c.CREATE_RANDOM_EVENT_VALID_4X4_WITH_SEED_EN, None)

    # Verify the response
    assert response["statusCode"] == 201, f"Expected 201 status code, got {response['statusCode']}"
    response_body = json.loads(response["body"])
    assert "gameId" in response_body, "Expected 'gameId' in the response body"
    assert "gameLayout" in response_body, "Expected 'gameLayout' in the response body"
    game_id = response_body["gameId"]

    # Verify the game was added to the database
    assert_game_in_db(game_id, dynamodb)
    assert_valid_words_in_db(game_id, dynamodb)

    # Verify that an atomic number was generated, and that the random game is
    # present in the random games DB under that number
    atomic_number = db_utils.fetch_random_game_count("en")
    assert_random_game_in_db(atomic_number, dynamodb)
    assert_random_game_count_equals(3, dynamodb) # Should be 3 games in the DB now

    # Fetch the game and validate the details
    fetched_game = db_utils.fetch_game_by_id(game_id)
    assert fetched_game is not None, f"Game with ID {game_id} should exist in the database"
    assert fetched_game["gameLayout"] == response_body["gameLayout"], "Game layout does not match the expected layout"
    assert fetched_game["language"] == "en", "Expected game language to be English ('en')"
    assert fetched_game["boardSize"] == "4x4", "Expected game board size to be '4x4'"
    assert fetched_game["randomSeedWords"] == ["DISPLACEMENT", "THORNBUSH"], "Seed words do not match the expected seed words"

    print(f"Successfully created and verified English 4x4 game with seed words and ID {game_id}.")


def create_random_valid_4x4_with_seed_es(aws_clients):
    """
    Test create_random flow with a valid 4x4 Spanish game with seed words.
    This should return a 201 status code and validate the game is stored in the DB.
    """
    dynamodb = aws_clients["dynamodb"]

    # Import the handler
    from lambdas.create_random.handler import handler

    print("Calling the handler with a valid 4x4 Spanish payload with seed words...")
    # Call the handler with the valid 4x4 Spanish payload including seed words
    response = handler(c.CREATE_RANDOM_EVENT_VALID_4x4_WITH_SEED_ES, None)

    print("Verifying the response...")
    # Verify the response
    assert response["statusCode"] == 201, f"Expected 201 status code, got {response['statusCode']}"
    response_body = json.loads(response["body"])
    assert "gameId" in response_body, "Expected 'gameId' in the response body"
    assert "gameLayout" in response_body, "Expected 'gameLayout' in the response body"
    game_id = response_body["gameId"]
    print(f"Handler returned gameId: {game_id}")

    print("Checking that the game was added to the database...")
    # Verify the game was added to the database
    assert_game_in_db(game_id, dynamodb)
    print(f"Game with ID {game_id} exists in the games DB.")
    assert_valid_words_in_db(game_id, dynamodb)
    print(f"Valid words for game ID {game_id} exist in the valid words DB.")

    print("Checking that the game is present in the random games table...")
    # Verify that an atomic number was generated, and that the random game is present in the random games DB
    atomic_number = db_utils.fetch_random_game_count("es")
    assert_random_game_in_db(atomic_number, dynamodb)
    print(f"Game is stored in the random games DB with atomic number {atomic_number}.")
    assert_random_game_count_equals(3, dynamodb)  # Should be three games in the DB now
    print("Random game count verified to be 3.")

    print("Fetching and validating game details...")
    # Fetch the game and validate the details
    fetched_game = db_utils.fetch_game_by_id(game_id)
    assert fetched_game is not None, f"Game with ID {game_id} should exist in the database"
    assert fetched_game["gameLayout"] == response_body["gameLayout"], "Game layout does not match the expected layout"
    assert fetched_game["language"] == "es", "Expected game language to be Spanish ('es')"
    assert fetched_game["boardSize"] == "4x4", "Expected game board size to be '4x4'"
    assert fetched_game["randomSeedWords"] == ["CHABOLISTA", "AMPURDANÉS"], "Seed words do not match the expected seed words"

    print(f"Successfully created and verified Spanish 4x4 game with seed words and ID {game_id}.")

    
# Invalid Event Tests
def create_random_unsupported_language(aws_clients):
    """
    Test create_random flow with an unsupported language.
    This should return a 400 status code and ensure no game is added to the database.
    """
    dynamodb = aws_clients["dynamodb"]

    # Import the handler
    from lambdas.create_random.handler import handler

    # Call the handler with the unsupported language payload
    response = handler(c.CREATE_RANDOM_EVENT_UNSUPPORTED_LANGUAGE, None)

    # Verify the response
    assert response["statusCode"] == 400, f"Expected 400 status code, got {response['statusCode']}"
    response_body = json.loads(response["body"])
    assert "message" in response_body, "Expected a 'message' key in the response body"
    assert "unsupported language" in response_body["message"].lower(), \
        "Expected an error message about unsupported language"

    # Verify no game was added to the database
    assert_table_is_empty(dynamodb, os.environ["GAMES_TABLE"])
    assert_table_is_empty(dynamodb, os.environ["VALID_WORDS_TABLE"])
    assert_table_is_empty(dynamodb, os.environ["METADATA_TABLE"])
    assert_table_is_empty(dynamodb, os.environ["SESSION_STATES_TABLE"])
    assert_table_is_empty(dynamodb, os.environ["ARCHIVE_TABLE"])
    assert_table_is_empty(dynamodb, os.environ["RANDOM_GAMES_TABLE_EN"])
    assert_table_is_empty(dynamodb, os.environ["RANDOM_GAMES_TABLE_ES"])

    print("Successfully tested create_random with unsupported language.")


def create_random_invalid_board_size(aws_clients):
    """
    Test create_random flow with an invalid board size.
    This should return a 400 status code and ensure no game is added to the database.
    """
    dynamodb = aws_clients["dynamodb"]

    # Import the handler
    from lambdas.create_random.handler import handler

    print("Calling the handler with invalid board size payload...")
    # Call the handler with the invalid board size payload
    response = handler(c.CREATE_RANDOM_EVENT_INVALID_BOARD_SIZE, None)

    print("Verifying the response...")
    # Verify the response
    assert response["statusCode"] == 400, f"Expected 400 status code, got {response['statusCode']}"
    response_body = json.loads(response["body"])
    assert "message" in response_body, "Expected a 'message' key in the response body"
    assert "invalid board size" in response_body["message"].lower(), "Expected an error message about invalid board size"
    print(f"Handler returned expected error response: {response_body['message']}")

    print("Checking all relevant DynamoDB tables for unintended changes...")
    # Verify no game was added to the database
    assert_table_is_empty(dynamodb, os.environ["GAMES_TABLE"])
    assert_table_is_empty(dynamodb, os.environ["VALID_WORDS_TABLE"])
    assert_table_is_empty(dynamodb, os.environ["METADATA_TABLE"])
    assert_table_is_empty(dynamodb, os.environ["SESSION_STATES_TABLE"])
    assert_table_is_empty(dynamodb, os.environ["ARCHIVE_TABLE"])
    assert_table_is_empty(dynamodb, os.environ["RANDOM_GAMES_TABLE_EN"])
    assert_table_is_empty(dynamodb, os.environ["RANDOM_GAMES_TABLE_ES"])

    print("Successfully tested create_random with an invalid board size.")


def create_random_invalid_seed_words(aws_clients):
    """
    Test create_random flow with invalid seed words that can't form a valid layout.
    This should return a 400 status code and ensure no game is added to the database.
    """
    dynamodb = aws_clients["dynamodb"]

    # Import the handler
    from lambdas.create_random.handler import handler

    print("Calling the handler with invalid seed words...")
    # Call the handler with the invalid seed words payload
    response = handler(c.CREATE_RANDOM_EVENT_INVALID_SEED_WORDS, None)

    print("Verifying the response...")
    # Verify the response
    assert response["statusCode"] == 400, f"Expected 400 status code, got {response['statusCode']}"
    response_body = json.loads(response["body"])
    assert "message" in response_body, "Expected a 'message' key in the response body"
    print(response_body["message"])
    assert "Could not create a random game" in response_body["message"], \
        "Expected an error message about not creating a random game"

    print("Checking that no game was added to the database...")
    # Verify no game was added to the database
    assert_table_is_empty(dynamodb, os.environ["GAMES_TABLE"])
    assert_table_is_empty(dynamodb, os.environ["VALID_WORDS_TABLE"])
    assert_table_is_empty(dynamodb, os.environ["METADATA_TABLE"])
    assert_table_is_empty(dynamodb, os.environ["SESSION_STATES_TABLE"])
    assert_table_is_empty(dynamodb, os.environ["ARCHIVE_TABLE"])
    assert_table_is_empty(dynamodb, os.environ["RANDOM_GAMES_TABLE_EN"])
    assert_table_is_empty(dynamodb, os.environ["RANDOM_GAMES_TABLE_ES"])

    print("Successfully tested create_random with invalid seed words.")


def create_random_malformed_json(aws_clients):
    """
    Test create_random flow with malformed JSON.
    This should return a 400 status code and ensure no game is added to the database.
    """
    dynamodb = aws_clients["dynamodb"]

    # Import the handler
    from lambdas.create_random.handler import handler

    print("Calling the handler with malformed JSON...")
    # Call the handler with the malformed JSON payload
    response = handler(c.CREATE_RANDOM_EVENT_MALFORMED_JSON, None)

    print("Verifying the response...")
    # Verify the response
    assert response["statusCode"] == 400, f"Expected 400 status code, got {response['statusCode']}"
    response_body = json.loads(response["body"])
    assert "message" in response_body, "Expected a 'message' key in the response body"
    assert "json decoding error" in response_body["message"].lower(), "Expected an error message about JSON decoding"

    print("Checking that no game was added to the database...")

    # Verify no game was added to the database
    assert_table_is_empty(dynamodb, os.environ["GAMES_TABLE"])
    assert_table_is_empty(dynamodb, os.environ["VALID_WORDS_TABLE"])
    assert_table_is_empty(dynamodb, os.environ["METADATA_TABLE"])
    assert_table_is_empty(dynamodb, os.environ["SESSION_STATES_TABLE"])
    assert_table_is_empty(dynamodb, os.environ["ARCHIVE_TABLE"])
    assert_table_is_empty(dynamodb, os.environ["RANDOM_GAMES_TABLE_EN"])
    assert_table_is_empty(dynamodb, os.environ["RANDOM_GAMES_TABLE_ES"])

    print("Successfully tested create_random with malformed JSON.")


def create_random_missing_body(aws_clients):
    """
    Test create_random flow with a missing body entirely.
    This should return a 400 status code and ensure no game is added to the database.
    """
    dynamodb = aws_clients["dynamodb"]

    # Import the handler
    from lambdas.create_random.handler import handler

    print("Calling the handler with a missing body...")
    # Call the handler with the missing body payload
    response = handler(c.CREATE_RANDOM_EVENT_MISSING_BODY, None)

    print("Verifying the response...")
    # Verify the response
    assert response["statusCode"] == 400, f"Expected 400 status code, got {response['statusCode']}"
    response_body = json.loads(response["body"])
    assert "message" in response_body, "Expected a 'message' key in the response body"
    assert "missing body" in response_body["message"].lower(), "Expected an error message about invalid input or missing body"

    print("Checking that no game was added to the database...")
    
    # Verify no game was added to the database
    assert_table_is_empty(dynamodb, os.environ["GAMES_TABLE"])
    assert_table_is_empty(dynamodb, os.environ["VALID_WORDS_TABLE"])
    assert_table_is_empty(dynamodb, os.environ["METADATA_TABLE"])
    assert_table_is_empty(dynamodb, os.environ["SESSION_STATES_TABLE"])
    assert_table_is_empty(dynamodb, os.environ["ARCHIVE_TABLE"])
    assert_table_is_empty(dynamodb, os.environ["RANDOM_GAMES_TABLE_EN"])
    assert_table_is_empty(dynamodb, os.environ["RANDOM_GAMES_TABLE_ES"])

    print("Successfully tested create_random with a missing body.")


# ===================================================================
# Fetch Game Handler tests
# ===================================================================
def fetch_game_valid_game_id(aws_clients, game_id):
    """
    Test fetch_game flow with a valid gameId taken from a previous integration test.
    This should return a 200 status code and the expected game details.
    """
    print("Testing fetch_game_valid_game_id")
    dynamodb = aws_clients["dynamodb"]

    # Import the handler
    from lambdas.fetch_game.handler import handler

    # Update the payload with the valid game ID
    event = c.FETCH_GAME_EVENT_VALID(game_id)

    # Call the handler with the valid payload
    response = handler(event, None)

    # Verify the response
    assert response["statusCode"] == 200, f"Expected 200 status code, got {response['statusCode']}"
    response_body = json.loads(response["body"])
    assert "gameId" in response_body, "Expected 'gameId' in the response body"
    assert response_body["gameId"] == game_id, f"Expected gameId to be {game_id}, got {response_body['gameId']}"

    # Fetch the game from the DB and compare details
    fetched_game = db_utils.fetch_game_by_id(game_id)
    assert fetched_game is not None, f"Game with ID {game_id} should exist in the database"
    assert fetched_game["gameLayout"] == response_body["gameLayout"], "Game layout does not match the expected layout"

    print(f"Successfully fetched game with ID {game_id}.")


def fetch_game_missing_game_id(aws_clients):
    """
    Test fetch_game handler with a missing gameId in the event payload.
    This should return a 400 status code with an appropriate error message.
    """
    print("Testing fetch_game_missing_game_id")
    dynamodb = aws_clients["dynamodb"]
    # Import the handler
    from lambdas.fetch_game.handler import handler

    # Call the handler
    response = handler(c.FETCH_GAME_EVENT_MISSING_GAME_ID, None)

    # Verify the response
    assert response["statusCode"] == 400, f"Expected 400 status code, got {response['statusCode']}"
    response_body = json.loads(response["body"])
    assert "message" in response_body, "Expected a 'message' key in the response body"
    assert "gameId is required" in response_body["message"], "Expected error message about missing gameId"

    # Verify no game was added to the database
    assert_table_is_empty(dynamodb, os.environ["GAMES_TABLE"])
    assert_table_is_empty(dynamodb, os.environ["VALID_WORDS_TABLE"])

    print("Successfully tested fetch_game with missing gameId.")


def fetch_game_nonexistent_game_id(aws_clients):
    """
    Test fetch_game handler with a non-existent gameId.
    This should return a 404 status code with an appropriate error message.
    """
    print("Testing fetch_game_nonexistent_game_id")
    dynamodb = aws_clients["dynamodb"]
    # Import the handler
    from lambdas.fetch_game.handler import handler

    # Call the handler
    response = handler(c.FETCH_GAME_EVENT_NONEXISTENT_GAME_ID, None)

    # Verify the response
    assert response["statusCode"] == 404, f"Expected 404 status code, got {response['statusCode']}"
    response_body = json.loads(response["body"])
    assert "message" in response_body, "Expected a 'message' key in the response body"
    assert "Game ID not found" in response_body["message"], "Expected error message about non-existent gameId"

    # Verify no game was added to the database
    assert_table_is_empty(dynamodb, os.environ["GAMES_TABLE"])
    assert_table_is_empty(dynamodb, os.environ["VALID_WORDS_TABLE"])

    print("Successfully tested fetch_game with a non-existent gameId.")


def fetch_game_invalid_json(aws_clients):
    """
    Test fetch_game handler with a malformed JSON payload.
    This should return a 400 status code with an appropriate error message.
    """
    print("Testing fetch_game_invalid_json")
    dynamodb = aws_clients["dynamodb"]
    # Import the handler
    from lambdas.fetch_game.handler import handler

    # Call the handler
    response = handler(c.FETCH_GAME_EVENT_INVALID_JSON, None)

    # Verify the response
    assert response["statusCode"] == 400, f"Expected 400 status code, got {response['statusCode']}"
    response_body = json.loads(response["body"])
    assert "message" in response_body, "Expected a 'message' key in the response body"
    assert "Invalid JSON format" in response_body["message"], "Expected error message about invalid JSON format"

    # Verify no game was added to the database
    assert_table_is_empty(dynamodb, os.environ["GAMES_TABLE"])
    assert_table_is_empty(dynamodb, os.environ["VALID_WORDS_TABLE"])

    print("Successfully tested fetch_game with malformed JSON.")


# ===================================================================
# Save User State Lambda Tests
# ===================================================================
def save_user_state_valid_initial_state_en(aws_clients):
    """
    Test initializing a valid user session state in English.
    Should create a new entry in the database with the correct initial values.
    """
    dynamodb = aws_clients["dynamodb"]

    # Import the handler
    from lambdas.save_user_state.handler import handler

    # Call the handler with the initial payload
    response = handler(c.SAVE_USER_STATE_INITIAL_PAYLOAD_EN, None)

    # Verify the response
    assert response["statusCode"] == 200, f"Expected 200 status code, got {response['statusCode']}"
    response_body = json.loads(response["body"])
    assert "message" in response_body, "Expected a 'message' key in the response body"
    assert not response_body["gameCompleted"], "Game should not be marked as completed initially"
    assert response_body["wordsUsed"] == [], "Words used should be empty in the initial state"
    print(f"Initial response message: {response_body['message']}")

    # Verify the game state was saved in the database
    user_state = db_utils.get_user_game_state("test-session-state-en", "test-game-state-en")
    assert user_state is not None, "User game state should exist in the database"
    assert user_state["wordsUsed"] == [], "Words used should be empty in the initial state"
    assert user_state["gameCompleted"] is False, "Game should not be completed in the initial state"
    assert user_state["TTL"] > int(time.time()), "TTL should be set to a future timestamp"

    print(f"Successfully initialized English game state: {user_state}")


def save_user_state_valid_update_state_en(aws_clients):
    """
    Test updating an existing user session state in English with new words.
    Should update the words used and extend the TTL.
    """
    dynamodb = aws_clients["dynamodb"]

    # Import the handler
    from lambdas.save_user_state.handler import handler

    # Call the handler with the update payload (playing the word "HUMONGOUS")
    response = handler(c.SAVE_USER_STATE_UPDATE_PAYLOAD_EN, None)

    # Verify the response
    assert response["statusCode"] == 200, f"Expected 200 status code, got {response['statusCode']}"
    response_body = json.loads(response["body"])
    assert "message" in response_body, "Expected a 'message' key in the response body"
    assert not response_body["gameCompleted"], "Game should not be marked as completed yet"
    assert response_body["wordsUsed"] == ["HUMONGOUS"], "Words used should now include 'HUMONGOUS'"
    print(f"Update response message: {response_body['message']}")

    # Verify the updated game state in the database
    user_state = db_utils.get_user_game_state("test-session-state-en", "test-game-state-en")
    assert user_state is not None, "User game state should still exist in the database"
    assert user_state["wordsUsed"] == ["HUMONGOUS"], "Words used should match the update"
    assert user_state["gameCompleted"] is False, "Game should not be completed after the update"
    assert user_state["TTL"] > int(time.time()), "TTL should be extended to a future timestamp"

    print(f"Successfully updated English game state: {user_state}")


def save_user_state_game_completion_en(aws_clients):
    """
    Test saving a state in English that completes the game.
    Should mark the game as completed in the database.
    """
    dynamodb = aws_clients["dynamodb"]

    # Import the handler
    from lambdas.save_user_state.handler import handler

    # Call the handler with the completion payload (playing the word "SCRATCHY")
    response = handler(c.SAVE_USER_STATE_COMPLETION_PAYLOAD_EN, None)

    # Verify the response
    assert response["statusCode"] == 200, f"Expected 200 status code, got {response['statusCode']}"
    response_body = json.loads(response["body"])
    assert "message" in response_body, "Expected a 'message' key in the response body"
    assert response_body["gameCompleted"], "Game should now be marked as completed"
    assert response_body["wordsUsed"] == ["HUMONGOUS", "SCRATCHY"], "Words used should now include 'HUMONGOUS' and 'SCRATCHY'"
    print(f"Completion response message: {response_body['message']}")

    # Verify the updated game state in the database
    user_state = db_utils.get_user_game_state("test-session-state-en", "test-game-state-en")
    assert user_state is not None, "User game state should still exist in the database"
    assert user_state["wordsUsed"] == ["HUMONGOUS", "SCRATCHY"], "Words used should match the update"
    assert user_state["gameCompleted"], "Game should be marked as completed after the update"

    print(f"Successfully completed English game state: {user_state}")


def save_user_state_valid_initial_state_es(aws_clients):
    """
    Test saving a valid initial user session state in Spanish.
    Should initialize the game state in the database.
    """
    dynamodb = aws_clients["dynamodb"]

    # Import the handler
    from lambdas.save_user_state.handler import handler

    # Call the handler with the initial Spanish payload
    response = handler(c.SAVE_USER_STATE_INITIAL_PAYLOAD_ES, None)

    # Verify the response
    assert response["statusCode"] == 200, f"Expected 200 status code, got {response['statusCode']}"
    response_body = json.loads(response["body"])
    assert "message" in response_body, "Expected a 'message' key in the response body"
    assert not response_body["gameCompleted"], "Game should not be completed at initialization"
    print(f"Response message: {response_body['message']}")

    # Verify the game state was added to the database
    user_state = db_utils.get_user_game_state("test-session-state-es", "test-game-state-es")
    assert user_state is not None, "User game state should exist in the database"
    assert user_state["wordsUsed"] == [], "Words used should be empty at initialization"
    assert user_state["originalWordsUsed"] == [], "Original words used should be empty at initialization"
    assert not user_state["gameCompleted"], "Game should not be completed at initialization"

    print(f"Successfully initialized Spanish game state: {user_state}")


def save_user_state_valid_update_state_es(aws_clients):
    """
    Test updating an existing user session state in Spanish with new words.
    Should update the words used and extend the TTL.
    """
    dynamodb = aws_clients["dynamodb"]

    # Import the handler
    from lambdas.save_user_state.handler import handler

    # Call the handler to update the Spanish game state
    response = handler(c.SAVE_USER_STATE_UPDATE_PAYLOAD_ES, None)

    # Verify the response
    assert response["statusCode"] == 200, f"Expected 200 status code, got {response['statusCode']}"
    response_body = json.loads(response["body"])
    assert "message" in response_body, "Expected a 'message' key in the response body"
    assert not response_body["gameCompleted"], "Game should not be completed after this update"
    assert "wordsUsed" in response_body, "Expected 'wordsUsed' key in the response body"
    print(f"Response words used: {response_body['wordsUsed']}")

    # Verify the game state was updated in the database
    user_state = db_utils.get_user_game_state("test-session-state-es", "test-game-state-es")
    assert user_state is not None, "User game state should exist in the database"
    assert user_state["wordsUsed"] == ["UNICAMENTE"], "Words used should include the normalized version of the word"
    assert user_state["originalWordsUsed"] == ["ÚNICAMENTE"], "Original words used should retain accents"
    assert not user_state["gameCompleted"], "Game should not be completed after this update"

    # Verify TTL was extended
    current_time = int(time.time())
    assert user_state["TTL"] > current_time, "TTL should be extended after the update"

    print(f"Successfully updated Spanish game state: {user_state}")


def save_user_state_game_completion_es(aws_clients):
    """
    Test saving a state in Spanish that completes the game.
    Should mark the game as completed in the database.
    """
    dynamodb = aws_clients["dynamodb"]

    # Import the handler
    from lambdas.save_user_state.handler import handler

    # Call the handler with the payload to complete the game
    response = handler(c.SAVE_USER_STATE_COMPLETION_PAYLOAD_ES, None)

    # Verify the response
    assert response["statusCode"] == 200, f"Expected 200 status code, got {response['statusCode']}"
    response_body = json.loads(response["body"])
    assert "message" in response_body, "Expected a 'message' key in the response body"
    assert response_body["gameCompleted"], "Game should be marked as completed after this update"
    assert "wordsUsed" in response_body, "Expected 'wordsUsed' key in the response body"
    print(f"Response words used: {response_body['wordsUsed']}")

    # Verify the game state was updated in the database
    user_state = db_utils.get_user_game_state("test-session-state-es", "test-game-state-es")
    assert user_state is not None, "User game state should exist in the database"
    assert user_state["wordsUsed"] == ["UNICAMENTE", "ELECTRICOS"], "Words used should include all played words"
    assert user_state["originalWordsUsed"] == ["ÚNICAMENTE", "ELECTRICOS"], "Original words used should retain accents"
    assert user_state["gameCompleted"], "Game should be marked as completed in the database"

    # Verify TTL was extended
    current_time = int(time.time())
    assert user_state["TTL"] > current_time, "TTL should be extended after the update"

    print(f"Successfully completed Spanish game state: {user_state}")


def save_user_state_same_session_different_games(aws_clients):
    """
    Test saving states with the same user session but different game IDs.
    Ensure they are stored as separate entries in the database.
    """
    dynamodb = aws_clients["dynamodb"]

    # Import the handler
    from lambdas.save_user_state.handler import handler

    print("Initializing game state for Game 1...")
    response1 = handler(c.SAVE_USER_STATE_INIT_GAME1, None)
    print(f"Response for Game 1 initialization: {response1}")

    print("Initializing game state for Game 2...")
    response2 = handler(c.SAVE_USER_STATE_INIT_GAME2, None)
    print(f"Response for Game 2 initialization: {response2}")

    # Verify responses
    assert response1["statusCode"] == 200, f"Expected 200 for game 1, got {response1['statusCode']}"
    assert response2["statusCode"] == 200, f"Expected 200 for game 2, got {response2['statusCode']}"

    game_id_1 = json.loads(response1["body"])["gameId"]
    game_id_2 = json.loads(response2["body"])["gameId"]

    print(f"Game ID 1: {game_id_1}")
    print(f"Game ID 2: {game_id_2}")

    assert game_id_1 != game_id_2, "Game IDs should be different for this test"

    print("Fetching user state for Game 1...")
    user_state_game1 = db_utils.get_user_game_state("test-session-same", game_id_1)
    print(f"User state for Game 1: {user_state_game1}")

    print("Fetching user state for Game 2...")
    user_state_game2 = db_utils.get_user_game_state("test-session-same", game_id_2)
    print(f"User state for Game 2: {user_state_game2}")

    assert user_state_game1 is not None, f"State for game ID {game_id_1} should exist"
    assert user_state_game2 is not None, f"State for game ID {game_id_2} should exist"

    print("Updating game state for Game 1 with unique words...")
    handler(c.SAVE_USER_STATE_UPDATE_GAME1, None)

    print("Updating game state for Game 2 with unique words...")
    handler(c.SAVE_USER_STATE_UPDATE_GAME2, None)

    print("Fetching updated user state for Game 1...")
    updated_game1 = db_utils.get_user_game_state("test-session-same", game_id_1)
    print(f"Updated user state for Game 1: {updated_game1}")

    print("Fetching updated user state for Game 2...")
    updated_game2 = db_utils.get_user_game_state("test-session-same", game_id_2)
    print(f"Updated user state for Game 2: {updated_game2}")

    assert updated_game1["wordsUsed"] == ["HUMONGOUS"], "Game 1 should reflect its unique words"
    assert updated_game2["wordsUsed"] == ["SCRATCHY"], "Game 2 should reflect its unique words"

    print("Successfully tested same session with different game IDs.")


def save_user_state_same_game_different_sessions(aws_clients):
    """
    Test saving states with the same game ID but different user sessions.
    Ensure they are stored as separate entries in the database.
    """
    dynamodb = aws_clients["dynamodb"]

    # Import the handler
    from lambdas.save_user_state.handler import handler

    # Initialize two separate game states for the same game ID but different sessions
    response1 = handler(c.SAVE_USER_STATE_INIT_SESSION1, None)
    response2 = handler(c.SAVE_USER_STATE_INIT_SESSION2, None)

    # Verify responses
    assert response1["statusCode"] == 200, f"Expected 200 for session 1, got {response1['statusCode']}"
    assert response2["statusCode"] == 200, f"Expected 200 for session 2, got {response2['statusCode']}"

    session_id_1 = json.loads(response1["body"])["sessionId"]
    session_id_2 = json.loads(response2["body"])["sessionId"]

    assert session_id_1 != session_id_2, "Session IDs should be different for this test"

    # Verify both states exist in the database
    user_state_session1 = db_utils.get_user_game_state(session_id_1, "test-game-same")
    user_state_session2 = db_utils.get_user_game_state(session_id_2, "test-game-same")

    assert user_state_session1 is not None, f"State for session ID {session_id_1} should exist"
    assert user_state_session2 is not None, f"State for session ID {session_id_2} should exist"

    # Verify entries are distinct by updating the sessions with different words
    handler(c.SAVE_USER_STATE_UPDATE_SESSION1, None)  # Play a word in session 1
    handler(c.SAVE_USER_STATE_UPDATE_SESSION2, None)  # Play a word in session 2

    updated_session1 = db_utils.get_user_game_state(session_id_1, "test-game-same")
    updated_session2 = db_utils.get_user_game_state(session_id_2, "test-game-same")

    assert updated_session1["wordsUsed"] == ["UNICAMENTE"], "Session 1 should reflect its unique words"
    assert updated_session2["wordsUsed"] == ["ELECTRICOS"], "Session 2 should reflect its unique words"

    print("Successfully tested same game ID with different user sessions.")


def save_user_state_missing_parameters(aws_clients):
    """
    Test saving user state when required parameters are missing (e.g., gameLayout, gameId, or sessionId).
    Should return a 400 status code and ensure no state is added to the database.
    """
    dynamodb = aws_clients["dynamodb"]

    # Import the handler
    from lambdas.save_user_state.handler import handler

    # Call the handler with a payload missing gameLayout
    print("Testing save_user_state with missing gameLayout...")
    response = handler(c.SAVE_USER_STATE_MISSING_GAME_LAYOUT, None)
    print("Response:", response)

    # Verify the response
    assert response["statusCode"] == 400, f"Expected 400 status code, got {response['statusCode']}"
    response_body = json.loads(response["body"])
    assert "message" in response_body, "Expected a 'message' key in the response body"
    assert "missing required parameters" in response_body["message"].lower(), (
        "Expected an error message about missing required parameters"
    )

    # Verify no state was added to the database
    assert_table_is_empty(dynamodb, os.environ["SESSION_STATES_TABLE"])

    print("Successfully tested save_user_state with missing parameters.")


def save_user_state_invalid_json(aws_clients):
    """
    Test saving user state with a malformed JSON payload.
    Should return a 400 status code and ensure no state is added to the database.
    """
    dynamodb = aws_clients["dynamodb"]

    # Import the handler
    from lambdas.save_user_state.handler import handler

    # Call the handler with a malformed JSON payload
    print("Testing save_user_state with invalid JSON...")
    response = handler(c.SAVE_USER_STATE_INVALID_JSON, None)
    print("Response:", response)

    # Verify the response
    assert response["statusCode"] == 400, f"Expected 400 status code, got {response['statusCode']}"
    response_body = json.loads(response["body"])
    assert "message" in response_body, "Expected a 'message' key in the response body"
    assert "invalid json format" in response_body["message"].lower(), (
        "Expected an error message about invalid JSON format"
    )

    # Verify no state was added to the database
    assert_table_is_empty(dynamodb, os.environ["SESSION_STATES_TABLE"])

    print("Successfully tested save_user_state with invalid JSON.")


def save_user_state_nonexistent_game(aws_clients):
    """
    Test saving user state for a non-existent gameId.
    Should initialize a new game state and store it in the database.
    """
    dynamodb = aws_clients["dynamodb"]

    # Import the handler
    from lambdas.save_user_state.handler import handler

    # Call the handler with a non-existent gameId payload
    response = handler(c.SAVE_USER_STATE_NONEXISTENT_GAME, None)

    # Verify the response
    assert response["statusCode"] == 200, f"Expected 200 status code, got {response['statusCode']}"
    response_body = json.loads(response["body"])
    assert "gameId" in response_body, "Expected 'gameId' in the response body"
    assert response_body["gameId"] == "nonexistent-game-id", "Game ID in response should match the non-existent game ID"

    # Verify a new state is created in the database
    user_game_state = db_utils.get_user_game_state("test-session-nonexistent", "nonexistent-game-id")
    assert user_game_state is not None, "Expected a new game state to be created for the non-existent game ID"
    assert user_game_state["gameCompleted"] is False, "Game should not be marked as completed"
    assert user_game_state["wordsUsed"] == [], "Words used should be an empty list for a new state"

    print(f"Successfully tested creation of a new state for non-existent game ID.")

# ===================================================================
# Fetch User State Lambda Tests
# ===================================================================
def fetch_user_state_valid(aws_clients):
    """
    Test fetching a valid user state.
    Should return a 200 status code with the correct game state.
    """
    print("Entering fetch_user_state_valid")
    dynamodb = aws_clients["dynamodb"]

    # Import the handler
    from lambdas.fetch_user_state.handler import handler

    # Initialize a user state in the database
    db_utils.save_user_session_state({
        "sessionId": "test-session-valid",
        "gameId": "test-game-id",
        "wordsUsed": ["HUMONGOUS"],
        "originalWordsUsed": ["HUMONGOUS"],
        "gameCompleted": False,
        "lastUpdated": 1732846529,
    })

    # Call the handler
    response = handler(c.FETCH_USER_STATE_VALID, None)

    # Verify response
    assert response["statusCode"] == 200, f"Expected 200 status code, got {response['statusCode']}"
    response_body = json.loads(response["body"])
    assert response_body["sessionId"] == "test-session-valid", "Session ID mismatch"
    assert response_body["gameId"] == "test-game-id", "Game ID mismatch"
    assert response_body["wordsUsed"] == ["HUMONGOUS"], "Words used mismatch"

    print("Successfully fetched valid user state.")


def fetch_user_state_missing_params(aws_clients):
    """
    Test fetching a user state with missing parameters.
    Should return a 400 status code.
    """
    print("Entering fetch_user_state_missing_params")
    dynamodb = aws_clients["dynamodb"]
    # Import the handler
    from lambdas.fetch_user_state.handler import handler

    # Call the handler
    response = handler(c.FETCH_USER_STATE_MISSING_PARAMS, None)

    # Verify response
    assert response["statusCode"] == 400, f"Expected 400 status code, got {response['statusCode']}"
    response_body = json.loads(response["body"])
    assert "message" in response_body, "Expected 'message' key in response body"
    assert "sessionId and gameId are required" in response_body["message"], "Expected missing parameter error message"

    # Verify no game was added to the database
    assert_table_is_empty(dynamodb, os.environ["SESSION_STATES_TABLE"])

    print("Successfully handled missing parameters.")


def fetch_user_state_nonexistent(aws_clients):
    """
    Test fetching user session state for a nonexistent session/game combination.
    Should initialize and return a new state instead of returning a 404.
    """
    print("Entering fetch_user_state_nonexistent")
    dynamodb = aws_clients["dynamodb"]

    # Import the handler
    from lambdas.fetch_user_state.handler import handler

    # Use a nonexistent session and game ID
    event = {
        "pathParameters": {"sessionId": "test-session-new"},
        "queryStringParameters": {"gameId": "test-game-new"}
    }

    print("Calling the fetch_user_state handler for a nonexistent session/game...")
    response = handler(event, None)

    # Verify response
    assert response["statusCode"] == 200, f"Expected 200, got {response['statusCode']}"
    response_body = json.loads(response["body"])
    print(f"Handler response: {response_body}")

    # Validate initialized state
    assert response_body["sessionId"] == "test-session-new", "Session ID does not match"
    assert response_body["gameId"] == "test-game-new", "Game ID does not match"
    assert response_body["wordsUsed"] == [], "Expected no words used in the initialized state"
    assert response_body["originalWordsUsed"] == [], "Expected no original words used in the initialized state"
    assert response_body["gameCompleted"] is False, "Expected gameCompleted to be False"

    # Check the state exists in the database
    state_in_db = db_utils.get_user_game_state("test-session-new", "test-game-new")
    assert state_in_db is not None, "Expected the new state to be saved in the database"
    assert state_in_db["wordsUsed"] == [], "Expected no words used in the database state"
    assert state_in_db["gameCompleted"] is False, "Expected gameCompleted to be False in the database state"

    print("Successfully fetched and initialized state for a nonexistent session/game.")


def fetch_user_state_malformed_event(aws_clients):
    """
    Test fetching a user state with a malformed event.
    Should return a 400 status code.
    """
    print("Entering fetch_user_state_malformed_event")
    dynamodb = aws_clients["dynamodb"]
    # Import the handler
    from lambdas.fetch_user_state.handler import handler

    # Call the handler
    response = handler(c.FETCH_USER_STATE_MALFORMED_EVENT, None)

    # Verify response
    assert response["statusCode"] == 400, f"Expected 400 status code, got {response['statusCode']}"
    response_body = json.loads(response["body"])
    print("the message:", response_body["message"])
    assert "message" in response_body, "Expected 'message' key in response body"
    assert "missing path parameters" in response_body["message"], "Expected missing parameter error message"

    # Verify no game was added to the database
    assert_table_is_empty(dynamodb, os.environ["SESSION_STATES_TABLE"])

    print("Successfully handled malformed event.")


# ===================================================================
# Fetch Random Game Tests
# ===================================================================
def fetch_random_valid_game_en(aws_clients):
    """
    Test fetch_random handler with a valid request for an English game.
    This should return a 200 status code and a valid game from the database.
    """
    print("Entering function fetch_random_valid_game_en")
    dynamodb = aws_clients["dynamodb"]

    # Import the handler
    from lambdas.fetch_random.handler import handler

    # Call the handler with the English payload
    response = handler(c.FETCH_RANDOM_EVENT_VALID_EN, None)

    # Verify the response
    assert response["statusCode"] == 200, f"Expected 200 status code, got {response['statusCode']}"
    response_body = json.loads(response["body"])
    assert "gameId" in response_body, "Expected 'gameId' in the response body"
    assert "gameLayout" in response_body, "Expected 'gameLayout' in the response body"
    assert "language" in response_body, "Expected 'language' in the response body"
    assert "boardSize" in response_body, "Expected 'boardSize' in the response body"
    assert response_body["language"] == "en", "Expected language to be 'en'"

    # Verify the game exists in the database
    game_id = response_body["gameId"]
    assert_game_in_db(game_id, dynamodb)

    print(f"Successfully fetched and verified English random game with ID {game_id}.")


def fetch_random_valid_game_es(aws_clients):
    """
    Test fetch_random handler with a valid request for a Spanish game.
    This should return a 200 status code and a valid game from the database.
    """
    print("Entering function fetch_random_valid_game_es")
    dynamodb = aws_clients["dynamodb"]

    # Import the handler
    from lambdas.fetch_random.handler import handler

    # Call the handler with the Spanish payload
    response = handler(c.FETCH_RANDOM_EVENT_VALID_ES, None)

    # Verify the response
    assert response["statusCode"] == 200, f"Expected 200 status code, got {response['statusCode']}"
    response_body = json.loads(response["body"])
    assert "gameId" in response_body, "Expected 'gameId' in the response body"
    assert "gameLayout" in response_body, "Expected 'gameLayout' in the response body"
    assert "language" in response_body, "Expected 'language' in the response body"
    assert "boardSize" in response_body, "Expected 'boardSize' in the response body"
    assert response_body["language"] == "es", "Expected language to be 'es'"

    # Verify the game exists in the database
    game_id = response_body["gameId"]
    assert_game_in_db(game_id, dynamodb)

    print(f"Successfully fetched and verified Spanish random game with ID {game_id}.")


def fetch_random_missing_language(aws_clients):
    """
    Test fetch_random handler with a missing language parameter (default to English).
    This should return a 200 status code and a valid English game from the database.
    """
    print("Entering function fetch_random_missing_language")
    dynamodb = aws_clients["dynamodb"]

    # Import the handler
    from lambdas.fetch_random.handler import handler

    # Call the handler with the default language payload
    response = handler(c.FETCH_RANDOM_EVENT_DEFAULT_LANGUAGE, None)

    # Verify the response
    assert response["statusCode"] == 200, f"Expected 200 status code, got {response['statusCode']}"
    response_body = json.loads(response["body"])
    assert "gameId" in response_body, "Expected 'gameId' in the response body"
    assert "gameLayout" in response_body, "Expected 'gameLayout' in the response body"
    assert "language" in response_body, "Expected 'language' in the response body"
    assert "boardSize" in response_body, "Expected 'boardSize' in the response body"
    assert response_body["language"] == "en", "Expected language to default to 'en'"

    # Verify the game exists in the database
    game_id = response_body["gameId"]
    assert_game_in_db(game_id, dynamodb)

    print(f"Successfully fetched and verified default (English) random game with ID {game_id}.")


def fetch_random_missing_query_params(aws_clients):
    """
    Test fetch_random handler with missing query parameters entirely.
    This should return a 400 status code with an appropriate error message.
    """
    print("Entering function fetch_random_missing_query_params")
    dynamodb = aws_clients["dynamodb"]
    # Import the handler
    from lambdas.fetch_random.handler import handler

    # Call the handler with missing query parameters
    response = handler(c.FETCH_RANDOM_EVENT_MISSING_QUERY_PARAMS, None)

    # Verify the response
    assert response["statusCode"] == 400, f"Expected 400 status code, got {response['statusCode']}"
    response_body = json.loads(response["body"])
    assert "message" in response_body, "Expected 'message' in the response body"
    assert "missing query parameters" in response_body["message"].lower(), \
        "Expected an error message about missing query parameters"

    # Verify no game was added to the database
    assert_table_is_empty(dynamodb, os.environ["GAMES_TABLE"])
    assert_table_is_empty(dynamodb, os.environ["VALID_WORDS_TABLE"])
    assert_table_is_empty(dynamodb, os.environ["METADATA_TABLE"])
    assert_table_is_empty(dynamodb, os.environ["RANDOM_GAMES_TABLE_EN"])
    assert_table_is_empty(dynamodb, os.environ["RANDOM_GAMES_TABLE_ES"])
    assert_table_is_empty(dynamodb, os.environ["RANDOM_GAMES_TABLE_IT"])
    assert_table_is_empty(dynamodb, os.environ["RANDOM_GAMES_TABLE_PL"])

    print("Successfully tested missing query parameters.")


def fetch_random_no_random_games_available(aws_clients):
    """
    Test fetch_random handler for a language with no random games available.
    This should return a 404 status code with an appropriate error message.
    """
    print("Entering function fetch_random_no_random_games_available")
    dynamodb = aws_clients["dynamodb"]
    # Import the handler
    from lambdas.fetch_random.handler import handler

    # Call the handler with a request for Italian, which has no games
    print("Calling the fetch_random handler with Italian language (no random games available)...")
    response = handler(c.FETCH_RANDOM_EVENT_VALID_IT, None)

    # Verify the response
    assert response["statusCode"] == 404, f"Expected 404 status code, got {response['statusCode']}"
    response_body = json.loads(response["body"])
    assert "message" in response_body, "Expected 'message' in the response body"
    assert "no random games available" in response_body["message"].lower(), \
        "Expected an error message about no random games"

    # Verify no game was added to the database
    assert_table_is_empty(dynamodb, os.environ["GAMES_TABLE"])
    assert_table_is_empty(dynamodb, os.environ["VALID_WORDS_TABLE"])
    assert_table_is_empty(dynamodb, os.environ["METADATA_TABLE"])
    assert_table_is_empty(dynamodb, os.environ["RANDOM_GAMES_TABLE_EN"])
    assert_table_is_empty(dynamodb, os.environ["RANDOM_GAMES_TABLE_ES"])
    assert_table_is_empty(dynamodb, os.environ["RANDOM_GAMES_TABLE_IT"])
    assert_table_is_empty(dynamodb, os.environ["RANDOM_GAMES_TABLE_PL"])

    print("Successfully tested no random games available for the specified language.")


def fetch_random_invalid_language(aws_clients):
    """
    Test fetch_random handler with an invalid language code.
    This should return a 400 status code with an appropriate error message.
    """
    print("Entering function fetch_random_invalid_language")
    dynamodb = aws_clients["dynamodb"]
    # Import the handler
    from lambdas.fetch_random.handler import handler

    # Call the handler with the invalid language payload
    print("Calling the fetch_random handler with an invalid language...")
    response = handler(c.FETCH_RANDOM_EVENT_INVALID_LANGUAGE, None)

    # Verify the response
    print("Verifying the response...")
    assert response["statusCode"] == 400, f"Expected 400 status code, got {response['statusCode']}"
    response_body = json.loads(response["body"])
    assert "message" in response_body, "Expected a 'message' key in the response body"
    assert "invalid language" in response_body["message"].lower(), "Expected an error message about invalid language"

    print("Successfully tested fetch_random with an invalid language.")


def fetch_random_invalid_query_params(aws_clients):
    """
    Test fetch_random handler with invalid query parameters format.
    This should return a 400 status code with an appropriate error message.
    """
    print("Entering function fetch_random_invalid_query_params")
    dynamodb = aws_clients["dynamodb"]
    # Import the handler
    from lambdas.fetch_random.handler import handler

    # Call the handler with invalid query parameters
    print("Calling the fetch_random handler with invalid query parameters...")
    response = handler(c.FETCH_RANDOM_EVENT_INVALID_QUERY_PARAMS, None)

    # Verify the response
    print("Verifying the response...")
    assert response["statusCode"] == 400, f"Expected 400 status code, got {response['statusCode']}"
    response_body = json.loads(response["body"])
    assert "message" in response_body, "Expected a 'message' key in the response body"
    assert "missing query parameters" in response_body["message"].lower(), "Expected an error message about missing query parameters"

    print("Successfully tested fetch_random with invalid query parameters.")

def fetch_random_malformed_event(aws_clients):
    """
    Test fetch_random handler with a malformed event payload.
    This should return a 400 status code with an appropriate error message.
    """
    print("Entering function fetch_random_malformed_event")
    dynamodb = aws_clients["dynamodb"]




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

# ===================================================================
# Validate Word Tests
# ===================================================================
def setup_game_and_state(aws_clients):
    """
    Create a known valid game and save its state for testing.
    Returns gameId and sessionId for further tests.
    """
    from lambdas.create_custom.handler import handler as create_handler
    from lambdas.save_user_state.handler import handler as save_handler

    # Step 1: Create a known good game
    response = create_handler(c.CREATE_CUSTOM_EVENT_VALID_EN, None)
    assert response["statusCode"] == 201, f"Game creation failed: {response}"
    response_body = json.loads(response["body"])
    game_id = response_body["gameId"]

    # Step 2: Save initial game state
    initial_state_payload = {
        "body": json.dumps({
            "gameId": game_id,
            "gameLayout": response_body["gameLayout"],
            "sessionId": "test-session-id",
            "wordsUsed": [],
            "originalWordsUsed": []
        }),
        "headers": {"Content-Type": "application/json"}
    }
    save_response = save_handler(initial_state_payload, None)
    assert save_response["statusCode"] == 200, f"Saving game state failed: {save_response}"

    print(f"Game setup complete. gameId: {game_id}, sessionId: test-session-id")
    return game_id, "test-session-id"


def validate_word_successful(aws_clients):
    """Test validating a valid word with all rules adhered to."""
    print("\nTesting function validate_word_successful")
    from lambdas.validate_word.handler import handler as validate_handler
    from lambdas.save_user_state.handler import handler as save_handler

    game_id, session_id = setup_game_and_state(aws_clients)

    # Step 1: Validate a known good word
    response = validate_handler(c.VALIDATE_WORD_SUCCESSFUL_PAYLOAD(game_id), None)

    assert response["statusCode"] == 200, f"Validation failed: {response}"
    response_body = json.loads(response["body"])
    assert response_body["valid"] is True, f"'valid' should be True, but was {response_body['valid']}"
    assert response_body["message"] == "Word is valid.", f"Returned message was {response_body['message']}"
    print("Successfully validated a correct word.")

    # Save the user state for the next tests
    save_response = save_handler(c.SAVE_USER_STATE_PAYLOAD_FOR_VALIDATE_WORD(game_id), None)
    assert save_response["statusCode"] == 200, f"Saving game state failed: {save_response}"

    # Return the game ID for future tests
    return game_id


def validate_word_already_used(aws_clients, game_id):
    """Test validating a word that has already been used."""
    print("\nTesting function validate_word_already_used")
    print(f"Playing game ID", game_id)
    from lambdas.validate_word.handler import handler as validate_handler

    # Validate the same word again from the previous test
    repeated_response = validate_handler(c.VALIDATE_WORD_ALREADY_USED_PAYLOAD(game_id), None)

    print("Repeated response:", repeated_response)

    assert repeated_response["statusCode"] == 200, f"Validation failed for repeated word: {repeated_response}"
    repeated_body = json.loads(repeated_response["body"])
    assert repeated_body["valid"] is False, f"'valid' should be False, but was {repeated_body['valid']}"
    assert "already been used" in repeated_body["message"], f"Returned message was {repeated_body['message']}"

    # Verify that the original user game state is not changed
    user_state = db_utils.get_user_game_state("test-session-id", game_id)
    assert user_state is not None, "User game state should not be None."
    assert user_state["wordsUsed"] == ["VAPORIZE"], f"Unexpected wordsUsed: {user_state['wordsUsed']}"

    print("Successfully validated that the word was already used.")


def validate_word_invalid(aws_clients, game_id):
    """Test validating a word that is not in the valid words list."""
    print("\nTesting function validate_word_invalid")
    print(f"Playing game ID", game_id)
    from lambdas.validate_word.handler import handler as validate_handler

    # Call the validate handler with an invalid word payload
    invalid_response = validate_handler(c.VALIDATE_WORD_INVALID_PAYLOAD(game_id), None)

    print("Invalid response:", invalid_response)

    # Assertions
    assert invalid_response["statusCode"] == 200, f"Validation failed for invalid word: {invalid_response}"
    invalid_body = json.loads(invalid_response["body"])
    assert invalid_body["valid"] is False, f"'valid' should be False, but was {invalid_body['valid']}"
    assert "not valid" in invalid_body["message"], f"Returned message was {invalid_body['message']}"

    # Verify that the original user game state is not changed
    user_state = db_utils.get_user_game_state("test-session-id", game_id)
    assert user_state is not None, "User game state should not be None."
    assert user_state["wordsUsed"] == ["VAPORIZE"], f"Unexpected wordsUsed: {user_state['wordsUsed']}"

    print("Successfully validated that the word was invalid and the game state is unchanged.")


def validate_word_chaining_rule_violation(aws_clients, game_id):
    """Test validating a word that violates the chaining rule."""
    print("\nTesting function validate_word_chaining_rule_violation")
    print(f"Playing game ID", game_id)
    from lambdas.validate_word.handler import handler as validate_handler
    from lambdas.common.db_utils import get_user_game_state

    # Call the validate handler with a word that violates the chaining rule
    chaining_rule_response = validate_handler(c.VALIDATE_WORD_CHAINING_RULE_VIOLATION_PAYLOAD(game_id), None)

    print("Chaining rule response:", chaining_rule_response)

    # Assertions
    assert chaining_rule_response["statusCode"] == 200, f"Validation failed for chaining rule violation: {chaining_rule_response}"
    chaining_rule_body = json.loads(chaining_rule_response["body"])
    assert chaining_rule_body["valid"] is False, f"'valid' should be False, but was {chaining_rule_body['valid']}"
    assert "must start with the last letter of the previous word" in chaining_rule_body["message"], (
        f"Returned message was {chaining_rule_body['message']}"
    )

    # Verify the user state remains unchanged
    user_state = get_user_game_state("test-session-id", game_id)
    assert user_state is not None, "User game state should not be None."
    assert user_state["wordsUsed"] == ["VAPORIZE"], f"Unexpected wordsUsed: {user_state['wordsUsed']}"

    print("Successfully validated chaining rule violation and verified user state remains unchanged.")


def validate_word_successful_chain(aws_clients, game_id):
    """Test validating a word that successfully chains with the previous word."""
    print("\nTesting function validate_word_successful_chain")
    from lambdas.validate_word.handler import handler as validate_handler

    # Payload for validating the next word "ELEMENT", which chains with "VAPORIZE"
    chain_payload = c.VALIDATE_WORD_CHAINING_SUCCESS_PAYLOAD(game_id)

    # Validate the chained word
    response = validate_handler(chain_payload, None)

    print("Chained word validation response:", response)

    # Assertions
    assert response["statusCode"] == 200, f"Expected 200 status code, got {response['statusCode']}."
    response_body = json.loads(response["body"])
    assert response_body["valid"] is True, f"'valid' should be True, but was {response_body['valid']}."
    assert response_body["message"] == "Word is valid.", f"Unexpected message: {response_body['message']}."

    print("Successfully validated a chained word.")


def validate_word_nonexistent_game(aws_clients):
    """Test validating a word for a nonexistent game ID."""
    print("\nTesting function validate_word_nonexistent_game")
    from lambdas.validate_word.handler import handler as validate_handler

    # Call the validate handler with a nonexistent game ID
    response = validate_handler(c.VALIDATE_WORD_NONEXISTENT_GAME_PAYLOAD, None)

    print("Nonexistent game response:", response)

    # Assertions
    assert response["statusCode"] == 404, f"Expected 404 status code, got {response['statusCode']}."
    response_body = json.loads(response["body"])
    assert response_body["valid"] is False, f"'valid' should be False, but was {response_body['valid']}."
    assert "Game with specified game ID not found" in response_body["message"], (
        f"Unexpected message: {response_body['message']}"
    )

    print("Successfully validated nonexistent game ID.")


def validate_word_empty_words_list(aws_clients, game_id):
    """Test validating the first word in a new session (no chaining rule)."""
    print("\nTesting function validate_word_empty_words_list")
    from lambdas.validate_word.handler import handler as validate_handler

    # Validate the first word
    response = validate_handler(c.VALIDATE_WORD_DIFFERENT_SESSION_PAYLOAD(game_id), None)

    print("First word validation response:", response)

    # Assertions
    assert response["statusCode"] == 200, f"Expected 200 status code, got {response['statusCode']}."
    response_body = json.loads(response["body"])
    assert response_body["valid"] is True, f"'valid' should be True, but was {response_body['valid']}."
    assert response_body["message"] == "Word is valid.", f"Unexpected message: {response_body['message']}."

    print("Successfully validated the first word.")


def validate_word_missing_parameters(aws_clients):
    """Test validating a word with missing required parameters."""
    print("\nTesting function validate_word_missing_parameters")
    from lambdas.validate_word.handler import handler as validate_handler

    # Missing gameId in the payload
    missing_game_id_payload = c.VALIDATE_WORD_MISSING_GAME_ID_PAYLOAD

    response_missing_game_id = validate_handler(missing_game_id_payload, None)
    print("Response with missing gameId:", response_missing_game_id)

    # Assertions for missing gameId
    assert response_missing_game_id["statusCode"] == 400, (
        f"Expected 400 status code for missing gameId, got {response_missing_game_id['statusCode']}."
    )
    response_body = json.loads(response_missing_game_id["body"])
    assert response_body["valid"] is False, f"'valid' should be False, but was {response_body['valid']}."
    assert "gameId" in response_body["message"], f"Expected error message to mention 'gameId', but got: {response_body['message']}."

    # Missing word in the payload
    missing_word_payload = c.VALIDATE_WORD_MISSING_WORD_PAYLOAD

    response_missing_word = validate_handler(missing_word_payload, None)
    print("Response with missing word:", response_missing_word)

    # Assertions for missing word
    assert response_missing_word["statusCode"] == 400, (
        f"Expected 400 status code for missing word, got {response_missing_word['statusCode']}."
    )
    response_body = json.loads(response_missing_word["body"])
    assert response_body["valid"] is False, f"'valid' should be False, but was {response_body['valid']}."
    assert "word" in response_body["message"], f"Expected error message to mention 'word', but got: {response_body['message']}."

    # Missing sessionId in the payload
    missing_session_id_payload = c.VALIDATE_WORD_MISSING_SESSION_ID_PAYLOAD

    response_missing_session_id = validate_handler(missing_session_id_payload, None)
    print("Response with missing sessionId:", response_missing_session_id)

    # Assertions for missing sessionId
    assert response_missing_session_id["statusCode"] == 400, (
        f"Expected 400 status code for missing sessionId, got {response_missing_session_id['statusCode']}."
    )
    response_body = json.loads(response_missing_session_id["body"])
    assert response_body["valid"] is False, f"'valid' should be False, but was {response_body['valid']}."
    assert "sessionId" in response_body["message"], f"Expected error message to mention 'sessionId', but got: {response_body['message']}."

    print("Successfully tested validation for missing required parameters.")


def validate_word_invalid_json(aws_clients):
    """Test validating a word with malformed JSON in the event body."""
    print("\nTesting function validate_word_invalid_json")
    from lambdas.validate_word.handler import handler as validate_handler

    # Malformed JSON payload
    malformed_json_payload = c.VALIDATE_WORD_INVALID_JSON_PAYLOAD

    # Call the handler with malformed JSON
    response = validate_handler(malformed_json_payload, None)
    print("Response with malformed JSON:", response)

    # Assertions
    assert response["statusCode"] == 400, (
        f"Expected 400 status code for malformed JSON, got {response['statusCode']}."
    )
    response_body = json.loads(response["body"])
    assert response_body["valid"] is False, f"'valid' should be False, but was {response_body['valid']}."
    assert "Invalid JSON" in response_body["message"], (
        f"Expected error message to mention 'Invalid JSON', but got: {response_body['message']}."
    )

    print("Successfully tested validation for malformed JSON.")
