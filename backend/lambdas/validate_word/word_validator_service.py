from typing import List, Optional
from lambdas.common.game_utils import normalize_to_base

def find_valid_word_from_normalized(submitted_word: str, valid_words: List[str]) -> Optional[str]:
    """
    Find the original word in the dictionary that matches a normalized word.

    Args:
        submitted_word (str): The normalized word to check against the dictionary.
        valid_words (List[str]): The list of valid words in their original form,
            which may include accents or special characters.

    Returns:
        str: The original word from the dictionary that matches the normalized 
        word, or None if no match is found.
    """
    for original_word in valid_words:
        base_original_word = normalize_to_base(original_word)
        if submitted_word == base_original_word:
            return original_word  # Return the original word that matches
    
    return None  # Return None if no match is found