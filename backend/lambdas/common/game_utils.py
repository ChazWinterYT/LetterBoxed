from uuid import uuid4
import hashlib
from collections import defaultdict
from lambdas.common.dictionary_utils import get_dictionary

def generate_game_id():
    """
    Generate a unique game id for a user-created game.
    """
    return str(uuid4())


def standardize_board(game_layout):
    """
    Create a standardized version of the board, by alphabetizing the letters on each side,
    and then alphabetizing the sides. This way, two boards with the same letters on each side 
    can be determined to be equivalent.

    Args:
        game_layout (List[str]): The input letters for this game.
    """
    sorted_sides = ["".join(sorted(side)) for side in game_layout]
    sorted_sides.sort()
    return sorted_sides


def validate_board_size(board_size):
    valid_board_sizes = ["3x3", "4x4", "5x5"]
    return board_size in valid_board_sizes


def validate_language(language):
    valid_languages = ["en", "es", "fr", "pl", "de", "it", "sv"]
    return language in valid_languages


def generate_standardized_hash(standardized_game_layout):
    """
    Generate a hash of the game layout, using a standardized letter layout so that 
    equivalent boards generate the same hash.
    
    Args:
        standardized_game_layout (List[str]): The input letters for this game, 
        sorted so that equivalent boards generate the same hash.
    """
    layout_str = "-".join(standardized_game_layout)
    return hashlib.sha256(layout_str.encode()).hexdigest()


def calculate_two_word_solutions(game_layout, language="en"):
    """
    Calculate the two word solutions to the given puzzle input.

    Args:
        game_layout (List[str]): The input letters for this game.
        language (str, optional): Language of the word dictionary to use to find solutions.
            Defaults to English.

    Returns:
        List[Tuple[str, str]]: List of pairs of words representing solutions to the puzzle.
    """
    try:
        dictionary = get_dictionary(language)
    except ValueError as e:
        # Log error if dictionary cannot be loaded
        print(f"Error loading dictionary for language '{language}': {e}")
        return []

    # Placeholder implementation: Return an empty list
    return []


def calculate_three_word_solutions(game_layout, language="en"):
    """
    Calculate three word solutions to the given puzzle input.

    Args:
        game_layout (List[str]): The input letters for this game.
        language (str, optional): Language of the word dictionary to use to find solutions.
            Defaults to English.
    
    Returns:
        List[Tuple[str, str, str]]: List of trios of words representing solutions to the puzzle.
    """
    try:
        dictionary = get_dictionary(language)
    except ValueError as e:
        # Log error if dictionary cannot be loaded
        print(f"Error loading dictionary for language '{language}': {e}")
        return []

    # Placeholder implementation: Return an empty list
    return []


def is_valid_word(word, game_layout, puzzle_sides=None):
    """
    Check if a word is valid for the given Letter Boxed puzzle.
    
    Args:
        word (str): Word to validate.
        game_layout (List[str]): Each side of the puzzle as a List.
        puzzle_sides (List[Set[str]], optional): Precomputed sets of letters for each side of the puzzle.
            Can be passed in to save repeated calculations (as in generate_valid_words).
        
    Returns:
        bool: True if the word is valid, False otherwise.
    """
    # Check minimum word length
    if len(word) < 3:
        return False
    
    # Check if all the word's letters are in the current puzzle
    letter_set = set("".join(game_layout))
    if not set(word).issubset(letter_set):
        return False
    
    # Compute puzzle_sides set if not provided
    if not puzzle_sides:
        puzzle_sides = sides_list_to_sides_set(game_layout)

    # Then ensure the letters alternate between sides
    last_side = None
    for char in word:
        for i, side in enumerate(puzzle_sides):
            if char in side:
                if last_side == i: # Next letter is on the same side as the previous
                    return False
                last_side = i
                break
    
    # If the loop survives, then this is a valid word
    return True


def generate_valid_words(dictionary, game_layout, puzzle_sides=None):
    """
    Generate valid words for the Letter Boxed puzzle.
    
    Args:
        dictionary (List[str]): Full word list.
        game_layout (List[str]): Each side of the puzzle as a List.
        puzzle_sides (List[Set[str]], optional): Precomputed sets of letters for each side of the puzzle.
            Can be passed in to save repeated calculations (as in generate_valid_words).
        
    Returns:
        List[str]: Words valid for the puzzle.
    """
    valid_words = []
    if not puzzle_sides:
        puzzle_sides = sides_list_to_sides_set(game_layout)
    for word in dictionary:
        if len(word) > 2 and is_valid_word(word, game_layout, puzzle_sides):
            valid_words.append(word)
    
    return valid_words


def sides_list_to_sides_set(game_layout):
    """
    Converts a list of string sides to a list of sets of characters.
    
    Args:
        game_layout (List[str]): List of strings representing the sides of the puzzle.
        
    Returns:
        List[Set[str]]: List of sets of characters for each side of the puzzle.
    """
    return [set(side) for side in game_layout]
