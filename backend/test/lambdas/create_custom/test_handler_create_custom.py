import json
import pytest
from unittest.mock import patch
from lambdas.create_custom.handler import handler


@pytest.fixture
def valid_event():
    return {
        "body": json.dumps({
            "gameLayout": ["ABC", "DEF", "GHI", "XYZ"],
            "boardSize": "3x3",
            "language": "en"
        })
    }


@patch("lambdas.create_custom.handler.add_game_to_db")
@patch("lambdas.create_custom.handler.create_game_schema")
def test_valid_custom_game(
    mock_create_game_schema,
    mock_add_game_to_db,
    valid_event,
):
    # Arrange
    mock_create_game_schema.return_value = {
        "gameId": "test-game-id",
        "gameLayout": ["ABC", "DEF", "GHI", "XYZ"],
        "standardizedHash": "standardized-hash",
        "twoWordSolutions": [("WORD1", "WORD2")],
        "threeWordSolutions": [("WORD3", "WORD4", "WORD5")],
        "validWords": ["WORD1", "WORD2", "WORD3", "WORD4", "WORD5"],
        "baseValidWords": ["WORD1", "WORD2", "WORD3", "WORD4", "WORD5"],
    }

    # Act
    response = handler(valid_event, {})

    # Assert
    assert response["statusCode"] == 200
    assert "test-game-id" in response["body"]
    mock_add_game_to_db.assert_called_once()



def test_invalid_game_layout():
    # Arrange
    event = {"body": json.dumps({"boardSize": "3x3", "language": "en"})}

    # Act
    response = handler(event, {})

    # Assert
    assert response["statusCode"] == 400
    assert "Game Layout is required" in response["body"]
