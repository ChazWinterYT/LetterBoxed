

def validate_submitted_word(game_id: str, submitted_word: str, user_id: str) -> dict:
    # Normalize the word
    submitted_word = submitted_word.upper()

    # Fetch game data
    