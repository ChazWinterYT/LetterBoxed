import os
import boto3
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key

# Initialize the DynamoDB resource
dynamodb = boto3.resource("dynamodb")


# ====================== Games Table Functions ======================

def add_game_to_db(game_data):
    """
    Adds a game entry to the DynamoDB table.

    Args:
        game_data (dict): A dictionary containing all game details.
    """
    try:
        table = get_games_table()
        print("Using Games Table:", table.table_name)
        table.put_item(Item=game_data)
        return True
    except ClientError as e:
        print(f"Error adding game to DB: {e}")
        return False


def fetch_game_by_id(game_id):
    """
    Fetches a game entry by its gameId.

    Args:
        game_id (str): The unique identifier for the game.

    Returns:
        dict or None: The game item if found, else None.
    """
    try:
        table = get_games_table()
        print("Using Games Table:", table.table_name)
        response = table.get_item(Key={"gameId": game_id})
        item = response.get("Item")
        return item if item else None
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
        table = get_games_table()
        response = table.query(
            IndexName="StandardizedHashIndex",
            KeyConditionExpression=Key("standardizedHash").eq(standardized_hash),
            ProjectionExpression="twoWordSolutions, threeWordSolutions"
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


def get_games_table():
    """
    Dynamically retrieves the DynamoDB table based on the environment variable.

    Returns:
        boto3.Table: The DynamoDB Table object.
    """
    table_name = os.environ.get("GAMES_TABLE_NAME", "LetterBoxedGames")
    return dynamodb.Table(table_name)


# ====================== Valid Words Table Functions ======================

def add_valid_words_to_db(game_id, valid_words) -> bool:
    """
    Stores all valid words for a game in a single item in the valid words table.

    Args:
        game_id (str): The unique identifier for the game.
        valid_words (list): List of valid words for the game.

    Returns:
        bool: True if operation was successful, False otherwise.
    """
    try:
        table = get_valid_words_table()
        print("Using Valid Words Table:", table.table_name)
        valid_words_entry = {
            "gameId": game_id,
            "validWords": valid_words
        }
        table.put_item(Item=valid_words_entry)
        return True
    except ClientError as e:
        print(f"Error adding valid words to DB: {e}")
        return False
    

def fetch_valid_words_by_game_id(game_id):
    """
    Fetches the valid words entry for a given gameId.

    Args:
        game_id (str): The unique identifier for the game.

    Returns:
        dict or None: The valid words entry if found, else None.
    """
    try:
        table = get_valid_words_table()
        print("Using Valid Words Table:", table.table_name)
        response = table.get_item(Key={"gameId": game_id})
        item = response.get("Item")
        return item if item else None
    except ClientError as e:
        print(f"Error fetching valid words by gameId: {e}")
        return None
    

def get_valid_words_table():
    """
    Dynamically retrieves the DynamoDB valid words table based on the environment variable.

    Returns:
        boto3.Table: The DynamoDB Table object.
    """
    table_name = os.environ.get("VALID_WORDS_TABLE", "LetterBoxedValidWords")
    return dynamodb.Table(table_name)
