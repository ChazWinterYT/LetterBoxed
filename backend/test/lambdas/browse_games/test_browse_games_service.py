import pytest
from datetime import datetime
from lambdas.browse_games.browse_games_service import query_games_by_language
from lambdas.common.db_utils import fetch_games_by_language


def test_query_games_valid_input(mocker):
    """Test query_games_by_language with valid inputs."""
    mock_response = {
        "games": [{"gameId": "1234", "name": "test_game"}],
        "lastEvaluatedKey": {
            "language": "en",
            "createdAt": "2024-12-24T12:00:00",
            "gameId": "1234",
        }
    }

    # Mock the fetch_games_by_language function
    mock_fetch_games = mocker.patch(
        "lambdas.browse_games.browse_games_service.fetch_games_by_language",
        return_value=mock_response
    )

    # Call the function under test
    last_key = {
        "language": "en",
        "createdAt": "2024-12-23T12:00:00",
        "gameId": "1233",
    }
    result = query_games_by_language(language="en", last_key=last_key, limit=10)

    # Assert the result matches the mock response
    assert result == mock_response

    # Assert the mock was called with the correct arguments
    mock_fetch_games.assert_called_once_with(language="en", last_key=last_key, limit=10)


def test_query_games_invalid_language_empty():
    """Test query_games_by_language with empty language."""
    with pytest.raises(ValueError, match="Language must be a non-empty string."):
        query_games_by_language(language="", last_key=None, limit=10)


def test_query_games_invalid_language_non_string():
    """Test query_games_by_language with non-string language."""
    with pytest.raises(ValueError, match="Language must be a non-empty string."):
        query_games_by_language(language=123, last_key=None, limit=10)


def test_query_games_invalid_limit_non_positive():
    """Test query_games_by_language with non-positive limit."""
    with pytest.raises(ValueError, match="Limit must be a positive integer."):
        query_games_by_language(language="en", last_key=None, limit=0)


def test_query_games_invalid_limit_non_integer():
    """Test query_games_by_language with non-integer limit."""
    with pytest.raises(ValueError, match="Limit must be a positive integer."):
        query_games_by_language(language="en", last_key=None, limit="ten")


def test_query_games_invalid_last_key_missing_keys():
    """Test query_games_by_language with last_key missing required keys."""
    last_key = {"language": "en", "createdAt": "2024-12-24T12:00:00"}  # Missing 'gameId'
    with pytest.raises(ValueError, match="last_key must include the following keys: language, createdAt, gameId"):
        query_games_by_language(language="en", last_key=last_key, limit=10)


def test_query_games_invalid_last_key_invalid_createdAt():
    """Test query_games_by_language with invalid createdAt in last_key."""
    last_key = {
        "language": "en",
        "createdAt": "invalid-timestamp",
        "gameId": "1234",
    }
    with pytest.raises(ValueError, match="Invalid createdAt in last_key. Must be an ISO 8601 timestamp."):
        query_games_by_language(language="en", last_key=last_key, limit=10)


def test_query_games_db_utility_error(mocker):
    """Test query_games_by_language when fetch_games_by_language raises an exception."""
    mocker.patch(
        "lambdas.browse_games.browse_games_service.fetch_games_by_language",
        side_effect=ValueError("Database query error")
    )

    with pytest.raises(ValueError, match="Database query error"):
        query_games_by_language(language="en", last_key=None, limit=10)


def test_query_games_unexpected_error(mocker):
    """Test query_games_by_language with an unexpected exception."""
    mocker.patch(
        "lambdas.browse_games.browse_games_service.fetch_games_by_language",
        side_effect=Exception("Unexpected error")
    )

    with pytest.raises(Exception, match="Unexpected error"):
        query_games_by_language(language="en", last_key=None, limit=10)
