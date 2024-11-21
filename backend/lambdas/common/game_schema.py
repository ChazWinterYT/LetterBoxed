from typing import Dict, Any
import uuid
from datetime import datetime, timezone

from lambdas.common.game_utils import (
    generate_game_id,
    standardize_board,
    generate_standardized_hash,
    calculate_two_word_solutions,
    calculate_three_word_solutions,
    generate_valid_words,
)


def create_game_schema(
    game_layout: list[str],
    is_random: bool = False,
    is_official: bool = False,
    nyt_game_id: str = None
) -> Dict[str, Any]:
    """
    Create a standardized schema for a game for DB operations.
    """
    # Validation: If is_official, then there should be a game ID already associated with it.


    timestamp = int(datetime.now(tz=timezone.utc).timestamp())
    game_id = str(uuid.uuid4()) if not is_official else nyt_game_id

    return {
        "gameId": game_id,
        "gameLayout": game_layout,
        "validWords": [],  
        "twoWordSolutions": [],
        "threeWordSolutions": [],
        "createdAt": timestamp,
        "isRandom": is_random,
        "isOfficial": is_official,
        "standardizedHash": "",
        "boardSize": board_size,
        "language": language,
    }