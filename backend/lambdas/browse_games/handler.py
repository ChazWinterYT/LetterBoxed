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

        # Validate language
        language = query_params.get("language")
        if not language:
            return error_response("Language is required for browsing games.", 400)
        if not validate_language(language):
            return error_response("Specified language is not supported.", 400)

        # Parse and validate lastEvaluatedKey
        last_key = query_params.get("lastEvaluatedKey")
        if last_key:
            try:
                last_key = json.loads(last_key)  # Parse as JSON object
                if not isinstance(last_key, dict):
                    raise ValueError("lastEvaluatedKey must be a JSON object.")
                if not all(key in last_key for key in ["language", "createdAt", "gameId"]):
                    raise ValueError(
                        "lastEvaluatedKey must include 'language', 'createdAt', and 'gameId'."
                    )
            except (json.JSONDecodeError, ValueError) as e:
                print(f"Invalid lastEvaluatedKey format: {last_key}")
                return error_response(
                    "Invalid lastEvaluatedKey format. Must be a JSON object with 'language', 'createdAt', and 'gameId'.",
                    400,
                )
        else:
            last_key = None

        # Parse and validate limit
        limit = query_params.get("limit", "10")
        try:
            limit = int(limit)
            if limit <= 0:
                raise ValueError("Limit must be a positive integer.")
        except ValueError:
            return error_response("Limit must be a positive integer.", 400)

        # Call the service layer
        response = query_games_by_language(language, last_key, limit)

        return {
            "statusCode": 200,
            "headers": HEADERS,
            "body": json.dumps(response),
        }

    except ValueError as ve:
        print(f"Validation error when browsing games: {str(ve)}")
        return error_response(f"Validation error: {str(ve)}", 400)
    except Exception as e:
        print(f"Error when browsing games: {str(e)}")
        return error_response("Internal Server Error", 500)
    