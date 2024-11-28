import json

# This game layout should yield the solution ["VAPORIZE", "ELEMENT"]
VALID_GAME_LAYOUT_EN = ["VZL", "PMI", "ONA", "ERT"]

# This gamy layout should yield the solution ["ALIANZA", "AUTOMOVILES"]
VALID_GAME_LAYOUT_ES = ['SOA', 'EVN', 'ITM', 'ZLU']

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
CREATE_CUSTOM_EVENT_VALID_LARGE = {
    "body": json.dumps({
        "gameLayout": ["ABCD", "EFGH", "IJKL", "MNOP"], 
        "sessionId": "test-session-id-large",
        "language": "en",
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
