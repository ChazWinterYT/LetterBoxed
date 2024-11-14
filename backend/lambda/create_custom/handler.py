import json
from common.db_utils import add_game_to_db, fetch_solutions_by_standardized_hash
from common.game_utils import (
    generate_game_id, 
    standardize_board, 
    calculate_two_word_solutions, 
    calculate_three_word_solutions, 
    generate_standardized_hash,
)

def handler(event, context):
    # Get the user-defined layout from the event payload
    user_layout = event.get("body")
    standardized_layout = standardize_board(user_layout)
    
    # Generate a unique game id and a standardized hash for solution lookup
    game_id = generate_game_id(user_layout, is_random=False)
    standardized_hash = generate_standardized_hash(standardized_layout)
    
    # Check if a solution already exists for this game via the standardized hash
    equivalent_game_solution = fetch_solutions_by_standardized_hash(standardized_hash)
    
    if equivalent_game_solution:
        # Use the cached solution for this game and associate it with this game id
        two_word_solutions = equivalent_game_solution["twoWordSolutions"]
        three_word_solutions = equivalent_game_solution["threeWordSolutions"]
        add_game_to_db(game_id, user_layout, standardized_hash, two_word_solutions, three_word_solutions)
        
        return {
            "statusCode": 200,
            "body": json.dumps({
                "gameId": game_id,
                "message": "Game created using existing solution to equivalent cached game."
            })
        }
    else:
        # This is a new unique game. Generate a solution and store it.
        two_word_solutions = calculate_two_word_solutions(user_layout)
        three_word_solutions = calculate_three_word_solutions(user_layout)
        add_game_to_db(game_id, user_layout, standardized_hash, two_word_solutions, three_word_solutions)
        
        return {
            "statusCode": 200,
            "body": json.dumps({
                "gameId": game_id,
                "message": "Game created. New solution generated and cached in DB."
            })
        }