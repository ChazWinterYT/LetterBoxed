import json
from typing import Dict, Any, Optional
from lambdas.common.db_utils import add_game_to_db, add_game_id_to_random_games_db
from lambdas.common.dictionary_utils import get_dictionary
from lambdas.common.game_schema import create_game_schema, validate_board_size, validate_language
from lambdas.create_random.random_game_service import create_random_game
from lambdas.common.response_utils import error_response


MAX_RETRIES = 5  # Maximum number of retries for ValueError exceptions

def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    try:
        # Check if the body is None before parsing
        if event.get("body") is None:
            return error_response("Missing body in JSON event.", 400)
            
        # Parse parameters for the event
        body = json.loads(event.get("body"))

        seed_words = body.get("seedWords", None) # Use seed words if provided
        language = body.get("language", "en")  # Default to English
        board_size = body.get("boardSize", "3x3")  # Default to 3x3

        # Validate language and board size
        if not validate_board_size(board_size):
            return error_response("Input contains an invalid board size.", 400)
        if not validate_language(language):
            return error_response("Input contains an unsupported language.", 400)

        # Retry random game creation if it fails
        random_game_data = retry_random_game_creation(language, board_size, seed_words)

        # Return the game details
        return {
            "statusCode": 201,
            "headers": {
                "Access-Control-Allow-Origin": "*",  # Allow all origins
                "Access-Control-Allow-Methods": "OPTIONS,GET,POST",  # Allowed methods
                "Access-Control-Allow-Headers": "Content-Type,Authorization",  # Allowed headers
            },
            "body": json.dumps({
                "message": "Random game created successfully.",
                "gameId": random_game_data["gameId"],
                "gameLayout": random_game_data["gameLayout"],
            })
        }
    except json.JSONDecodeError as e:
        return error_response("JSON decoding error.", 400)
    except ValueError as e:
        print(f"Handler failed due to ValueError: {e}")
        return error_response("Could not create a random game from the given seed words.", 400)
    except Exception as e:
        print(f"Handler failed: {e}")
        return error_response(f"There was a problem creating the game: {e}", 500)


def retry_random_game_creation(language: str, board_size: str, seed_words: Optional[tuple[str, str]]) -> Dict[str, Any]:
    retries = 0
    while retries < MAX_RETRIES:
        try:
            # Create a random game
            return create_random_game(language, board_size, seed_words)
        except ValueError as e:
            retries += 1
            print(f"Retrying ({retries}/{MAX_RETRIES}) due to error generating game: {e}")
    raise ValueError("Failed to create a random game after multiple retries.")
    