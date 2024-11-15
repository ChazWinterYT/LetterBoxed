import json
from common.db_utils import fetch_game_by_id

def handler(event, context):
    # Parse the gameId from path parameters
    game_id = event.get("pathParameters", {}).get("gameId")
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
            "message": "Game fetched successfully."
        })
    }