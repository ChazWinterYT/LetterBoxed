import json
import pytest
from unittest.mock import MagicMock
from lambdas.validate_word.handler import handler


@pytest.fixture
def mock_db_utils(mocker):
    """
    Mock the db_utils functions for interacting with DynamoDB.
    """
    mocker.patch("lambdas.validate_word.handler.fetch_game_by_id")
    mocker.patch("lambdas.validate_word.handler.fetch_valid_words_by_game_id")
    mocker.patch("lambdas.validate_word.handler.get_user_game_state")
    mocker.patch("lambdas.validate_word.handler.save_user_session_state")


def test_validate_word_success(mock_db_utils, mocker):
    # Arrange
    mocker.patch(
        "lambdas.validate_word.handler.fetch_valid_words_by_game_id",
        return_value=["APPLE", "ORANGE", "ELEPHANT"]
    )
    mocker.patch(
        "lambdas.validate_word.handler.get_user_game_state",
        return_value={"sessionId": "test-session", "gameId": "test-game", "wordsUsed": ["ORANGE"]}
    )

    event = {
        "body": json.dumps({
            "gameId": "test-game",
            "word": "ELEPHANT",
            "sessionId": "test-session"
        })
    }

    # Act
    response = handler(event, None)
    body = json.loads(response["body"])

    # Assert
    assert response["statusCode"] == 200
    assert body["valid"] is True
    assert body["message"] == "Word is valid."  # Updated message


def test_validate_word_already_used(mock_db_utils, mocker):
    # Arrange
    mocker.patch("lambdas.validate_word.handler.fetch_valid_words_by_game_id", return_value=["APPLE", "ORANGE"])
    mocker.patch("lambdas.validate_word.handler.get_user_game_state", return_value={"sessionId": "test-session", "gameId": "test-game", "wordsUsed": ["APPLE"]})

    event = {
        "body": json.dumps({"gameId": "test-game", "word": "APPLE", "sessionId": "test-session"})
    }

    # Act
    response = handler(event, None)
    body = json.loads(response["body"])

    # Assert
    assert response["statusCode"] == 200
    assert body["valid"] is False
    assert body["message"] == "Word 'APPLE' has already been used."


def test_validate_word_invalid_word(mock_db_utils, mocker):
    # Arrange
    mocker.patch("lambdas.validate_word.handler.fetch_valid_words_by_game_id", return_value=["APPLE", "ORANGE"])
    mocker.patch("lambdas.validate_word.handler.get_user_game_state", return_value={"sessionId": "test-session", "gameId": "test-game", "wordsUsed": []})

    event = {
        "body": json.dumps({"gameId": "test-game", "word": "BANANA", "sessionId": "test-session"})
    }

    # Act
    response = handler(event, None)
    body = json.loads(response["body"])

    # Assert
    assert response["statusCode"] == 200
    assert body["valid"] is False
    assert body["message"] == "Word is not valid for this puzzle."


def test_validate_word_db_error(mock_db_utils, mocker):
    # Arrange
    mocker.patch("lambdas.validate_word.handler.fetch_valid_words_by_game_id", side_effect=Exception("DB Error"))
    mocker.patch("lambdas.validate_word.handler.get_user_game_state", return_value={"sessionId": "test-session", "gameId": "test-game", "wordsUsed": []})

    event = {
        "body": json.dumps({"gameId": "test-game", "word": "APPLE", "sessionId": "test-session"})
    }

    # Act
    response = handler(event, None)
    body = json.loads(response["body"])

    # Assert
    assert response["statusCode"] == 500
    assert body["message"] == "An unexpected error occurred: DB Error"
