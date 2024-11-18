import json
import os
import boto3

from lambdas.validate_word.validate_service import validate_submitted_word


def handler(event, context):
    """
    AWS Lambda handler for validating submitted words in the LetterBoxed game.

    Parameters:
    - event: The event data from API Gateway.
    - context: The runtime information of the Lambda function.

    Returns:
    - dict: The response object with statusCode and body.
    """
    try:
        # Extract parameters from the event
        body = json.loads(event.get('body'))
        game_id = body.get('gameId')
        submitted_word = body.get('word')
        session_id = body.get('sessionId')

        # Validate required parameters
        if not game_id or not submitted_word or not session_id:
            return {
                "statusCode": 400,
                "body": json.dumps({
                    "message": "Missing required parameters: gameId, word, or sessionId."
                })
            }
        
        result = validate_submitted_word(game_id, submitted_word, session_id)
        status_code = 200 if result.get("valid") else 400

        return {
            "statusCode": status_code,
            "body": json.dumps(result)
        }
    except Exception as e:
        print(f"Error during validation: {e}")

        return {
            "statusCode": 500,
            "body": json.dumps({
                "message": "An error occurred."
            })
        }