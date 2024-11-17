import json
from lambdas.prefetch_todays_game.prefetch_service import fetch_todays_game
from lambdas.common.db_utils import add_game_to_db, fetch_game_by_id
from lambdas.common.game_utils import (
    standardize_board, 
    generate_standardized_hash,
    calculate_two_word_solutions,
    calculate_three_word_solutions,
)

def handler(event, context):
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

        # Generate standardized hash
        standardized_game_layout = standardize_board(todays_game["gameLayout"])
        standardized_hash = generate_standardized_hash(standardized_game_layout)
        twoWordSolutions = calculate_two_word_solutions(standardized_game_layout)
        threeWordSolutions = calculate_three_word_solutions(standardized_game_layout)

        # Prepare the game object
        game_object = {
            "gameId": todays_game["gameId"],
            "gameLayout": todays_game["gameLayout"],
            "standardizedHash": standardized_hash,
            "nytSolution": todays_game["nytSolution"],
            "twoWordSolutions": twoWordSolutions,
            "threeWordSolutions": threeWordSolutions,
            "dictionary": todays_game["dictionary"],
            "par": todays_game["par"],
            "boardSize": "3x3",  # NYT games are always 3x3
            "language": "English"  # Default to English
        }

        # Add today's game to the database
        add_game_to_db(game_object)

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
