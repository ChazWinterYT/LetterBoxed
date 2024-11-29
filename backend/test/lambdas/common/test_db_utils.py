import pytest
from unittest import mock
from unittest.mock import MagicMock, ANY
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError
from lambdas.common import db_utils

# Helper function to create a mock DynamoDB table
def create_mock_table():
    mock_table = MagicMock()
    mock_table.table_name = "MockTable"
    return mock_table

# Fixture to mock DynamoDB resource specifically in the `db_utils` module
@pytest.fixture(autouse=True)
def mock_dynamodb_resource(mocker):
    """Mock DynamoDB resource in the db_utils module."""
    mock_dynamodb = MagicMock()
    mocker.patch("lambdas.common.db_utils.dynamodb", mock_dynamodb)
    return mock_dynamodb

# ====================== Games Table Tests ======================

def test_add_game_to_db_success(mock_dynamodb_resource):
    # Arrange
    mock_table = create_mock_table()
    mock_dynamodb_resource.Table.return_value = mock_table
    game_data = {"gameId": "test-game-id", "gameLayout": ["ABC", "DEF", "GHI", "JKL"]}

    # Act
    result = db_utils.add_game_to_db(game_data)

    # Assert
    assert result is True
    mock_table.put_item.assert_called_once_with(Item=game_data)

def test_add_game_to_db_failure(mock_dynamodb_resource):
    # Arrange
    mock_table = create_mock_table()
    mock_table.put_item.side_effect = ClientError(
        error_response={"Error": {"Code": "500", "Message": "Internal Server Error"}},
        operation_name="PutItem",
    )
    mock_dynamodb_resource.Table.return_value = mock_table
    game_data = {"gameId": "test-game-id", "gameLayout": ["ABC", "DEF", "GHI", "JKL"]}

    # Act
    result = db_utils.add_game_to_db(game_data)

    # Assert
    assert result is False
    mock_table.put_item.assert_called_once_with(Item=game_data)

def test_fetch_game_by_id_success(mock_dynamodb_resource):
    # Arrange
    mock_table = create_mock_table()
    expected_item = {"gameId": "test-game-id", "gameLayout": ["ABC", "DEF", "GHI", "JKL"]}
    mock_table.get_item.return_value = {"Item": expected_item}
    mock_dynamodb_resource.Table.return_value = mock_table

    # Act
    result = db_utils.fetch_game_by_id("test-game-id")

    # Assert
    assert result == expected_item
    mock_table.get_item.assert_called_once_with(Key={"gameId": "test-game-id"})

def test_fetch_game_by_id_not_found(mock_dynamodb_resource):
    # Arrange
    mock_table = create_mock_table()
    mock_table.get_item.return_value = {}
    mock_dynamodb_resource.Table.return_value = mock_table

    # Act
    result = db_utils.fetch_game_by_id("non-existent-id")

    # Assert
    assert result is None
    mock_table.get_item.assert_called_once_with(Key={"gameId": "non-existent-id"})

def test_fetch_game_by_id_error(mock_dynamodb_resource):
    # Arrange
    mock_table = create_mock_table()
    mock_table.get_item.side_effect = ClientError(
        error_response={"Error": {"Code": "500", "Message": "Internal Server Error"}},
        operation_name="GetItem",
    )
    mock_dynamodb_resource.Table.return_value = mock_table

    # Act
    result = db_utils.fetch_game_by_id("test-game-id")

    # Assert
    assert result is None
    mock_table.get_item.assert_called_once_with(Key={"gameId": "test-game-id"})

def test_fetch_solutions_by_standardized_hash_found(mock_dynamodb_resource):
    # Arrange
    mock_table = create_mock_table()
    expected_item = {
        "twoWordSolutions": [["WORD1", "WORD2"]],
        "threeWordSolutions": [["WORD3", "WORD4", "WORD5"]],
    }
    mock_table.query.return_value = {"Items": [expected_item]}
    mock_dynamodb_resource.Table.return_value = mock_table

    # Act
    result = db_utils.fetch_solutions_by_standardized_hash("test-hash")

    # Assert
    assert result == expected_item
    mock_table.query.assert_called_once_with(
        IndexName="StandardizedHashIndex",
        KeyConditionExpression=ANY,
        ProjectionExpression="twoWordSolutions, threeWordSolutions"
    )

def test_fetch_solutions_by_standardized_hash_not_found(mock_dynamodb_resource):
    # Arrange
    mock_table = create_mock_table()
    mock_table.query.return_value = {"Items": []}
    mock_dynamodb_resource.Table.return_value = mock_table

    # Act
    result = db_utils.fetch_solutions_by_standardized_hash("test-hash")

    # Assert
    assert result is None
    mock_table.query.assert_called_once_with(
        IndexName="StandardizedHashIndex",
        KeyConditionExpression=ANY,
        ProjectionExpression="twoWordSolutions, threeWordSolutions"
    )

def test_fetch_solutions_by_standardized_hash_error(mock_dynamodb_resource):
    # Arrange
    mock_table = create_mock_table()
    mock_table.query.side_effect = ClientError(
        error_response={"Error": {"Code": "500", "Message": "Internal Server Error"}},
        operation_name="Query",
    )
    mock_dynamodb_resource.Table.return_value = mock_table

    # Act
    result = db_utils.fetch_solutions_by_standardized_hash("test-hash")

    # Assert
    assert result is None
    mock_table.query.assert_called_once_with(
        IndexName="StandardizedHashIndex",
        KeyConditionExpression=ANY,
        ProjectionExpression="twoWordSolutions, threeWordSolutions"
    )

# ====================== Valid Words Table Tests ======================

def test_add_valid_words_to_db_success(mock_dynamodb_resource):
    # Arrange
    mock_table = create_mock_table()
    mock_dynamodb_resource.Table.return_value = mock_table
    game_id = "test-game-id"
    valid_words = ["WORD1", "WORD2", "WORD3"]
    base_valid_words = ["WORD1", "WORD2", "WORD3"]

    # Act
    result = db_utils.add_valid_words_to_db(game_id, valid_words, base_valid_words)

    # Assert
    assert result is True
    mock_table.put_item.assert_called_once_with(
        Item={
            "gameId": game_id, 
            "validWordCount": len(valid_words),
            "validWords": valid_words, 
            "baseValidWords": base_valid_words
        }
    )

def test_add_valid_words_to_db_failure(mock_dynamodb_resource):
    # Arrange
    mock_table = create_mock_table()
    mock_table.put_item.side_effect = ClientError(
        error_response={"Error": {"Code": "500", "Message": "Internal Server Error"}},
        operation_name="PutItem",
    )
    mock_dynamodb_resource.Table.return_value = mock_table
    game_id = "test-game-id"
    valid_words = ["WORD1", "WORD2", "WORD3"]
    base_valid_words = ["WORD1", "WORD2", "WORD3"]

    # Act
    result = db_utils.add_valid_words_to_db(game_id, valid_words, base_valid_words)

    # Assert
    assert result is False
    mock_table.put_item.assert_called_once_with(
        Item={
            "gameId": game_id, 
            "validWordCount": len(valid_words),
            "validWords": valid_words, 
            "baseValidWords": base_valid_words
        }
    )

def test_fetch_valid_words_by_game_id_success(mock_dynamodb_resource):
    # Arrange
    mock_table = create_mock_table()
    game_id = "test-game-id"
    expected_valid_words = ["WORD1", "WORD2", "WORD3"]
    mock_table.get_item.return_value = {
        "Item": {"gameId": game_id, "validWords": expected_valid_words}
    }
    mock_dynamodb_resource.Table.return_value = mock_table

    # Act
    result = db_utils.fetch_valid_words_by_game_id(game_id)

    # Assert
    assert result == expected_valid_words
    mock_table.get_item.assert_called_once_with(Key={"gameId": game_id})

def test_fetch_valid_words_by_game_id_not_found(mock_dynamodb_resource):
    # Arrange
    mock_table = create_mock_table()
    game_id = "non-existent-id"
    mock_table.get_item.return_value = {}
    mock_dynamodb_resource.Table.return_value = mock_table

    # Act
    result = db_utils.fetch_valid_words_by_game_id(game_id)

    # Assert
    assert result is None
    mock_table.get_item.assert_called_once_with(Key={"gameId": game_id})

def test_fetch_valid_words_by_game_id_error(mock_dynamodb_resource):
    # Arrange
    mock_table = create_mock_table()
    game_id = "test-game-id"
    mock_table.get_item.side_effect = ClientError(
        error_response={"Error": {"Code": "500", "Message": "Internal Server Error"}},
        operation_name="GetItem",
    )
    mock_dynamodb_resource.Table.return_value = mock_table

    # Act
    result = db_utils.fetch_valid_words_by_game_id(game_id)

    # Assert
    assert result is None
    mock_table.get_item.assert_called_once_with(Key={"gameId": game_id})

# ====================== User Game States Table Tests ======================

def test_get_user_game_state_existing_session(mock_dynamodb_resource):
    # Arrange
    mock_table = create_mock_table()
    session_id = "test-session-id"
    game_id = "test-game-id"
    expected_item = {
        "sessionId": session_id,
        "gameId": game_id,
        "wordsUsed": ["WORD1"],
        "originalWordsUsed": ["WORD1"],
        "gameCompleted": False,
        "lastUpdated": 1234567890,
        "TTL": 1234567890 + 30 * 24 * 60 * 60,
    }
    mock_table.get_item.return_value = {"Item": expected_item}
    mock_dynamodb_resource.Table.return_value = mock_table

    # Act
    result = db_utils.get_user_game_state(session_id, game_id)

    # Assert
    assert result == expected_item
    mock_table.get_item.assert_called_once_with(Key={"sessionId": session_id, "gameId": game_id})

def test_get_user_game_state_new_session(mocker, mock_dynamodb_resource):
    # Arrange
    mock_table = create_mock_table()
    session_id = "new-session-id"
    game_id = "test-game-id"
    mock_table.get_item.return_value = {}
    mock_dynamodb_resource.Table.return_value = mock_table

    # Mock time.time() to return a fixed timestamp
    mocker.patch("time.time", return_value=1234567890)

    # Act
    result = db_utils.get_user_game_state(session_id, game_id)

    # Assert
    assert result["sessionId"] == session_id
    assert result["gameId"] == game_id
    assert result["wordsUsed"] == []
    assert result["originalWordsUsed"] == []
    assert result["gameCompleted"] is False
    assert result["lastUpdated"] == 1234567890
    assert result["TTL"] == 1234567890 + 30 * 24 * 60 * 60
    mock_table.get_item.assert_called_once_with(Key={"sessionId": session_id, "gameId": game_id})

def test_get_user_game_state_error(mock_dynamodb_resource):
    # Arrange
    mock_table = create_mock_table()
    session_id = "test-session-id"
    game_id = "test-game-id"
    mock_table.get_item.side_effect = ClientError(
        error_response={"Error": {"Code": "500", "Message": "Internal Server Error"}},
        operation_name="GetItem",
    )
    mock_dynamodb_resource.Table.return_value = mock_table

    # Act
    result = db_utils.get_user_game_state(session_id, game_id)

    # Assert
    assert result is None
    mock_table.get_item.assert_called_once_with(Key={"sessionId": session_id, "gameId": game_id})

def test_save_user_session_state_success(mock_dynamodb_resource):
    # Arrange
    mock_table = create_mock_table()
    session_data = {
        "sessionId": "test-session-id",
        "gameId": "test-game-id",
        "wordsUsed": ["WORD1"],
        "gameCompleted": False,
        "lastUpdated": 1234567890,
        "TTL": 1234567890 + 30 * 24 * 60 * 60,
    }
    mock_dynamodb_resource.Table.return_value = mock_table

    # Act
    result = db_utils.save_user_session_state(session_data)

    # Assert
    assert result is True
    mock_table.put_item.assert_called_once_with(Item=session_data)

def test_save_user_session_state_failure(mock_dynamodb_resource):
    # Arrange
    mock_table = create_mock_table()
    session_data = {
        "sessionId": "test-session-id",
        "gameId": "test-game-id",
        "wordsUsed": ["WORD1"],
        "gameCompleted": False,
        "lastUpdated": 1234567890,
        "TTL": 1234567890 + 30 * 24 * 60 * 60,
    }
    mock_table.put_item.side_effect = ClientError(
        error_response={"Error": {"Code": "500", "Message": "Internal Server Error"}},
        operation_name="PutItem",
    )
    mock_dynamodb_resource.Table.return_value = mock_table

    # Act
    result = db_utils.save_user_session_state(session_data)

    # Assert
    assert result is False
    mock_table.put_item.assert_called_once_with(Item=session_data)

# ====================== Random Game Table Tests ======================

def test_add_game_id_to_random_games_db_success(mocker, mock_dynamodb_resource):
    # Arrange
    mock_random_games_table = create_mock_table()
    mock_metadata_table = create_mock_table()
    # Mock increment_random_game_count to return a fixed value
    mocker.patch("lambdas.common.db_utils.increment_random_game_count", return_value=42)

    # Need to ensure get_random_games_table and get_metadata_table return different tables
    def side_effect(table_name):
        if table_name == "LetterBoxedRandomGames_en":
            return mock_random_games_table
        elif table_name == "LetterBoxedMetadata":
            return mock_metadata_table
        else:
            return create_mock_table()

    mock_dynamodb_resource.Table.side_effect = side_effect

    game_id = "test-game-id"

    # Act
    result = db_utils.add_game_id_to_random_games_db(game_id)

    # Assert
    assert result == 42
    mock_random_games_table.put_item.assert_called_once_with(
        Item={"atomicNumber": 42, "gameId": game_id}
    )

# ====================== Metadata Table Tests ======================

def test_fetch_random_game_count_success(mock_dynamodb_resource):
    # Arrange
    mock_table = create_mock_table()
    mock_table.get_item.return_value = {
        "Item": {"metadataType": "randomGameCount_en", "value": 100}
    }
    mock_dynamodb_resource.Table.return_value = mock_table

    # Act
    result = db_utils.fetch_random_game_count()

    # Assert
    assert result == 100
    mock_table.get_item.assert_called_once_with(Key={"metadataType": "randomGameCount_en"})

def test_fetch_random_game_count_no_item(mock_dynamodb_resource):
    # Arrange
    mock_table = create_mock_table()
    mock_table.get_item.return_value = {}
    mock_dynamodb_resource.Table.return_value = mock_table

    # Act
    result = db_utils.fetch_random_game_count()

    # Assert
    assert result == 0
    mock_table.get_item.assert_called_once_with(Key={"metadataType": "randomGameCount_en"})

def test_increment_random_game_count_success(mock_dynamodb_resource):
    # Arrange
    mock_table = create_mock_table()
    mock_table.update_item.return_value = {
        "Attributes": {"value": 101}
    }
    mock_dynamodb_resource.Table.return_value = mock_table

    # Act
    result = db_utils.increment_random_game_count()

    # Assert
    assert result == 101
    mock_table.update_item.assert_called_once_with(
        Key={"metadataType": "randomGameCount_en"},
        UpdateExpression="SET #val = if_not_exists(#val, :start) + :inc",
        ExpressionAttributeNames={"#val": "value"},
        ExpressionAttributeValues={":start": 0, ":inc": 1},
        ReturnValues="UPDATED_NEW",
    )

def test_increment_random_game_count_failure(mock_dynamodb_resource):
    # Arrange
    mock_table = create_mock_table()
    mock_table.update_item.side_effect = ClientError(
        error_response={"Error": {"Code": "500", "Message": "Internal Server Error"}},
        operation_name="UpdateItem",
    )
    mock_dynamodb_resource.Table.return_value = mock_table

    # Act & Assert
    with pytest.raises(ClientError):
        db_utils.increment_random_game_count()
    mock_table.update_item.assert_called_once_with(
        Key={"metadataType": "randomGameCount_en"},
        UpdateExpression="SET #val = if_not_exists(#val, :start) + :inc",
        ExpressionAttributeNames={"#val": "value"},
        ExpressionAttributeValues={":start": 0, ":inc": 1},
        ReturnValues="UPDATED_NEW",
    )

def test_update_metadata_success(mock_dynamodb_resource):
    # Arrange
    mock_table = create_mock_table()
    mock_dynamodb_resource.Table.return_value = mock_table
    metadata_type = "testMetadata"
    new_value = 123

    # Act
    db_utils.update_metadata(metadata_type, new_value)

    # Assert
    mock_table.update_item.assert_called_once_with(
        Key={"metadataType": metadata_type},
        UpdateExpression="SET #val = :newVal",
        ExpressionAttributeNames={"#val": "value"},
        ExpressionAttributeValues={":newVal": new_value},
    )

def test_update_metadata_failure(mock_dynamodb_resource):
    # Arrange
    mock_table = create_mock_table()
    mock_table.update_item.side_effect = ClientError(
        error_response={"Error": {"Code": "500", "Message": "Internal Server Error"}},
        operation_name="UpdateItem",
    )
    mock_dynamodb_resource.Table.return_value = mock_table
    metadata_type = "testMetadata"
    new_value = 123

    # Act & Assert
    with pytest.raises(ClientError):
        db_utils.update_metadata(metadata_type, new_value)
    mock_table.update_item.assert_called_once_with(
        Key={"metadataType": metadata_type},
        UpdateExpression="SET #val = :newVal",
        ExpressionAttributeNames={"#val": "value"},
        ExpressionAttributeValues={":newVal": new_value},
    )

# ====================== Archive Table Tests ======================

def test_add_game_to_archive_success(mock_dynamodb_resource):
    # Arrange
    mock_table = create_mock_table()
    mock_dynamodb_resource.Table.return_value = mock_table
    game_id = "test-game-id"

    # Act
    result = db_utils.add_game_to_archive(game_id)

    # Assert
    assert result is True
    mock_table.put_item.assert_called_once_with(Item={"gameId": game_id})


def test_add_game_to_archive_failure(mock_dynamodb_resource):
    # Arrange
    mock_table = create_mock_table()
    mock_table.put_item.side_effect = ClientError(
        error_response={"Error": {"Code": "500", "Message": "Internal Server Error"}},
        operation_name="PutItem",
    )
    mock_dynamodb_resource.Table.return_value = mock_table
    game_id = "test-game-id"

    # Act
    result = db_utils.add_game_to_archive(game_id)

    # Assert
    assert result is False
    mock_table.put_item.assert_called_once_with(Item={"gameId": game_id})


def test_fetch_archived_games_success(mock_dynamodb_resource):
    # Arrange
    mock_table = create_mock_table()
    mock_dynamodb_resource.Table.return_value = mock_table

    # Mock the scan method
    mock_table.scan.return_value = {
        "Items": [
            {"gameId": "2024-11-22", "officialGame": True},
            {"gameId": "2024-11-21", "officialGame": True},
        ],
        "LastEvaluatedKey": None,
    }

    # Act
    result = db_utils.fetch_archived_games(limit=10)

    # Assert
    assert result["items"] == [
        {"gameId": "2024-11-22", "officialGame": True},
        {"gameId": "2024-11-21", "officialGame": True},
    ]
    assert result["lastKey"] is None
    mock_table.scan.assert_called_once_with(Limit=10)


def test_fetch_archived_games_with_pagination(mock_dynamodb_resource):
    # Arrange
    mock_table = create_mock_table()
    mock_dynamodb_resource.Table.return_value = mock_table

    # Properly mock the scan or query response
    mock_table.scan.return_value = {
        "Items": [
            {"gameId": "2024-11-20", "officialGame": True},
            {"gameId": "2024-11-19", "officialGame": True},
        ],
        "LastEvaluatedKey": {"gameId": "2024-11-19"},
    }

    # Act
    result = db_utils.fetch_archived_games(limit=10, last_key={"gameId": "2024-11-21"})

    # Assert
    assert result["items"] == [
        {"gameId": "2024-11-20", "officialGame": True},
        {"gameId": "2024-11-19", "officialGame": True},
    ]
    assert result["lastKey"] == {"gameId": "2024-11-19"}

    # Verify the scan call was made with the correct parameters
    mock_table.scan.assert_called_once_with(
        Limit=10,
        ExclusiveStartKey={"gameId": "2024-11-21"},
    )


def test_fetch_archived_games_failure(mock_dynamodb_resource):
    # Arrange
    mock_table = create_mock_table()
    # Mock scan to raise a ClientError
    mock_table.scan.side_effect = ClientError(
        error_response={"Error": {"Code": "500", "Message": "Internal Server Error"}},
        operation_name="Scan",
    )
    mock_dynamodb_resource.Table.return_value = mock_table

    # Act
    result = db_utils.fetch_archived_games(limit=10)

    # Assert
    assert result["items"] == []  # Should return an empty list on failure
    assert result["lastKey"] is None  # Should return None for lastKey

    # Verify that scan was attempted
    mock_table.scan.assert_called_once_with(Limit=10)
    