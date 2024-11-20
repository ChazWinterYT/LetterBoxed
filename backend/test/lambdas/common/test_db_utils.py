import pytest
from unittest.mock import MagicMock
from botocore.exceptions import ClientError
from lambdas.common.db_utils import (
    add_game_to_db,
    fetch_game_by_id,
    fetch_solutions_by_standardized_hash,
    add_valid_words_to_db,
    fetch_valid_words_by_game_id,
    get_user_game_state,
    save_session_state,
)


sample_game = {
    "gameId": "test-game-id",
    "gameLayout": ["ABC", "DEF", "GHI", "XYZ"],
    "standardizedHash": "sample-hash",
    "twoWordSolutions": ["WORD1", "WORD2"],
    "threeWordSolutions": ["WORD3", "WORD4", "WORD5"],
    "boardSize": "3x3",
    "language": "en",
}

bad_sample_game_no_board_size = {
    "gameId": "test-game-id",
    "gameLayout": ["ABC", "DEF", "GHI", "XYZ"],
    "standardizedHash": "sample-hash",
    "twoWordSolutions": ["WORD1", "WORD2"],
    "threeWordSolutions": ["WORD3", "WORD4", "WORD5"],
    "boardSize": "",
    "language": "en",
}


@pytest.fixture
def mock_games_table(mocker):
    mock_table = MagicMock()
    mocker.patch("lambdas.common.db_utils.get_games_table", return_value=mock_table)  
    return mock_table


@pytest.fixture
def mock_valid_words_table(mocker):
    mock_table = MagicMock()
    mocker.patch("lambdas.common.db_utils.get_valid_words_table", return_value=mock_table)
    return mock_table


@pytest.fixture
def mock_session_states_table(mocker):
    mock_table = MagicMock()
    mocker.patch("lambdas.common.db_utils.get_session_states_table", return_value=mock_table)
    return mock_table


@pytest.fixture
def mock_solution_calculations(mocker):
    mocker.patch("lambdas.common.game_utils.calculate_two_word_solutions", return_value=["WORD1", "WORD2"])
    mocker.patch("lambdas.common.game_utils.calculate_three_word_solutions", return_value=["WORD3", "WORD4"])

# ========================= Games DB tests =========================

def test_add_game_to_db(mock_games_table):
    # Act
    add_game_to_db(sample_game)

    # Assert
    mock_games_table.put_item.assert_called_once_with(Item=sample_game)


def test_add_game_to_db_client_error(mock_games_table):
    mock_games_table.put_item.side_effect = ClientError(
        error_response={"Error": {"Code": "MockError", "Message": "Mocked error"}},
        operation_name="PutItem",
    )
    sample_game = {...}  # Your game data
    add_game_to_db(sample_game)  # Expect no exception, just print error
    mock_games_table.put_item.assert_called_once()


def test_fetch_game_by_id(mock_games_table):
    # Arrange
    game_id = "test-game-id"
    mock_games_table.get_item.return_value = {"Item": sample_game}

    # Act
    result = fetch_game_by_id(game_id)

    # Assert
    assert result == sample_game
    mock_games_table.get_item.assert_called_once_with(Key={"gameId": game_id})


def test_fetch_game_by_id_client_error(mock_games_table):
    # Arrange
    game_id = "test-game-id"
    mock_games_table.get_item.side_effect = ClientError(
        error_response={"Error": {"Code": "MockError", "Message": "Mocked error"}},
        operation_name="GetItem"
    )

    # Act
    result = fetch_game_by_id(game_id)

    # Assert
    assert result is None
    mock_games_table.get_item.assert_called_once_with(Key={"gameId": game_id})


def test_fetch_game_by_id_no_data(mock_games_table):
    # Arrange
    game_id = "nonexistent-game-id"
    mock_games_table.get_item.return_value = {}  # No item found

    # Act
    result = fetch_game_by_id(game_id)

    # Assert
    assert result is None
    mock_games_table.get_item.assert_called_once_with(Key={"gameId": game_id})


def test_fetch_solutions_by_standardized_hash(mocker, mock_games_table, mock_solution_calculations):
    # Arrange
    standardized_hash = "sample-hash"
    items = [
        {"twoWordSolutions": ["WORD1", "WORD2"], "threeWordSolutions": ["WORD3", "WORD4"]},
        {"twoWordSolutions": ["ALT1", "ALT2"]},  # Missing one solution field
    ]
    mock_games_table.query.return_value = {"Items": items}

    # Act
    result = fetch_solutions_by_standardized_hash(standardized_hash)

    # Assert
    assert result == items[0]
    mock_games_table.query.assert_called_once_with(
        IndexName="StandardizedHashIndex",
        KeyConditionExpression=mocker.ANY,
        ProjectionExpression="twoWordSolutions, threeWordSolutions",
    )


def test_fetch_solutions_by_standardized_hash_client_error(mocker, mock_games_table):
    # Arrange
    standardized_hash = "sample-hash"
    mock_games_table.query.side_effect = ClientError(
        error_response={"Error": {"Code": "MockError", "Message": "Mocked error"}},
        operation_name="Query"
    )

    # Act
    result = fetch_solutions_by_standardized_hash(standardized_hash)

    # Assert
    assert result is None
    mock_games_table.query.assert_called_once_with(
        IndexName="StandardizedHashIndex",
        KeyConditionExpression=mocker.ANY,
        ProjectionExpression="twoWordSolutions, threeWordSolutions",
    )


def test_fetch_solutions_by_standardized_hash_no_data(mocker, mock_games_table):
    # Arrange
    standardized_hash = "nonexistent-hash"
    mock_games_table.query.return_value = {"Items": []}  # No items found

    # Act
    result = fetch_solutions_by_standardized_hash(standardized_hash)

    # Assert
    assert result is None
    mock_games_table.query.assert_called_once_with(
        IndexName="StandardizedHashIndex",
        KeyConditionExpression=mocker.ANY,
        ProjectionExpression="twoWordSolutions, threeWordSolutions",
    )


def test_fetch_solutions_by_standardized_hash_missing_fields(mocker, mock_games_table):
    # Arrange
    standardized_hash = "sample-hash"
    items = [
        {"twoWordSolutions": ["WORD1", "WORD2"]},  # Missing threeWordSolutions
        {"threeWordSolutions": ["WORD3", "WORD4"]}  # Missing twoWordSolutions
    ]
    mock_games_table.query.return_value = {"Items": items}

    # Act
    result = fetch_solutions_by_standardized_hash(standardized_hash)

    # Assert
    assert result is None  # No item has both fields
    mock_games_table.query.assert_called_once_with(
        IndexName="StandardizedHashIndex",
        KeyConditionExpression=mocker.ANY,
        ProjectionExpression="twoWordSolutions, threeWordSolutions",
    )


# ========================= Valid Words DB tests =========================

def test_add_valid_words_to_db(mock_valid_words_table):
    game_id = "test-game-id"
    valid_words = ["apple", "banana", "cherry"]
    # Act
    result = add_valid_words_to_db(game_id, valid_words)
    # Assert
    assert result is True
    mock_valid_words_table.put_item.assert_called_once_with(Item={"gameId": game_id, "validWords": valid_words})

def test_add_valid_words_to_db_client_error(mock_valid_words_table):
    mock_valid_words_table.put_item.side_effect = ClientError(
        error_response={"Error": {"Code": "MockError", "Message": "Mocked error"}},
        operation_name="PutItem",
    )
    game_id = "test-game-id"
    valid_words = ["apple", "banana", "cherry"]
    # Act
    result = add_valid_words_to_db(game_id, valid_words)
    # Assert
    assert result is False
    mock_valid_words_table.put_item.assert_called_once()

def test_fetch_valid_words_by_game_id(mock_valid_words_table):
    game_id = "test-game-id"
    valid_words = ["apple", "banana", "cherry"]
    mock_valid_words_table.get_item.return_value = {"Item": {"gameId": game_id, "validWords": valid_words}}
    # Act
    result = fetch_valid_words_by_game_id(game_id)
    # Assert
    assert result == valid_words
    mock_valid_words_table.get_item.assert_called_once_with(Key={"gameId": game_id})

def test_fetch_valid_words_by_game_id_no_data(mock_valid_words_table):
    game_id = "nonexistent-game-id"
    mock_valid_words_table.get_item.return_value = {}  # No item found
    # Act
    result = fetch_valid_words_by_game_id(game_id)
    # Assert
    assert result is None
    mock_valid_words_table.get_item.assert_called_once_with(Key={"gameId": game_id})

def test_fetch_valid_words_by_game_id_client_error(mock_valid_words_table):
    mock_valid_words_table.get_item.side_effect = ClientError(
        error_response={"Error": {"Code": "MockError", "Message": "Mocked error"}},
        operation_name="GetItem",
    )
    game_id = "test-game-id"
    # Act
    result = fetch_valid_words_by_game_id(game_id)
    # Assert
    assert result is None
    mock_valid_words_table.get_item.assert_called_once_with(Key={"gameId": game_id})


# ========================= Sessions DB tests =========================

def test_get_user_game_state_existing_session(mock_session_states_table):
    session_id = "test-session-id"
    game_id = "test-game-id"
    session_data = {
        "sessionId": session_id,
        "gameId": game_id,
        "wordsUsed": ["apple", "banana"],
    }
    mock_session_states_table.get_item.return_value = {"Item": session_data}
    # Act
    result = get_user_game_state(session_id, game_id)
    # Assert
    assert result == session_data
    mock_session_states_table.get_item.assert_called_once_with(Key={"sessionId": session_id, "gameId": game_id})

def test_get_user_game_state_new_session(mock_session_states_table):
    session_id = "new-session-id"
    game_id = "test-game-id"
    mock_session_states_table.get_item.return_value = {}  # No item found
    # Act
    result = get_user_game_state(session_id, game_id)
    # Assert
    expected_result = {
        "sessionId": session_id,
        "gameId": game_id, 
        "wordsUsed": [],
    }
    assert result == expected_result
    mock_session_states_table.get_item.assert_called_once_with(Key={"sessionId": session_id, "gameId": game_id})

def test_get_user_game_state_client_error(mock_session_states_table):
    session_id = "test-session-id"
    game_id = "test-game-id"
    mock_session_states_table.get_item.side_effect = ClientError(
        error_response={"Error": {"Code": "MockError", "Message": "Mocked error"}},
        operation_name="GetItem",
    )
    # Act
    result = get_user_game_state(session_id, game_id)
    # Assert
    assert result is None
    mock_session_states_table.get_item.assert_called_once_with(Key={"sessionId": session_id, "gameId": game_id})

def test_save_session_state(mock_session_states_table):
    session_data = {
        "sessionId": "test-session-id",
        "gameId": "test-game-id",
        "wordsUsed": ["apple", "banana"],
    }
    # Act
    result = save_session_state(session_data)
    # Assert
    assert result is True
    mock_session_states_table.put_item.assert_called_once_with(Item=session_data)

def test_save_session_state_client_error(mock_session_states_table):
    session_data = {
        "sessionId": "test-session-id",
        "gameId": "test-game-id",
        "wordsUsed": ["apple", "banana"],
    }
    mock_session_states_table.put_item.side_effect = ClientError(
        error_response={"Error": {"Code": "MockError", "Message": "Mocked error"}},
        operation_name="PutItem",
    )
    # Act
    result = save_session_state(session_data)
    # Assert
    assert result is False
    mock_session_states_table.put_item.assert_called_once_with(Item=session_data)
