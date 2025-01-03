from datetime import datetime
from typing import Optional, Dict, Any, List
from lambdas.common.db_utils import fetch_games_by_language


def query_games_by_language(
    language: str,
    last_key: Optional[Dict[str, str]] = None,
    limit: int = 10
) -> Dict[str, Any]:
    """
    Service layer function to query games by language, handling validation and errors.

    Args:
        language (str): The language to filter games by.
        last_key (Optional[Dict[str, str]]): Pagination key for DynamoDB query (optional).
        limit (int): Number of results to return (default 10).

    Returns:
        dict: A dictionary containing the list of games and pagination metadata.
    """
    # Input validation
    if not isinstance(language, str) or not language:
        raise ValueError("Language must be a non-empty string.")
    if not isinstance(limit, int) or limit <= 0:
        raise ValueError("Limit must be a positive integer.")
    if last_key:
        required_keys = ["language", "createdAt", "gameId"]
        if not all(key in last_key for key in required_keys):
            raise ValueError(
                f"last_key must include the following keys: {', '.join(required_keys)}"
            )
        try:
            # Validate ISO 8601 timestamp in createdAt
            datetime.fromisoformat(last_key["createdAt"])
        except ValueError:
            raise ValueError("Invalid createdAt in last_key. Must be an ISO 8601 timestamp.")
    
    try:
        # Call the DB Utility function to fetch games
        print(f"Querying games with language={language}, last_key={last_key}, limit={limit}")
        result = fetch_games_by_language(
            language=language,
            last_key=last_key,
            limit=limit
        )
        print(f"Query successful. Fetched {len(result['games'])} games.")
        return result
    except ValueError as ve:
        print(f"Validation error while querying games: {str(ve)}")
        raise
    except Exception as e:
        print(f"Unexpected error while querying games: {str(e)}")
        raise
    