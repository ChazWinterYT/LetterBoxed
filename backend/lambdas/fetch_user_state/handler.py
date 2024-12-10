import json
from typing import Dict, Any
from lambdas.common.db_utils import get_user_game_state
from lambdas.common.response_utils import error_response, HEADERS


def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Lambda handler for fetching user session state.
    
    Args:
        event (dict): The API Gateway event object.
        context: The Lambda context object.
    
    Returns:
        dict: The HTTP response object.
    """
    try:
        # Extract sessionId and gameId from parameters
        path_params = event.get("pathParameters")
        query_params = event.get("queryStringParameters")

        if not isinstance(path_params, dict):
            return error_response("Invalid or missing path parameters.", 400)

        if not isinstance(query_params, dict):
            return error_response("Invalid or missing query parameters.", 400)

        if not path_params or not query_params:
            return error_response("Missing path or query parameters.", 400)

        session_id = path_params.get("sessionId")
        game_id = query_params.get("gameId")

        if not session_id or not game_id:
            return error_response("sessionId and gameId are required.", 400)
        
        # Fetch user game state
        game_state = get_user_game_state(session_id, game_id)
        
        if not game_state:
            return error_response("User game state not found.", 404)
        
        # Return the game state
        return {
            "statusCode": 200,
            "headers": HEADERS,
            "body": json.dumps(game_state),
        }
    except Exception as e:
        print(f"Error fetching game state: {e}")
        return error_response("Internal server error.", 500)
