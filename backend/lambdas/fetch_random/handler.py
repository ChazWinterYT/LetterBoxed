import json
import random
from typing import Dict, Any
from lambdas.common.db_utils import (
    fetch_random_game_count,
    fetch_game_id_from_random_games_db,
    fetch_game_by_id
)
from lambdas.common.game_schema import validate_board_size, validate_language
from lambdas.common.response_utils import error_response


def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Lambda handler for fetching a random game for a specified language.
    
    Args:
        event (dict): The API Gateway event object.
        context: The Lambda context object.
    
    Returns:
        dict: The HTTP response object.
    """
    # Extract and validate query parameters
    query_params = event.get("queryStringParameters", {})
    if query_params is None:
        return error_response("Missing query parameters.", 400)
    
    language = query_params.get("language", "en") # Default to English

    # Fetch metadata for the random game count
    max_atomic_number = fetch_random_game_count(language)
    
    if not isinstance(max_atomic_number, int) or max_atomic_number < 1:
        return error_response("No random games available for the specified language.", 404)
    
    try:
        # Select a random atomic number
        random_atomic_number = random.randint(1, max_atomic_number)
        print(f"Selected random atomic number: {random_atomic_number}")

        # Fetch game ID using the atomic number
        game_id = fetch_game_id_from_random_games_db(random_atomic_number, language)
        if not game_id:
            return error_response("Game ID not found when fetching raandom game", 500)

        # Fetch the full game details using the game ID
        game_data = fetch_game_by_id(game_id)
        if not game_data:
            return error_response("Game data not found for the fetched game ID.", 500)
        
        # Return the game details
        return {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "OPTIONS,GET",
                "Access-Control-Allow-Headers": "Content-Type,Authorization",
            },
            "body": json.dumps({
                "message": "Random game fetched successfully.",
                "gameId": game_id,
                "gameLayout": game_data["gameLayout"],
                "language": game_data["language"],
                "boardSize": game_data["boardSize"],
                "hint": game_data["clue"],
            })
        }
    except Exception as e:
        print(f"Error fetching random game: {e}")
        return error_response("Internal server error.", 500)