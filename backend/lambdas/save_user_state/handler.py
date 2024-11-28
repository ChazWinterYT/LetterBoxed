import json
from typing import Dict, Any
import time
from lambdas.common.db_utils import save_user_session_state, get_user_game_state
from lambdas.common.game_utils import check_game_completion
from lambdas.common.response_utils import error_response


def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Lambda handler for saving user session state.
    
    Args:
        event (dict): The API Gateway event object.
        context: The Lambda context object.
    
    Returns:
        dict: The HTTP response object.
    """
    try:
        # Extract parameters from the event
        body = json.loads(event.get('body', '{}'))
        game_layout = body.get('gameLayout')
        game_id = body.get('gameId')
        session_id = body.get('sessionId')

        # Validate required parameters
        if not game_layout or not game_id or not session_id:
            return error_response(
                "Missing required parameters: gameLayout, gameId or sessionId.", 400
            )

        # Fetch the user game state
        user_game_state = get_user_game_state(session_id, game_id)
        if not user_game_state:
            # Initialize a new game state if it doesn't exist
            user_game_state = {
                "sessionId": session_id,
                "gameId": game_id,
                "wordsUsed": [],
                "originalWordsUsed": [], # May contain accents or special characters
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
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "OPTIONS,GET,PUT",
                "Access-Control-Allow-Headers": "Content-Type,Authorization",
            },
            "body": json.dumps({
                "message": message,
                "gameCompleted": game_completed,
                "wordsUsed": user_game_state["wordsUsed"],
                "originalWordsUsed": user_game_state["originalWordsUsed"],
                "lastUpdated": updated_time,
            }),
        }

    except Exception as e:
        print(f"Error during state saving: {e}")
        return error_response(f"An unexpected error occurred: {e}", 500)
    