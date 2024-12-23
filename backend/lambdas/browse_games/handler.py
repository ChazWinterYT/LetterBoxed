import json
from typing import Dict, Any
from lambdas.common.response_utils import error_response, HEADERS
from lambdas.browse_games.browse_games_service import query_games_by_language

def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Lambda handler for browsing games by various properties.

    Args:
        event (Dict[str, Any]): The event object containing query parameters.
        context (Any): The context object provided by AWS Lambda.

    Returns:
        Dict[str, Any]: HTTP response with status code, headers, and body.
    """
    try: 
        # Extract query parameters
        query_params = event.get("queryStringParameters", {}) or {}
        language = query_params.get("language", "en")
        last_key = query_params.get("lastEvaluatedKey")
        limit = int(query_params.get("limit", 10)) # Default to 10
        if limit <= 0:
            return error_response("Limit must be a positive integer.", 400)
        
        # Call service function
        response = query_games_by_language(language, last_key, limit)
        
        return {
            "statusCode": 200,
            "headers": HEADERS,
            "body": json.dumps(response)
        }
    
    except ValueError as e:
        print(f"Validation error when browsing games: {str(e)}")
        return error_response(f"Validation error: {str(e)}", 400)    
    except Exception as e:
        print(f"Error when browsing games: {str(e)}")
        return error_response("Internal Server Error", 500)
    