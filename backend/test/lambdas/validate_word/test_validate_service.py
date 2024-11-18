import pytest
from unittest.mock import MagicMock, patch
from lambdas.validate_word.validate_service import (
    validate_submitted_word,
    check_word_validity,
    get_user_game_state,
    save_session_state,
    check_game_completion,
)


@pytest.fixture
def mock_dynamodb_tables(mocker):
    # Create mock tables
    mock_valid_words_table = MagicMock()
    mock_session_states_table = MagicMock()
    mock_games_table = MagicMock()

    # Patch the DynamoDB tables in validate_service
    mocker.patch('lambdas.validate_word.validate_service.valid_words_table', mock_valid_words_table)
    mocker.patch('lambdas.validate_word.validate_service.session_states_table', mock_session_states_table)
    mocker.patch('lambdas.validate_word.validate_service.games_table', mock_games_table)

    return mock_valid_words_table, mock_session_states_table, mock_games_table


def test_validate_valid_word(mock_dynamodb_tables):
    mock_valid_words_table, mock_session_states_table, mock_games_table = mock_dynamodb_tables

    # Arrange
    game_id = "game123"
    submitted_word = "APPLE"
    session_id = "session1"

    # Mock check_word_validity to return True
    mock_valid_words_table.get_item.return_value = {'Item': {'word': submitted_word}}

    # Mock get_user_game_state to return an empty wordsUsed list
    mock_session_states_table.get_item.return_value = {'Item': {'sessionId': session_id, 'gameId': game_id, 'wordsUsed': []}}

    # Mock save_session_state to do nothing
    mock_session_states_table.put_item.return_value = {}

    # Mock check_game_completion to return game not completed
    mock_games_table.get_item.return_value = {'Item': {'gameId': game_id, 'gameLayout': ['A', 'B', 'C', 'D']}}

    # Act
    result = validate_submitted_word(game_id, submitted_word, session_id)

    # Assert
    assert result['valid'] == True
    assert result['message'] == 'Word accepted.'
    assert result['game_completed'] == False
    assert result['words_used'] == [submitted_word]


def test_validate_invalid_word(mock_dynamodb_tables):
    mock_valid_words_table, _, _ = mock_dynamodb_tables

    # Arrange
    game_id = "game123"
    submitted_word = "INVALID"
    session_id = "session1"

    # Mock check_word_validity to return False
    mock_valid_words_table.get_item.return_value = {}

    # Act
    result = validate_submitted_word(game_id, submitted_word, session_id)

    # Assert
    assert result['valid'] == False
    assert result['message'] == 'Word is not valid for this puzzle.'


def test_word_already_used(mock_dynamodb_tables):
    mock_valid_words_table, mock_session_states_table, _ = mock_dynamodb_tables

    # Arrange
    game_id = "game123"
    submitted_word = "APPLE"
    session_id = "session1"

    # Mock valid_words_table to treat APPLE as a valid word
    mock_valid_words_table.get_item.return_value = {'Item': {'word': submitted_word}}

    # Mock get_user_game_state to return wordsUsed with the submitted word
    mock_session_states_table.get_item.return_value = {
        'Item': {
            'sessionId': session_id,
            'gameId': game_id,
            'wordsUsed': [submitted_word]
        }
    }

    # Act
    result = validate_submitted_word(game_id, submitted_word, session_id)

    # Assert
    assert result['valid'] == False
    assert result['message'] == 'Word has already been used.'


def test_incorrect_starting_letter(mock_dynamodb_tables):
    mock_valid_words_table, mock_session_states_table, _ = mock_dynamodb_tables

    # Arrange
    game_id = "game123"
    submitted_word = "TIGER"
    session_id = "session1"
    previous_word = "APPLE"

    # Mock valid_words_table to treat TIGER as a valid word
    mock_valid_words_table.get_item.return_value = {'Item': {'word': submitted_word}}

    # Mock get_user_game_state to return wordsUsed with a previous word
    mock_session_states_table.get_item.return_value = {
        'Item': {
            'sessionId': session_id,
            'gameId': game_id,
            'wordsUsed': [previous_word]
        }
    }

    # Act
    result = validate_submitted_word(game_id, submitted_word, session_id)

    # Assert
    assert result['valid'] == False
    assert result['message'] == 'Word must start with the last letter of the previous word.'


def test_correct_starting_letter(mock_dynamodb_tables):
    mock_valid_words_table, mock_session_states_table, _ = mock_dynamodb_tables

    # Arrange
    game_id = "game123"
    submitted_word = "ELEPHANT"
    session_id = "session1"
    previous_word = "APPLE"

    # Mock check_word_validity to return True
    mock_valid_words_table.get_item.return_value = {'Item': {'word': submitted_word}}

    # Mock get_user_game_state to return wordsUsed with a previous word
    mock_session_states_table.get_item.return_value = {
        'Item': {
            'sessionId': session_id,
            'gameId': game_id,
            'wordsUsed': [previous_word]
        }
    }

    # Act
    result = validate_submitted_word(game_id, submitted_word, session_id)

    # Assert
    assert result['valid'] == True
    assert result['message'] == 'Word accepted.'
    assert result['game_completed'] == False
    assert result['words_used'] == [previous_word, submitted_word]


def test_game_completion(mock_dynamodb_tables):
    mock_valid_words_table, mock_session_states_table, mock_games_table = mock_dynamodb_tables

    # Arrange
    game_id = "game123"
    submitted_word = "ELEPHANT"
    session_id = "session1"
    previous_word = "APPLE"

    # Mock check_word_validity to return True
    mock_valid_words_table.get_item.return_value = {'Item': {'word': submitted_word}}

    # Mock get_user_game_state to return wordsUsed with a previous word
    words_used = [previous_word]
    mock_session_states_table.get_item.return_value = {
        'Item': {
            'sessionId': session_id,
            'gameId': game_id,
            'wordsUsed': words_used
        }
    }

    # Mock save_session_state to do nothing
    mock_session_states_table.put_item.return_value = {}

    # Mock game layout to include letters used in words
    mock_games_table.get_item.return_value = {
        'Item': {
            'gameId': game_id,
            'gameLayout': ['A', 'E', 'L', 'P', 'H', 'N', 'T']
        }
    }

    # Act
    result = validate_submitted_word(game_id, submitted_word, session_id)

    # Assert
    assert result['valid'] == True
    assert result['message'] == 'Puzzle successfully solved! Congrats!'
    assert result['game_completed'] == True
    assert result['words_used'] == [previous_word, submitted_word]


def test_exception_handling(mock_dynamodb_tables):
    mock_valid_words_table, _, _ = mock_dynamodb_tables

    # Arrange
    game_id = "game123"
    submitted_word = "APPLE"
    session_id = "session1"

    # Mock check_word_validity to raise an exception
    mock_valid_words_table.get_item.side_effect = Exception('DynamoDB error')

    # Act
    result = validate_submitted_word(game_id, submitted_word, session_id)

    # Assert
    assert result['valid'] == False
    assert result['message'] == 'Word is not valid for this puzzle.'
