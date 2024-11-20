import os
import json
from typing import Any, Dict
import boto3
from boto3.dynamodb.conditions import Attr


# Dynamically retrieve the table name from environment variables
def get_table() -> Any:
    dynamodb = boto3.resource("dynamodb")
    table_name = os.environ.get("GAMES_TABLE_NAME", "LetterBoxedGames") 
    return dynamodb.Table(table_name)


def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
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

    try:
        # Initialize variables for pagination
        nyt_games: list[str] = []
        last_evaluated_key = None
        table = get_table()

        while True:
            # Scan DB table for official NYT games with pagination
            scan_kwargs = {"FilterExpression": filter_expression}
            if last_evaluated_key:
                scan_kwargs["ExclusiveStartKey"] = last_evaluated_key

            response = table.scan(**scan_kwargs)
            nyt_games.extend(item["gameId"] for item in response.get("Items", []) if item.get("officialGame"))

            # Break the loop if there are no more pages
            last_evaluated_key = response.get("LastEvaluatedKey")
            if not last_evaluated_key:
                break

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
