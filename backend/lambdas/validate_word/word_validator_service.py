from typing import List, Optional, Dict, Any, Tuple
import random
from lambdas.common.db_utils import update_game_in_db
from lambdas.common.game_utils import normalize_to_base

def find_valid_word_from_normalized(submitted_word: str, valid_words: List[str]) -> Optional[str]:
    """
    Find the original word in the dictionary that matches a normalized word.

    Args:
        submitted_word (str): The normalized word to check against the dictionary.
        valid_words (List[str]): The list of valid words in their original form,
            which may include accents or special characters.

    Returns:
        str: The original word from the dictionary that matches the normalized 
        word, or None if no match is found.
    """
    for original_word in valid_words:
        base_original_word = normalize_to_base(original_word)
        if submitted_word == base_original_word:
            return original_word  # Return the original word that matches
    
    return None  # Return None if no match is found


def handle_post_game_logic(game_data: Dict[str, Any], words_used: List[str]) -> Dict[str, Any]:
    """
    Handles all post-game completion logic, including determining the official solution,
    sampling solutions, and any additional post-game tasks.

    Args:
        game_data (Dict[str, Any]): The game data fetched from the database.
        words_used: List[str]: The words used to complete the puzzle.

    Returns:
        Dict[str, Any]: Post-game data including solutions and additional info.
    """
    NUM_SAMPLE_SOLUTIONS = 25  # Number of solutions to show

    official_solution = []
    some_one_word_solutions = []
    some_two_word_solutions = []

    # Prioritize NYT solution if it exists
    if "nytSolution" in game_data and game_data["nytSolution"]:
        official_solution = game_data["nytSolution"]
    # Otherwise, prefer a one-word solution if it exists
    elif "randomSeedWord" in game_data and game_data["randomSeedWord"]:
        official_solution = [game_data["randomSeedWord"]]
    # Otherwise, use the two-word solution if it exists
    elif "randomSeedWords" in game_data and game_data["randomSeedWords"]:
        official_solution = game_data["randomSeedWords"]

    # Provide a sample of one-word solutions if available
    if "oneWordSolutions" in game_data and game_data["oneWordSolutions"]:
        some_one_word_solutions = random.sample(
            game_data["oneWordSolutions"],
            min(len(game_data["oneWordSolutions"]), NUM_SAMPLE_SOLUTIONS)
        )

    # Provide a sample of two-word solutions if available
    if "twoWordSolutions" in game_data and game_data["twoWordSolutions"]:
        some_two_word_solutions = random.sample(
            [tuple(solution) for solution in game_data["twoWordSolutions"]],
            min(len(game_data["twoWordSolutions"]), NUM_SAMPLE_SOLUTIONS)
        )

    # Provide game statistics
    total_completions = game_data["totalCompletions"] + 1  # We just finished the game
    total_words_used = game_data["totalWordsUsed"] + len(words_used)
    total_letters_used = game_data["totalLettersUsed"] + sum(len(word) for word in words_used)
    total_ratings = game_data["totalRatings"]
    total_stars = game_data["totalStars"]

    print("Game data:", game_data)

    # Update game data in the database
    updated_game_data = {
        "gameId": game_data["gameId"],
        "totalCompletions": total_completions,
        "totalWordsUsed": total_words_used,
        "totalLettersUsed": total_letters_used,
    }
    if not update_game_in_db(updated_game_data):
        print(f"[WARN] Failed to update game stats for gameId {game_data['gameId']}")

    average_rating = total_stars / total_ratings if total_ratings > 0 else 0.0
    average_words_used = total_words_used / total_completions
    average_word_length = total_letters_used / total_words_used

    # Return the processed post-game data
    return {
        "officialSolution": official_solution,
        "someOneWordSolutions": some_one_word_solutions,
        "someTwoWordSolutions": some_two_word_solutions,
        "averageRating": average_rating,
        "averageWordsUsed": average_words_used,
        "averageWordLength": average_word_length,
    }
