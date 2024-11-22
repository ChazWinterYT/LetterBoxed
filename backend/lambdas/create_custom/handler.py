import json
from typing import Dict, Any

from lambdas.common.db_utils import (
    add_game_to_db, 
    fetch_solutions_by_standardized_hash,
    add_valid_words_to_db,
    fetch_valid_words_by_game_id,
)
from lambdas.common.game_utils import ( 
    standardize_board, 
    calculate_two_word_solutions, 
    calculate_three_word_solutions, 
    generate_valid_words,
)
from lambdas.common.game_schema import (
    generate_game_id,
    create_game_schema,
    validate_board_matches_layout,
    generate_game_id, 
    generate_standardized_hash,
)

def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    # Get the user-defined layout from the event payload
    body = json.loads(event.get("body", "{}"))
    game_layout = body.get("gameLayout")
    created_by = body.get("sessionId", "")
    if not game_layout:
        return {
            "statusCode": 400,
            "body": json.dumps({
                "message": "Game Layout is required."
            })
        }

    language = body.get("language", "en") # Default to English
    board_size = body.get("boardSize", "3x3") # Default to 3x3
    standardized_layout = standardize_board(game_layout)

    
    if not validate_board_matches_layout(game_layout, board_size):
        return {
            "statusCode": 400,
            "body": json.dumps({
                "message": f"Game layout does not match board size."
            })
        }
    
    # Generate a unique game id and a standardized hash for solution lookup
    game_id = generate_game_id()
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
            "boardSize": board_size,
            "language": language,
            "officialGame": False,
        }
        add_game_to_db(game_data)
        valid_words = fetch_valid_words_by_game_id(game_id)
        add_valid_words_to_db(game_id, valid_words)
        
        return {
            "statusCode": 200,
            "body": json.dumps({
                "gameId": game_id,
                "message": "Game created using existing solution to equivalent cached game."
            })
        }
    else:
        # This is a new unique game. Generate a solution and store it.
        valid_words = generate_valid_words(game_layout, language)
        two_word_solutions = calculate_two_word_solutions(
            game_layout, language, valid_words
        )
        three_word_solutions = calculate_three_word_solutions(game_layout, language)
        game_data = {
            "gameId": game_id,
            "gameLayout": game_layout,
            "standardizedHash": standardized_hash,
            "twoWordSolutions": two_word_solutions,
            "threeWordSolutions": three_word_solutions,
            "boardSize": board_size,
            "language": language,
            "officialGame": False,
        }
        add_game_to_db(game_data)
        add_valid_words_to_db(game_id, valid_words)
        
        return {
            "statusCode": 200,
            "body": json.dumps({
                "gameId": game_id,
                "message": "Game created. New solution generated and cached in DB."
            })
        }
   