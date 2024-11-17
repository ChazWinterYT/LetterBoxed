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
    dictionary = ["PARDONS", "BAD", "DAPHNIA", "DAAPHNIA", "AAAA", "SNAPDRAGON", "PHONIATRISTS", "SONANTI"]
    game_layout = ["PRO","CTI","DGN","SAH"]
    valid_words = generate_valid_words(dictionary, game_layout)
    assert valid_words == ["PARDONS", "DAPHNIA", "SNAPDRAGON", "PHONIATRISTS"]
