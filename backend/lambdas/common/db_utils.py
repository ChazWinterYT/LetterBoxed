import os
from typing import List, Optional, Dict, Any
import time
import boto3
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key

# Initialize the DynamoDB resource
dynamodb = boto3.resource("dynamodb")


# ====================== Games Table Functions ======================

def add_game_to_db(game_data: Dict[str, Any]) -> bool:
    """
    Adds a game entry to the DynamoDB table.

    Args:
        game_data (dict): A dictionary containing all game details.

    Returns:
        bool: True if operation was successful, False otherwise.
    """
    try:
        table = get_games_table()
        print("Using Games Table:", table.table_name)
        table.put_item(Item=game_data)
        return True
    except ClientError as e:
        print(f"Error adding game to DB: {e}")
        return False


def fetch_game_by_id(game_id: str) -> Optional[Dict[str, Any]]:
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


def fetch_solutions_by_standardized_hash(standardized_hash: str) -> Optional[Dict[str, Any]]:
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
        items: List[Dict[str, Any]] = response.get("Items", [])
        
        # Iterate over items to find the first with both solution fields
        for item in items:
            if "twoWordSolutions" in item and "threeWordSolutions" in item:
                return item
        
        # Return None if no item with both solutions is found
        return None
    
    except ClientError as e:
        print(f"Error fetching solutions by standardized hash: {e}")
        return None


def get_games_table() -> Any:
    """
    Dynamically retrieves the DynamoDB table based on the environment variable.

    Returns:
        boto3.Table: The DynamoDB Table object.
    """
    table_name = os.environ.get("GAMES_TABLE_NAME", "LetterBoxedGames")
    return dynamodb.Table(table_name)


# ====================== Valid Words Table Functions ======================

def add_valid_words_to_db(game_id: str, valid_words: List[str]) -> bool:
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
    

def fetch_valid_words_by_game_id(game_id: str) -> Optional[List[str]]:
    """
    Fetches the valid words entry for a given gameId.

    Args:
        game_id (str): The unique identifier for the game.

    Returns:
        list or None: The list of valid words if found, else None.
    """
    try:
        table = get_valid_words_table()
        print("Using Valid Words Table:", table.table_name)
        response = table.get_item(Key={"gameId": game_id})
        item: Optional[Dict[str, List[str]]] = response.get("Item")
        return item.get("validWords", []) if item else None
    except ClientError as e:
        print(f"Error fetching valid words by gameId: {e}")
        return None
    

def get_valid_words_table() -> Any:
    """
    Dynamically retrieves the DynamoDB valid words table based on the environment variable.

    Returns:
        boto3.Table: The DynamoDB Table object.
    """
    table_name = os.environ.get("VALID_WORDS_TABLE", "LetterBoxedValidWords1")
    return dynamodb.Table(table_name)


# ====================== User Game States Table Functions ======================

def get_user_game_state(session_id: str, game_id: str) -> Optional[Dict[str, Any]]:
    """
    Retrieves or initializes the game state for a user session.
    If the session does not exist, it is created.

    Args:
        session_id (str): The unique session identifier for the user.
        game_id (str): The unique identifier for the game.

    Returns:
        dict: The user's game state.
    """
    try:
        table = get_session_states_table()
        print("Using Session States Table:", table.table_name)
        key = {
            "sessionId": session_id,
            "gameId": game_id
        }
        response = table.get_item(Key=key)
        user_game_data: Dict[str, Any] = response.get("Item")

        if user_game_data is None:
            # Initialize the game state for a new session
            return {
                "sessionId": session_id,
                "gameId": game_id,
                "wordsUsed": [],
                "gameCompleted": False,
                "lastUpdated": int(time.time()),
                "TTL": int(time.time()) + 30 * 24 * 60 * 60,  # 30 days from now
            }
        
        return user_game_data
    except ClientError as e:
        print(f"Error fetching game state for session '{session_id}', game '{game_id}': {e}")
        return None


def save_session_state(session_data: Dict[str, Any]) -> bool:
    """
    Saves the user's game state to the DynamoDB session states table.

    Args:
        session_data (dict): The user's game state data.

    Returns:
        bool: True if operation was successful, False otherwise.
    """
    try:
        table = get_session_states_table()
        print("Using Session States Table:", table.table_name)
        table.put_item(Item=session_data)
        return True
    except ClientError as e:
        print(f"Error saving session state: {e}")
        return False
    

def get_session_states_table() -> Any:
    """
    Dynamically retrieves the DynamoDB session states table based on the environment variable.

    Returns:
        boto3.Table: The DynamoDB Table object.
    """
    table_name = os.environ.get("SESSION_STATES_TABLE", "LetterBoxedSessionStates")
    return dynamodb.Table(table_name)


# ====================== Random Game Table Functions ======================

def add_game_id_to_random_games_db(game_id: str) -> int:
    """
    Insert the game ID and atomic number into the Random Games table.

    Args:
        game_id (str): The unique game ID.
        atomic_number (int): The atomic number assigned to this game.
    
    Returns:
        int: The atomic number assigned to this game.
    """
    atomic_number = increment_random_game_count()
    table = get_random_games_table()
    table.put_item(Item={
        "atomicNumber": atomic_number,
        "gameId": game_id
    })
    return atomic_number


def get_random_games_table() -> Any:
    """
    Dynamically retrieves the DynamoDB Random Games table based on the environment variable.

    Returns:
        boto3.Table: The DynamoDB Table object.
    """
    table_name = os.environ.get("RANDOM_GAMES_TABLE", "LetterBoxedRandomGames")
    return dynamodb.Table(table_name)

# ====================== Metadata Table Functions ======================

def fetch_random_game_count() -> int:
    """
    Fetch the current random game count from the metadata table.

    Returns:
        int: The current count of random games.
    """
    table = get_metadata_table()
    response = table.get_item(Key={"metadataType": "randomGameCount"})
    return response.get("Item", {}).get("value", 0) if response else 0


def increment_random_game_count() -> int:
    """
    Increment the random game count in the metadata table and return the new count.

    Returns:
        int: The new count of random games.
    """
    table = get_metadata_table()
    response = table.update_item(
        Key={"metadataType": "randomGameCount"},
        UpdateExpression="SET #val = if_not_exists(#val, :start) + :inc",
        ExpressionAttributeNames={"#val": "value"},
        ExpressionAttributeValues={":start": 0, ":inc": 1},
        ReturnValues="UPDATED_NEW"
    )
    return int(response["Attributes"]["value"])


def update_metadata(metadata_type: str, new_value: int) -> None:
    """
    Update the metadata table with a new value for the specified metadata type.
    Meant as a generic metadata updater. If the specific metadata is known,
    a different function may be more appropriate (such as increment_random_game_count)

    Args:
        metadata_type (str): The type of metadata to update.
        new_value (int): The new value to set for the metadata.
    """
    table = get_metadata_table()
    table.update_item(
        Key={"metadataType": metadata_type},
        UpdateExpression="SET #val = :newVal",
        ExpressionAttributeNames={"#val": "value"},
        ExpressionAttributeValues={":newVal": new_value}
    )


def get_metadata_table() -> Any:
    """
    Dynamically retrieves the DynamoDB metadata table based on the environment variable.

    Returns:
        boto3.Table: The DynamoDB Table object.
    """
    table_name = os.environ.get("METADATA_TABLE", "LetterBoxedMetadata")
    return dynamodb.Table(table_name)
