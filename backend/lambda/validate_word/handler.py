import json

def handler(event, context):
    """
    Check the validity of a word
    """
    word = event.get("word")
    is_valid = True # Placeholder
    return {
        "statusCode": 200,
        "body": json.dumps({
            "word": word,
            "isValid": is_valid
        })
    }