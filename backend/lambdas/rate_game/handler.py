from typing import Dict, Any
from lambdas.common.db_utils import fetch_game_by_id


def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Lambda handler for saving user session state.
    
    Args:
        event (dict): The API Gateway event object.
        context: The Lambda context object.
    
    Returns:
        dict: The HTTP response object.
    """