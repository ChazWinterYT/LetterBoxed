import json
from typing import Dict, Any
from lambdas.common.db_utils import fetch_game_by_id
from lambdas.common.response_utils import error_response, HEADERS
from lambdas.rate_game.rate_game_service import rate_game


def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Lambda handler for adding a game rating and saving it to the game object.
    
    Args:
        event (dict): The API Gateway event object.
        context: The Lambda context object.
    
    Returns:
        dict: The HTTP response object.
    """
    try:
        # Parse the body of the request
        body = json.loads(event.get("body", "{}"))
        game_id = body.get("gameId")
        stars = body.get("stars")
        
        if not game_id or stars is None:
            return error_response(f"Missing required parameters: Game ID and Stars are required.", 400)
        
        if not isinstance(stars, int) or stars < 1 or stars > 5:
            return error_response("Invalid 'stars' value: must be an integer between 1 and 5.", 400)
        
        # Fetch the game object from the DB
        game = fetch_game_by_id(game_id)
        if not game:
            return error_response("Game not found in DB", 404)
        
        # Call the service function
        success = rate_game(game, stars)
        
        if success:
            new_review_count = game["totalRatings"] + 1
            new_star_count = game["totalStars"] + stars
            return {
                "statusCode": 200,
                "headers": HEADERS,
                "body": json.dumps({
                    "message": "Game rated successfully.",
                    "newReviewCount": new_review_count,
                    "newStarCount": new_star_count,                    
                })
            }
        else:
            return error_response("Failed to rate the game.", 500)
        
    except json.JSONDecodeError:
        return error_response("Invalid JSON in request body.", 400)
    except Exception as e:
        return error_response(f"An unexpected error occurred: {str(e)}", 500)