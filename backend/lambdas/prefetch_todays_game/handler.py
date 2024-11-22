import json
from typing import Dict, Any
from lambdas.prefetch_todays_game.prefetch_service import fetch_todays_game
from lambdas.common.db_utils import add_game_to_db, fetch_game_by_id, add_valid_words_to_db
from lambdas.common.game_schema import create_game_schema


def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    AWS Lambda handler for prefetching today's game from the NYT website.
    """
    try:
        # Fetch today's game
        todays_game = fetch_todays_game()
        game_id = todays_game["gameId"]

        # Check if the game is already in the database
        if fetch_game_by_id(game_id):
            return {
                "statusCode": 200,
                "body": json.dumps({
                    "message": "Today's game is already cached.",
                    "gameId": game_id
                })
            }

        # Create the game schema using the centralized function
        game_object = create_game_schema(
            game_id=game_id,
            game_layout=todays_game["gameLayout"],
            game_type="nyt",
            official_game=True,
            nyt_solution=todays_game["nytSolution"],
            dictionary=todays_game["dictionary"],
            par=todays_game["par"],
            board_size="3x3",  # NYT games are always 3x3
            language="en",  # Default to English
        )

        # Add today's game to the database
        add_game_to_db(game_object)
        add_valid_words_to_db(game_id, game_object["validWords"])

        return {
            "statusCode": 201,
            "body": json.dumps({
                "message": "Today's game cached successfully.",
                "gameId": game_id
            })
        }

    except Exception as e:
        print(f"Error prefetching today's game: {e}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
