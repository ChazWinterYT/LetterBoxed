import pytest
import decimal
from lambdas.common.validation_utils import (
    validate_game_schema,
    convert_decimal,
    validate_board_size,
    validate_language,
    validate_board_matches_layout,
)


def test_validate_game_schema_with_missing_fields():
    game_item = {"gameId": "1234"}
    validated = validate_game_schema(game_item)

    assert validated["gameId"] == "1234"
    assert validated["gameLayout"] == []
    assert validated["officialGame"] is False
    assert validated["oneWordSolutions"] == []


def test_validate_game_schema_with_decimal_fields():
    game_item = {
        "validWordCount": decimal.Decimal("10.0"),
        "oneWordSolutionCount": decimal.Decimal("2"),
    }
    validated = validate_game_schema(game_item)

    assert validated["validWordCount"] == 10  # Converted to int
    assert validated["oneWordSolutionCount"] == 2  # Converted to int


def test_validate_game_schema_nested_structure():
    game_item = {
        "randomSeedWords": [decimal.Decimal("1.0"), decimal.Decimal("2.5")],
        "dictionary": {"word1": decimal.Decimal("3"), "word2": decimal.Decimal("4.4")},
    }
    validated = validate_game_schema(game_item)

    assert validated["randomSeedWords"] == [1.0, 2.5]
    assert validated["dictionary"] == {"word1": 3, "word2": 4.4}


def test_convert_decimal_with_mixed_data():
    data = {
        "count": decimal.Decimal("5"),
        "items": [decimal.Decimal("1.2"), decimal.Decimal("3.0")],
        "nested": {"value": decimal.Decimal("7")},
    }
    converted = convert_decimal(data)

    assert converted["count"] == 5
    assert converted["items"] == [1.2, 3.0]
    assert converted["nested"]["value"] == 7


def test_validate_board_size_valid():
    assert validate_board_size("3x3") is True
    assert validate_board_size("5x5") is True
    assert validate_board_size("2x2") is True


def test_validate_board_size_invalid():
    assert validate_board_size("6x6") is False
    assert validate_board_size("abc") is False


def test_validate_language_valid():
    assert validate_language("en") is True
    assert validate_language("fr") is True


def test_validate_language_invalid():
    assert validate_language("jp") is False
    assert validate_language("xx") is False


def test_validate_board_matches_layout_valid():
    layout = ["AB", "CD", "EF", "GH"]
    board_size = "2x2"

    try:
        validate_board_matches_layout(layout, board_size)  # Should not raise
    except ValueError:
        pytest.fail("validate_board_matches_layout() raised ValueError unexpectedly!")


def test_validate_board_matches_layout_invalid():
    layout = ["ABC", "CDE", "FGH", "IJH"]
    board_size = "2x2"

    with pytest.raises(ValueError):
        validate_board_matches_layout(layout, board_size)


def test_validate_board_matches_layout_invalid_format():
    layout = ["AB", "CD", "EF", "GH"]
    board_size = "invalid_format"

    with pytest.raises(ValueError):
        validate_board_matches_layout(layout, board_size)
