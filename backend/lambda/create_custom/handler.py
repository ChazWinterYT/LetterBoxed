import json
from common.db_utils import add_game_to_db, check_equivalent_game_exists_in_db
from common.game_utils import generate_game_id, standardize_board, calculate_solution, generate_standardized_hash

def handler(event, context):
    # Get the user-defined layout from the event payload
    user_layout = event.get("body")
    standardized_layout = standardize_board(user_layout)
    
    # Generate a unique game id and a standardized hash for solution lookup
    game_id = generate_game_id(user_layout)
    standardized_hash = generate_standardized_hash(standardized_layout)
    
    # Check if a solution already exists for this game via the standardized hash
    equivalent_game_solution = check_equivalent_game_exists_in_db(standardized_hash)
    
    if equivalent_game_solution:
        # Use the cached solution for this game and associate it with this game id
        add_game_to_db(game_id, user_layout, standardized_hash, equivalent_game_solution)
        return {
            "statusCode": 200,
            "body": json.dumps({
                "gameId": game_id,
                "solution": equivalent_game_solution,
                "message": "Game created using existing solution to equivalent cached game."
            })
        }
    else:
        # This is a new unique game. Generate a solution and store it.
        solution = calculate_solution(user_layout)
        add_game_to_db(game_id, user_layout, standardized_hash, solution)
        return {
            "statusCode": 200,
            "body": json.dumps({
                "gameId": game_id,
                "solution": solution,
                "message": "Game created. New solution generated and cached in DB."
            })
        }