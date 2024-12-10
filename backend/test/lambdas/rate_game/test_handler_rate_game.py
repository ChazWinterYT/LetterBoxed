import json
import pytest
from unittest.mock import patch, MagicMock
from lambdas.rate_game.handler import handler

@pytest.fixture
def valid_event():
    """Fixture for a valid API Gateway event."""
    return {
        "body": json.dumps({
            "gameId": "12345",
            "stars": 4
        })
    }

@pytest.fixture
def invalid_event_missing_game_id():
    """Fixture for an event missing gameId."""
    return {
        "body": json.dumps({
            "stars": 4
        })
    }

@pytest.fixture
def invalid_event_missing_stars():
    """Fixture for an event missing stars."""
    return {
        "body": json.dumps({
            "gameId": "12345"
        })
    }

@pytest.fixture
def invalid_event_invalid_stars():
    """Fixture for an event with invalid stars."""
    return {
        "body": json.dumps({
            "gameId": "12345",
            "stars": 6  # Out of valid range
        })
    }

@pytest.fixture
def invalid_json_event():
    """Fixture for an event with invalid JSON in the body."""
    return {
        "body": "Invalid JSON"
    }

# Mock dependencies
@patch("lambdas.rate_game.handler.fetch_game_by_id")
@patch("lambdas.rate_game.handler.rate_game")
def test_handler_success(mock_rate_game, mock_fetch_game_by_id, valid_event):
    """Test successful game rating."""
    # Arrange
    mock_fetch_game_by_id.return_value = {"gameId": "12345", "totalRatings": 10, "totalStars": 40}
    mock_rate_game.return_value = True

    # Act
    response = handler(valid_event, None)

    # Assert
    assert response["statusCode"] == 200
    body = json.loads(response["body"])
    assert body["message"] == "Game rated successfully."
    assert body["newReviewCount"] == 11
    assert body["newStarCount"] == 44
    mock_fetch_game_by_id.assert_called_once_with("12345")
    mock_rate_game.assert_called_once_with({"gameId": "12345", "totalRatings": 10, "totalStars": 40}, 4)


@patch("lambdas.rate_game.handler.fetch_game_by_id")
def test_handler_game_not_found(mock_fetch_game_by_id, valid_event):
    """Test handling when the game is not found in the database."""
    # Arrange
    mock_fetch_game_by_id.return_value = None

    # Act
    response = handler(valid_event, None)

    # Assert
    assert response["statusCode"] == 404
    body = json.loads(response["body"])
    assert body["message"] == "Game not found in DB"


def test_handler_missing_game_id(invalid_event_missing_game_id):
    """Test handling when gameId is missing."""
    # Act
    response = handler(invalid_event_missing_game_id, None)

    # Assert
    assert response["statusCode"] == 400
    body = json.loads(response["body"])
    assert body["message"] == "Missing required parameters: Game ID and Stars are required."


def test_handler_missing_stars(invalid_event_missing_stars):
    """Test handling when stars are missing."""
    # Act
    response = handler(invalid_event_missing_stars, None)

    # Assert
    assert response["statusCode"] == 400
    body = json.loads(response["body"])
    assert body["message"] == "Missing required parameters: Game ID and Stars are required."


def test_handler_invalid_stars(invalid_event_invalid_stars):
    """Test handling when stars are out of valid range."""
    # Act
    response = handler(invalid_event_invalid_stars, None)

    # Assert
    assert response["statusCode"] == 400
    body = json.loads(response["body"])
    assert body["message"] == "Invalid 'stars' value: must be an integer between 1 and 5."


def test_handler_invalid_json(invalid_json_event):
    """Test handling when the request body contains invalid JSON."""
    # Act
    response = handler(invalid_json_event, None)

    # Assert
    assert response["statusCode"] == 400
    body = json.loads(response["body"])
    assert body["message"] == "Invalid JSON in request body."


@patch("lambdas.rate_game.handler.fetch_game_by_id")
@patch("lambdas.rate_game.handler.rate_game")
def test_handler_rate_game_failure(mock_rate_game, mock_fetch_game_by_id, valid_event):
    """Test handling when rate_game fails."""
    # Arrange
    mock_fetch_game_by_id.return_value = {"gameId": "12345", "totalRatings": 10, "totalStars": 40}
    mock_rate_game.return_value = False

    # Act
    response = handler(valid_event, None)

    # Assert
    assert response["statusCode"] == 500
    body = json.loads(response["body"])
    assert body["message"] == "Failed to rate the game."
    mock_fetch_game_by_id.assert_called_once_with("12345")
    mock_rate_game.assert_called_once_with({"gameId": "12345", "totalRatings": 10, "totalStars": 40}, 4)
