import json
from unittest.mock import patch, MagicMock
from lambdas.game_archive.handler import handler

@patch("lambdas.game_archive.handler.fetch_archived_games")
def test_handler_no_query_params(mock_fetch_archived_games):
    # Arrange
    mock_fetch_archived_games.return_value = {
        "items": [
            {"gameId": "20210101", "officialGame": True},
            {"gameId": "20210102", "officialGame": True},
            {"gameId": "20200101", "officialGame": True},
            {"gameId": "20190101", "officialGame": True},
        ],
        "lastKey": None,
    }

    event = {
        "queryStringParameters": None  # No query parameters
    }

    # Act
    response = handler(event, None)
    body = json.loads(response["body"])

    # Assert
    assert response["statusCode"] == 200
    assert "nytGames" in body
    assert len(body["nytGames"]) == 4  # All items returned
    assert body["lastKey"] is None
    assert body["message"] == "Fetched official NYT games archive successfully."
    mock_fetch_archived_games.assert_called_once_with(limit=12, last_key=None)


@patch("lambdas.game_archive.handler.fetch_archived_games")
def test_handler_with_pagination(mock_fetch_archived_games):
    # Arrange
    mock_fetch_archived_games.return_value = {
        "items": [
            {"gameId": "20210103", "officialGame": True},
            {"gameId": "20210104", "officialGame": True},
        ],
        "lastKey": {"gameId": "20210104"},
    }

    event = {
        "queryStringParameters": {
            "limit": 2,
            "lastKey": json.dumps({"gameId": "20210102"})
        }
    }

    # Act
    response = handler(event, None)
    body = json.loads(response["body"])

    # Assert
    assert response["statusCode"] == 200
    assert "nytGames" in body
    assert len(body["nytGames"]) == 2  # Only 2 items
    assert body["lastKey"] == json.dumps({"gameId": "20210104"})
    mock_fetch_archived_games.assert_called_once_with(
        limit=2,
        last_key={"gameId": "20210102"}
    )


@patch("lambdas.game_archive.handler.fetch_archived_games")
def test_handler_error(mock_fetch_archived_games):
    # Arrange
    mock_fetch_archived_games.side_effect = Exception("Database error")

    event = {
        "queryStringParameters": None  # No query parameters
    }

    # Act
    response = handler(event, None)
    body = json.loads(response["body"])

    # Assert
    assert response["statusCode"] == 500
    assert body["message"] == "Error fetching New York Times Archive"
    mock_fetch_archived_games.assert_called_once_with(limit=12, last_key=None)
