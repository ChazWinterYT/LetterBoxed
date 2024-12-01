import json
import random
from typing import Any, Dict
from lambdas.common.game_utils import normalize_to_base, check_game_completion
from lambdas.common.db_utils import (
    fetch_game_by_id,
    fetch_valid_words_by_game_id,
    get_user_game_state,
    save_user_session_state,
)
from lambdas.validate_word.word_validator_service import find_valid_word_from_normalized


def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    AWS Lambda handler for validating submitted words in the LetterBoxed game.

    Parameters:
    - event: The event data from API Gateway.
    - context: The runtime information of the Lambda function.

    Returns:
    - dict: The response object with statusCode and body.
    """
    try: 
        body = json.loads(event.get('body', {}))
    except json.JSONDecodeError:
        return _error_response(
            "Invalid JSON in request.", 400
        )
    
    try:
        # Extract parameters from the event
        game_id = body.get('gameId')
        submitted_word = body.get('word')
        session_id = body.get('sessionId')

        # Validate required parameters
        if not game_id or not submitted_word or not session_id:
            return _error_response(
                "Missing required parameters: gameId, word, or sessionId.", 400
            )

        # Fetch game details and valid words
        game_data = fetch_game_by_id(game_id)
        if not game_data:
            return _error_response(
                "Game with specified game ID not found", 404
            )

        valid_words = fetch_valid_words_by_game_id(game_id)
        if not valid_words:
            return _error_response(
                "Valid words list for specified game ID not found", 404
            )

        # Check if the submitted word is valid
        matching_word = find_valid_word_from_normalized(submitted_word, valid_words)
        if not matching_word:
            return _error_response(
                "Word is not valid for this puzzle.", 200
            )

        # Fetch the user game state
        user_game_state = get_user_game_state(session_id, game_id)
        if not user_game_state:
            return _error_response(
                "An error occurred while fetching the game state", 500
            )

        # Check if the word has already been used
        if submitted_word in user_game_state["wordsUsed"]:
            return _error_response(
                f"Word '{submitted_word}' has already been used.", 200
            )

        # Validate word chaining rules (for the second word onward)
        if user_game_state["wordsUsed"]:
            last_word = user_game_state["wordsUsed"][-1]
            if submitted_word[0] != last_word[-1]:
                return _error_response(
                    f"Word '{submitted_word}' must start with the last letter of the previous word '{last_word}", 200
                )

        # All checks passed. Check game completion.
        game_layout = game_data["gameLayout"]
        words_used = user_game_state["wordsUsed"].copy()
        words_used.append(submitted_word)
        game_completed, completion_message = check_game_completion(game_layout, words_used)
        
        # If the game is complete, also send the solution to the user
        official_solution = []
        some_one_word_solutions = []
        some_two_word_solutions = []
        if game_completed:
            # Prioritize NYT solution if it exists
            if "nytSolution" in game_data and game_data["nytSolution"]:
                official_solution = game_data["nytSolution"]
            # Otherwise, prefer a one word solution if it exists
            elif "randomSeedWord" in game_data and game_data["randomSeedWord"]:
                official_solution = [game_data["randomSeedWord"]]
            # Otherwise, use the two word solution if it exists
            elif "randomSeedWords" in game_data and game_data["randomSeedWords"]:
                official_solution = game_data["randomSeedWords"]
            
            # Also provide a sample of one-word solutions if available
            NUM_SAMPLE_SOLUTIONS = 5 # How many solutions to show
            if "oneWordSolutions" in game_data and game_data["oneWordSolutions"]:
                some_one_word_solutions = random.sample(
                    game_data["oneWordSolutions"],
                    min(game_data["oneWordSolutionCount"], NUM_SAMPLE_SOLUTIONS)
                )
                
            # Also provide a sample of two-word solutions if available
            if "twoWordSolutions" in game_data and game_data["twoWordSolutions"]:
                some_two_word_solutions = random.sample(
                    [tuple(solution) for solution in game_data["twoWordSolutions"]],
                    min(game_data["twoWordSolutionCount"], NUM_SAMPLE_SOLUTIONS)
                )
            
        return {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "OPTIONS,GET,POST",
                "Access-Control-Allow-Headers": "Content-Type,Authorization",
            },
            "body": json.dumps({
                "valid": True,
                "message": completion_message,
                "submittedWord": submitted_word,
                "originalWord": matching_word,
                "gameCompleted": game_completed,
                "officialSolution": official_solution,
                "someOneWordSolutions": some_one_word_solutions,
                "someTwoWordSolutions": some_two_word_solutions,
            }),
        }

    except Exception as e:
        print(f"Error during validation: {e.with_traceback}")
        return _error_response(f"An unexpected error occurred: {e}", 500)
    

def _error_response(message: str, status_code: int) -> Dict[str, Any]:
    """
    Helper function to generate an error response.

    Args:
        message (str): The error message.
        status_code (int): The HTTP status code.

    Returns:
        dict: The error response.
    """
    return {
        "statusCode": status_code,
        "headers": {
                "Access-Control-Allow-Origin": "*",  # Allow all origins
                "Access-Control-Allow-Methods": "OPTIONS,GET,POST",  # Allowed methods
                "Access-Control-Allow-Headers": "Content-Type,Authorization",  # Allowed headers
            },
        "body": json.dumps({"message": message, "valid": False}),
    }
    