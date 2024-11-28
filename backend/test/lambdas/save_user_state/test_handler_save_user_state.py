import json
import pytest
from unittest.mock import MagicMock
from lambdas.save_user_state.handler import handler
import time

# Mock time.time to return a consistent value for testing
@pytest.fixture(autouse=True)
def mock_time(monkeypatch):
    mock_time = MagicMock(return_value=1620000000)  # Fixed timestamp
    monkeypatch.setattr(time, 'time', mock_time)
    yield


def test_save_user_state_puzzle_solved(mocker):
    # Arrange
    game_layout = ["PRO", "CTI", "DGN", "SAH"]
    words_used = ["CHINSTRAP", "PAGODA"]  # Assume these words use all letters
    original_words_used = ["CHINSTRAP", "PAGODA"]

    # Mock get_user_game_state to return None, simulating a new session
    mocker.patch(
        "lambdas.save_user_state.handler.get_user_game_state",
        return_value=None
    )

    # Mock save_user_session_state to simply pass
    mock_save_user_session_state = mocker.patch(
        "lambdas.save_user_state.handler.save_user_session_state",
        return_value=True
    )

    # Event data simulating API Gateway request
    event = {
        "body": json.dumps({
            "sessionId": "test-session",
            "gameId": "test-game",
            "gameLayout": game_layout,
            "wordsUsed": words_used,
            "originalWordsUsed": original_words_used
        })
    }

    # Act
    response = handler(event, None)
    body = json.loads(response["body"])

    # Assert
    assert response["statusCode"] == 200
    assert body["gameCompleted"] is True
    assert body["message"] == "Puzzle solved successfully! Congrats!"
    assert body["wordsUsed"] == words_used
    assert body["originalWordsUsed"] == original_words_used

    # Verify that save_user_session_state was called with the expected arguments
    expected_game_state = {
        "sessionId": "test-session",
        "gameId": "test-game",
        "wordsUsed": words_used,
        "originalWordsUsed": original_words_used,
        "gameCompleted": True,
        "lastUpdated": int(time.time()),
        "TTL": int(time.time()) + 30 * 24 * 60 * 60  # 30 days TTL
    }
    mock_save_user_session_state.assert_called_once_with(expected_game_state)


def test_save_user_state_incomplete(mocker):
    # Arrange
    game_layout = ["PRO", "CTI", "DGN", "SAH"]
    words_used = ["CHINSTRAP"]  # Only one word used
    original_words_used = ["CHINSTRAP"]  

    # Mock get_user_game_state to return None, simulating a new session
    mocker.patch(
        "lambdas.save_user_state.handler.get_user_game_state",
        return_value=None
    )

    # Mock save_user_session_state to simply pass
    mock_save_user_session_state = mocker.patch(
        "lambdas.save_user_state.handler.save_user_session_state",
        return_value=True
    )

    # Event data simulating API Gateway request
    event = {
        "body": json.dumps({
            "sessionId": "test-session",
            "gameId": "test-game",
            "gameLayout": game_layout,
            "wordsUsed": words_used,
            "originalWordsUsed": original_words_used
        })
    }

    # Act
    response = handler(event, None)
    body = json.loads(response["body"])

    # Assert
    assert response["statusCode"] == 200
    assert body["gameCompleted"] is False
    assert body["message"] == "Word accepted."
    assert body["wordsUsed"] == words_used
    assert body["originalWordsUsed"] == original_words_used

    # Verify that save_user_session_state was called with the expected arguments
    expected_game_state = {
        "sessionId": "test-session",
        "gameId": "test-game",
        "wordsUsed": words_used,
        "originalWordsUsed": original_words_used,
        "gameCompleted": False,
        "lastUpdated": int(time.time()),
        "TTL": int(time.time()) + 30 * 24 * 60 * 60  # 30 days TTL
    }
    mock_save_user_session_state.assert_called_once_with(expected_game_state)
