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
    body = json.loads(response["body"])
    assert body["gameId"] == game_id
    assert body["gameLayout"] == sample_game["gameLayout"]
    assert body["boardSize"] == sample_game["boardSize"]
    assert body["language"] == sample_game["language"]
    assert body["message"] == "Game fetched successfully."
    mock_fetch_game_by_id.assert_called_once_with(game_id)


def test_fetch_game_invalid_input(mock_fetch_game_by_id):
    # Arrange
    event = {"pathParameters": {}}
    context = {}

    # Act
    response = handler(event, context)

    # Assert
    assert response["statusCode"] == 400
    body = json.loads(response["body"])
    assert body["message"] == "Invalid input: gameId is required."
    mock_fetch_game_by_id.assert_not_called()


def test_fetch_game_not_found(mock_fetch_game_by_id):
    # Arrange
    game_id = "non-existent-game-id"
    mock_fetch_game_by_id.return_value = None

    event = {"pathParameters": {"gameId": game_id}}
    context = {}

    # Act
    response = handler(event, context)

    # Assert
    assert response["statusCode"] == 400
    body = json.loads(response["body"])
    assert body["message"] == "Game ID not found."
    mock_fetch_game_by_id.assert_called_once_with(game_id)
