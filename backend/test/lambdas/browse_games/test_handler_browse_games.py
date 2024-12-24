import json
import pytest
from datetime import datetime
from lambdas.browse_games.handler import handler
from lambdas.browse_games.browse_games_service import query_games_by_language


@pytest.fixture
def mock_event():
    """Fixture to create a base event structure."""
    return {
        "queryStringParameters": {
            "language": "en",
            "limit": "10",
            "lastEvaluatedKey": json.dumps({
                "language": "en",
                "createdAt": datetime.now().isoformat(),
                "gameId": "test-game-id"
            })
        }
    }


def test_handler_valid_request(mocker, mock_event):
    """Test handler with valid input."""
    mock_response = {
        "games": [{"gameId": "1234", "name": "test_game"}],
        "lastEvaluatedKey": {
            "language": "en",
            "createdAt": "2024-12-24T15:26:14.634415",
            "gameId": "1234",
        }
    }
    mocker.patch("lambdas.browse_games.handler.query_games_by_language", return_value=mock_response)

    result = handler(mock_event, None)

    assert result["statusCode"] == 200
    assert json.loads(result["body"]) == mock_response


def test_handler_missing_language(mocker, mock_event):
    """Test handler with missing language."""
    mock_event["queryStringParameters"].pop("language")
    result = handler(mock_event, None)

    assert result["statusCode"] == 400
    assert json.loads(result["body"])["message"] == "Language is required for browsing games."


def test_handler_invalid_language(mocker, mock_event):
    """Test handler with invalid language."""
    mock_event["queryStringParameters"]["language"] = "xx"
    result = handler(mock_event, None)

    assert result["statusCode"] == 400
    assert json.loads(result["body"])["message"] == "Specified language is not supported."


def test_handler_invalid_last_key_format(mocker, mock_event):
    """Test handler with invalid lastEvaluatedKey format."""
    mock_event["queryStringParameters"]["lastEvaluatedKey"] = "invalid-json-string"
    result = handler(mock_event, None)

    assert result["statusCode"] == 400
    assert json.loads(result["body"])["message"] == "Invalid lastEvaluatedKey format. Must be a JSON object with 'language', 'createdAt', and 'gameId'."


def test_handler_invalid_last_key_missing_keys(mocker, mock_event):
    """Test handler with missing keys in lastEvaluatedKey."""
    mock_event["queryStringParameters"]["lastEvaluatedKey"] = json.dumps({
        "language": "en",
        "createdAt": "2024-12-24T15:26:14.634415"  # Missing gameId
    })
    result = handler(mock_event, None)

    assert result["statusCode"] == 400
    assert json.loads(result["body"])["message"] == "Invalid lastEvaluatedKey format. Must be a JSON object with 'language', 'createdAt', and 'gameId'."


def test_handler_invalid_limit_non_integer(mocker, mock_event):
    """Test handler with non-integer limit."""
    mock_event["queryStringParameters"]["limit"] = "abc"
    result = handler(mock_event, None)

    assert result["statusCode"] == 400
    assert json.loads(result["body"])["message"] == "Limit must be a positive integer."


def test_handler_invalid_limit_negative(mocker, mock_event):
    """Test handler with negative limit."""
    mock_event["queryStringParameters"]["limit"] = "-5"
    result = handler(mock_event, None)

    assert result["statusCode"] == 400
    assert json.loads(result["body"])["message"] == "Limit must be a positive integer."


def test_handler_service_error(mocker, mock_event):
    """Test handler when service layer raises an exception."""
    mocker.patch("lambdas.browse_games.handler.query_games_by_language", side_effect=ValueError("Service Error"))

    result = handler(mock_event, None)
    assert result["statusCode"] == 400
    assert json.loads(result["body"])["message"] == "Validation error: Service Error"


def test_handler_unexpected_error(mocker, mock_event):
    """Test handler with an unexpected exception."""
    mocker.patch("lambdas.browse_games.handler.query_games_by_language", side_effect=Exception("Unexpected Error"))

    result = handler(mock_event, None)
    assert result["statusCode"] == 500
    assert json.loads(result["body"])["message"] == "Internal Server Error"
