import os
import unicodedata

def has_double_letters(word):
    """
    Check if a word contains double consecutive letters.
    
    Args:
        word (str): The word to check.
        
    Returns:
        bool: True if the word contains double letters, False otherwise.
    """
    for i in range(len(word) - 1):
        if word[i] == word[i + 1]:
            return True
    return False

def clean_word_list(input_file, output_file):
    """
    Process and clean a word list by applying filters and save the cleaned version.

    Args:
        input_file (str): Path to the raw word list file.
        output_file (str): Path to save the cleaned word list.
    """
    with open(input_file, 'r', encoding='utf-8') as infile, open(output_file, 'w', encoding='utf-8') as outfile:
        for line in infile:
            word = line.strip()  # Remove whitespace and newline

            # Normalize word to NFC form (preserve accents but standardize representation)
            word = unicodedata.normalize("NFC", word)

            # Skip words with double letters
            if has_double_letters(word):
                continue

            # Skip very short words (less than 3 characters)
            if len(word) < 3:
                continue

            # Write the cleaned word to the output file
            outfile.write(word + '\n')

script_dir = os.path.dirname(os.path.abspath(__file__))

# Example for French
french_input_file = os.path.join(script_dir, "espanol_basic.txt")
french_output_file = os.path.join(script_dir, "espanol_basic_cleaned.txt")
clean_word_list(french_input_file, french_output_file)
print(f"Cleaned French word list saved to {french_output_file}")

# Example for Spanish
spanish_input_file = os.path.join(script_dir, "espanol.txt")
spanish_output_file = os.path.join(script_dir, "espanol_cleaned.txt")
clean_word_list(spanish_input_file, spanish_output_file)
print(f"Cleaned Spanish word list saved to {spanish_output_file}")
