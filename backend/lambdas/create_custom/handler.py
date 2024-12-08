import json
from typing import Dict, Any

from lambdas.common.db_utils import add_game_to_db
from lambdas.common.game_utils import generate_valid_words
from lambdas.common.game_schema import create_game_schema, validate_board_matches_layout
from lambdas.common.response_utils import error_response


def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    # Parse the event body
    try:
        body = json.loads(event.get("body", "{}"))
    except json.JSONDecodeError as e:
        return error_response("Invalid JSON.", 400)

    game_layout = body.get("gameLayout")
    created_by = body.get("sessionId", "")
    language = body.get("language", "en")  # Default to English
    board_size = body.get("boardSize", "3x3")  # Default to 3x3

    # Validate input
    if not game_layout:
        return error_response("Game Layout is required.", 400)

    # Create the game schema
    try:
        game_data = create_game_schema(
            game_layout=game_layout,
            board_size=board_size,
            language=language,
            created_by=created_by,
            game_type="custom",
        )
    except ValueError as e:
        return error_response("Custom game specs are invalid.", 400)
    except Exception as e:
        return error_response(f"Failed to create game schema: {e}", 500)

    # Save the new game schema to the database
    add_game_to_db(game_data)

    return {
        "statusCode": 201,
        "headers": {
            "Access-Control-Allow-Origin": "*",  # Allow all origins
            "Access-Control-Allow-Methods": "OPTIONS,GET,POST",  # Allowed methods
            "Access-Control-Allow-Headers": "Content-Type,Authorization",  # Allowed headers
        },
        "body": json.dumps({
            "gameId": game_data["gameId"],
            "gameLayout": game_data["gameLayout"],
            "oneWordSolutionCount": game_data["oneWordSolutionCount"],
            "twoWordSolutionCount": game_data["twoWordSolutionCount"],
            "validWordCount": game_data["validWordCount"],
            "message": "Game created successfully."
        })
    }
