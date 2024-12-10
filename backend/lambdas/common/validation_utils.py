from typing import List, Dict, Tuple, Optional, Any
import decimal


def validate_game_schema(game_item: Dict) -> Dict:
    """
    Validates a game item and populates missing fields with default values.
    """
    if game_item is None:
        return None
    
    defaults = {
        "gameId": "",
        "gameLayout": [],
        "gameType": "",
        "officialGame": False,
        "standardizedHash": "",
        "validWords": [],
        "validWordCount": 0,
        "baseValidWords": [],
        "oneWordSolutions": [],
        "twoWordSolutions": [],
        "threeWordSolutions": [],
        "oneWordSolutionCount": 0,
        "twoWordSolutionCount": 0,
        "threeWordSolutionCount": 0,
        "nytSolution": [],
        "randomSeedWord": "",
        "randomSeedWords": [],
        "dictionary": [],
        "par": "",
        "boardSize": "3x3",
        "language": "en",
        "totalRatings": 0,
        "totalStars": 0,
        "totalCompletions": 0,
        "totalWordsUsed": 0,
        "totalLettersUsed": 0,
        "createdAt": "",
        "createdBy": "",
        "clue": "",
    }
    
    # Populate missing fields with their defaults
    for field, default in defaults.items():
        if field not in game_item or game_item[field] is None:
            game_item[field] = default
    
    return convert_decimal(game_item)


def convert_decimal(obj: Any) -> Any:
    """
    Recursively converts DynamoDB Decimal types to JSON-compatible types.
    
    Args:
        obj: The object to be converted (can be dict, list, or other types).
    
    Returns:
        A JSON-compatible version of the object.
    """
    if isinstance(obj, dict):
        return {k: convert_decimal(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_decimal(i) for i in obj]
    elif isinstance(obj, tuple):
        return tuple(convert_decimal(i) for i in obj)  # Ensure tuple compatibility
    elif isinstance(obj, set):
        return {convert_decimal(i) for i in obj}  # Ensure set compatibility
    elif isinstance(obj, decimal.Decimal):
        # Convert to int if it's a whole number, otherwise convert to float
        return int(obj) if obj % 1 == 0 else float(obj)
    else:
        # Return the object as is if no conversion is needed
        return obj
    

def validate_board_size(board_size: str) -> bool:
    """
    Validate if the board size is allowed.

    Args:
        board_size (str): The board size to validate.

    Returns:
        bool: True if the board size is valid, False otherwise.
    """
    valid_board_sizes = ["2x2", "3x3", "4x4"]
    return board_size in valid_board_sizes


def validate_language(language: str) -> bool:
    """
    Validate if the language is supported for game creation.

    Args:
        language (str): The language to validate.

    Returns:
        bool: True if the language is supported, False otherwise.
    """
    valid_languages = ["de", "en", "es", "it", "pl", "ru"]
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