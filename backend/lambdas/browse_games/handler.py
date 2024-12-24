import json
from typing import Dict, Any
from lambdas.common.response_utils import error_response, HEADERS
from lambdas.browse_games.browse_games_service import query_games_by_language
from lambdas.common.validation_utils import validate_language

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
        print(f"Received query parameters: {query_params}")
        
        language = query_params.get("language")
        if not language:
            return error_response("Language is required for browsing games.", 400)
        
        if not validate_language(language):
            return error_response("Specified langauge is not supported.", 400)        
        
        last_key = query_params.get("lastEvaluatedKey")
        if last_key:
            try:
                # Ensure last_key is a valid ISO 8601 timestamp
                from datetime import datetime
                datetime.fromisoformat(last_key)
            except ValueError:
                print(f"Invalid lastEvaluatedKey format: {last_key}")
                return error_response("Invalid lastEvaluatedKey format. Must be an ISO 8601 timestamp.", 400)
        
        limit = int(query_params.get("limit", 10)) # Default to 10
        try:
            limit = int(limit)
            if limit <= 0:
                return error_response("Limit must be a positive integer.", 400)
        except ValueError:
            return error_response("Limit must be an integer.", 400)
        
        # Call service function
        response = query_games_by_language(language, last_key, limit)
        
        return {
            "statusCode": 200,
            "headers": HEADERS,
            "body": json.dumps(response)
        }
    
    except ValueError as ve:
        print(f"Validation error when browsing games: {str(ve)}")
        return error_response(f"Validation error: {str(ve)}", 400)    
    except Exception as e:
        print(f"Error when browsing games: {str(e)}")
        return error_response("Internal Server Error", 500)
    