import json
from typing import Dict, Any
from lambdas.prefetch_todays_game.prefetch_service import (
    fetch_todays_game,
)
from lambdas.common.db_utils import (
    add_game_to_db, 
    fetch_game_by_id, 
    add_game_to_archive
)
from lambdas.common.game_schema import create_game_schema
from lambdas.common.response_utils import error_response, HEADERS


def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    AWS Lambda handler for prefetching today's game from the NYT website.
    """
    try:
        # Fetch today's game
        todays_game = fetch_todays_game()
        game_id = todays_game["gameId"]

        print(f"Today's game fetched from NYT website: {game_id}")

        # Check if the game is already in the database
        if fetch_game_by_id(game_id):
            return {
                "statusCode": 200,
                "headers": HEADERS,
                "body": json.dumps({
                    "message": "Today's game is already cached.",
                    "gameId": game_id
                })
            }

        # Create the game schema using the centralized function
        game_data = create_game_schema(
            game_id=game_id,
            game_layout=todays_game["gameLayout"],
            game_type="nyt",
            official_game=True,
            nyt_solution=todays_game["nytSolution"],
            dictionary=todays_game["dictionary"],
            par=todays_game["par"],
            board_size="3x3",  # NYT games are always 3x3
            language="en",  # Default to English
            created_by=todays_game["createdBy"],
            clue="",
        )

        # Add today's game to the games and archives DB tables
        success = add_game_to_db(game_data)
        if success:
            add_game_to_archive(game_id)

        return {
            "statusCode": 201,
            "headers": HEADERS,
            "body": json.dumps({
                "message": "Today's game cached successfully.",
                "gameId": game_id
            })
        }

    except Exception as e:
        print(f"Error prefetching today's game: {e}")
        return error_response(f"Error: {str(e)}", 500)
