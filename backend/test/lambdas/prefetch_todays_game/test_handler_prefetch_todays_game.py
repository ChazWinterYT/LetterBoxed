import pytest
from unittest.mock import patch
from lambdas.prefetch_todays_game.handler import handler


@patch("lambdas.prefetch_todays_game.prefetch_service.fetch_todays_game")
@patch("lambdas.prefetch_todays_game.handler.fetch_game_by_id")
@patch("lambdas.prefetch_todays_game.handler.add_game_to_db")
@patch("lambdas.prefetch_todays_game.handler.generate_standardized_hash")
@patch("lambdas.prefetch_todays_game.handler.standardize_board")
def test_prefetch_todays_game_handler_game_cached(
    mock_standardize_board,
    mock_generate_standardized_hash,
    mock_add_game_to_db,
    mock_fetch_game_by_id,
    mock_fetch_todays_game
):
    # Arrange
    mock_fetch_todays_game.return_value = {
        "gameId": "2024-11-16",
        "sides": ["ABC", "DEF", "GHI", "XYZ"],
        "nytSolution": ["WORD1", "WORD2"],
        "dictionary": ["WORD1", "WORD2", "WORD3"],
        "par": 4
    }
    mock_fetch_game_by_id.return_value = {"gameId": "2024-11-16"}

    # Act
    response = handler({}, {})

    # Assert
    assert response["statusCode"] == 200
    assert "already cached" in response["body"]
    mock_add_game_to_db.assert_not_called()


@patch("lambdas.prefetch_todays_game.prefetch_service.fetch_todays_game")
@patch("lambdas.prefetch_todays_game.handler.fetch_game_by_id")
@patch("lambdas.prefetch_todays_game.handler.add_game_to_db")
@patch("lambdas.prefetch_todays_game.handler.generate_standardized_hash")
@patch("lambdas.prefetch_todays_game.handler.standardize_board")
def test_prefetch_todays_game_handler_game_not_cached(
    mock_standardize_board,
    mock_generate_standardized_hash,
    mock_add_game_to_db,
    mock_fetch_game_by_id,
    mock_fetch_todays_game
):
    # Arrange
    mock_fetch_todays_game.return_value = {
        "gameId": "2024-11-16",
        "sides": ["ABC", "DEF", "GHI", "XYZ"],
        "nytSolution": ["WORD1", "WORD2"],
        "dictionary": ["WORD1", "WORD2", "WORD3"],
        "par": 4
    }
    mock_standardize_board.return_value = ["A", "B", "C", "D"]
    mock_generate_standardized_hash.return_value = "standardized-hash"
    mock_fetch_game_by_id.return_value = None

    # Act
    response = handler({}, {})

    # Assert
    assert response["statusCode"] == 201
    assert "cached successfully" in response["body"]
    mock_add_game_to_db.assert_called_once()
