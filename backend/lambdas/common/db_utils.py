import os
from typing import List, Optional, Dict, Any
import time
import boto3
import decimal
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key
from lambdas.common.validation_utils import convert_decimal, validate_game_schema

# Initialize the DynamoDB resource
dynamodb = boto3.resource("dynamodb")


# ====================== Games Table Functions ======================

def add_game_to_db(game_data: Dict[str, Any]) -> bool:
    """
    Adds a game entry to the DynamoDB table.
    Also adds the valid words for that game into the Valid Words table, so
    it doesn't need to be done manually in the handler.

    Args:
        game_data (dict): A dictionary containing all game details.

    Returns:
        bool: True if operation was successful, False otherwise.
    """
    try:
        # First add the valid words to the ValidWords Table
        game_id = game_data["gameId"]
        valid_words = game_data.pop("validWords")  # Remove from main game data to save space
        base_valid_words = game_data.pop("baseValidWords")
        if not add_valid_words_to_db(game_id, valid_words, base_valid_words):
            return False
        
        # Then add the rest of the data to the Games DB
        table = get_games_table()
        table.put_item(Item=game_data)
        return True
    except ClientError as e:
        print(f"Error adding game to DB: {e}")
        return False


def update_game_in_db(game_data: Dict[str, Any]) -> bool:
    """
    Updates a game entry in the DynamoDB table.

    Args:
        game_data (dict): A dictionary containing all game details to update.
                          Must include the gameId as the primary key.

    Returns:
        bool: True if operation was successful, False otherwise.
    """
    try:
        # Extract the gameId, which is the primary key
        game_id = game_data.get("gameId")
        if not game_id:
            raise ValueError("gameId is required for updating a game in the DB.")
        
        # Build the update expression and attribute values
        update_expression = []
        expression_attribute_values = {}
        for key, value in game_data.items():
            if key != "gameId":  # Skip primary key
                update_expression.append(f"{key} = :{key}")
                expression_attribute_values[f":{key}"] = value
        
        if not update_expression:
            raise ValueError("No fields provided to update.")
        
        # Combine update expression into a single string
        update_expression_str = "SET " + ", ".join(update_expression)
        
        # Update the item in the table
        table = get_games_table()
        table.update_item(
            Key={"gameId": game_id},
            UpdateExpression=update_expression_str,
            ExpressionAttributeValues=expression_attribute_values,
        )
        return True
    except ClientError as e:
        print(f"Error updating game in DB: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
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
        response = table.get_item(Key={"gameId": game_id})
        item = response.get("Item")
        
        validated_item = validate_game_schema(item)
        return validated_item
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
    table_name = os.environ.get("GAMES_TABLE", "LetterBoxedGames")
    return dynamodb.Table(table_name)


# ====================== Valid Words Table Functions ======================

def add_valid_words_to_db(game_id: str, valid_words: List[str], base_valid_words: List[str]) -> bool:
    """
    Stores all valid words for a game in a single item in the valid words table.

    Args:
        game_id (str): The unique identifier for the game.
        valid_words (list): List of valid words for the game.
        base_valid_words: List of valid words, with accents removed.

    Returns:
        bool: True if operation was successful, False otherwise.
    """
    try:
        table = get_valid_words_table()
        valid_words_entry = {
            "gameId": game_id,
            "validWordCount": len(valid_words),
            "validWords": valid_words,
            "baseValidWords": base_valid_words
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
        Optional[dict]: The user's game state, or None if an error occurred.
    """
    try:
        table = get_session_states_table()
        
        # Composite key for querying the table
        key = {
            "sessionId": session_id,
            "gameId": game_id
        }

        # Retrieve the game state from the database
        response = table.get_item(Key=key)
        user_game_data: Optional[Dict[str, Any]] = response.get("Item")

        # If no game state exists, initialize it
        if user_game_data is None:
            print(f"No existing game state for session '{session_id}' and game '{game_id}'. Initializing...")
            user_game_data = {
                "sessionId": session_id,
                "gameId": game_id,
                "wordsUsed": [],
                "originalWordsUsed": [],
                "gameCompleted": False,
                "lastUpdated": int(time.time()),
                "TTL": int(time.time()) + 30 * 24 * 60 * 60,  # 30 days from now
            }

            # Save the initialized state
            if not save_user_session_state(user_game_data):
                print(f"Failed to save initialized game state for session '{session_id}', game '{game_id}'.")
                return None
            print(f"Initialized and saved new game state: {user_game_data}")

        # Convert any Decimal values to JSON-compatible types
        user_game_data = convert_decimal(user_game_data)
        return user_game_data

    except ClientError as e:
        print(f"Error fetching game state for session '{session_id}', game '{game_id}': {e}")
        return None


def save_user_session_state(session_data: Dict[str, Any]) -> bool:
    """
    Saves the user's game state to the DynamoDB session states table.

    Args:
        session_data (dict): The user's game state data.

    Returns:
        bool: True if operation was successful, False otherwise.
    """
    try:
        table = get_session_states_table()
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

def add_game_id_to_random_games_db(game_id: str, language: str = "en") -> int:
    """
    Insert the game ID and atomic number into the language-specific Random Games table.

    Args:
        game_id (str): The unique game ID.
        language (str): The language code for the table (e.g., 'en', 'es').

    Returns:
        int: The atomic number assigned to this game.
    """
    atomic_number = increment_random_game_count(language)
    table = get_random_games_table(language)
    table.put_item(Item={
        "atomicNumber": atomic_number,
        "gameId": game_id
    })
    return atomic_number


def fetch_game_id_from_random_games_db(atomic_number: int, language: str) -> str:
    """
    Fetch the game ID for the given atomic number from the Random Games table.

    Args:
        atomic_number (int): Atomic number to fetch.
        language (str): Language code.

    Returns:
        str: Game ID.
    """
    random_games_table = get_random_games_table(language)
    response = random_games_table.get_item(Key={"atomicNumber": atomic_number})
    game_id: str = response.get("Item", {}).get("gameId", "")
    if not game_id:
        raise ValueError("Atomic number not associated with Game ID.")
    return game_id
    

def get_random_games_table(language: str = "en") -> Any:
    """
    Dynamically retrieves the DynamoDB Random Games table for the specified language.

    Args:
        language (str): The language code for the table (e.g., 'en', 'es').

    Returns:
        boto3.Table: The DynamoDB Table object.
    """

    table_name = os.environ.get(f"RANDOM_GAMES_TABLE_{language.upper()}", f"LetterBoxedRandomGames_{language}")
    return dynamodb.Table(table_name)


# ====================== Metadata Table Functions ======================

def fetch_random_game_count(language: str = "en") -> int:
    """
    Fetch the current random game count for the specified language from the metadata table.

    Args:
        language (str): The language code for the count (e.g., 'en', 'es').

    Returns:
        int: The current count of random games for the language.
    """
    table = get_metadata_table()
    metadata_key = f"randomGameCount_{language}"
    response = table.get_item(Key={"metadataType": metadata_key})
    game_count = response.get("Item", {}).get("value", 0) if response else 0
    return int(game_count)


def increment_random_game_count(language: str = "en") -> int:
    """
    Increment the random game count for the specified language in the metadata table.

    Args:
        language (str): The language code for the count (e.g., 'en', 'es').

    Returns:
        int: The new count of random games for the language.
    """
    table = get_metadata_table()
    metadata_key = f"randomGameCount_{language}"
    response = table.update_item(
        Key={"metadataType": metadata_key},
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


# ====================== Archive Table Functions ======================

def add_game_to_archive(game_id: str) -> bool:
    """
    Adds a game to the archive DB.
    
    Args:
        game_id (str): The ID of the game to add.
        game_date (str): The date of the game in ISO 8601 format.

    Returns:
        bool: True if the operation was successful, False otherwise.
    """
    try:
        table = get_archive_table()
        table.put_item(Item={
            "NYTGame": "NYTGame", # Hard coded primary key
            "gameId": game_id
        })
        return True
    except ClientError as e:
        print(f"Error adding game to archive: {e}")
        return False
    

def fetch_archived_games(limit: int, last_key: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Fetches a paginated list of archived games from the archive DB.

    Args:
        limit (int): The maximum number of items to fetch.
        last_key (Optional[Dict[str, Any]]): The key to start fetching from (for pagination).

    Returns:
        Dict[str, Any]: A dictionary containing the items and the LastEvaluatedKey for pagination.
    """
    try:
        table = get_archive_table()

        # Query the DB table
        query_params = {
            "KeyConditionExpression": Key("NYTGame").eq("NYTGame"),
            "Limit": limit,
            "ScanIndexForward": False, # Descending order
        }
        
        if last_key:
            query_params["ExclusiveStartKey"] = last_key

        print(f"Querying Game Archive table with params: {query_params}")
        response = table.query(**query_params)
        print(f"DynamoDB Response:", response)
        
        # Extract items and get pagination key
        items= response.get("Items", [])
        last_evaluated_key = response.get("LastEvaluatedKey")
        
        return {
            "items": items,
            "lastKey": last_evaluated_key,
        }
    except Exception as e:
        print(f"Error fetching archived games: {e}")
        return {"items": [], "lastKey": None}


def get_archive_table() -> Any:
    """
    Dynamically retrieves the DynamoDB archive table based on the environment variable.

    Returns:
        boto3.Table: The DynamoDB Table object.
    """
    table_name = os.environ.get("ARCHIVE_TABLE", "LetterBoxedNYTArchives")
    return dynamodb.Table(table_name)
