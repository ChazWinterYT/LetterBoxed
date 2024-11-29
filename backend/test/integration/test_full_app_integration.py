import sys
import os
import boto3
import json
import pytest
import constants as c
import helper_functions as f

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

@pytest.fixture(scope="module")
def setup_environment():
    # Set up environment variables
    os.environ["S3_BUCKET_NAME"] = "test-dictionary-bucket"
    os.environ["DICTIONARY_BASE_S3_PATH"] = "Dictionaries/"
    os.environ["DEFAULT_LANGUAGE"] = "en"
    os.environ["GAMES_TABLE"] = "LetterBoxedGamesTest"
    os.environ["VALID_WORDS_TABLE"] = "LetterBoxedValidWords1Test"
    os.environ["SESSION_STATES_TABLE"] = "LetterBoxedSessionStatesTest"
    os.environ["METADATA_TABLE"] = "LetterBoxedMetadataTableTest"
    os.environ["ARCHIVE_TABLE"] = "LetterBoxedArchiveTest"
    os.environ["RANDOM_GAMES_TABLE_EN"] = "LetterBoxedRandomGames_enTest"
    os.environ["RANDOM_GAMES_TABLE_ES"] = "LetterBoxedRandomGames_esTest"
    os.environ["RANDOM_GAMES_TABLE_IT"] = "LetterBoxedRandomGames_itTest"
    os.environ["RANDOM_GAMES_TABLE_PL"] = "LetterBoxedRandomGames_plTest"

    # Define constants for table names
    DYNAMO_DB_TABLE_NAMES = [
        os.environ["GAMES_TABLE"],
        os.environ["VALID_WORDS_TABLE"],
        os.environ["SESSION_STATES_TABLE"],
        os.environ["METADATA_TABLE"],
        os.environ["ARCHIVE_TABLE"],
        os.environ["RANDOM_GAMES_TABLE_EN"],
        os.environ["RANDOM_GAMES_TABLE_ES"],
        os.environ["RANDOM_GAMES_TABLE_IT"],
        os.environ["RANDOM_GAMES_TABLE_PL"],
    ]

    # Yield to run the tests
    yield DYNAMO_DB_TABLE_NAMES

    # Clean up environment variables
    os.environ.pop("S3_BUCKET_NAME", None)
    os.environ.pop("DICTIONARY_BASE_S3_PATH", None)
    os.environ.pop("DEFAULT_LANGUAGE", None)
    os.environ.pop("GAMES_TABLE", None)
    os.environ.pop("VALID_WORDS_TABLE", None)
    os.environ.pop("SESSION_STATES_TABLE", None)
    os.environ.pop("METADATA_TABLE", None)
    os.environ.pop("ARCHIVE_TABLE", None)
    os.environ.pop("RANDOM_GAMES_TABLE_EN", None)
    os.environ.pop("RANDOM_GAMES_TABLE_ES", None)
    os.environ.pop("RANDOM_GAMES_TABLE_IT", None)
    os.environ.pop("RANDOM_GAMES_TABLE_PL", None)

@pytest.fixture(scope="module")
def aws_clients():
    """
    Fixture to initialize AWS clients.
    """
    dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
    s3 = boto3.client("s3", region_name="us-east-1")
    lambda_client = boto3.client("lambda", region_name="us-east-1")
    return {"dynamodb": dynamodb, "s3": s3, "lambda_client": lambda_client}

@pytest.fixture(scope="module")
def setup_aws_resources(setup_environment, aws_clients):
    dynamodb = aws_clients["dynamodb"]
    s3 = aws_clients["s3"]
    DYNAMO_DB_TABLE_NAMES = setup_environment
    
    # Cleanup before tests
    cleanup_dynamodb_tables(dynamodb, DYNAMO_DB_TABLE_NAMES)
    assert_tables_empty(dynamodb, DYNAMO_DB_TABLE_NAMES)
    
    # Run the tests
    yield
    
    # Cleanup after tests
    # cleanup_dynamodb_tables(dynamodb, DYNAMO_DB_TABLE_NAMES)
    # assert_tables_empty(dynamodb, DYNAMO_DB_TABLE_NAMES)

# Function intentionally misspelled "est" to prevent integration tests from running when not needed
# When ready to test, change "est_full_app_integration" to "test_full_app_integration"
def test_full_app_integration(setup_environment, aws_clients, setup_aws_resources):
    dynamodb = aws_clients["dynamodb"]
    s3 = aws_clients["s3"]
    lambda_client = aws_clients["lambda_client"]


    # ===========================================================================
    # Begin Integration Tests
    # ===========================================================================
    print("BEGINNING INTEGRATION TESTS...")

    # First try a bunch of invalid game scenarios. These should not add any entries to the DB
    # We will assert that the database is empty for each of these tests. 
    f.create_custom_missing_layout(aws_clients)
    f.create_custom_invalid_layout(aws_clients)
    f.create_custom_size_mismatch(aws_clients)
    f.create_custom_unsupported_language(aws_clients)
    f.create_custom_malformed_json(aws_clients)

    f.create_random_unsupported_language(aws_clients)
    f.create_random_invalid_board_size(aws_clients)
    f.create_random_invalid_seed_words(aws_clients)
    f.create_random_malformed_json(aws_clients)
    f.create_random_missing_body(aws_clients)

    f.fetch_game_missing_game_id(aws_clients)
    f.fetch_game_nonexistent_game_id(aws_clients)
    f.fetch_game_invalid_json(aws_clients)
    f.fetch_game_internal_server_error(aws_clients)
    f.fetch_game_optional_field_defaults(aws_clients)

    f.save_user_state_missing_parameters(aws_clients)
    f.save_user_state_invalid_json(aws_clients)
    f.save_user_state_nonexistent_game(aws_clients)

    f.fetch_user_state_missing_params(aws_clients)
    f.fetch_user_state_nonexistent(aws_clients)
    f.fetch_user_state_malformed_event(aws_clients)

    # Now we'll handle tests that result in writes to the database

    # Create a custom game, and fetch a game by game ID
    print("Testing create_custom and fetch_game lambdas...")
    game_id = f.create_custom_english_game(aws_clients)
    f.create_custom_spanish_game(aws_clients)
    f.create_custom_4x4_game_english(aws_clients)
    f.create_custom_4x4_game_spanish(aws_clients)
    f.fetch_game_valid_game_id(aws_clients, game_id)

    # Create a random game
    print("Testing create_random lambda...")
    f.create_random_valid_en(aws_clients)
    f.create_random_valid_es(aws_clients)
    f.create_random_valid_en_with_seed(aws_clients)
    f.create_random_valid_es_with_seed(aws_clients)
    f.create_random_valid_4x4_with_seed_en(aws_clients)
    f.create_random_valid_4x4_with_seed_es(aws_clients)

    # Save a user game state
    print("Testing save_user_state and fetch_user_state lambdas...")
    f.save_user_state_valid_initial_state_en(aws_clients)
    f.save_user_state_valid_update_state_en(aws_clients)
    f.save_user_state_game_completion_en(aws_clients)
    f.save_user_state_valid_initial_state_es(aws_clients)
    f.save_user_state_valid_update_state_es(aws_clients)
    f.save_user_state_game_completion_es(aws_clients)
    f.save_user_state_same_session_different_games(aws_clients)
    f.save_user_state_same_game_different_sessions(aws_clients)
    f.fetch_user_state_valid(aws_clients)
    


# ===========================================================================
# Cleanup and Table Checking Utilities
# ===========================================================================
def cleanup_dynamodb_tables(dynamodb, table_names):
    for current_table in table_names:
        try:
            table = dynamodb.Table(current_table)

            # Retrieve the key schema to determine the key names dynamically
            key_schema = table.key_schema
            key_names = [key["AttributeName"] for key in key_schema]

            response = table.scan()
            with table.batch_writer() as batch:
                for item in response.get("Items", []):
                    # Dynamically build the key dictionary
                    key = {key_name: item[key_name] for key_name in key_names}
                    batch.delete_item(Key=key)
        except dynamodb.meta.client.exceptions.ResourceNotFoundException:
            print(f"Table {current_table} does not exist. Skipping cleanup.")
        except Exception as e:
            print(f"Error cleaning table {current_table}: {e}")

def assert_tables_empty(dynamodb, table_names):
    for current_table in table_names:
        table = dynamodb.Table(current_table)
        print(f"Verifying {current_table} is empty...")
        scan = table.scan()
        assert scan["Count"] == 0, f"Table {current_table} is not empty. Found items: {scan['Items']}"

def assert_dynamodb_item_exists(dynamodb, game_id):
    """Assert that a specific item exists in DynamoDB."""
    table = dynamodb.Table(games_table_name)
    response = table.get_item(Key={"gameId": game_id})
    assert "Item" in response, f"Item with gameId {game_id} not found in {table}."
    print(f"Item with gameId {game_id} was found in DynamoDB table.")

