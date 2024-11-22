import json
from typing import Dict, Any

from lambdas.common.db_utils import add_game_to_db, add_valid_words_to_db
from lambdas.common.game_utils import generate_valid_words
from lambdas.common.game_schema import create_game_schema, validate_board_matches_layout


def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    # Parse the event body
    body = json.loads(event.get("body", "{}"))
    game_layout = body.get("gameLayout")
    created_by = body.get("sessionId", "")
    language = body.get("language", "en")  # Default to English
    board_size = body.get("boardSize", "3x3")  # Default to 3x3

    # Validate input
    if not game_layout:
        return {
            "statusCode": 400,
            "body": json.dumps({"message": "Game Layout is required."})
        }

    if not validate_board_matches_layout(game_layout, board_size):
        return {
            "statusCode": 400,
            "body": json.dumps({"message": "Game layout does not match board size."})
        }

    # Create the game schema
    try:
        game_data = create_game_schema(
            game_layout=game_layout,
            board_size=board_size,
            language=language,
            created_by=created_by,
            game_type="custom",
        )
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"message": f"Failed to create game schema: {e}"})
        }

    # Save the new game schema and valid words to the database
    add_game_to_db(game_data)
    add_valid_words_to_db(game_data["gameId"], game_data["validWords"])

    return {
        "statusCode": 200,
        "body": json.dumps({
            "gameId": game_data["gameId"],
            "message": "Game created successfully."
        })
    }
