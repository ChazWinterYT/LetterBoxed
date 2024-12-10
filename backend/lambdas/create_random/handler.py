import json
from typing import Dict, Any, Optional
from lambdas.common.db_utils import add_game_to_db, add_game_id_to_random_games_db
from lambdas.common.dictionary_utils import get_dictionary
from lambdas.common.game_schema import create_game_schema, validate_board_size, validate_language
from lambdas.create_random.random_game_service import create_random_game, create_random_small_board_game
from lambdas.common.response_utils import error_response, HEADERS


MAX_RETRIES = 5  # Maximum number of retries for ValueError exceptions

def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    try:
        print("Received event:", event)
        
        # Check if the body is None before parsing
        if event.get("body") is None:
            return error_response("Missing body in JSON event.", 400)
            
        # Parse parameters for the event
        body = json.loads(event.get("body", {}))
        print("Parsed body:", body) 

        language = body.get("language", "en")  # Default to English
        board_size = body.get("boardSize", "3x3")  # Default to 3x3
        clue = body.get("clue", "")
        created_by = body.get("createdBy", None)
        single_word = body.get("fromSingleWord", False)
        from_lambda_console = body.get("fromLambdaConsole", False)
        is_casual = body.get("isCasual", False)
        
        ALLOWED_TO_CREATE_TO_RANDOM_POOL = ["Sara!", "Sara", "Chaz Winter", "Chaz"]
        
        # Temporarily handle games created by Sara so they go to the correct game pool
        if created_by in ALLOWED_TO_CREATE_TO_RANDOM_POOL:
            from_lambda_console = True
        
        
        # Validate language and board size
        if not validate_board_size(board_size):
            return error_response("Input contains an invalid board size.", 400)
        if not validate_language(language):
            return error_response("Input contains an unsupported language.", 400)
        
        # Use seed words if provided
        seed_words = body.get("seedWords", None) # Can be a tuple or a single string
        
        if not seed_words:
            clue = "" # Don't allow a clue if it's not based on seed words
        
        print(f"Language: {language}, Board Size: {board_size}, Clue: {clue}, Seed Words: {seed_words}, Single Word: {single_word}")
        
        small_boards = ["1x1", "2x2"]
        if board_size not in small_boards and isinstance(seed_words, str):
            return error_response("Only small boards can have a single seed word", 400)
        
        # Special handling for small boards
        if board_size in small_boards and single_word:
            random_game_data = create_random_small_board_game(
                language, 
                board_size, 
                seed_words, 
                clue, 
                created_by, 
                from_lambda_console,
                is_casual,
            )
        else:
            # Use existing service for all other boards
            random_game_data = create_random_game(
                language, 
                board_size, 
                seed_words, 
                clue, 
                created_by, 
                from_lambda_console,
                is_casual,
            )

        # Return the game details
        return {
            "statusCode": 201,
            "headers": HEADERS,
            "body": json.dumps({
                "message": "Random game created successfully.",
                "gameType": random_game_data["gameType"],
                "gameId": random_game_data["gameId"],
                "gameLayout": random_game_data["gameLayout"],
                "createdBy": random_game_data["createdBy"],
                "clue": random_game_data["clue"]
            })
        }
    except json.JSONDecodeError as e:
        return error_response("JSON decoding error.", 400)
    except ValueError as e:
        print(f"Handler failed due to ValueError: {e}")
        return error_response(f"Could not create a random game from the given seed words: {str(e)}", 400)
    except Exception as e:
        print(f"Handler failed: {e}")
        return error_response(f"There was a problem creating the game: {e}", 500)
    