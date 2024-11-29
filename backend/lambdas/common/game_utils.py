from typing import List, Set, Optional, Dict, Tuple
import logging
import unicodedata
from uuid import uuid4
from collections import defaultdict, Counter
from lambdas.common.dictionary_utils import get_dictionary

logging.basicConfig(level=logging.INFO)
_logger = logging.getLogger(__name__)


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

    # Normalize letters to uppercase
    normalized_sides = [''.join(sorted(set(side.upper()))) for side in game_layout]

    # Sort the sides themselves
    standardized_sides = sorted(normalized_sides)

    return standardized_sides


def check_game_completion(game_layout: list[str], words_used: list[str]) -> tuple[bool, str]:
    """
    Checks if the game is completed by verifying if all letters have been used.

    Args:
        game_layout (list): The game layout containing letters.
        words_used (list): The list of words used by the user.

    Returns:
        tuple: (game_completed (bool), message (str)).
    """
    base_words = []
    for word in words_used:
        base_word = normalize_to_base(word)
        base_words.append(base_word)

    all_letters = set("".join(game_layout))
    used_letters = set("".join(base_words))

    if used_letters == all_letters:
        return True, "Puzzle solved successfully! Congrats!"
    else:
        return False, "Word accepted."


def calculate_two_word_solutions(
    game_layout: List[str],
    language: str = "en",
    valid_words: Optional[List[str]] = None,
    starting_letter_to_words: Optional[Dict[str, List[str]]] = None
) -> List[Tuple[str, str]]:
    """
    Calculate the two-word solutions to the given puzzle input.

    Args:
        game_layout (List[str]): The input letters for this game.
        language (str, optional): Language of the word dictionary.
        valid_words (List[str], optional): Pre-calculated list of valid words.
        starting_letter_to_words (Dict[str, List[str]], optional): Mapping of starting letters to words.

    Returns:
        List[Tuple[str, str]]: Pairs of words representing solutions to the puzzle.
    """
    try:
        # Preprocess words to generate a list of valid words for this puzzle
        if not valid_words or valid_words is None:
            valid_words = generate_valid_words(game_layout, language)
        if not starting_letter_to_words or starting_letter_to_words is None:
            starting_letter_to_words = create_starting_letter_to_words_dict(game_layout, language, valid_words)
    except ValueError as e:
        print(f"Error preprocessing words for two word solution: {e}")
        return []
    
    # Create a mapping of letters to their sides, and a set of all letters on the board
    # (this requires all letters on the board to be unique)
    letter_to_side = create_letter_to_side_mapping(game_layout)
    all_letters = set(letter_to_side.keys())
    total_letters = len(all_letters)

    solutions = []
    letter_usage: Counter[str] = Counter()

    # Iterate through all valid words
    for word1 in valid_words:
        base_word1 = normalize_to_base(word1)
        # Update letter usage with word1
        update_letter_usage(letter_usage, base_word1, increment=True)

        # Look for word2 candidates that start with the last letter of word1
        last_letter = base_word1[-1]
        potential_second_words = starting_letter_to_words[last_letter]

        for word2 in potential_second_words:
            base_word2 = normalize_to_base(word2)
            # Skip pairs that can't cover all letters in the puzzle
            if len(base_word1) + len(base_word2) < total_letters:
                continue

            # Skip repeated words
            if base_word1 == base_word2:
                continue

            # Update letter usage with word2
            update_letter_usage(letter_usage, base_word2, increment=True)

            # If all letters have been used, then we have a solution!
            if all(letter_usage[letter] > 0 for letter in all_letters):
                solutions.append((word1, word2)) # Show the orignial words in the solution
            
            # Revert word2 letter usage so we can try the next candidate
            update_letter_usage(letter_usage, base_word2, increment=False)
        
        # Revert word1 letter usage so we can try the next word in the dictionary
        update_letter_usage(letter_usage, base_word1, increment=False)
    
    return solutions


def calculate_three_word_solutions(
    game_layout: List[str],
    language: str = "en",
    valid_words: Optional[List[str]] = None,
    starting_letter_to_words: Optional[Dict[str, List[str]]] = None
) -> List[Tuple[str, str, str]]:
    """
    Calculate three word solutions to the given puzzle input.

    Args:
        game_layout (List[str]): The input letters for this game.
        language (str, optional): Language of the word dictionary.
        valid_words (List[str], optional): Pre-calculated list of valid words.
        starting_letter_to_words (Dict[str, List[str]], optional): Mapping of starting letters to words.
    
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
        base_word = normalize_to_base(word)
        base_word = base_word.upper()
        if len(base_word) < 3:
            continue  # Skip words shorter than 3 letters
        if is_valid_word(base_word, letter_to_side, all_letters):
            valid_words.append(word) # Add the original word to the list

    return valid_words


def sides_list_to_sides_set(game_layout: List[str]) -> List[Set[str]]:
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


def create_starting_letter_to_words_dict(
    game_layout: List[str], 
    language: str, 
    valid_words: Optional[List[str]]
) -> Dict[str, List[str]]:
    """
    Creates a dictionary that maps each starting letter to a list of valid words starting with that letter.

    Args:
        game_layout (List[str]): The game layout containing letters.
        language (str): The language of the dictionary to use.
        valid_words (List[str]): If provided, a list of valid words for this game layout

    Returns:
        Dict[str, List[str]]: A dictionary where keys are starting letters and values are 
        lists of words starting with those letters.
    """
    valid_words = generate_valid_words(game_layout, language)
    starting_letter_to_words = defaultdict(list)

    for word in valid_words:
        first_letter = word[0]
        starting_letter_to_words[first_letter].append(word)
    
    return starting_letter_to_words


def update_letter_usage(letter_usage: Counter[str], word: str, increment: bool = True) -> None:
    """
    Updates the letter usage count for a word.

    Args:
        letter_usage (Counter): Tracks the current letter usage.
        word (str): The word being added or removed.
        increment (bool): Whether to increment or decrement usage counts.
    """
    change = 1 if increment else -1
    for letter in word:
        letter_usage[letter] += change
        if letter_usage[letter] == 0 and not increment:
            del letter_usage[letter]


def normalize_to_base(word: str) -> str:
    """
    Normalize a word to its base form by removing accents and diacritical marks.
    """
    return ''.join(
        char for char in unicodedata.normalize('NFD', word)
        if unicodedata.category(char) != 'Mn'
    )
    