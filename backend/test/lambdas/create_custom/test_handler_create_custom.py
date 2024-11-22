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
@patch("lambdas.create_custom.handler.fetch_solutions_by_standardized_hash")
@patch("lambdas.create_custom.handler.create_game_schema")
def test_valid_custom_game(
    mock_create_game_schema,
    mock_fetch_solutions_by_standardized_hash,
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
    }
    mock_fetch_solutions_by_standardized_hash.return_value = None  # No equivalent game

    # Act
    response = handler(valid_event, {})

    # Assert
    assert response["statusCode"] == 200
    assert "New solution generated" in response["body"]
    mock_add_game_to_db.assert_called_once()


@patch("lambdas.create_custom.handler.add_game_to_db")
@patch("lambdas.create_custom.handler.fetch_solutions_by_standardized_hash")
@patch("lambdas.create_custom.handler.create_game_schema")
def test_custom_game_with_equivalent_solution(
    mock_create_game_schema,
    mock_fetch_solutions_by_standardized_hash,
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
    }
    mock_fetch_solutions_by_standardized_hash.return_value = {
        "twoWordSolutions": ["WORD1", "WORD2"],
        "threeWordSolutions": ["WORD3", "WORD4"]
    }

    # Act
    response = handler(valid_event, {})
    print(response)

    # Assert
    assert response["statusCode"] == 200
    assert "using existing solution" in response["body"]
    mock_add_game_to_db.assert_called_once()


def test_invalid_game_layout():
    # Arrange
    event = {"body": json.dumps({"boardSize": "3x3", "language": "en"})}

    # Act
    response = handler(event, {})

    # Assert
    assert response["statusCode"] == 400
    assert "Game Layout is required" in response["body"]
