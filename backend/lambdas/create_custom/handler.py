import json
from common.db_utils import add_game_to_db, fetch_solutions_by_standardized_hash
from common.game_utils import (
    generate_game_id, 
    standardize_board, 
    calculate_two_word_solutions, 
    calculate_three_word_solutions, 
    generate_standardized_hash,
    validate_language,
    validate_board_size,
)

def handler(event, context):
    # Get the user-defined layout from the event payload
    body = json.loads(event.get("body", "{}"))
    game_layout = body.get("gameLayout")
    language = body.get("language", "English") # Default to English
    board_size = body.get("boardSize", "3x3") # Default to 3x3
    standardized_layout = standardize_board(game_layout)

    # Validate required fields
    if not game_layout:
        return {
            "statusCode": 400,
            "body": json.dumps({
                "message": "Game Layout is required."
            })
        }
    
    # Validate boardSize and language
    if not validate_board_size(board_size):
        return {
            "statusCode": 400,
            "body": json.dumps({
                "message": "Invalid Game Board Size."
            })
        }
    
    if not validate_language(language):
        return {
            "statusCode": 400,
            "body": json.dumps({
                "message": "Selected language is not supported."
            })
        }
    
    # Generate a unique game id and a standardized hash for solution lookup
    game_id = generate_game_id(game_layout, is_random=False)
    standardized_hash = generate_standardized_hash(standardized_layout)
    
    # Check if a solution already exists for this game via the standardized hash
    equivalent_game_solution = fetch_solutions_by_standardized_hash(standardized_hash)
    
    if equivalent_game_solution:
        # Use the cached solution for this game and associate it with this game id
        two_word_solutions = equivalent_game_solution["twoWordSolutions"]
        three_word_solutions = equivalent_game_solution["threeWordSolutions"]
        game_data = {
            "gameId": game_id,
            "gameLayout": game_layout,
            "standardizedHash": standardized_hash,
            "twoWordSolutions": two_word_solutions,
            "threeWordSolutions": three_word_solutions,
            "boardSize": "3x3",
            "language": "English",
        }

        add_game_to_db(game_data)
        
        return {
            "statusCode": 200,
            "body": json.dumps({
                "gameId": game_id,
                "message": "Game created using existing solution to equivalent cached game."
            })
        }
    else:
        # This is a new unique game. Generate a solution and store it.
        two_word_solutions = calculate_two_word_solutions(game_layout)
        three_word_solutions = calculate_three_word_solutions(game_layout)
        game_data = {
            "gameId": game_id,
            "gameLayout": game_layout,
            "standardizedHash": standardized_hash,
            "twoWordSolutions": two_word_solutions,
            "threeWordSolutions": three_word_solutions,
            "boardSize": "3x3",
            "language": "English",
        }

        add_game_to_db(game_data)
        
        return {
            "statusCode": 200,
            "body": json.dumps({
                "gameId": game_id,
                "message": "Game created. New solution generated and cached in DB."
            })
        }