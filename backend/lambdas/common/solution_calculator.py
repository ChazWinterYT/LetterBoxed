import sys
import os

# Add the backend directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from lambdas.common.game_utils import (
    calculate_two_word_solutions, 
    calculate_three_word_solutions,
)

game_layout = ["TLQ","SRU","BFI","EMO"]

def calculate_solutions():
    two_word_solutions = calculate_two_word_solutions(game_layout, "en")

    print(f"{len(two_word_solutions)} Two word solutions for game layout: {game_layout}")
    for solution in two_word_solutions:
        print(solution)


if __name__ == "__main__":
    calculate_solutions()