import random
import os
import unicodedata
import sys
import time
from typing import List, Optional, Tuple, Dict, Any
from collections import Counter

# Add the backend directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from lambdas.common.game_utils import (
    standardize_board,
    generate_valid_words,
    calculate_two_word_solutions,
)

from lambdas.create_random.random_game_service import create_random_game, create_random_small_board_game


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
    

def select_two_words(dictionary: List[str], max_attempts: int = 10000) -> Optional[Tuple[str, str]]:
    """
    Select two words that together contain exactly 12 unique base letters and where
    the first base letter of one word matches the last base letter of the other.

    Args:
        dictionary (List[str]): List of words from the dictionary.
        max_attempts (int): Maximum number of attempts to find a valid pair.

    Returns:
        Optional[Tuple[str, str]]: A tuple of two words or None if no pair is found.
    """
    for _ in range(max_attempts):
        word1, word2 = random.sample(dictionary, 2)
        # Compare base letters for linking
        if (
            normalize_to_base(word1[-1]) == normalize_to_base(word2[0]) and
            len(set(normalize_to_base(word1 + word2))) == 12  # Ensure 12 unique base letters
        ):
            return word1, word2
    return None


def generate_layout(word1: str, word2: str) -> Optional[List[str]]:
    """
    Generate a game layout with letters from two words distributed across 4 sides,
    maintaining adjacency constraints and handling shared and repeated letters.

    Args:
        word1 (str): The first word.
        word2 (str): The second word.

    Returns:
        Optional[List[str]]: A list of 4 strings representing the sides of the board,
        or None if no valid layout can be generated.
    """
    base_word1 = normalize_to_base(word1)
    base_word2 = normalize_to_base(word2)

    combined_letters = base_word1 + base_word2[1:]  # Combine words, excluding duplicate shared letter
    if len(set(combined_letters)) != 12:
        raise ValueError("The combined words must have exactly 12 unique letters.")

    sides = [""] * 4  # Initialize 4 empty sides
    letter_to_side: Dict[str, int] = {}  # Track where each letter is placed

    def backtrack(index: int, current_side: int) -> bool:
        # Base case: all letters are placed
        if index == len(combined_letters):
            return True

        letter = combined_letters[index]

        # If letter already placed, ensure adjacency rule is respected
        if letter in letter_to_side:
            next_side = letter_to_side[letter]
            if next_side == current_side:
                return False  # Violates adjacency rule
            return backtrack(index + 1, next_side)

        # Randomize side order
        side_indices = list(range(4))
        random.shuffle(side_indices)

        # Try placing the letter on each valid side
        for side_index in side_indices:
            if side_index == current_side or len(sides[side_index]) >= 3:
                continue  # Skip same side or full side

            # Place the letter
            sides[side_index] += letter
            letter_to_side[letter] = side_index

            # Recurse to the next letter
            if backtrack(index + 1, side_index):
                return True

            # Undo placement (backtrack)
            sides[side_index] = sides[side_index][:-1]
            del letter_to_side[letter]

        # If no valid placement found, return False
        return False

    # Start the backtracking process
    if backtrack(0, -1):
        # Shuffle the layout for additional randomness
        return shuffle_final_layout(sides)
    else:
        return None


def normalize_to_base(word: str) -> str:
    """
    Normalize a word to its base form by removing accents and diacritical marks.
    """
    return ''.join(
        char for char in unicodedata.normalize('NFD', word)
        if unicodedata.category(char) != 'Mn'
    )


def shuffle_final_layout(layout: List[str]) -> List[str]:
    """
    Shuffle the letters within each side and shuffle the sides themselves.

    Args:
        layout (List[str]): The generated layout with letters placed.

    Returns:
        List[str]: The shuffled layout.
    """
    # Shuffle letters within each side
    shuffled_sides = [''.join(random.sample(side, len(side))) for side in layout]

    # Shuffle the sides
    random.shuffle(shuffled_sides)

    return shuffled_sides


def main() -> Any:
    small_board = True
    
    if small_board:
        create_random_small_board_game(
            "en",
            "2x2"
        )
    else:
        create_random_game(
            "en",
            "3x3",
        )

# def main() -> Any:
#     language = "en"

#     # Path to the directory
#     script_dir = os.path.dirname(os.path.abspath(__file__))
#     basic_dictionary_path = os.path.join(script_dir, "..", "..", "dictionaries", language, "basic.txt")
#     basic_dictionary_path = os.path.abspath(basic_dictionary_path)
#     dictionary_path = os.path.join(script_dir, "..", "..", "dictionaries", language, "dictionary.txt")
#     dictionary_path = os.path.abspath(dictionary_path)

#     # Load the dictionaries
#     basic_dictionary = load_dictionary(basic_dictionary_path)
#     dictionary = load_dictionary(dictionary_path)

#     # Try to generate a random game
#     word_pair = select_two_words(dictionary)

#     if not word_pair:
#         print("Failed to find a valid word pair after max attempts.")
#         return None
    
#     word1, word2 = word_pair
#     print(f"Found two candidate words: {word1}, {word2}")

#     game_layout = generate_layout(word1, word2)

#     if not game_layout:
#         print("Failed to generate a valid layout.")
#         return None
    
#     print(f"Layout found! {game_layout}")

#     # Standardize the layout
#     standardized_layout = standardize_board(game_layout)

#     # Generate valid words for this puzzle
#     valid_words = generate_valid_words(standardized_layout, language)

#     # Calculate two word solutions
#     solutions = calculate_two_word_solutions(standardized_layout, language, valid_words=valid_words)
#     if not solutions:
#         print("Generated layout is not a viable puzzle")
#         return None

#     print("Viable random puzzle generated!")

#     return {
#         "gameLayout": game_layout,
#     }

def benchmark(n: int) -> None:
    import time

    times = []
    successful_runs = 0
    fails = 0

    for i in range(n):
        start_time = time.perf_counter()
        while True:
            result = main()  # Run the main function and capture the result
            if result:  # Check if a valid result is returned
                break  # Exit the loop on success
            fails += 1
        end_time = time.perf_counter()

        successful_runs += 1
        times.append(end_time - start_time)
        print(f"Run {successful_runs}/{n} completed in {times[-1]:.4f} seconds.")

    # Calculate and print the benchmark results
    avg_time = sum(times) / len(times)
    print("\n=== Benchmark Results ===")
    print(f"Number of successful runs: {successful_runs}")
    print(f"Number of fails: {fails}")
    print(f"Average time: {avg_time:.4f} seconds")
    print(f"Longest time: {max(times):.4f} seconds")
    print(f"Shortest time: {min(times):.4f} seconds")


if __name__ == "__main__":
    RUN_BENCHMARK = True  # Set to False to disable benchmarking
    
    # Set up environment variables
    os.environ["DICTIONARY_SOURCE"] = "s3"
    os.environ["S3_BUCKET_NAME"] = "test-dictionary-bucket"
    os.environ["DICTIONARY_BASE_S3_PATH"] = "Dictionaries/"
    os.environ["DEFAULT_LANGUAGE"] = "en"
    os.environ["GAMES_TABLE"] = "LetterBoxedGamesTest"
    os.environ["VALID_WORDS_TABLE"] = "LetterBoxedValidWords1Test"
    os.environ["SESSION_STATES_TABLE"] = "LetterBoxedSessionStatesTest"
    os.environ["METADATA_TABLE"] = "LetterBoxedMetadataTableTest"
    os.environ["ARCHIVE_TABLE"] = "LetterBoxedArchiveTest"
    os.environ["RANDOM_GAMES_TABLE_EN"] = "LetterBoxedRandomGames_enTest"
    os.environ["RANDOM_GAMES_TABLE_ES"] = "LetterBoxedRandomGames_esTest"
    os.environ["RANDOM_GAMES_TABLE_IT"] = "LetterBoxedRandomGames_itTest"
    os.environ["RANDOM_GAMES_TABLE_PL"] = "LetterBoxedRandomGames_plTest"
    
    if RUN_BENCHMARK:
        benchmark(10)  # Change 10 to the desired number of iterations
    else:
        main()
        
    # Clean up environment variables
    os.environ.pop("DICTIONARY_SOURCE", None)
    os.environ.pop("S3_BUCKET_NAME", None)
    os.environ.pop("DICTIONARY_BASE_S3_PATH", None)
    os.environ.pop("DEFAULT_LANGUAGE", None)
    os.environ.pop("GAMES_TABLE", None)
    os.environ.pop("VALID_WORDS_TABLE", None)
    os.environ.pop("SESSION_STATES_TABLE", None)
    os.environ.pop("METADATA_TABLE", None)
    os.environ.pop("ARCHIVE_TABLE", None)
    os.environ.pop("RANDOM_GAMES_TABLE_EN", None)
    os.environ.pop("RANDOM_GAMES_TABLE_ES", None)
    os.environ.pop("RANDOM_GAMES_TABLE_IT", None)
    os.environ.pop("RANDOM_GAMES_TABLE_PL", None)
