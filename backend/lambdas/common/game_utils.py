from typing import List, Set, Optional, Dict
import logging
from uuid import uuid4
import hashlib
from collections import defaultdict
from lambdas.common.dictionary_utils import get_dictionary

logging.basicConfig(level=logging.INFO)
_logger = logging.getLogger(__name__)

def generate_game_id() -> str:
    """
    Generate a unique game id for a user-created game.

    Returns:
        str: A unique identifier string.
    """
    return str(uuid4())


def standardize_board(game_layout: List[str]) -> List[str]:
    """
    Standardize the board by alphabetizing letters on each side and the sides themselves.

    Args:
        game_layout (List[str]): The input letters for this game.

    Returns:
        List[str]: The standardized board layout.

    Raises:
        ValueError: If the input is invalid.
    """
    if not isinstance(game_layout, list) or not all(isinstance(side, str) for side in game_layout):
        raise ValueError("game_layout must be a list of strings.")
    
    for side in game_layout:
        if not isinstance(side, str):
            raise ValueError("Each side in game_layout must be a string.")
        if not side:
            raise ValueError("Each side in game_layout must be a non-empty string.")
        if not side.isalpha():
            raise ValueError("Sides must contain only alphabetic characters.")

    if len(game_layout) != 4:
        raise ValueError("game_layout must have 4 sides.")
    
    # Enforce equal side lengths...for now!
    side_lengths = [len(side) for side in game_layout]
    if len(set(side_lengths)) != 1:
        raise ValueError("All sides must have the same number of letters.")

    # Normalize letters to lowercase
    normalized_sides = [''.join(sorted(set(side.upper()))) for side in game_layout]

    # Sort the sides themselves
    standardized_sides = sorted(normalized_sides)

    return standardized_sides


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


def is_valid_word(word: str, letter_to_side: Dict[str, int], all_letters: Set[str]) -> bool:
    """
    Check if a word is valid for the given Letter Boxed puzzle.

    Args:
        word (str): The word to validate.
        letter_to_side (Dict[str, int]): Mapping of letters to their side indices.
        all_letters (Set[str]): Set of all letters in the puzzle.

    Returns:
        bool: True if the word is valid, False otherwise.
    """
    if len(word) < 3:
        return False

    # Check if all letters are in the puzzle
    if not set(word).issubset(all_letters):
        return False

    # Check for alternating sides
    last_side = None
    for char in word:
        side = letter_to_side.get(char)
        if side is None:
            return False  # Letter not in puzzle (shouldn't happen due to previous check)
        if side == last_side:
            return False  # Consecutive letters from the same side
        last_side = side

    return True


def generate_valid_words(game_layout: List[str], language: str = "en") -> List[str]:
    """
    Generate valid words for the Letter Boxed puzzle.

    Args:
        game_layout (List[str]): Each side of the puzzle as a list.
        language (str): The language code for the dictionary to use.

    Returns:
        List[str]: Words valid for the puzzle.
    """
    try:
        dictionary = get_dictionary(language)
    except (ValueError, RuntimeError) as e:
        _logger.error(f"Error loading dictionary for language '{language}': {e}")
        return []

    # Create a mapping from letters to sides
    letter_to_side = create_letter_to_side_mapping(game_layout)
    all_letters = set(letter_to_side.keys())

    valid_words = []
    for word in dictionary:
        word = word.upper()
        if len(word) < 3:
            continue  # Skip words shorter than 3 letters
        if is_valid_word(word, letter_to_side, all_letters):
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


def create_letter_to_side_mapping(game_layout: List[str]) -> Dict[str, int]:
    """
    Creates a mapping from each letter to the index of the side it belongs to.

    Args:
        game_layout (List[str]): The puzzle layout.

    Returns:
        Dict[str, int]: Mapping of letters to side indices.
    """
    letter_to_side = {}
    for index, side in enumerate(game_layout):
        for letter in side.upper():
            letter_to_side[letter] = index
    return letter_to_side
