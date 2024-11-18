import pytest
from lambdas.common.game_utils import (
    standardize_board, 
    generate_standardized_hash,
    is_valid_word,
    sides_list_to_sides_set,
    generate_valid_words,
)

@pytest.fixture
def equivalent_layouts():
    # Equivalent layouts that should result in the same standardized hash
    return [
        ["CAB", "XYZ", "MNO", "JKL"],
        ["ABC", "ZXY", "NOM", "LJK"]
    ]

@pytest.mark.parametrize("layout", [
    ["CAB", "XYZ", "MNO", "JKL"],
    ["ABC", "ZXY", "NOM", "LJK"]
])
def test_generate_standardized_hash(equivalent_layouts, layout):
    # Standardize and hash the layout
    standardized_layout = standardize_board(layout)
    result_hash = generate_standardized_hash(standardized_layout)
    
    # Check if all equivalent layouts produce the same hash
    for eq_layout in equivalent_layouts:
        standardized_eq_layout = standardize_board(eq_layout)
        equivalent_hash = generate_standardized_hash(standardized_eq_layout)
        assert result_hash == equivalent_hash


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
    assert is_valid_word("PIANIST", game_layout) == True
    assert is_valid_word("HOGO", game_layout) == True
    assert is_valid_word("TRAGACANTHIN", game_layout) == True
    assert is_valid_word("TRAGACANTHIC", game_layout) == False
    assert is_valid_word("PP", game_layout) == False
    assert is_valid_word("CD", game_layout) == False
    assert is_valid_word("PROC", game_layout) == False


def test_generate_valid_words():
    dictionary = ["PARDONS", "BAD", "DAPHNIA", "DAAPHNIA", "AAAA", "SO", "SNAPDRAGON", "PHONIATRISTS", "SONANTI"]
    game_layout = ["PRO","CTI","DGN","SAH"]
    valid_words = generate_valid_words(dictionary, game_layout)
    assert valid_words == ["PARDONS", "DAPHNIA", "SNAPDRAGON", "PHONIATRISTS"]
