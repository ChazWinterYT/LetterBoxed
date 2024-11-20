import sys
import os
from typing import List

# Add the backend directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from lambdas.common.game_utils import (  # Ensure this module complies with mypy
    calculate_two_word_solutions,
    calculate_three_word_solutions,
)

# THIS FILE IS MEANT TO BE RUN FROM YOUR LOCAL MACHINE ONLY

# Define the game layout as a list of strings
game_layout: List[str] = ["TLQ", "SRU", "BFI", "EMO"]

def calculate_solutions() -> None:
    """
    Calculate and print two-word solutions for the given game layout.
    """
    # Calculate two-word solutions
    two_word_solutions: List[List[str]] = calculate_two_word_solutions(game_layout, "en")

    # Print results
    print(f"{len(two_word_solutions)} Two-word solutions for game layout: {game_layout}")
    for solution in two_word_solutions:
        print(solution)


if __name__ == "__main__":
    calculate_solutions()
