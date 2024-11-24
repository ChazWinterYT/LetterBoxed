import json
from typing import Dict, Any
from lambdas.common.db_utils import add_game_to_db, add_game_id_to_random_games_db
from lambdas.common.dictionary_utils import get_dictionary
from lambdas.common.game_schema import create_game_schema
from lambdas.create_random.random_game_service import create_random_game


MAX_RETRIES = 5  # Maximum number of retries for ValueError exceptions

def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    try:
        # Parse parameters for the event
        body = json.loads(event.get("body", "{}"))
        seed_words = body.get("seedWords", None) # Use seed words if provided
        language = body.get("language", "en")  # Default to English
        board_size = body.get("boardSize", "3x3")  # Default to 3x3

        # Retry random game creation if it fails
        random_game_data = retry_random_game_creation(language, board_size, seed_words)

        # Return the game details
        return {
            "statusCode": 201,
            "body": json.dumps({
                "message": "Random game created successfully.",
                "gameId": random_game_data["gameId"],
                "gameLayout": random_game_data["gameLayout"],
            })
        }
    except ValueError as e:
        print(f"Handler failed: {e}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)}),
        }


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
    