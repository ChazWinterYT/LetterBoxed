import time
import random
import unicodedata
from typing import List, Optional, Tuple, Dict, Any
from lambdas.common.game_utils import normalize_to_base
from lambdas.common.dictionary_utils import get_dictionary, get_basic_dictionary
from lambdas.common.db_utils import (
    add_game_to_db,
    add_game_id_to_random_games_db,
)
from lambdas.common.game_schema import create_game_schema

DEFAULT_LANGUAGE = "en"
USE_BASIC_DICTIONARY = True # Determine which dictionary to use for seed words

def create_random_game(
    language: str = "en", 
    board_size: str = "3x3", 
    seed_words: Optional[tuple[str, str]] = None,
    clue: Optional[str] = "",
    created_by: Optional[str] = None,
    from_lambda_console: bool = False,
    is_casual: bool = False,
) -> Dict[str, Any]:
    """
    Create a random game by selecting two words from the dictionary and generating a layout.

    Args:
        language (str): The language code for the dictionary (default: 'en').
        board_size (str): The size of the board to generate (default: '3x3).
        seed_words (tuple[str, str], optional): The two words to use to generate the puzzle, if provided.
            If not provided, the function will select two compatible words at random.
        clue (str): A clue for finding the solution based on the seed words.
        created_by (str): The author of the puzzle, if provided.
        from_lambda_console (bool): True if the game creation request came from Lambda, or false it came from the web UI.
        is_casual: If true, seed words do not have to be in the dictionary.

    Returns:
        Dict[str, Optional[List[str]]]: A dictionary containing the selected words and the game layout.
    
    Raises:
        ValueError if a step in the process fails.
    """
    start_time = time.time()
    print(f"\n[INFO] Starting random game creation for language '{language}' and board size '{board_size}'")

    # Fetch the dictionary for the specified language
    dict_start = time.time()
    dictionary = get_dictionary(language)
    basic_dictionary = get_basic_dictionary(language) if USE_BASIC_DICTIONARY else dictionary
    # Use the full dictionary for larger boards
    larger_boards = ["4x4", "5x5"]
    if board_size in larger_boards:
        basic_dictionary = dictionary
    
    dict_time = time.time() - dict_start
    print(f"[INFO] Dictionary fetch completed in {dict_time:.2f} seconds")

    if not dictionary:
        raise ValueError("Dictionary not found for the specified language.")
    if not basic_dictionary:
        raise ValueError("Basic dictionary not found for the specified language.")

    # Select two words that can be potentially linked for the random puzzle, if not provided
    select_words_start = time.time()
    if not seed_words:
        print(f"Seed words not passed. Selecting two words from {len(basic_dictionary)}-word dictionary.")
        seed_words = select_two_words(basic_dictionary, board_size)
        if not seed_words:
            raise ValueError("[ERROR] Failed to find a valid pair of words for the game.")
    select_words_time = time.time() - select_words_start
    print(f"[INFO] Word selection completed in {select_words_time:.2f} seconds")

    word1, word2 = seed_words
    print(f"[INFO] Selected words: {word1}, {word2}")

    # Validate that the two provided words are actually in the dictionary
    if not is_casual:
        if word1 not in dictionary or word2 not in dictionary:
            raise ValueError(f"One or both words ({word1}, {word2}) are not valid dictionary words.")

    # Generate the game layout
    layout_start = time.time()
    game_layout = generate_layout(word1, word2, board_size)
    layout_time = time.time() - layout_start
    if not game_layout:
        raise ValueError("[ERROR] Failed to generate a valid layout for the game.")
    print(f"[INFO] Layout generation completed in {layout_time:.2f} seconds")

    game_type = "custom"
    if is_casual:
        game_type = "casual"
    elif from_lambda_console:
        game_type = "random"

    game_data = create_game_schema(
        game_layout=game_layout,
        game_type=game_type,
        language=language,
        board_size=board_size,
        random_seed_words=[word1, word2],
        created_by=created_by or "",
        clue=clue or "",
    )

    # Insert the two seed words into the valid words list for this game (for casual games)
    if is_casual:
        game_data["validWords"].append(word1)
        game_data["validWords"].append(word2)
        game_data["baseValidWords"].append(word1)
        game_data["baseValidWords"].append(word2)
        print(f"{word1} and {word2} added to valid words list for this casual game.")

    # Store the game in the games DB
    db_start = time.time()
    success = add_game_to_db(game_data)
    db_time = time.time() - db_start
    print(f"[INFO] Database operations completed in {db_time:.2f} seconds")

    if success and from_lambda_console:
    # Add the game to the random games table and track the count (if created via Lambda console)
        atomic_start = time.time()
        atomic_number = add_game_id_to_random_games_db(game_data["gameId"], language)
        atomic_time = time.time() - atomic_start
        print(f"[INFO] Atomic number tracking completed in {atomic_time:.2f} seconds")

    total_time = time.time() - start_time
    print(f"[INFO] Random game creation completed in {total_time:.2f} seconds\n")

    return game_data


def create_random_small_board_game(
    language: str, 
    board_size: str, 
    seed_word: Optional[str] = None,
    clue: Optional[str] = "",
    created_by: Optional[str] = None,
    from_lambda_console: bool = False,
    is_casual: bool = False,
) -> Dict[str, Any]:
    """
    Create a random game by selecting a single word from the dictionary and generating a layout.

    Args:
        language (str): The language code for the dictionary.
        board_size (str): The size of the board to generate.
        seed_word (Optional[str], optional): The seed word to use for puzzle generation, if provided. Defaults to None.
        clue (Optional[str], optional): A clue for finding the solution based on the seed words, if provided.
        created_by (str): The author of the puzzle, if provided.
        from_lambda_console (bool): True if the game creation request came from Lambda, or false it came from the web UI.
        is_casual: If true, seed words do not have to be in the dictionary.

    Returns:
        Dict[str, Optional[List[str]]]: A dictionary containing the selected words and the game layout.
    """
    crsb_start_time = time.time()
    print(f"\n[INFO] Starting random game creation for language '{language}' and board size '{board_size}'")

    # Fetch the dictionary for the specified language
    dict_start = time.time()
    dictionary = get_dictionary(language)
    basic_dictionary = get_basic_dictionary(language) if USE_BASIC_DICTIONARY else dictionary

    
    dict_time = time.time() - dict_start
    print(f"[INFO] Dictionary fetch completed in {dict_time:.2f} seconds")

    if not dictionary:
        raise ValueError("Dictionary not found for the specified language.")
    if not basic_dictionary:
        raise ValueError("Basic dictionary not found for the specified language.")
    
    # Select a single word that can be potentially used for the random puzzle, if not provided
    select_word_start = time.time()
    if not seed_word:
        print(f"Seed word not passed. Selecting a word from {len(basic_dictionary)}-word dictionary.")
        seed_word = select_one_word(basic_dictionary, board_size)
        if not seed_word:
            raise ValueError("[ERROR] Failed to find a valid word for the game.")
    select_word_time = time.time() - select_word_start
    print(f"[INFO] Word selection completed in {select_word_time:.2f} seconds")
    
    if not is_casual and seed_word not in dictionary:
        raise ValueError(f"Seed word '{seed_word}' is not a valid dictionary word.")
    
    # Generate the game layout
    layout_start = time.time()
    game_layout = generate_layout_from_single_word(seed_word, board_size)
    layout_time = time.time() - layout_start
    if not game_layout:
        raise ValueError("[ERROR] Failed to generate a valid layout for the game.")
    print(f"[INFO] Layout generation completed in {layout_time:.2f} seconds")
    
    game_type = "custom"
    if is_casual:
        game_type = "casual"
    elif from_lambda_console:
        game_type = "random"

    game_data = create_game_schema(
        game_layout=game_layout,
        game_type=game_type,
        language=language,
        random_seed_word=seed_word,
        board_size=board_size,
        created_by=created_by or "",
        clue=clue or "",
    )

    # Insert the seed word into the valid words list for this game (for casual games)
    if is_casual:
        game_data["validWords"].append(seed_word)
        game_data["baseValidWords"].append(seed_word)
        print(f"{seed_word} added to valid words list for this casual game.")
    
    # Store the game in the games DB
    db_start = time.time()
    success = add_game_to_db(game_data)
    db_time = time.time() - db_start
    print(f"[INFO] Database operations completed in {db_time:.2f} seconds")

    # Add the game to the random games table and track the count, if game was created from lambda console
    if success and from_lambda_console:
        atomic_start = time.time()
        atomic_number = add_game_id_to_random_games_db(game_data["gameId"], language)
        atomic_time = time.time() - atomic_start
        print(f"[INFO] Atomic number tracking completed in {atomic_time:.2f} seconds")

    total_time = time.time() - crsb_start_time
    print(f"[INFO] Random game creation completed in {total_time:.2f} seconds\n")

    return game_data
    

def generate_layout(word1: str, word2: str, board_size: str) -> Optional[List[str]]:
    """
    Generate a game layout with letters from two words distributed across 4 sides,
    maintaining adjacency constraints and handling shared and repeated letters.

    Args:
        word1 (str): The first word.
        word2 (str): The second word.
        board_size (str): The size of the board to generate.

    Returns:
        Optional[List[str]]: A list of 4 strings representing the sides of the board,
        or None if no valid layout can be generated.
    """
    layout_start = time.time()
    print(f"[INFO] Starting layout generation for words '{word1}' and '{word2}' with board size '{board_size}'")
    try:
        rows, cols = map(int, board_size.lower().split('x'))
    except ValueError:
        raise ValueError(f"Invalid board size format: '{board_size}'. Expected 'm x n'.")

    total_spaces = (2 * rows) + (2 * cols)
    base_word1 = normalize_to_base(word1)
    base_word2 = normalize_to_base(word2)

    if base_word2[0] != base_word1[-1]:
        return None

    combined_letters = base_word1 + base_word2[1:]
    if len(set(combined_letters)) != total_spaces:
        return None

    sides = [""] * 4
    letter_to_side: Dict[str, int] = {}

    def backtrack(index: int, current_side: int) -> bool:
        if index == len(combined_letters):
            return True

        letter = combined_letters[index]
        if letter in letter_to_side:
            next_side = letter_to_side[letter]
            return next_side != current_side and backtrack(index + 1, next_side)

        # Try placing the letter on a valid side
        side_indices = list(range(4))  # Four sides
        random.shuffle(side_indices)  # Shuffle to introduce randomness

        for side_index in side_indices:
            if side_index == current_side or len(sides[side_index]) >= rows:
                continue

            sides[side_index] += letter
            letter_to_side[letter] = side_index

            if backtrack(index + 1, side_index):
                return True

            sides[side_index] = sides[side_index][:-1]
            del letter_to_side[letter]

        return False

    if backtrack(0, -1):
        shuffled_sides = shuffle_final_layout(sides)
        layout_time = time.time() - layout_start
        print(f"[INFO] Layout generation {shuffled_sides} completed in {layout_time:.2f} seconds")
        return shuffled_sides
    layout_time = time.time() - layout_start
    print(f"[ERROR] Layout generation failed after {layout_time:.2f} seconds")
    return None


def generate_layout_from_single_word(word: str, board_size: str) -> Optional[List[str]]:
    """
    Generate a game layout using letters from a single word distributed across 4 sides,
    maintaining adjacency constraints and handling shared and repeated letters.

    Args:
        word (str): The seed word to generate the layout.
        board_size (str): The size of the board to generate.

    Returns:
        Optional[List[str]]: A list of 4 strings representing the sides of the board,
        or None if no valid layout can be generated.
    """
    layout_start = time.time()
    print(f"[INFO] Starting layout generation for word '{word}' with board size '{board_size}'")

    # Validate the board size
    try:
        rows, cols = map(int, board_size.lower().split('x'))
    except ValueError:
        raise ValueError(f"Invalid board size format: '{board_size}'. Expected 'm x n'.")

    total_spaces = (2 * rows) + (2 * cols)
    base_word = normalize_to_base(word)

    if len(set(base_word)) != total_spaces:
        print(f"[ERROR] Word '{word}' does not contain the exact number of unique letters required for the board size.")
        return None

    # Initialize the sides of the board
    sides = [""] * 4
    letter_to_side: Dict[str, int] = {}

    def backtrack(index: int, current_side: int) -> bool:
        if index == len(base_word):
            return True  # Successfully placed all letters

        letter = base_word[index]

        # Check if the letter has already been assigned to a side
        if letter in letter_to_side:
            next_side = letter_to_side[letter]
            return next_side != current_side and backtrack(index + 1, next_side)

        # Try placing the letter on a valid side
        side_indices = list(range(4))  # Four sides
        random.shuffle(side_indices)  # Shuffle to introduce randomness

        for side_index in side_indices:
            if side_index == current_side or len(sides[side_index]) >= rows:
                continue  # Skip the current side or sides that are full

            # Place the letter
            sides[side_index] += letter
            letter_to_side[letter] = side_index

            # Recurse to the next letter
            if backtrack(index + 1, side_index):
                return True

            # Undo placement if it doesn't lead to a solution
            sides[side_index] = sides[side_index][:-1]
            del letter_to_side[letter]

        return False

    # Begin backtracking
    if backtrack(0, -1):
        shuffled_sides = shuffle_final_layout(sides)
        layout_time = time.time() - layout_start
        print(f"[INFO] Layout generation {shuffled_sides} completed in {layout_time:.2f} seconds")
        return shuffled_sides

    # If no valid layout is found
    layout_time = time.time() - layout_start
    print(f"[ERROR] Layout generation failed after {layout_time:.2f} seconds")
    return None


def select_one_word(dictionary: List[str], board_size: str, max_attempts: int = 10000) -> Optional[str]:
    """
    Select one word that contains enough unique letters to fill the board.

    Args:
        dictionary (List[str]): List of words from the dictionary.
        board_size (str): The size of the board that the word must fit on.
        max_attempts (int): Maximum number of attempts to find a valid word.

    Returns:
        Optional[str]: A single word that fits the board or None if no word is found.
    """
    print(f"[INFO] Starting single-word selection with board size '{board_size}'")
    
    try:
        rows, cols = map(int, board_size.lower().split('x'))
    except ValueError:
        raise ValueError(f"Invalid board size format: '{board_size}'. Expected 'm x n'.")
    
    num_unique_letters_required = (2 * rows) + (2 * cols)
    print(f"[INFO] Searching for a word with {num_unique_letters_required} unique letters.")
    
    for attempt in range(max_attempts):
        word = random.choice(dictionary)
        base_word = normalize_to_base(word)
        
        # Check if the word has exactly the required number of unique letters
        if len(set(base_word)) == num_unique_letters_required:
            print(f"[INFO] Word selection succeeded after {attempt + 1} attempts: '{word}'")
            return word
    
    print(f"[ERROR] Single-word selection failed after {max_attempts} attempts")
    return None


def load_dictionary(file_path: str) -> List[str]:
    """
    Load the dictionary from the specified file.

    Args:
        file_path (str): Path to the dictionary file.

    Returns:
        List[str]: List of words in the dictionary.
    """
    with open(file_path, 'r') as file:
        return [line.strip().upper() for line in file if line.strip().isalpha()]


def select_two_words(dictionary: List[str], board_size: str, max_attempts: int = 10000) -> Optional[Tuple[str, str]]:
    """
    Select two words that together contain enough unique letters to fill the board, and where
    the first base letter of one word matches the last base letter of the other.

    Args:
        dictionary (List[str]): List of words from the dictionary.
        board_size (str): The size of the board that the words must fit on.
        max_attempts (int): Maximum number of attempts to find a valid pair.

    Returns:
        Optional[Tuple[str, str]]: A tuple of two words or None if no pair is found.
    """
    print(f"[INFO] Starting word selection with board size '{board_size}'")
    try:
        rows, cols = map(int, board_size.lower().split('x'))
    except ValueError:
        raise ValueError(f"Invalid board size format: '{board_size}'. Expected 'm x n'.")
    num_unique_letters_required = (2 * rows) + (2 * cols)
    print(f"Searching for two words with {num_unique_letters_required} unique letters.")

    # Don't allow the two words to share too many common letters, for better puzzle variety
    MAX_SHARED_LETTERS = 1

    for attempt in range(max_attempts):
        word1 = random.choice(dictionary)
        base_word1 = normalize_to_base(word1)
        
        for word2 in dictionary:
            base_word2 = normalize_to_base(word2)
            shared_letters = set(base_word1).intersection(base_word2)
            if (
                base_word1[-1] == base_word2[0]
                and len(set(base_word1 + base_word2)) == num_unique_letters_required
                and len(shared_letters) <= MAX_SHARED_LETTERS
            ):
                print(f"[INFO] Word selection succeeded after {attempt + 1} attempts")
                return word1, word2
    print(f"[ERROR] Word selection failed after {max_attempts} attempts")
    return None


def shuffle_final_layout(layout: List[str]) -> List[str]:
    """
    Shuffle the letters within each side and shuffle the sides themselves.

    Args:
        layout (List[str]): The generated layout with letters placed.

    Returns:
        List[str]: The shuffled layout.
    """
    shuffled_sides = [''.join(random.sample(side, len(side))) for side in layout]
    random.shuffle(shuffled_sides)
    return shuffled_sides
