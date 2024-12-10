import pytest
import random
from unittest.mock import patch
from typing import List, Dict, Any
from lambdas.validate_word.word_validator_service import (
    find_valid_word_from_normalized, 
    handle_post_game_logic
)


@pytest.mark.parametrize("submitted_word, valid_words, expected", [
    ("apple", ["apple", "banana", "cherry"], "apple"),  # Exact match
    ("apple", ["àpple", "banana", "cherry"], "àpple"),  # Accent matching
    ("pear", ["apple", "banana", "cherry"], None),      # Word not in valid words
    ("", ["apple", "banana", "cherry"], None),          # Empty input
    ("banana", [], None),                               # Empty valid words list
])
def test_find_valid_word_from_normalized(submitted_word: str, valid_words: List[str], expected: str):
    # Call the actual implementation without mocking normalize_to_base
    result = find_valid_word_from_normalized(submitted_word, valid_words)
    assert result == expected


def test_handle_post_game_logic():
    random.seed(0) # For consistent random logic
    game_data = {
        "gameId": "test-game-id",
        "nytSolution": ["nyt1", "nyt2"],
        "randomSeedWord": "random_word",
        "randomSeedWords": ["seed1", "seed2"],
        "oneWordSolutions": ["one1", "one2", "one3", "one4", "one5", "one6"],
        "twoWordSolutions": [["two1a", "two1b"], ["two2a", "two2b"], ["two3a", "two3b"]],
        "totalCompletions": 10,
        "totalWordsUsed": 50,
        "totalLettersUsed": 300,
        "totalRatings": 5,
        "totalStars": 25,
    }
    words_used = ["test1", "test2"]

    result = handle_post_game_logic(game_data, words_used)
    print("Result:", result)

    assert result["officialSolution"] == ["nyt1", "nyt2"]  # NYT solution takes priority
    assert result["someOneWordSolutions"] == ['one4', 'one6', 'one1', 'one2', 'one3']  # Sampled solutions
    assert result["someTwoWordSolutions"] == [('two2a', 'two2b'), ('two3a', 'two3b'), ('two1a', 'two1b')]  # Sampled two-word solutions
    assert result["averageRating"] == 5.0  # Total stars / total ratings
    assert result["averageWordsUsed"] == (50 + 2) / 11  # Updated totalWordsUsed / updated totalCompletions
    assert result["averageWordLength"] == (300 + len("test1") + len("test2")) / (50 + 2)
