from unittest.mock import patch
import pytest
from lambdas.common.game_utils import (
    standardize_board, 
    is_valid_word,
    sides_list_to_sides_set,
    generate_valid_words,
    create_letter_to_side_mapping,
    check_game_completion,
)

@pytest.fixture
def equivalent_layouts():
    # Equivalent layouts that should result in the same standardized hash
    return [
        ["CAB", "XYZ", "MNO", "JKL"],
        ["ABC", "ZXY", "NOM", "LJK"]
    ]



def test_standardize_board():
    game_layout = ["ZYX", "CAB", "FED", "IHG"]
    expected = ["ABC", "DEF", "GHI", "XYZ"]
    assert standardize_board(game_layout) == expected


def test_standardize_board_equivalence():
    board1 = ["ABC", "XYZ", "FED", "IHG"]
    board2 = ["IHG", "ZYX", "CAB", "DFE"]
    assert standardize_board(board1) == standardize_board(board2)


def test_standardize_board_invalid_board_length():
    # Test case with too few sides
    board_too_short = ["ABC", "XYZ"]  # Not enough sides
    # Test case with too many sides
    board_too_long = ["XYZ", "TUV", "PQR", "MNO", "JKL"]  # Too many sides

    # Test board with too few sides
    with pytest.raises(ValueError) as exc_info_short:
        standardize_board(board_too_short)
    assert str(exc_info_short.value) == "game_layout must have 4 sides."

    # Test board with too many sides
    with pytest.raises(ValueError) as exc_info_long:
        standardize_board(board_too_long)
    assert str(exc_info_long.value) == "game_layout must have 4 sides."


def test_standardize_board_invalid_inputs():
    # Test case where game_layout is not a list
    not_a_list = "ABCDEF"
    # Test case where sides are not strings
    sides_with_non_string = ["ABC", 123, "DEF", "GHI"]

    # Test when game_layout is not a list
    with pytest.raises(ValueError) as exc_info_not_list:
        standardize_board(not_a_list)
    assert str(exc_info_not_list.value) == "game_layout must be a list of strings."

    # Test when a side is not a string
    with pytest.raises(ValueError) as exc_info_non_string:
        standardize_board(sides_with_non_string)
    assert str(exc_info_non_string.value) == "game_layout must be a list of strings."


def test_standardize_board_empty_sides():
    empty_sides = ["ABC", "", "DEF", "GHI"]
    with pytest.raises(ValueError) as exc_info_empty_side:
        standardize_board(empty_sides)
    assert str(exc_info_empty_side.value) == "Each side in game_layout must be a non-empty string."


def test_standardize_board_invalid_characters():
    invalid_chars = ["AB1", "CDE", "FGH", "IJK"]
    with pytest.raises(ValueError) as exc_info_invalid_chars:
        standardize_board(invalid_chars)
    assert str(exc_info_invalid_chars.value) == "Sides must contain only alphabetic characters."


def test_standardize_board_sides_not_equal_length():
    board = ["ABC", "DEF", "GHIJ", "KLM"]
    with pytest.raises(ValueError) as exc_info:
        standardize_board(board)
    assert str(exc_info.value) == "All sides must have the same number of letters."


def test_is_valid_word():
    game_layout = ["PRO","CTI","DGN","SAH"]
    letter_to_side = create_letter_to_side_mapping(game_layout)
    all_letters = set(letter_to_side.keys())
    assert is_valid_word("PIANIST", letter_to_side, all_letters) == True
    assert is_valid_word("HOGO", letter_to_side, all_letters) == True
    assert is_valid_word("TRAGACANTHIN", letter_to_side, all_letters) == True
    assert is_valid_word("TRAGACANTHIC", letter_to_side, all_letters) == False
    assert is_valid_word("PP", letter_to_side, all_letters) == False
    assert is_valid_word("CD", letter_to_side, all_letters) == False
    assert is_valid_word("PROC", letter_to_side, all_letters) == False


def test_generate_valid_words():
    dictionary = ["PARDONS", "BAD", "DAPHNIA", "DAAPHNIA", "AAAA", "SO", "SNAPDRAGON", "PHONIATRISTS", "SONANTI"]
    game_layout = ["PRO", "CTI", "DGN", "SAH"]

    # Mock the get_cached_dictionary function in the lambdas.common.game_utils module
    with patch('lambdas.common.dictionary_utils._load_dictionary', return_value=dictionary):
        valid_words = generate_valid_words(game_layout, "en")
        assert valid_words == ["PARDONS", "DAPHNIA", "SNAPDRAGON", "PHONIATRISTS"]


def test_check_game_completion_success():
    # Arrange
    game_layout = ["PRO", "CTI", "DGN", "SAH"]
    words_used = ["CHINSTRAP", "PAGODA"]  # Assume these words use all letters

    # Act
    game_completed, message = check_game_completion(game_layout, words_used)

    # Assert
    assert game_completed is True
    assert message == "Puzzle solved successfully! Congrats!"
    
    
def test_check_game_completion_incomplete():
    # Arrange
    game_layout = ["PRO", "CTI", "DGN", "SAH"]
    words_used = ["CHINSTRAP"]  # Only one word used

    # Act
    game_completed, message = check_game_completion(game_layout, words_used)

    # Assert
    assert game_completed is False
    assert message == "Word accepted."


def test_check_game_completion_no_words_used():
    # Arrange
    game_layout = ["PRO", "CTI", "DGN", "SAH"]
    words_used = []

    # Act
    game_completed, message = check_game_completion(game_layout, words_used)

    # Assert
    assert game_completed is False
    assert message == "Word accepted."
