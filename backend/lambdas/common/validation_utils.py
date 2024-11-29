from typing import List

def validate_board_size(board_size: str) -> bool:
    """
    Validate if the board size is allowed.

    Args:
        board_size (str): The board size to validate.

    Returns:
        bool: True if the board size is valid, False otherwise.
    """
    valid_board_sizes = ["3x3", "4x4", "5x5"]
    return board_size in valid_board_sizes


def validate_language(language: str) -> bool:
    """
    Validate if the language is supported.

    Args:
        language (str): The language to validate.

    Returns:
        bool: True if the language is supported, False otherwise.
    """
    valid_languages = ["en", "es", "fr", "pl", "de", "it", "sv"]
    return language in valid_languages


def validate_board_matches_layout(game_layout: List[str], board_size: str) -> None:
    """
    Validates the game layout against the specified board size.
    Raises a ValueError if the layout does not match the board size.

    Args:
        game_layout (List[str]): The game layout as a list of strings.
        board_size (str): The board size in the format "m x n" (e.g., "3x3" or "4x5").

    Raises:
        ValueError: If the layout does not match the specified board size.
    """
    try:
        rows, cols = map(int, board_size.lower().split('x'))
    except ValueError:
        raise ValueError(f"Invalid board size format: '{board_size}'. Expected 'm x n'.")

    total_spaces = (2 * rows) + (2 * cols)
    layout_letter_count = sum(len(side) for side in game_layout)

    if layout_letter_count != total_spaces:
        raise ValueError(
            f"Invalid game layout: Expected {total_spaces} letters for a {rows}x{cols} board, "
            f"but got {layout_letter_count}."
        )