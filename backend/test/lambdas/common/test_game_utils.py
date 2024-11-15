import pytest
from lambdas.common.game_utils import standardize_board, generate_standardized_hash

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