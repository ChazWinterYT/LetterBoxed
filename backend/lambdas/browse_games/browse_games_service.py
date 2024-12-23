from typing import Optional, Dict, Any, List
from lambdas.common.db_utils import fetch_games_by_language


def query_games_by_language(
    language: str,
    last_key: Optional[Dict[str, Any]] = None,
    limit: int = 10
) -> Dict[str, Any]:
    """
    Service layer function to query games by language, handling validation and errors.

    Args:
        language (str): The language to filter games by.
        last_key (Optional[dict]): Pagination key for DynamoDB query (optional).
        limit (int): Number of results to return (default 10).

    Returns:
        dict: A dictionary containing the list of games and pagination metadata.
    """
    # Input validation
    if limit <= 0:
        raise ValueError("Limit must be a positive integer.")
    
    try:
        # Call the DB Utility function to fetch games
        result = fetch_games_by_language(
            language=language,
            last_key=last_key,
            limit=limit
        )
        return result
    except Exception as e:
        print(f"Error querying games: {str(e)}")
        raise
    