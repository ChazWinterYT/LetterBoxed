from uuid import uuid4
import hashlib

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


def calculate_two_word_solutions(game_layout):
    """
    Calculate the two word solutions to the given puzzle input.

    Args:
        game_layout (List[str]): The input letters for this game.
    """
    pass


def calculate_three_word_solutions(game_layout):
    """
    Calculate three word solutions to the given puzzle input.

    Args:
        game_layout (List[str]): The input letters for this game.
    """
    pass
