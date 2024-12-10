import json
import logging
from typing import Dict, Any
import time
from lambdas.common.db_utils import save_user_session_state, get_user_game_state
from lambdas.common.game_utils import check_game_completion
from lambdas.common.response_utils import error_response, HEADERS


_logger = logging.getLogger(__name__)

def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Lambda handler for saving user session state.
    
    Args:
        event (dict): The API Gateway event object.
        context: The Lambda context object.
    
    Returns:
        dict: The HTTP response object.
    """
    # Parse and validate the event body
    try:
        body = json.loads(event.get("body", "{}"))
    except json.JSONDecodeError as e:
        _logger.error(f"JSON decode error: {str(e)}")
        return error_response("Invalid JSON format in request body.", 400)

    # Extract required parameters
    game_layout = body.get('gameLayout')
    game_id = body.get('gameId')
    session_id = body.get('sessionId')

    # Validate presence of required parameters
    if not game_layout or not game_id or not session_id:
        _logger.error("Missing required parameters: gameLayout, gameId, or sessionId.")
        return error_response(
            "Missing required parameters: gameLayout, gameId, or sessionId.", 400
        )

    try:
        # Fetch the user game state
        user_game_state = get_user_game_state(session_id, game_id)
        if not user_game_state:
            # Initialize a new game state if it doesn't exist
            user_game_state = {
                "sessionId": session_id,
                "gameId": game_id,
                "wordsUsed": [],
                "originalWordsUsed": [],  # May contain accents or special characters
                "gameCompleted": False,
                "lastUpdated": int(time.time()),
                "TTL": int(time.time()) + 30 * 24 * 60 * 60,  # 30 days TTL
            }

        # Update the game state based on the request body
        if "wordsUsed" in body:
            user_game_state["wordsUsed"] = body["wordsUsed"]
            user_game_state["originalWordsUsed"] = body["originalWordsUsed"]

        # Check for game completion
        game_completed, message = check_game_completion(game_layout, user_game_state["wordsUsed"])
        user_game_state["gameCompleted"] = game_completed

        # Update timestamps
        updated_time = int(time.time())
        user_game_state["lastUpdated"] = updated_time
        user_game_state["TTL"] = updated_time + 30 * 24 * 60 * 60  # Extend TTL

        # Save the updated game state
        save_user_session_state(user_game_state)

        return {
            "statusCode": 200,
            "headers": HEADERS,
            "body": json.dumps({
                "message": message,
                "gameId": game_id,
                "sessionId": session_id,
                "gameCompleted": game_completed,
                "wordsUsed": user_game_state["wordsUsed"],
                "originalWordsUsed": user_game_state["originalWordsUsed"],
                "lastUpdated": updated_time,
            }),
        }

    except Exception as e:
        _logger.error(f"Error during state saving: {e}")
        return error_response(f"An unexpected error occurred: {e}", 500)
    