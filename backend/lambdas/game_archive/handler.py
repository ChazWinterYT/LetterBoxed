import json
import re
import boto3
from boto3.dynamodb.conditions import Attr

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("LetterBoxedGames")

def handler(event, context):
    """
    Fetch an archive of official New York Times games based on the gameId.
    Supports optional filtering based on the year via query parameters.
    """
    
    # Parse query parameters for pagination
    query_params = event.get("queryStringParameters", {})
    year_filter = query_params.get("year") if query_params else None

    # Build the filter expression
    filter_expression = Attr("officialGame").eq(True)
    if year_filter:
        filter_expression &= Attr("gameId").begins_with(f"{year_filter}")

    # Scan DB table for official NYT games
    try:
        response = table.scan(FilterExpression=filter_expression)
        nyt_games = [item["gameId"] for item in response.get("Items", [])]

        # Handle pagination
        while "LastEvaluatedKey" in response:
            response = table.scan(
                FilterExpression=filter_expression,
                ExclusiveStartKey=response["LastEvaluatedKey"]
            )
            nyt_games.extend(item["gameId"] for item in response.get("Items", []))
        
        # Return the list of official games
        return {
            "statusCode": 200,
            "body": json.dumps({
                "nytGames": nyt_games,
                "message": "Fetched official NYT games archive successfully."
            })
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({
                "message": "Error fetching NYT games archive",
                "error": str(e)
            })
        }