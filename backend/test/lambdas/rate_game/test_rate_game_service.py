import pytest
from unittest.mock import patch, MagicMock
from lambdas.rate_game.rate_game_service import rate_game

# Mock functions
@patch("lambdas.rate_game.rate_game_service.update_game_schema")
@patch("lambdas.rate_game.rate_game_service.update_game_in_db")
def test_rate_game_success(mock_update_game_in_db, mock_update_game_schema):
    """
    Test the success case for rate_game.
    """
    # Arrange
    mock_update_game_in_db.return_value = True
    mock_update_game_schema.return_value = {
        "gameId": "123",
        "totalStars": 15,
        "totalRatings": 5
    }
    
    game = {
        "gameId": "123",
        "totalStars": 10,
        "totalRatings": 4
    }
    stars = 5

    # Act
    result = rate_game(game, stars)

    # Assert
    assert result is True
    mock_update_game_schema.assert_called_once_with(
        game,
        updates={
            "totalRatings": 5,
            "totalStars": 15
        },
    )
    mock_update_game_in_db.assert_called_once_with({
        "gameId": "123",
        "totalStars": 15,
        "totalRatings": 5
    })


@patch("lambdas.rate_game.rate_game_service.update_game_schema")
@patch("lambdas.rate_game.rate_game_service.update_game_in_db")
def test_rate_game_failure_update_db(mock_update_game_in_db, mock_update_game_schema):
    """
    Test the failure case when update_game_in_db fails.
    """
    # Arrange
    mock_update_game_in_db.return_value = False
    mock_update_game_schema.return_value = {
        "gameId": "123",
        "totalStars": 15,
        "totalRatings": 5
    }
    
    game = {
        "gameId": "123",
        "totalStars": 10,
        "totalRatings": 4
    }
    stars = 5

    # Act
    result = rate_game(game, stars)

    # Assert
    assert result is False
    mock_update_game_schema.assert_called_once()
    mock_update_game_in_db.assert_called_once()


@patch("lambdas.rate_game.rate_game_service.update_game_schema")
@patch("lambdas.rate_game.rate_game_service.update_game_in_db")
def test_rate_game_missing_game_id(mock_update_game_in_db, mock_update_game_schema):
    """
    Test the case where the game object is missing a gameId.
    """
    # Arrange
    mock_update_game_in_db.return_value = True
    mock_update_game_schema.side_effect = ValueError("gameId is required in the game schema.")
    game = {
        "totalStars": 10,
        "totalRatings": 4
    }
    stars = 5

    # Act
    result = rate_game(game, stars)

    # Assert
    assert result is False
    mock_update_game_schema.assert_called_once_with(game, updates={"totalRatings": 5, "totalStars": 15})
    mock_update_game_in_db.assert_not_called()


@patch("lambdas.rate_game.rate_game_service.update_game_schema")
@patch("lambdas.rate_game.rate_game_service.update_game_in_db")
def test_rate_game_error_handling(mock_update_game_in_db, mock_update_game_schema):
    """
    Test error handling when an exception is raised.
    """
    # Arrange
    mock_update_game_schema.side_effect = Exception("Unexpected error")

    game = {
        "gameId": "123",
        "totalStars": 10,
        "totalRatings": 4
    }
    stars = 5

    # Act
    result = rate_game(game, stars)

    # Assert
    assert result is False
    mock_update_game_schema.assert_called_once()
    mock_update_game_in_db.assert_not_called()
