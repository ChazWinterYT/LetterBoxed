import json
from typing import Dict, Any, Optional
import time
import random
from lambdas.common.response_utils import error_response
from lambdas.create_random.random_game_service import select_two_words, select_one_word
from lambdas.common.dictionary_utils import get_dictionary, get_basic_dictionary
from lambdas.common.validation_utils import validate_language, validate_board_size


def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    AWS Lambda handler for generating word pairs for potential puzzles
    """
    try:
        body = json.loads(event.get("body", "{}"))
        print("body:", body)

        if not isinstance(body, dict):
            return error_response("Invalid or missing JSON body.", 400) 
        
        language = body.get("language", "en")
        board_size = body.get("boardSize", "3x3")
        num_tries = body.get("numTries", 10)
        single_word = body.get("singleWord", False)
        basic_dictionary = body.get("basicDictionary", True)
        min_word_length = body.get("minWordLength", 3)
        max_word_length = body.get("maxWordLength", 99)
        max_shared_letters = body.get("maxSharedLetters", 4)
        
        # Validate parameters
        if not validate_language(language):
            return error_response("Language is not supported for game creation.", 400)
        if not validate_board_size(board_size):
            return error_response("Board size is not supported for game creation.", 400)
        if num_tries < 1 or num_tries > 10:
            return error_response("Number of tries must be between 1 and 10.", 400)
        if not single_word:
            if max_word_length < 7 or max_word_length > 99:
                return error_response("Maximum word length must be between 7 and 99.", 400)
            if max_shared_letters < 1 or max_shared_letters > 7:
                return error_response(
                    f"Maximum shared letters ({max_shared_letters}) must be between 1 and 7.", 400
                )
        
        dictionary = get_basic_dictionary(language) if basic_dictionary else get_dictionary(language)
        random.shuffle(dictionary)
        word_pairs = []
        words = []
        
        for _ in range(num_tries):
            if single_word:
                seed_word = select_one_word(dictionary, "2x2")
                if seed_word:
                    words.append(seed_word)
            elif board_size == "3x3":
                seed_words = select_two_words(
                    dictionary, 
                    "3x3", 
                    10000, 
                    min_word_length, 
                    max_word_length, 
                    max_shared_letters
                )
                if seed_words:
                    word_pairs.append(seed_words)
            elif board_size == "4x4":
                seed_words = select_two_words(
                    dictionary, 
                    "4x4", 
                    10000, 
                    min_word_length, 
                    max_word_length, 
                    max_shared_letters
                )
                if seed_words:
                    word_pairs.append(seed_words)
        
        return {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": "*",  # Allow all origins
                "Access-Control-Allow-Methods": "OPTIONS,GET,POST",  # Allowed methods
                "Access-Control-Allow-Headers": "Content-Type,Authorization",  # Allowed headers
            },
            "body": json.dumps({
                "message": "Words generated successfully.",
                "singleWords": words,
                "singleWordsCount": len(words),
                "wordPairs": word_pairs,
                "wordPairsCount": len(word_pairs),
            })
        }
        
    except Exception as e:
        print(f"Error generating candidate words: {str(e)}")
        return error_response(f"There was an error when fetching words: {str(e)}", 500)
        