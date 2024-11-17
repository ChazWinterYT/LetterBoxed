import pytest
from unittest.mock import MagicMock
from botocore.exceptions import ClientError
from lambdas.common.db_utils import (
    add_game_to_db,
    fetch_game_by_id,
    fetch_solutions_by_standardized_hash,
)


sample_game = {
    "gameId": "test-game-id",
    "gameLayout": ["ABC", "DEF", "GHI", "XYZ"],
    "standardizedHash": "sample-hash",
    "twoWordSolutions": ["WORD1", "WORD2"],
    "threeWordSolutions": ["WORD3", "WORD4", "WORD5"],
    "boardSize": "3x3",
    "language": "English",
}

bad_sample_game_no_board_size = {
    "gameId": "test-game-id",
    "gameLayout": ["ABC", "DEF", "GHI", "XYZ"],
    "standardizedHash": "sample-hash",
    "twoWordSolutions": ["WORD1", "WORD2"],
    "threeWordSolutions": ["WORD3", "WORD4", "WORD5"],
    "boardSize": "",
    "language": "English",
}


@pytest.fixture
def mock_dynamodb_table(mocker):
    mock_table = MagicMock()
    mocker.patch("lambdas.common.db_utils.table", mock_table)  # Replace `table` in db_utils with the mock
    return mock_table


@pytest.fixture
def mock_solution_calculations(mocker):
    mocker.patch("lambdas.common.game_utils.calculate_two_word_solutions", return_value=["WORD1", "WORD2"])
    mocker.patch("lambdas.common.game_utils.calculate_three_word_solutions", return_value=["WORD3", "WORD4"])


def test_add_game_to_db(mock_dynamodb_table):
    # Act
    add_game_to_db(sample_game)

    # Assert
    mock_dynamodb_table.put_item.assert_called_once_with(Item=sample_game)


def test_add_game_to_db_client_error(mock_dynamodb_table):
    mock_dynamodb_table.put_item.side_effect = ClientError(
        error_response={"Error": {"Code": "MockError", "Message": "Mocked error"}},
        operation_name="PutItem",
    )
    sample_game = {...}  # Your game data
    add_game_to_db(sample_game)  # Expect no exception, just print error
    mock_dynamodb_table.put_item.assert_called_once()


def test_fetch_game_by_id(mock_dynamodb_table):
    # Arrange
    game_id = "test-game-id"
    mock_dynamodb_table.get_item.return_value = {"Item": sample_game}

    # Act
    result = fetch_game_by_id(game_id)

    # Assert
    assert result == sample_game
    mock_dynamodb_table.get_item.assert_called_once_with(Key={"gameId": game_id})


def test_fetch_game_by_id_client_error(mock_dynamodb_table):
    # Arrange
    game_id = "test-game-id"
    mock_dynamodb_table.get_item.side_effect = ClientError(
        error_response={"Error": {"Code": "MockError", "Message": "Mocked error"}},
        operation_name="GetItem"
    )

    # Act
    result = fetch_game_by_id(game_id)

    # Assert
    assert result is None
    mock_dynamodb_table.get_item.assert_called_once_with(Key={"gameId": game_id})


def test_fetch_solutions_by_standardized_hash(mocker, mock_dynamodb_table, mock_solution_calculations):
    # Arrange
    standardized_hash = "sample-hash"
    items = [
        {"twoWordSolutions": ["WORD1", "WORD2"], "threeWordSolutions": ["WORD3", "WORD4"]},
        {"twoWordSolutions": ["ALT1", "ALT2"]},  # Missing one solution field
    ]
    mock_dynamodb_table.query.return_value = {"Items": items}

    # Act
    result = fetch_solutions_by_standardized_hash(standardized_hash)

    # Assert
    assert result == items[0]
    mock_dynamodb_table.query.assert_called_once_with(
        IndexName="StandardizedHashIndex",
        KeyConditionExpression=mocker.ANY,
    )


def test_fetch_solutions_by_standardized_hash_client_error(mocker, mock_dynamodb_table):
    # Arrange
    standardized_hash = "sample-hash"
    mock_dynamodb_table.query.side_effect = ClientError(
        error_response={"Error": {"Code": "MockError", "Message": "Mocked error"}},
        operation_name="Query"
    )

    # Act
    result = fetch_solutions_by_standardized_hash(standardized_hash)

    # Assert
    assert result is None
    mock_dynamodb_table.query.assert_called_once_with(
        IndexName="StandardizedHashIndex",
        KeyConditionExpression=mocker.ANY
    )
