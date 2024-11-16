import boto3
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key

# Initialize the DynamoDB resource
dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("LetterBoxedGames")  


def add_game_to_db(
        game_id, 
        game_layout, 
        standardized_hash, 
        two_word_solutions, 
        three_word_solutions,
        board_size="3x3",
        language="English"
    ):
    """
    Adds a game entry to the DynamoDB table.

    Args:
        game_id (str): Unique ID for the game.
        game_layout (List[str]): The specific board layout.
        standardized_hash (str): Hash for detecting equivalent games.
        two_word_solutions (List[str]): List of two-word solutions.
        three_word_solutions (List[str]): List of three-word solutions.
        board_size (str): The size of the game board (default is 3x3).
        language (str): The language for the game (default is English).
    """
    item = {
        "gameId": game_id,
        "gameLayout": game_layout,
        "standardizedHash": standardized_hash,
        "twoWordSolutions": two_word_solutions,
        "threeWordSolutions": three_word_solutions,
        "boardSize": board_size,
        "language": language,
    }
    try:
        table.put_item(Item=item)
    except ClientError as e:
        print(f"Error adding game to DB: {e}")


def fetch_game_by_id(game_id):
    """
    Fetches a game entry by its gameId.
    """
    try:
        response = table.get_item(Key={"gameId": game_id})
        return response.get("Item")
    except ClientError as e:
        print(f"Error fetching game by gameId: {e}")
        return None


def fetch_solutions_by_standardized_hash(standardized_hash):
    """
    Fetches the first item with both `twoWordSolutions` and `threeWordSolutions`
    based on the standardized hash.

    Args:
        standardized_hash (str): The standardized hash to query.

    Returns:
        dict: The first item containing both solution fields, or None if not found.
    """
    try:
        response = table.query(
            IndexName="StandardizedHashIndex",
            KeyConditionExpression=Key("standardizedHash").eq(standardized_hash)
        )
        items = response.get("Items", [])
        
        # Iterate over items to find the first with both solution fields
        for item in items:
            if "twoWordSolutions" in item and "threeWordSolutions" in item:
                return item
        
        # Return None if no item with both solutions is found
        return None
    
    except ClientError as e:
        print(f"Error fetching solutions by standardized hash: {e}")
        return None
