import json
from typing import Any, Dict
import time

from lambdas.common.db_utils import (
    fetch_game_by_id,
    fetch_valid_words_by_game_id,
    get_user_game_state,
    save_session_state,
)


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
        # Extract parameters from the event
        body = json.loads(event.get('body', '{}'))
        game_id = body.get('gameId')
        submitted_word = body.get('word').upper() # Normalize to uppercase
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
        if submitted_word not in valid_words:
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

        # All checks passed. Update user game state
        user_game_state["wordsUsed"].append(submitted_word)
        
        # Check if the user completed the game
        game_completed, message = _check_game_completion(game_data["gameLayout"], user_game_state["wordsUsed"])
    
        user_game_state["gameCompleted"] = game_completed
        updated_time = int(time.time())
        user_game_state["lastUpdated"] = updated_time
        user_game_state["TTL"] = updated_time + 30 * 24 * 60 * 60  # Extend TTL
        save_session_state(user_game_state)

        # Success response
        return {
            "statusCode": 200,
            "body": json.dumps({
                "valid": True,
                "message": message,
                "gameCompleted": game_completed,
                "wordsUsed": user_game_state["wordsUsed"],
                "lastUpdated": updated_time,
            })
        }

    except Exception as e:
        print(f"Error during validation: {e}")
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
        "body": json.dumps({"message": message, "valid": False}),
    }


def _check_game_completion(game_layout: list[str], words_used: list[str]) -> tuple[bool, str]:
    """
    Checks if the game is completed by verifying if all letters have been used.

    Args:
        game_layout (list): The game layout containing letters.
        words_used (list): The list of words used by the user.

    Returns:
        tuple: (game_completed (bool), message (str)).
    """
    all_letters = set("".join(game_layout))
    used_letters = set("".join(words_used))

    if used_letters == all_letters:
        return True, "Puzzle solved successfully! Congrats!"
    else:
        return False, "Word accepted."
    