import json
from typing import Dict, Any
from lambdas.common.db_utils import fetch_game_by_id

def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    # Parse the gameId from path parameters
    body = json.loads(event.get("body", "{}"))
    game_id = body.get("gameId")
    if not game_id:
        return {
            "statusCode": 400,
            "body": json.dumps({
                "message": "Invalid input: gameId is required."
            })
        }
    
    # Fetch the game from the database
    game_data = fetch_game_by_id(game_id)
    if not game_data:
        return {
            "statusCode": 400,
            "body": json.dumps({"message": "Game ID not found."})
        }
        
    # Return game details
    return {
        "statusCode": 200,
        "body": json.dumps({
            "gameId": game_id,
            "gameLayout": game_data.get("gameLayout"),
            "boardSize": game_data.get("boardSize", "3x3"), # Default to 3x3
            "language": game_data.get("language", "en"), # Default to English
            "message": "Game fetched successfully."
        })
    }