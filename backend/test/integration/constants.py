import json

# This game layout should yield the solution ["VAPORIZE", "ELEMENT"]
VALID_GAME_LAYOUT_EN = ["VZL", "PMI", "ONA", "ERT"]

# This gamy layout should yield the solution ["ALIANZA", "AUTOMOVILES"]
VALID_GAME_LAYOUT_ES = ['SOA', 'EVN', 'ITM', 'ZLU']

# This game layout should yield the solution ["CLAUSTROPHOBE", "ELIMINATED"]
VALID_GAME_LAYOUT_4x4_EN = ["AERP", "OLSN", "BITC", "HUDM"]

# This game layout should yield the solution ["IMPLEMENTABLE", "ESCUCHADOR"]
VALID_GAME_LAYOUT_4x4_ES = ["AERP", "DLSN", "BITC", "HUOM"]

# Valid event with a 3x3 layout in English
CREATE_CUSTOM_EVENT_VALID_EN = {
    "body": json.dumps({
        "gameLayout": VALID_GAME_LAYOUT_EN,
        "sessionId": "test-session-id-en",
        "language": "en",
        "boardSize": "3x3"
    }),
    "headers": {
        "Content-Type": "application/json"
    }
}

# Valid event with a 3x3 layout in Spanish
CREATE_CUSTOM_EVENT_VALID_ES = {
    "body": json.dumps({
        "gameLayout": VALID_GAME_LAYOUT_ES,
        "sessionId": "test-session-id-es",
        "language": "es",
        "boardSize": "3x3"
    }),
    "headers": {
        "Content-Type": "application/json"
    }
}

# Valid event with a larger layout (4x4). I have no idea if this will work lol
CREATE_CUSTOM_EVENT_VALID_LARGE_EN = {
    "body": json.dumps({
        "gameLayout": VALID_GAME_LAYOUT_4x4_EN, 
        "sessionId": "test-session-id-large",
        "language": "en",
        "boardSize": "4x4"
    }),
    "headers": {
        "Content-Type": "application/json"
    }
}
CREATE_CUSTOM_EVENT_VALID_LARGE_ES = {
    "body": json.dumps({
        "gameLayout": VALID_GAME_LAYOUT_4x4_ES, 
        "sessionId": "test-session-id-large",
        "language": "es",
        "boardSize": "4x4"
    }),
    "headers": {
        "Content-Type": "application/json"
    }
}

# Invalid event: Missing game layout
CREATE_CUSTOM_EVENT_MISSING_LAYOUT = {
    "body": json.dumps({
        "sessionId": "test-session-id",
        "language": "en",
        "boardSize": "3x3"
    }),
    "headers": {
        "Content-Type": "application/json"
    }
}

CREATE_CUSTOM_EVENT_INVALID_LAYOUT = {
    "body": json.dumps({
        "gameLayout": ["ABC", "DEFG", "HI", "JKL"],  # Inconsistent row lengths
        "sessionId": "test-session-id-invalid-layout",
        "language": "en",
        "boardSize": "3x3"
    }),
    "headers": {
        "Content-Type": "application/json"
    }
}

CREATE_CUSTOM_EVENT_SIZE_MISMATCH = {
    "body": json.dumps({
        "gameLayout": ["ABC", "DEF", "GHI", "JKL"],  # 3x3 board
        "sessionId": "test-session-id-size-mismatch",
        "language": "en",
        "boardSize": "4x4" # 4x4 board specified in payload
    }),
    "headers": {
        "Content-Type": "application/json"
    }
}

# Invalid event: Unsupported language
CREATE_CUSTOM_EVENT_UNSUPPORTED_LANGUAGE = {
    "body": json.dumps({
        "gameLayout": ['MSU', 'ZIA', 'RNC', 'EOT'],
        "sessionId": "test-session-id-unsupported",
        "language": "xy",  # xy is not a language, it's a boy
        "boardSize": "3x3"
    }),
    "headers": {
        "Content-Type": "application/json"
    }
}

# Invalid event: Malformed JSON
CREATE_CUSTOM_EVENT_MALFORMED_JSON = {
    "body": "{gameLayout: ['ABC', 'DEF', 'GHI', 'JKL']",  # Missing closing brace
    "headers": {
        "Content-Type": "application/json"
    }
}


# ===================================================================
# Constants for Event Payloads
# ===================================================================

# Valid event: English game, 3x3 board, no seed words
CREATE_RANDOM_EVENT_VALID_EN = {
    "body": json.dumps({
        "language": "en",
        "boardSize": "3x3"
    }),
    "headers": {
        "Content-Type": "application/json"
    }
}

# Valid event: Spanish game, 3x3 board, no seed words
CREATE_RANDOM_EVENT_VALID_ES = {
    "body": json.dumps({
        "language": "es",
        "boardSize": "3x3"
    }),
    "headers": {
        "Content-Type": "application/json"
    }
}

# Valid event: English game, 3x3 board, with seed words
CREATE_RANDOM_EVENT_VALID_SEED_WORDS_EN = {
    "body": json.dumps({
        "language": "en",
        "boardSize": "3x3",
        "seedWords": ["VAPORIZE", "ELEMENT"]
    }),
    "headers": {
        "Content-Type": "application/json"
    }
}

# Valid event: Spanish game, 3x3 board, with seed words
CREATE_RANDOM_EVENT_VALID_SEED_WORDS_ES = {
    "body": json.dumps({
        "language": "es",
        "boardSize": "3x3",
        "seedWords": ["ÚNICAMENTE", "ELECTRICOS"]
    }),
    "headers": {
        "Content-Type": "application/json"
    }
}

# Valid event: English game, 4x4 board, with seed words
CREATE_RANDOM_EVENT_VALID_4X4_WITH_SEED_EN = {
    "body": json.dumps({
        "language": "en",
        "boardSize": "4x4",
        "seedWords": ["DISPLACEMENT", "THORNBUSH"]
    }),
    "headers": {
        "Content-Type": "application/json"
    }
}

# Valid event: Spanish game, 4x4 board, with seed words
CREATE_RANDOM_EVENT_VALID_4x4_WITH_SEED_ES = {
    "body": json.dumps({
        "language": "es",
        "boardSize": "4x4",
        "seedWords": ["CHABOLISTA", "AMPURDANÉS"]
    }),
    "headers": {
        "Content-Type": "application/json"
    }
}

# Invalid event: Unsupported language
CREATE_RANDOM_EVENT_UNSUPPORTED_LANGUAGE = {
    "body": json.dumps({
        "language": "xy",  # xy is not a language, it's a boy
        "boardSize": "3x3"
    }),
    "headers": {
        "Content-Type": "application/json"
    }
}

# Invalid event: Invalid board size
CREATE_RANDOM_EVENT_INVALID_BOARD_SIZE = {
    "body": json.dumps({
        "language": "en",
        "boardSize": "5x7"  # '5x7' is unsupported
    }),
    "headers": {
        "Content-Type": "application/json"
    }
}

# Invalid event: Seed words can't form a valid layout (not enough unique letters)
CREATE_RANDOM_EVENT_INVALID_SEED_WORDS = {
    "body": json.dumps({
        "language": "en",
        "boardSize": "3x3",
        "seedWords": ["INVALID", "DONUTS"]
    }),
    "headers": {
        "Content-Type": "application/json"
    }
}

# Invalid event: Malformed JSON
CREATE_RANDOM_EVENT_MALFORMED_JSON = {
    "body": '{"language": "en", "boardSize": "3x3"',  # Missing closing brace
    "headers": {
        "Content-Type": "application/json"
    }
}

# Invalid event: Missing body entirely
CREATE_RANDOM_EVENT_MISSING_BODY = {
    "body": None,
    "headers": {
        "Content-Type": "application/json"
    }
}

# ===================================================================
# Constants for Fetch Game Event Payloads
# ===================================================================

# Valid event with an existing game ID
FETCH_GAME_EVENT_VALID = lambda game_id: {
    "body": json.dumps({"gameId": game_id}),
    "headers": {
        "Content-Type": "application/json"
    }
}

# Event with a missing game ID
FETCH_GAME_EVENT_MISSING_GAME_ID = {
    "body": json.dumps({}),  # No gameId provided
    "headers": {
        "Content-Type": "application/json"
    }
}

# Event with a non-existent game ID
FETCH_GAME_EVENT_NONEXISTENT_GAME_ID = {
    "body": json.dumps({"gameId": "nonexistent-game-id"}),
    "headers": {
        "Content-Type": "application/json"
    }
}

# Event with invalid JSON payload
FETCH_GAME_EVENT_INVALID_JSON = {
    "body": '{"gameId": "missing-quote}',  # Malformed JSON
    "headers": {
        "Content-Type": "application/json"
    }
}

# Event with a valid game ID but no optional fields
FETCH_GAME_EVENT_OPTIONAL_FIELDS_DEFAULT = lambda game_id: {
    "body": json.dumps({"gameId": game_id}),
    "headers": {
        "Content-Type": "application/json"
    }
}

# ===================================================================
# Constants for Save User State Event Payloads
# ===================================================================
SAVE_USER_STATE_INITIAL_PAYLOAD_EN = {
    "body": json.dumps({
        "gameLayout": ["THN", "YSO", "ACU", "RMG"],
        "gameId": "test-game-state-en",
        "sessionId": "test-session-state-en",
        "wordsUsed": [],
        "originalWordsUsed": []
    }),
    "headers": {
        "Content-Type": "application/json"
    }
}

SAVE_USER_STATE_UPDATE_PAYLOAD_EN = {
    "body": json.dumps({
        "gameLayout": ["THN", "YSO", "ACU", "RMG"],
        "gameId": "test-game-state-en",
        "sessionId": "test-session-state-en",
        "wordsUsed": ["HUMONGOUS"],
        "originalWordsUsed": ["HUMONGOUS"]
    }),
    "headers": {
        "Content-Type": "application/json"
    }
}

SAVE_USER_STATE_COMPLETION_PAYLOAD_EN = {
    "body": json.dumps({
        "gameLayout": ["THN", "YSO", "ACU", "RMG"],
        "gameId": "test-game-state-en",
        "sessionId": "test-session-state-en",
        "wordsUsed": ["HUMONGOUS", "SCRATCHY"],
        "originalWordsUsed": ["HUMONGOUS", "SCRATCHY"]
    }),
    "headers": {
        "Content-Type": "application/json"
    }
}

SAVE_USER_STATE_INITIAL_PAYLOAD_ES = {
    "body": json.dumps({
        "gameLayout": ["OER", "MLT", "CSN", "AUI"],
        "gameId": "test-game-state-es",
        "sessionId": "test-session-state-es",
        "wordsUsed": [],
        "originalWordsUsed": []
    }),
    "headers": {
        "Content-Type": "application/json"
    }
}

SAVE_USER_STATE_UPDATE_PAYLOAD_ES = {
    "body": json.dumps({
        "gameLayout": ["OER", "MLT", "CSN", "AUI"],
        "gameId": "test-game-state-es",
        "sessionId": "test-session-state-es",
        "wordsUsed": ["UNICAMENTE"],
        "originalWordsUsed": ["ÚNICAMENTE"]
    }),
    "headers": {
        "Content-Type": "application/json"
    }
}

SAVE_USER_STATE_COMPLETION_PAYLOAD_ES = {
    "body": json.dumps({
        "gameLayout": ["OER", "MLT", "CSN", "AUI"],
        "gameId": "test-game-state-es",
        "sessionId": "test-session-state-es",
        "wordsUsed": ["UNICAMENTE", "ELECTRICOS"],
        "originalWordsUsed": ["ÚNICAMENTE", "ELECTRICOS"]
    }),
    "headers": {
        "Content-Type": "application/json"
    }
}

# Initialize game state for Game 1
SAVE_USER_STATE_INIT_GAME1 = {
    "body": json.dumps({
        "gameLayout": ["THN", "YSO", "ACU", "RMG"],
        "gameId": "test-game-1",
        "sessionId": "test-session-same",
    }),
    "headers": {
        "Content-Type": "application/json"
    }
}

# Initialize game state for Game 2
SAVE_USER_STATE_INIT_GAME2 = {
    "body": json.dumps({
        "gameLayout": ["OER", "MLT", "CSN", "AUI"],
        "gameId": "test-game-2",
        "sessionId": "test-session-same",
    }),
    "headers": {
        "Content-Type": "application/json"
    }
}

# Update Game 1
SAVE_USER_STATE_UPDATE_GAME1 = {
    "body": json.dumps({
        "gameLayout": ["THN", "YSO", "ACU", "RMG"],
        "gameId": "test-game-1",
        "sessionId": "test-session-same",
        "wordsUsed": ["HUMONGOUS"],
        "originalWordsUsed": ["HUMONGOUS"]
    }),
    "headers": {
        "Content-Type": "application/json"
    }
}

# Update Game 2
SAVE_USER_STATE_UPDATE_GAME2 = {
    "body": json.dumps({
        "gameLayout": ["OER", "MLT", "CSN", "AUI"],
        "gameId": "test-game-2",
        "sessionId": "test-session-same",
        "wordsUsed": ["SCRATCHY"],
        "originalWordsUsed": ["SCRATCHY"]
    }),
    "headers": {
        "Content-Type": "application/json"
    }
}

# Initialize game state for Session 1
SAVE_USER_STATE_INIT_SESSION1 = {
    "body": json.dumps({
        "gameLayout": ["OER", "MLT", "CSN", "AUI"],
        "gameId": "test-game-same",
        "sessionId": "test-session-1",
    }),
    "headers": {
        "Content-Type": "application/json"
    }
}

# Initialize game state for Session 2
SAVE_USER_STATE_INIT_SESSION2 = {
    "body": json.dumps({
        "gameLayout": ["OER", "MLT", "CSN", "AUI"],
        "gameId": "test-game-same",
        "sessionId": "test-session-2",
    }),
    "headers": {
        "Content-Type": "application/json"
    }
}

# Update Session 1
SAVE_USER_STATE_UPDATE_SESSION1 = {
    "body": json.dumps({
        "gameLayout": ["OER", "MLT", "CSN", "AUI"],
        "gameId": "test-game-same",
        "sessionId": "test-session-1",
        "wordsUsed": ["UNICAMENTE"],
        "originalWordsUsed": ["ÚNICAMENTE"]
    }),
    "headers": {
        "Content-Type": "application/json"
    }
}

# Update Session 2
SAVE_USER_STATE_UPDATE_SESSION2 = {
    "body": json.dumps({
        "gameLayout": ["OER", "MLT", "CSN", "AUI"],
        "gameId": "test-game-same",
        "sessionId": "test-session-2",
        "wordsUsed": ["ELECTRICOS"],
        "originalWordsUsed": ["ELECTRICOS"]
    }),
    "headers": {
        "Content-Type": "application/json"
    }
}

SAVE_USER_STATE_MISSING_GAME_LAYOUT = {
    "body": json.dumps({
        "gameId": "test-game-1",
        "sessionId": "test-session-1"
        # Missing 'gameLayout'
    }),
    "headers": {
        "Content-Type": "application/json"
    }
}

SAVE_USER_STATE_INVALID_JSON = {
    "body": '{"gameLayout": ["THN", "YSO", "ACU", "RMG"], "gameId": "test-game-1", "sessionId": "test-session-1"',  # Missing closing brace
    "headers": {
        "Content-Type": "application/json"
    }
}

# Invalid event: Non-existent gameId
SAVE_USER_STATE_NONEXISTENT_GAME = {
    "body": json.dumps({
        "gameLayout": ["ABC", "DEF", "GHI", "JKL"],  # Example layout
        "gameId": "nonexistent-game-id",  # Non-existent gameId
        "sessionId": "test-session-nonexistent",  # Test session ID
        "wordsUsed": [],
        "originalWordsUsed": []
    }),
    "headers": {
        "Content-Type": "application/json"
    }
}

# Constants for event payloads
FETCH_USER_STATE_VALID = {
    "pathParameters": {
        "sessionId": "test-session-valid",
    },
    "queryStringParameters": {
        "gameId": "test-game-id",
    },
}

FETCH_USER_STATE_MISSING_PARAMS = {
    "pathParameters": {
        "sessionId": "test-session-missing",
    },
    "queryStringParameters": {"notGameId": "test-game-id"},  # Missing gameId
}

FETCH_USER_STATE_NONEXISTENT = {
    "pathParameters": {
        "sessionId": "test-session-nonexistent",
    },
    "queryStringParameters": {
        "gameId": "nonexistent-game-id",
    },
}

FETCH_USER_STATE_MALFORMED_EVENT = {
    # Missing both pathParameters and queryStringParameters
}
