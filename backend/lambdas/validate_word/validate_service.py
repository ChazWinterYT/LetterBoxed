import os
import time
import boto3
from boto3.dynamodb.conditions import Key


dynamodb = boto3.resource('dynamodb')
valid_words_table_name = os.environ['VALID_WORDS_TABLE']
user_sessions_table_name = os.environ['SESSION_STATES_TABLE']
games_table_name = os.environ['GAMES_TABLE_NAME']

valid_words_table = dynamodb.Table(valid_words_table_name)
session_states_table = dynamodb.Table(user_sessions_table_name)
games_table = dynamodb.Table(games_table_name)

def validate_submitted_word(game_id: str, submitted_word: str, session_id: str) -> dict:
    """
    Validates a submitted word in the context of a game session.

    Parameters:
    - game_id (str): The unique identifier for the game.
    - submitted_word (str): The word submitted by the user.
    - session_id (str): The unique session identifier for the user.

    Returns:
    - dict: A dictionary containing validation results and messages.
    """
    # Normalize the word
    submitted_word = submitted_word.upper()

    # Check if the word is valid for the current game
    word_exists = check_word_validity(game_id, submitted_word)
    if not word_exists:
        return {
            "valid": False,
            "message": "Word is not valid for this puzzle."
        }
    
    # Fetch user game state
    session_data = get_user_game_state(session_id, game_id)

    # Check if the word has been used already
    if submitted_word in session_data["wordsUsed"]:
        return {
            "valid": False,
            "message": "Word has already been used."
        }
    
    # Check starting letter for subsequent words
    if session_data["wordsUsed"]:
        last_word = session_data["wordsUsed"][-1]
        if submitted_word[0] != last_word[-1]:
            return {
                "valid": False,
                "message": "Word must start with the last letter of the previous word."
            }
    
    # All checks passed. This is a valid word. Update the game state
    session_data["wordsUsed"].append(submitted_word)

    # Set TTL for 30 days (delete this DB entry if not updated for 30 days)
    ttl = int(time.time()) + 30 * 24 * 60 * 60 # 30 days x 24 hours x 60 minutes x 60 seconds
    session_data["TTL"] = ttl

    # Save the updated game state
    save_session_state(session_data)

    # Check if all letters have been used (puzzle has been solved)
    game_completed, message = check_game_completion(game_id, session_data["wordsUsed"])

    return {
        "valid": True,
        "message": message,
        "game_completed": game_completed,
        "words_used": session_data["wordsUsed"],
    }


def check_word_validity(game_id: str, word: str) -> bool:
    """
    Checks if a word is valid for the given game.

    Parameters:
    - game_id (str): The unique identifier for the game.
    - word (str): The word to check.

    Returns:
    - bool: True if the word is valid, False otherwise.
    """
    try:
        response = valid_words_table.get_item(
            Key={"gameId": game_id, "word": word}
        )
        return "Item" in response
    except Exception as e:
        print(f"Error checking word validity: {e}")
        return False


def get_user_game_state(session_id: str, game_id: str) -> dict:
    """
    Retrieves or initializes the game state for a user session.

    Parameters:
    - session_id (str): The unique session identifier for the user.
    - game_id (str): The unique identifier for the game.

    Returns:
    - dict: The user's game state.

    Raises:
    - Exception: If there is an error accessing the database.
    """
    user_game_key = {"sessionId": session_id, "gameId": game_id}
    try:
        response = session_states_table.get_item(Key=user_game_key)
        user_game_data = response.get("Item")

        if user_game_data is None:
            # Return initialized game state for a new session
            return {
                "sessionId": session_id,
                "gameId": game_id,
                'wordsUsed': []
            }

        return user_game_data
    except Exception as e:
        print(f"Error fetching game state for session '{session_id}', game '{game_id}': {e}")
        return None
    

def save_session_state(user_game_data: dict) -> bool:
    """
    Saves the user's game state to the DynamoDB table.

    Parameters:
    - user_game_data (dict): The user's game state data.

    Returns:
    - True if save is successful, False otherwise
    """
    try:
        session_states_table.put_item(Item=user_game_data)
        return True
    except Exception as e:
        print(f"Error saving game state: {e}")
        return False
    

def check_game_completion(game_id: str, words_used: list) -> (bool, str):
    """
    Checks if the game is completed by verifying if all letters have been used.

    Parameters:
    - game_id (str): The unique identifier for the game.
    - words_used (list): The list of words used by the user.

    Returns:
    - tuple: (game_completed (bool), message (str))
    """
    try:
        # Fetch the game layout to get all the letters
        game_data = games_table.get_item(Key={"gameId": game_id}).get("Item")
        if not game_data:
            return False, "Game data not found."
        
        game_layout = game_data.get("gameLayout", [])
        all_letters = set(''.join(game_layout))

        # Collect all letters used by the user
        letters_used = set(''.join(words_used))

        if letters_used == all_letters:
            return True, "Puzzle successfully solved! Congrats!"
        else:
            return False, "Word accepted."
    except Exception as e:
        print(f"Error checking game completion status: {e}")
        return False, "There was an error."
    