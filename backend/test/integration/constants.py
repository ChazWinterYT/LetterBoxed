# Dictionary Data
EN_DICTIONARY_1 = "PARDONS\nBAD\nDAPHNIA\nAAAA\nSO\nSNAPDRAGON\nPHONIATRISTS\nSONANTI"
EN_DICTIONARY_2 = "ANOTHER\nTEST\nDICTIONARY\nWITH\nWORDS\nFOR\nVALIDATION"
EN_DICTIONARY_EMPTY = ""  # For testing empty dictionaries

# Valid Game Layouts
VALID_LAYOUT_1 = ["PRO", "CTI", "DGN", "SAH"]  # Standard 3x3 layout
VALID_LAYOUT_2 = ["MUX", "LRT", "DEB", "AFI"]  # Another valid 3x3 layout

# Equivalent Layouts (Should produce the same standardized hash)
EQUIVALENT_LAYOUT_1 = ["SAH", "TIC", "ROP", "NGD"]
EQUIVALENT_LAYOUT_2 = ["AIF", "XUM", "TRL", "EBD"]

# Invalid Game Layouts
INVALID_LAYOUT_TOO_FEW_SIDES = ["ABC", "DEF"]  # Fewer than required sides
INVALID_LAYOUT_TOO_MANY_SIDES = ["ABC", "DEF", "GHI", "XYZ", "JKL"]  # More than required sides
INVALID_LAYOUT_DUPLICATE_LETTERS = ["AAA", "AAA", "AAA", "AAA"]  # Repeated letters on all sides

# Test Words for Validation
VALID_WORD_1 = "PARDONS"
VALID_WORD_2 = "PHONIATRISTS"
VALID_WORD_CONNECT_TO_PREVIOUS_WORD = "SNAPDRAGON"
VALID_WORD_DOES_NOT_CONNECT_TO_PREVIOUS_WORD = "DAPHNIA"
INVALID_WORD_NOT_IN_PUZZLE = "BAD"
INVALID_WORD_TOO_SHORT = "AA"  # Too short to be valid
INVALID_WORD_NOT_IN_DICTIONARY = "INVALID"  # Not in the dictionary
INVALID_WORD_SAME_SIDE = "AAAA"  # Repeats letters from the same side

# Game ID and Hashes
VALID_GAME_ID = "test-game-id"
VALID_STANDARDIZED_HASH = "valid-standardized-hash"
EQUIVALENT_GAME_ID = "equivalent-game-id"

# Event Payloads
CREATE_CUSTOM_GAME_PAYLOAD = {
    "body": {
        "gameLayout": VALID_LAYOUT_1,
        "boardSize": "3x3",
        "language": "en",
    }
}

EQUIVALENT_CUSTOM_GAME_PAYLOAD = {
    "body": {
        "gameLayout": EQUIVALENT_LAYOUT_1,
        "boardSize": "3x3",
        "language": "en",
    }
}

INVALID_CUSTOM_GAME_PAYLOAD = {
    "body": {
        "gameLayout": INVALID_LAYOUT_TOO_FEW_SIDES,
        "boardSize": "3x3",
        "language": "en",
    }
}

# Validation Payloads
VALIDATE_WORD_PAYLOAD_VALID = {
    "body": {
        "gameId": "example-game-id",
        "word": "example-word",
        "sessionId": "example-session-id"
    }
}

VALIDATE_WORD_PAYLOAD_INVALID = {
    "body": {
        "word": INVALID_WORD_NOT_IN_DICTIONARY,
        "gameLayout": VALID_LAYOUT_1,
    }
}

# S3 Keys
VALID_DICTIONARY_KEY = "Dictionaries/en/dictionary.txt"
INVALID_DICTIONARY_KEY = "Dictionaries/invalid/dictionary.txt"

# Miscellaneous
DEFAULT_LANGUAGE = "en"
INVALID_LANGUAGE = "xx"  # Nonexistent language
