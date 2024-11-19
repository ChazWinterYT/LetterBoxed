import json

from lambdas.common.db_utils import add_game_to_db, fetch_solutions_by_standardized_hash
from lambdas.common.game_utils import (
    generate_game_id, 
    standardize_board, 
    calculate_two_word_solutions, 
    calculate_three_word_solutions, 
    generate_standardized_hash,
    validate_language,
    validate_board_size,
    preprocess_words,
)

def handler(event, context):
    # Get the user-defined layout from the event payload
    body = json.loads(event.get("body", "{}"))
    game_layout = body.get("gameLayout")
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
                "message": f"Selected language is not supported."
            })
        }
    
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
        
        return {
            "statusCode": 200,
            "body": json.dumps({
                "gameId": game_id,
                "message": "Game created using existing solution to equivalent cached game."
            })
        }
    else:
        # This is a new unique game. Generate a solution and store it.
        valid_words, starting_letter_to_words = preprocess_words(game_layout, language)
        two_word_solutions = calculate_two_word_solutions(
            game_layout, language, valid_words, starting_letter_to_words
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
        
        return {
            "statusCode": 200,
            "body": json.dumps({
                "gameId": game_id,
                "message": "Game created. New solution generated and cached in DB."
            })
        }


def validate_board_matches_layout(game_layout, board_size):
    """
    Validates the game layout against the specified board size.

    Args:
        game_layout (list[str]): The game layout as a list of strings.
        board_size (str): The board size in the format "m x n" (e.g., "3x3" or "4x5").

    Returns:
        bool: True if the layout is valid, False otherwise.
    """
    # Parse board size
    try:
        rows, cols = map(int, board_size.lower().split('x'))
    except ValueError:
        raise ValueError(f"Invalid board size format: '{board_size}'. Expected 'm x n'.")

    # Calculate total expected spaces
    total_spaces = (2 * rows) + (2 * cols)

    # Check that the number of letters in game_layout matches total_spaces
    layout_letter_count = sum(len(side) for side in game_layout)

    if layout_letter_count != total_spaces:
        raise ValueError(
            f"Invalid game layout: Expected {total_spaces} letters for a {rows}x{cols} board, "
            f"but got {layout_letter_count}."
        )

    return True
   