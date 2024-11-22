from typing import Dict, Any, Optional, List, Tuple
import uuid
import hashlib
from datetime import datetime, timezone

from lambdas.common.game_utils import (
    standardize_board,
    calculate_two_word_solutions,
    calculate_three_word_solutions,
    generate_valid_words,
    standardize_board,
)


def create_game_schema(
    game_id: Optional[str] = None,
    game_layout: Optional[List[str]] = None,
    game_type: str = "",
    official_game: Optional[bool] = None,
    standardized_hash: Optional[str] = None,
    valid_words: Optional[List[str]] = None,
    valid_word_count: Optional[int] = 0,
    two_word_solutions: Optional[List[Tuple[str, str]]] = None,
    three_word_solutions: Optional[List[Tuple[str, str, str]]] = None,
    two_word_solution_count: Optional[int] = 0,
    three_word_solution_count: Optional[int] = 0,
    nyt_solution: Optional[List[str]] = None,
    dictionary: Optional[List[str]] = None,
    par: Optional[str] = None,
    board_size: str = "3x3",
    language: str = "en",
    created_at: Optional[str] = None,
    created_by: str = "",
    clue: str = "",
) -> Dict[str, Any]:
    """
    Create a game schema with validation and default values.

    Args:
        game_id: Optional game ID. Generated if not provided.
        game_layout: List of letters forming the game layout.
        game_type: Type of the game ("nyt", "custom", "random").
        official_game: Whether the game is official (NYT).
        standardized_hash: Hash of the board layout.
        valid_words: Precomputed list of valid words. Generated if not provided.
        valid_word_count: Total count of valid words in the puzzle.
        two_word_solutions: Precomputed two-word solutions. Generated if not provided.
        three_word_solutions: Precomputed three-word solutions. Generated if not provided.
        two_word_solution_count: Total count of two-word solutions in the puzzle.
        three_word_solution_count: Total count of three-word solutions in the puzzle.
        nyt_solution: NYT-provided solution.
        dictionary: List of words used by NYT official games for validation.
        par: Expected minimum word count.
        board_size: Size of the board (e.g., "3x3").
        language: Language of the game (e.g., "en").
        created_at: ISO timestamp for when the gae was created.
        created_by: Identifier for the user who created the game, if applicable.
        clue: Clue for the two-word solution to this puzzle.

    Returns:
        A dictionary representing the game schema.
    """

    # Validate input fields
    if not validate_board_size(board_size):
        raise ValueError("Selected board size is not supported.")
    
    if not validate_language(language):
        raise ValueError("Selected language is not supported.")
    
    if not game_layout:
        raise ValueError("Game layout is required to create a game schema.")
    
    # Validate board layout (raises an error if invalid)
    validate_board_matches_layout(game_layout, board_size)

    # Generate missing fields
    game_id = game_id or generate_game_id()
    if not standardized_hash:
        standardized_game_layout = standardize_board(game_layout)
        standardized_hash = generate_standardized_hash(game_layout)
    valid_words = valid_words or generate_valid_words(game_layout, language) or []
    two_word_solutions = (
        two_word_solutions 
        or calculate_two_word_solutions(game_layout, language, valid_words=valid_words)
        or []
    )
    three_word_solutions = (
        three_word_solutions 
        or calculate_three_word_solutions(game_layout, language, valid_words=valid_words)
        or []
    )
    nyt_solution = nyt_solution or []
    par = par or "N/A"
    official_game = official_game if official_game is not None else (game_type == "nyt")
    created_time = datetime.utcnow().isoformat()

    return {
        "gameId": game_id,
        "gameLayout": game_layout,
        "gameType": game_type,
        "officialGame": official_game,
        "standardizedHash": standardized_hash,
        "validWords": valid_words,
        "validWordCount": len(valid_words),
        "twoWordSolutions": two_word_solutions,
        "threeWordSolutions": three_word_solutions,
        "twoWordSolutionCount": len(two_word_solutions),
        "threeWordSolutionCount": len(three_word_solutions),
        "nytSolution": nyt_solution,
        "dictionary": dictionary,
        "par": par,
        "boardSize": board_size,
        "language": language,
        "createdAt": created_time,
        "createdBy": created_by,
        "clue": clue,
    }


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


def generate_standardized_hash(standardized_game_layout: List[str]) -> str:
    """
    Generate a hash of the game layout, using a standardized letter layout so that 
    equivalent boards generate the same hash.
    
    Args:
        standardized_game_layout (List[str]): The input letters for this game, 
        sorted so that equivalent boards generate the same hash.
    """
    layout_str = "-".join(standardized_game_layout)
    return hashlib.sha256(layout_str.encode()).hexdigest()


def generate_game_id() -> str:
    """
    Generate a unique game id for a user-created game.

    Returns:
        str: A unique identifier string.
    """
    return str(uuid.uuid4())