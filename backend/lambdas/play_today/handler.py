import json
from typing import Dict, Any
from datetime import date, timedelta
from lambdas.common.db_utils import fetch_game_by_id
from lambdas.common.response_utils import error_response, HEADERS

def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Lambda handler for fetching today's NYT game from the DB.
    If today's game is not yet available, it falls back to yesterday's game.
    """
    try:
        # Get today's date as the game ID
        today = date.today().isoformat()
        yesterday = (date.today() - timedelta(days=1)).isoformat()

        # Fetch the game from the database
        todays_game = fetch_game_by_id(today)

        if not todays_game:
            # Fall back to yesterday's game if today's game is not available
            todays_game = fetch_game_by_id(yesterday)

            if not todays_game:
                return error_response(
                    f"{today}'s game is not yet available, and {yesterday}'s game isn't either. Please try again later.", 
                    404
                )
            else:
                # Serve yesterday's game, including a message to indicate that it's yesterday's game
                return {
                    "statusCode": 200,
                    "headers": HEADERS,
                    "body": json.dumps({
                        "gameId": todays_game["gameId"],
                        "gameLayout": todays_game["gameLayout"],
                        "boardSize": todays_game["boardSize"],
                        "language": todays_game["language"],
                        "par": todays_game["par"],
                        "hint": todays_game.get("clue", ""),
                        "message": f"{today}'s game is not available yet. Serving {yesterday}'s game instead."
                    })
                }
        
        # Return today's game
        return {
            "statusCode": 200,
            "headers": HEADERS,
            "body": json.dumps({
                "gameId": todays_game["gameId"],
                "gameLayout": todays_game["gameLayout"],
                "boardSize": todays_game["boardSize"],
                "language": todays_game["language"],
                "par": todays_game["par"],
                "hint": todays_game.get("clue", ""),
                "message": f"{today}'s game fetched successfully."
            })
        }
    except Exception as e:
        print(str(e))
        return error_response(f"An error occurred while fetching today's game: {str(e)}", 500)