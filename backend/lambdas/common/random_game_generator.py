import random
import os
import unicodedata
import sys
import time
from typing import List, Optional, Tuple, Dict, Any
from collections import Counter
from unittest.mock import patch, MagicMock
import boto3

# Add the backend directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from lambdas.create_random.random_game_service import create_random_game, create_random_small_board_game


def main() -> Any:
    small_board = False
    
    if small_board:
        create_random_small_board_game(
            "en",
            "2x2"
        )
    else:
        create_random_game(
            "ru",
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
    os.environ["RANDOM_GAMES_TABLE_RU"] = "LetterBoxedRandomGames_ruTest"
    
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
