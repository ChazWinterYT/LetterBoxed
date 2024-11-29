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

    print("Test for create_custom_english_game passed successfully.")


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
    assert "unsupported language" in response_body["message"].lower(), "Expected an error message about unsupported language"

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
