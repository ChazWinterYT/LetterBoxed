from typing import List, Dict, Any, Optional
import decimal

# Constants for validation
VALID_GAME_TYPES = ["random", "custom", "nyt", "casual"]
VALID_BOARD_SIZES = ["2x2", "3x3", "4x4"]
VALID_LANGUAGES = ["de", "en", "es", "fr", "it", "pl", "ru"]

# Required keys for pagination based on filtering type
LANGUAGE_PAGINATION_KEYS = ["language", "createdAt", "gameId"]
GAME_TYPE_PAGINATION_KEYS = ["gameTypeLanguage", "createdAt", "gameId"]


def validate_game_schema(game_item: Dict[str, Any]) -> Dict[str, Any]:
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
        "createdBy": "Anonymous",
        "clue": "",
    }
    
    # Populate missing fields with their defaults
    for field, default in defaults.items():
        if field not in game_item or game_item[field] is None:
            game_item[field] = default
    
    converted_game_item: Dict[str, Any] = convert_decimal(game_item)
    return converted_game_item


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
    return board_size in VALID_BOARD_SIZES


def validate_language(language: str) -> bool:
    """
    Validate if the language is supported for game creation.

    Args:
        language (str): The language to validate.

    Returns:
        bool: True if the language is supported, False otherwise.
    """
    return language in VALID_LANGUAGES


def validate_pagination_key(last_key: Dict[str, str], game_type: Optional[str] = None) -> None:
    """
    Validates pagination key based on filtering type.
    
    Args:
        last_key: The pagination key to validate
        game_type: If provided, validates for gameType filtering, otherwise for language filtering
        
    Raises:
        ValueError: If the pagination key is invalid
    """
    if game_type:
        required_keys = GAME_TYPE_PAGINATION_KEYS
        context = "gameType filtering"
    else:
        required_keys = LANGUAGE_PAGINATION_KEYS
        context = "language filtering"
    
    if not all(key in last_key for key in required_keys):
        raise ValueError(
            f"last_key for {context} must include {', '.join(required_keys)}."
        )


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
