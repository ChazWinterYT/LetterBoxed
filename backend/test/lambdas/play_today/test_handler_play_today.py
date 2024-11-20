import pytest
from unittest.mock import MagicMock
from lambdas.play_today.handler import handler
from datetime import date, timedelta


@pytest.fixture
def mock_dynamodb_table(mocker):
    # Mock the DynamoDB table and replace `boto3.resource` globally
    mock_table = MagicMock()
    mocker.patch("lambdas.common.db_utils.get_games_table", return_value=mock_table) 
    return mock_table


def test_play_today_game_exists(mock_dynamodb_table):
    # Arrange: Mock today's game in the DB
    today = date.today().isoformat()
    mock_dynamodb_table.get_item.return_value = {
        "Item": {
            "gameId": today,
            "gameLayout": ["ABC", "DEF", "GHI", "XYZ"],
            "boardSize": "3x3",
            "language": "en",
            "par": 4,
        }
    }

    # Act
    event = {}
    context = {}
    response = handler(event, context)

    # Assert
    assert response["statusCode"] == 200
    assert today in response["body"]
    mock_dynamodb_table.get_item.assert_called_once_with(Key={"gameId": today})


def test_play_today_fallback_to_yesterday(mock_dynamodb_table):
    # Arrange: Mock yesterday's game since today's game is unavailable
    today = date.today().isoformat()
    yesterday = (date.today() - timedelta(days=1)).isoformat()
    mock_dynamodb_table.get_item.side_effect = [
        {},  # No game found for today
        {"Item": {
            "gameId": yesterday, 
            "gameLayout": ["XYZ", "DEF", "ABC", "LMN"], 
            "boardSize": "3x3", 
            "language": "en",
            "par": 4
        }}
    ]

    # Act
    event = {}
    context = {}
    response = handler(event, context)

    # Assert
    assert response["statusCode"] == 200
    assert yesterday in response["body"]
    mock_dynamodb_table.get_item.assert_any_call(Key={"gameId": today})
    mock_dynamodb_table.get_item.assert_any_call(Key={"gameId": yesterday})


def test_play_today_no_games_available(mock_dynamodb_table):
    # Arrange: No games for either today or yesterday
    today = date.today().isoformat()
    yesterday = (date.today() - timedelta(days=1)).isoformat()
    
    # Mock the return values for get_item to simulate no games in the DB
    mock_dynamodb_table.get_item.side_effect = [
        {},  # Today's game is not found
        {},  # Yesterday's game is not found
    ]

    # Act
    event = {}
    context = {}
    response = handler(event, context)

    # Assert
    assert response["statusCode"] == 404
    assert f"{today}'s game is not yet available" in response["body"]
    assert f"{yesterday}'s game isn't either" in response["body"]

    # Ensure `get_item` is called for both today and yesterday
    mock_dynamodb_table.get_item.assert_any_call(Key={"gameId": today})
    mock_dynamodb_table.get_item.assert_any_call(Key={"gameId": yesterday})
