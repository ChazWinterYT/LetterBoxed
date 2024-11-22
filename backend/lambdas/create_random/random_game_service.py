import random
from typing import List, Optional, Tuple


def generate_layout(word1: str, word2: str) -> Optional[List[str]]:
    """
    Generate a game layout with letters from two words distributed across 4 sides,
    maintaining adjacency constraints and handling shared and repeated letters.

    Args:
        word1 (str): The first word.
        word2 (str): The second word.

    Returns:
        Optional[List[str]]: A list of 4 strings representing the sides of the board,
        or None if no valid layout can be generated.
    """
    combined_letters = word1 + word2[1:]
    if len(set(combined_letters)) != 12:
        return None

    sides = [""] * 4
    letter_to_side = {}

    def backtrack(index: int, current_side: int) -> bool:
        if index == len(combined_letters):
            return True

        letter = combined_letters[index]
        if letter in letter_to_side:
            next_side = letter_to_side[letter]
            return next_side != current_side and backtrack(index + 1, next_side)

        side_indices = list(range(4))
        random.shuffle(side_indices)

        for side_index in side_indices:
            if side_index == current_side or len(sides[side_index]) >= 3:
                continue

            sides[side_index] += letter
            letter_to_side[letter] = side_index

            if backtrack(index + 1, side_index):
                return True

            sides[side_index] = sides[side_index][:-1]
            del letter_to_side[letter]

        return False

    if backtrack(0, -1):
        return shuffle_final_layout(sides)
    return None


def load_dictionary(file_path: str) -> List[str]:
    """
    Load the dictionary from the specified file.

    Args:
        file_path (str): Path to the dictionary file.

    Returns:
        List[str]: List of words in the dictionary.
    """
    with open(file_path, 'r') as file:
        return [line.strip().upper() for line in file if line.strip().isalpha()]

def select_two_words(dictionary: List[str], max_attempts: int = 10000) -> Optional[Tuple[str, str]]:
    """
    Select two words that together contain exactly 12 unique letters and where
    the first letter of one word matches the last letter of the other.

    Args:
        dictionary (List[str]): List of words from the dictionary.
        max_attempts (int): Maximum number of attempts to find a valid pair.

    Returns:
        Optional[Tuple[str, str]]: A tuple of two words or None if no pair is found.
    """
    for _ in range(max_attempts):
        word1, word2 = random.sample(dictionary, 2)
        if word1[-1] == word2[0] and len(set(word1) | set(word2)) == 12:
            return word1, word2
    return None


def shuffle_final_layout(layout: List[str]) -> List[str]:
    """
    Shuffle the letters within each side and shuffle the sides themselves.

    Args:
        layout (List[str]): The generated layout with letters placed.

    Returns:
        List[str]: The shuffled layout.
    """
    shuffled_sides = [''.join(random.sample(side, len(side))) for side in layout]
    random.shuffle(shuffled_sides)
    return shuffled_sides