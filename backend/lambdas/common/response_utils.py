import json
from typing import Dict, Any


HEADERS = {
    "Access-Control-Allow-Origin": "*",  # Allow all origins
    "Access-Control-Allow-Methods": "OPTIONS,GET,POST",  # Allowed methods
    "Access-Control-Allow-Headers": "Content-Type,Authorization",  # Allowed headers
}


def error_response(message: str, status_code: int) -> Dict[str, Any]:
    """
    Helper function to generate an error response.

    Args:
        message (str): The error message.
        status_code (int): The HTTP status code.

    Returns:
        dict: The error response.
    """
    return {
        "statusCode": status_code,
        "headers": HEADERS,
        "body": json.dumps({"message": message}),
    }