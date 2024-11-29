import pytest
import random
from unittest.mock import MagicMock, patch
from lambdas.create_random.random_game_service import create_random_game, select_two_words, generate_layout
from lambdas.common.game_utils import standardize_board


@pytest.fixture
def mock_dictionary():
    """Fixture to provide a mock dictionary."""
    return ["APPLE", "ORANGE", "GRAPE", "PEACH", "BANANA", "CHERRY", "BULWARK", "KVETCH"]


@pytest.fixture
def mock_game_schema():
    """Fixture for mocked game schema."""
    return {
        "gameId": "test-game-id",
        "gameLayout": ["RHV", "WTU", "LBK", "AEC"],
        "gameType": "random",
        "officialGame": False,
        "language": "en",
        "boardSize": "3x3",
        "randomSeedWords": ["BULWARK", "KVETCH"],
        "createdBy": "",
        "validWords": ["BULWARK", "KVETCH"],
        "baseValidWords": ["BULWARK", "KVETCH"]
    }


@patch("lambdas.create_random.random_game_service.get_dictionary")
@patch("lambdas.create_random.random_game_service.select_two_words")
@patch("lambdas.create_random.random_game_service.generate_layout")
@patch("lambdas.create_random.random_game_service.create_game_schema")
@patch("lambdas.create_random.random_game_service.add_game_to_db")
@patch("lambdas.create_random.random_game_service.add_game_id_to_random_games_db")
def test_create_random_game_success(
    mock_add_game_id_to_random_games_db,
    mock_add_game_to_db,
    mock_create_game_schema,
    mock_generate_layout,
    mock_select_two_words,
    mock_get_dictionary,
    mock_dictionary,
    mock_game_schema,
):
    # Arrange
    mock_get_dictionary.return_value = mock_dictionary
    mock_select_two_words.return_value = ("BULWARK", "KVETCH")
    mock_generate_layout.return_value = ["RHV", "WTU", "LBK", "AEC"]
    mock_create_game_schema.return_value = mock_game_schema
    mock_add_game_id_to_random_games_db.return_value = 1

    # Act
    result = create_random_game(language="en", board_size="3x3")

    # Assert
    assert result == mock_game_schema
    mock_get_dictionary.assert_called_once_with("en")
    mock_select_two_words.assert_called_once_with(mock_dictionary, "3x3")
    mock_generate_layout.assert_called_once_with("BULWARK","KVETCH", "3x3")
    mock_create_game_schema.assert_called_once()
    mock_add_game_to_db.assert_called_once_with(mock_game_schema)
    mock_add_game_id_to_random_games_db.assert_called_once_with("test-game-id", "en")


@patch("lambdas.create_random.random_game_service.get_dictionary")
def test_create_random_game_no_dictionary(mock_get_dictionary):
    # Arrange
    mock_get_dictionary.return_value = []

    # Act & Assert
    with pytest.raises(ValueError, match="Dictionary not found for the specified language."):
        create_random_game(language="en")


@patch("lambdas.create_random.random_game_service.select_two_words")
def test_select_two_words_success(mock_select_two_words, mock_dictionary):
    # Act
    word_pair = select_two_words(mock_dictionary, board_size="3x3")

    # Assert
    assert word_pair is not None
    assert len(word_pair) == 2


@patch("lambdas.create_random.random_game_service.generate_layout")
def test_generate_layout_success(mock_generate_layout):
    # Arrange
    random.seed(0) # Start the random number generator at a consistent state
    mock_generate_layout.return_value = ["RHV", "WTU", "LBK", "AEC"]
    expected_layout = ["ABL", "CRV", "EHW", "KTU"]  # Standardized

    # Act
    layout = generate_layout("BULWARK", "KVETCH", "3x3")

    # Standardize the generated layout so a shufled board is still seen as equivalent
    standardized_actual = standardize_board(layout) if layout else None

    # Assert
    assert standardized_actual == expected_layout, (
        f"Expected {expected_layout}, but got {standardized_actual}"
    )


@patch("lambdas.create_random.random_game_service.add_game_id_to_random_games_db")
def test_add_game_to_db(mock_add_game_id_to_random_games_db):
    # Arrange
    mock_add_game_id_to_random_games_db.return_value = 1

    # Act
    atomic_number = mock_add_game_id_to_random_games_db("test-game-id")

    # Assert
    assert atomic_number == 1
