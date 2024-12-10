import json
import pytest
import random
from unittest.mock import MagicMock, patch
from lambdas.validate_word.handler import handler


@pytest.fixture
def mock_db_utils(mocker):
    """
    Mock the db_utils functions for interacting with DynamoDB.
    """
    fetch_game_by_id_mock = mocker.patch("lambdas.validate_word.handler.fetch_game_by_id")
    fetch_valid_words_by_game_id_mock = mocker.patch("lambdas.validate_word.handler.fetch_valid_words_by_game_id")
    get_user_game_state_mock = mocker.patch("lambdas.validate_word.handler.get_user_game_state")
    save_user_session_state_mock = mocker.patch("lambdas.validate_word.handler.save_user_session_state")

    return {
        "fetch_game_by_id": fetch_game_by_id_mock,
        "fetch_valid_words_by_game_id": fetch_valid_words_by_game_id_mock,
        "get_user_game_state": get_user_game_state_mock,
        "save_user_session_state": save_user_session_state_mock,
    }


@pytest.fixture
def mock_random_sample():
    """Mock random.sample to return the first N items for predictable tests."""
    with patch("random.sample", side_effect=lambda x, n: x[:n]):
        yield
        

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
    assert body["message"] == "Word accepted."  # Updated message


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


def test_game_completion_with_nyt_solution(mock_db_utils, mock_random_sample, mocker):
    # Arrange
    mocker.patch(
        "lambdas.validate_word.handler.fetch_valid_words_by_game_id",
        return_value=["APPLE", "ORANGE", "ELEPHANT"]
    )
    mocker.patch(
        "lambdas.validate_word.handler.get_user_game_state",
        return_value={"sessionId": "test-session", "gameId": "test-game", "wordsUsed": ["APPLE", "ORANGE"]}
    )
    mocker.patch(
        "lambdas.validate_word.handler.check_game_completion",
        return_value=(True, "Congratulations! Puzzle solved.")
    )
    mock_db_utils["fetch_game_by_id"].return_value = {
        "gameLayout": ["ABC", "DEF", "GHI", "JKL"],
        "nytSolution": ["APPLE", "ORANGE", "ELEPHANT"],
        "oneWordSolutions": ["GRAPE", "PLUM"],
        "twoWordSolutions": [("BANANA", "CHERRY"), ("PEACH", "KIWI")],
        "oneWordSolutionCount": 2,
        "twoWordSolutionCount": 2,
        "totalCompletions": 10,
        "totalWordsUsed": 50,
        "totalLettersUsed": 300,
        "totalRatings": 5,
        "totalStars": 25,
    }

    event = {
        "body": json.dumps({"gameId": "test-game", "word": "ELEPHANT", "sessionId": "test-session"})
    }

    # Act
    response = handler(event, None)
    body = json.loads(response["body"])
    print("Response:", response)

    # Assert
    assert response["statusCode"] == 200
    assert body["gameCompleted"] is True
    assert body["message"] == "Congratulations! Puzzle solved."
    assert body["officialSolution"] == ["APPLE", "ORANGE", "ELEPHANT"]
    assert body["someOneWordSolutions"] == ["GRAPE", "PLUM"]
    assert body["someTwoWordSolutions"] == [["BANANA", "CHERRY"], ["PEACH", "KIWI"]]


def test_game_completion_with_random_seed_word(mock_db_utils, mock_random_sample, mocker):
    # Arrange
    mocker.patch(
        "lambdas.validate_word.handler.fetch_valid_words_by_game_id",
        return_value=["APPLE", "ORANGE", "ELEPHANT"]
    )
    mocker.patch(
        "lambdas.validate_word.handler.get_user_game_state",
        return_value={"sessionId": "test-session", "gameId": "test-game", "wordsUsed": ["ORANGE"]}
    )
    mocker.patch(
        "lambdas.validate_word.handler.check_game_completion",
        return_value=(True, "Congratulations! Puzzle solved.")
    )
    mock_db_utils["fetch_game_by_id"].return_value = {
        "gameLayout": ["OMG", "WTF", "BLT", "SEX"],
        "randomSeedWord": "ORANGE",
        "oneWordSolutions": ["LIME"],
        "oneWordSolutionCount": 1,
        "twoWordSolutions": [("BANANA", "CHERRY"), ("PEACH", "KIWI")],
        "twoWordSolutionCount": 2,
        "totalCompletions": 10,
        "totalWordsUsed": 50,
        "totalLettersUsed": 300,
        "totalRatings": 5,
        "totalStars": 25,
    }

    event = {
        "body": json.dumps({"gameId": "test-game", "word": "ELEPHANT", "sessionId": "test-session"})
    }

    # Act
    response = handler(event, None)
    body = json.loads(response["body"])
    print("Response:", response)

    # Assert
    assert response["statusCode"] == 200
    assert body["gameCompleted"] is True
    assert body["officialSolution"] == ["ORANGE"]
    assert body["someOneWordSolutions"] == ["LIME"]
    assert body["someTwoWordSolutions"] == [["BANANA", "CHERRY"], ["PEACH", "KIWI"]]


def test_validate_word_chaining_rule_failure(mock_db_utils, mocker):
    # Arrange
    mocker.patch("lambdas.validate_word.handler.fetch_valid_words_by_game_id", return_value=["APPLE", "ORANGE", "BANANA", "ELEPHANT"])
    mocker.patch("lambdas.validate_word.handler.get_user_game_state", return_value={"wordsUsed": ["APPLE"]})

    event = {
        "body": json.dumps({"gameId": "test-game", "word": "BANANA", "sessionId": "test-session"})
    }

    # Act
    response = handler(event, None)
    body = json.loads(response["body"])

    # Assert
    assert response["statusCode"] == 200
    assert body["valid"] is False
    assert "must start with the last letter of the previous word" in body["message"]
    
    
def test_validate_word_chaining_rule_success(mock_db_utils, mocker):
    # Arrange
    mocker.patch("lambdas.validate_word.handler.fetch_valid_words_by_game_id", return_value=["APPLE", "ORANGE", "BANANA", "ELEPHANT"])
    mocker.patch("lambdas.validate_word.handler.get_user_game_state", return_value={"wordsUsed": ["APPLE"]})

    event = {
        "body": json.dumps({"gameId": "test-game", "word": "ELEPHANT", "sessionId": "test-session"})
    }

    # Act
    response = handler(event, None)
    body = json.loads(response["body"])

    # Assert
    assert response["statusCode"] == 200
    assert body["valid"] is True
    assert "Word accepted." in body["message"]


def test_validate_word_missing_parameters(mock_db_utils, mocker):
    # Arrange
    event = {"body": json.dumps({"gameId": "test-game", "word": "APPLE"})}

    # Act
    response = handler(event, None)
    body = json.loads(response["body"])

    # Assert
    assert response["statusCode"] == 400
    assert body["message"] == "Missing required parameters: gameId, word, or sessionId."


def test_random_sample_with_fewer_items(mock_random_sample):
    # Arrange
    items = ["ITEM1", "ITEM2"]

    # Act
    result = random.sample(items, 5)

    # Assert
    assert result == ["ITEM1", "ITEM2"]