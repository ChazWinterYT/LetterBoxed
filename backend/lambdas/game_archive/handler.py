import os
import json
from typing import Any, Dict
import boto3
from lambdas.common.db_utils import fetch_archived_games
from lambdas.common.response_utils import error_response, HEADERS


def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Lambda handler for retrieving the game archive with pagination.

    Args:
        event (Dict[str, Any]): The event triggering the Lambda function.
        context (Any): The Lambda context object.

    Returns:
        Dict[str, Any]: API Gateway response containing the archive data or an error message.
    """
    try:
        # Parse query parameters
        query_params = event.get("queryStringParameters", {}) or {}
        limit = int(query_params.get("limit", 12))  # Default to 12 items
        last_key = query_params.get("lastKey")  # Last key for pagination
        
        # Decode lastKey if provided
        if last_key:
            last_key = json.loads(last_key)
        
        # Fetch paginated archived games
        result = fetch_archived_games(limit=limit, last_key=last_key)
        items = result["items"]
        last_evaluated_key = result["lastKey"]
        
        # Build the response
        response_body = {
            "nytGames": items,
            "lastKey": json.dumps(last_evaluated_key) if last_evaluated_key else None,
            "message": "Fetched official NYT games archive successfully.",
        }

        return {
            "statusCode": 200,
            "headers": HEADERS,
            "body": json.dumps(response_body),
        }

    except Exception as e:
        print(f"Error in handler: {e}")
        return error_response("Error fetching New York Times Archive", 500)
