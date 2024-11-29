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
    assert response["statusCode"] == 200, f"Expected 200 status code, got {response['statusCode']}"
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
    assert response["statusCode"] == 200, f"Expected 200 status code, got {response['statusCode']}"
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
    assert response["statusCode"] == 200, f"Expected 200 status code, got {response['statusCode']}"
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
    assert response["statusCode"] == 200, f"Expected 200 status code, got {response['statusCode']}"
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
    print(f"Verified table {os.environ['GAMES_TABLE']} is empty.")
    assert_table_is_empty(dynamodb, os.environ["VALID_WORDS_TABLE"])
    print(f"Verified table {os.environ['VALID_WORDS_TABLE']} is empty.")
    assert_table_is_empty(dynamodb, os.environ["METADATA_TABLE"])
    print(f"Verified table {os.environ['METADATA_TABLE']} is empty.")
    assert_table_is_empty(dynamodb, os.environ["RANDOM_GAMES_TABLE_EN"])
    print(f"Verified table {os.environ['RANDOM_GAMES_TABLE_EN']} is empty.")
    assert_table_is_empty(dynamodb, os.environ["RANDOM_GAMES_TABLE_ES"])
    print(f"Verified table {os.environ['RANDOM_GAMES_TABLE_ES']} is empty.")

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
    print("Verified: No game was added to the games DB.")
    assert_table_is_empty(dynamodb, os.environ["VALID_WORDS_TABLE"])
    print("Verified: No valid words were added to the valid words DB.")
    assert_table_is_empty(dynamodb, os.environ["METADATA_TABLE"])
    print("Verified: No metadata was added to the metadata DB.")
    assert_table_is_empty(dynamodb, os.environ["RANDOM_GAMES_TABLE_EN"])
    print("Verified: No random games were added to the random games table (English).")
    assert_table_is_empty(dynamodb, os.environ["RANDOM_GAMES_TABLE_ES"])
    print("Verified: No random games were added to the random games table (Spanish).")

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
    print("Verified: No game was added to the games DB.")
    assert_table_is_empty(dynamodb, os.environ["VALID_WORDS_TABLE"])
    print("Verified: No valid words were added to the valid words DB.")
    assert_table_is_empty(dynamodb, os.environ["METADATA_TABLE"])
    print("Verified: No metadata was added to the metadata DB.")
    assert_table_is_empty(dynamodb, os.environ["RANDOM_GAMES_TABLE_EN"])
    print("Verified: No random games were added to the random games table (English).")
    assert_table_is_empty(dynamodb, os.environ["RANDOM_GAMES_TABLE_ES"])
    print("Verified: No random games were added to the random games table (Spanish).")

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
    print("Verified: No game was added to the games DB.")
    assert_table_is_empty(dynamodb, os.environ["VALID_WORDS_TABLE"])
    print("Verified: No valid words were added to the valid words DB.")
    assert_table_is_empty(dynamodb, os.environ["METADATA_TABLE"])
    print("Verified: No metadata was added to the metadata DB.")
    assert_table_is_empty(dynamodb, os.environ["RANDOM_GAMES_TABLE_EN"])
    print("Verified: No random games were added to the random games table (English).")
    assert_table_is_empty(dynamodb, os.environ["RANDOM_GAMES_TABLE_ES"])
    print("Verified: No random games were added to the random games table (Spanish).")

    print("Successfully tested create_random with a missing body.")


# ===================================================================
# Fetch Game Handler tests
# ===================================================================
def fetch_game_valid_game_id(aws_clients, game_id):
    """
    Test fetch_game flow with a valid gameId taken from a previous integration test.
    This should return a 200 status code and the expected game details.
    """
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
    pass


def fetch_game_nonexistent_game_id(aws_clients):
    """
    Test fetch_game handler with a non-existent gameId.
    This should return a 404 status code with an appropriate error message.
    """
    pass


def fetch_game_invalid_json(aws_clients):
    """
    Test fetch_game handler with a malformed JSON payload.
    This should return a 400 status code with an appropriate error message.
    """
    pass


def fetch_game_internal_server_error(aws_clients):
    """
    Test fetch_game handler when the database fetch raises an exception.
    This should return a 500 status code with an appropriate error message.
    """
    pass


def fetch_game_optional_field_defaults(aws_clients):
    """
    Test fetch_game handler with optional fields missing in the fetched game data.
    This should verify that default values are correctly populated.
    """
    pass


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


def fetch_user_state_valid(aws_clients):
    """
    Test fetching a valid user state.
    Should return a 200 status code with the correct game state.
    """
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
    response = handler(FETCH_USER_STATE_VALID, None)

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
    # Import the handler
    from lambdas.fetch_user_state.handler import handler

    # Call the handler
    response = handler(FETCH_USER_STATE_MISSING_PARAMS, None)

    # Verify response
    assert response["statusCode"] == 400, f"Expected 400 status code, got {response['statusCode']}"
    response_body = json.loads(response["body"])
    assert "message" in response_body, "Expected 'message' key in response body"
    assert "sessionId and gameId are required" in response_body["message"], "Expected missing parameter error message"

    print("Successfully handled missing parameters.")


def fetch_user_state_nonexistent(aws_clients):
    """
    Test fetching a user state for a non-existent game state.
    Should return a 404 status code.
    """
    # Import the handler
    from lambdas.fetch_user_state.handler import handler

    # Call the handler
    response = handler(FETCH_USER_STATE_NONEXISTENT, None)

    # Verify response
    assert response["statusCode"] == 404, f"Expected 404 status code, got {response['statusCode']}"
    response_body = json.loads(response["body"])
    assert "message" in response_body, "Expected 'message' key in response body"
    assert "User game state not found" in response_body["message"], "Expected not found error message"

    print("Successfully handled non-existent user state.")


def fetch_user_state_malformed_event(aws_clients):
    """
    Test fetching a user state with a malformed event.
    Should return a 400 status code.
    """
    # Import the handler
    from lambdas.fetch_user_state.handler import handler

    # Call the handler
    response = handler(FETCH_USER_STATE_MALFORMED_EVENT, None)

    # Verify response
    assert response["statusCode"] == 400, f"Expected 400 status code, got {response['statusCode']}"
    response_body = json.loads(response["body"])
    assert "message" in response_body, "Expected 'message' key in response body"
    assert "sessionId and gameId are required" in response_body["message"], "Expected missing parameter error message"

    print("Successfully handled malformed event.")

# ===================================================================
# Save User State Lambda Tests
# ===================================================================
def fetch_user_state_internal_server_error(aws_clients):
    """
    Simulate an internal server error during fetching.
    Should return a 500 status code.
    """
    from lambdas.fetch_user_state.handler import handler
    from lambdas.common.db_utils import get_user_game_state

    # Mock the get_user_game_state function to raise an exception
    import pytest
    pytest_mock = pytest.importorskip("pytest_mock")
    mocker = pytest_mock.MockerFixture()
    mocker.patch("lambdas.common.db_utils.get_user_game_state", side_effect=Exception("Simulated internal server error"))

    # Call the handler
    response = handler(FETCH_USER_STATE_VALID_BUT_INTERNAL_ERROR, None)

    # Verify response
    assert response["statusCode"] == 500, f"Expected 500 status code, got {response['statusCode']}"
    response_body = json.loads(response["body"])
    assert "message" in response_body, "Expected 'message' key in response body"
    assert "internal server error" in response_body["message"].lower(), "Expected internal server error message"

    print("Successfully handled internal server error.")


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
