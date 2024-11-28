import json
import logging
from typing import Dict, Any
from lambdas.common.db_utils import fetch_game_by_id
from lambdas.common.response_utils import error_response

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    logger.info(f"Received event: {json.dumps(event)}")

    # Parse gameId from path parameters
    try:
        # Ensure the event body is valid JSON
        body = json.loads(event.get("body", "{}"))
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error: {str(e)}")
        return error_response("Invalid JSON format in request body.", 400)

    # Parse gameId from path parameters
    game_id = body.get("gameId") or event.get("pathParameters", {}).get("gameId")
    if not game_id:
        logger.error("Missing gameId in request")
        return error_response("Invalid input: gameId is required.", 400)
    
    # Fetch the game from the database
    try:
        game_data = fetch_game_by_id(game_id)
        if not game_data:
            logger.warning(f"Game ID {game_id} not found")
            return error_response("Game ID not found.", 404)
    except Exception as e:
        logger.error(f"Error fetching game: {str(e)}")
        return error_response(f"Internal server error: {e}", 500)
        
    # Return game details
    return {
        "statusCode": 200,
        "headers": {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "OPTIONS,GET,POST",
            "Access-Control-Allow-Headers": "Content-Type,Authorization",
        },
        "body": json.dumps({
            "gameId": game_id,
            "gameLayout": game_data.get("gameLayout"),
            "boardSize": game_data.get("boardSize", "3x3"), # Default to 3x3
            "language": game_data.get("language", "en"), # Default to English
            "message": "Game fetched successfully."
        })
    }
