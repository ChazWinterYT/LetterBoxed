import pytest
from unittest.mock import patch
import json
from lambdas.fetch_game.handler import handler


@pytest.fixture
def mock_fetch_game_by_id(mocker):
    return mocker.patch("lambdas.fetch_game.handler.fetch_game_by_id")


def test_fetch_game_success(mock_fetch_game_by_id):
    # Arrange
    game_id = "2024-11-16"
    sample_game = {
        "gameId": game_id,
        "gameLayout": ["ABC", "DEF", "GHI", "XYZ"],
        "boardSize": "3x3",
        "language": "en"
    }
    mock_fetch_game_by_id.return_value = sample_game

    event = {"pathParameters": {"gameId": game_id}}  
    context = {}

    # Act
    response = handler(event, context)

    # Assert
    assert response["statusCode"] == 200
    assert json.loads(response["body"]) == {
        "gameId": game_id,
        "gameLayout": ["ABC", "DEF", "GHI", "XYZ"],
        "boardSize": "3x3",
        "language": "en",
        "hint": "",
        "message": "Game fetched successfully."
    }


# Test: Missing gameId in the path parameters
def test_fetch_game_invalid_input():
    # Arrange
    event = {"pathParameters": {}}  # No gameId in the request
    context = {}

    # Act
    response = handler(event, context)

    # Assert
    assert response["statusCode"] == 400
    body = json.loads(response["body"])
    assert body["message"] == "Invalid input: gameId is required."


# Test: Valid gameId but game not found in the database
@patch("lambdas.fetch_game.handler.fetch_game_by_id")
def test_fetch_game_not_found(mock_fetch_game_by_id):
    # Arrange
    game_id = "non-existent-id"
    mock_fetch_game_by_id.return_value = None  # Simulate game not found
    event = {"pathParameters": {"gameId": game_id}}
    context = {}

    # Act
    response = handler(event, context)

    # Assert
    assert response["statusCode"] == 404
    body = json.loads(response["body"])
    assert body["message"] == "Game ID not found."
    mock_fetch_game_by_id.assert_called_once_with(game_id)
    