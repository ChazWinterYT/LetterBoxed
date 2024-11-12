from uuid import uuid4
import hashlib

def generate_game_id(sides, is_random=False, max_retries=3):
    """
    Create a standardized layout and hash it to generate a unique game ID
    """
    standardized_layout = standardize_board(sides)
    game_id = hashlib.sha256(standardized_layout.encode()).hexdigest()
    return game_id, standardized_layout


def standardize_board(sides):
    """
    Alphabetize the letters on each side of the board and create a 
    standardized layout string
    """
    standardized_sides = ["".join(sorted(side)) for side in sides]
    standardized_layout = ["-".join(standardized_sides)]
    return standardized_layout
