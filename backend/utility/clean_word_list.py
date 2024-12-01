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

            # Skip capitalized words
            if (word[0].isupper()):
                continue

            # Skip words with double letters
            if has_double_letters(word):
                continue

            # Skip very short words (less than 3 characters)
            if len(word) < 3:
                continue

            # Write the cleaned word to the output file
            outfile.write(word + '\n')
            

def clean_word_list_with_numbers(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as infile, open(output_file, 'w', encoding='utf-8') as outfile:
        for line in infile:
            # Split the line into word and number
            word = line.split()[0]
            
            # Normalize word to NFC form (preserve accents but standardize representation)
            word = unicodedata.normalize("NFC", word)

            # Skip capitalized words
            if (word[0].isupper()):
                continue

            # Skip words with double letters
            if has_double_letters(word):
                continue

            # Skip very short words (less than 3 characters)
            if len(word) < 3:
                continue

            # Write the cleaned word to the output file
            outfile.write(word + '\n')
        

def filter_basic_dictionary(main_dict_file, basic_dict_file, output_file):
    # Load the main dictionary into a set
    with open(main_dict_file, 'r', encoding='utf-8') as main_file:
        main_words = set(line.strip() for line in main_file)

    # Filter the basic dictionary
    with open(basic_dict_file, 'r', encoding='utf-8') as basic_file, \
         open(output_file, 'w', encoding='utf-8') as output:
        for word in basic_file:
            word = word.strip()
            if word in main_words:
                output.write(word + '\n')





script_dir = os.path.dirname(os.path.abspath(__file__))

# Example for French
french_input_file = os.path.join(script_dir, "basic.txt")
french_output_file = os.path.join(script_dir, "basic_cleaned.txt")
clean_word_list(french_input_file, french_output_file)
print(f"Cleaned French word list saved to {french_output_file}")

# # Example for Spanish
# spanish_input_file = os.path.join(script_dir, "espanol.txt")
# spanish_output_file = os.path.join(script_dir, "espanol_cleaned.txt")
# clean_word_list(spanish_input_file, spanish_output_file)
# print(f"Cleaned Spanish word list saved to {spanish_output_file}")

# polish_input_file = os.path.join(script_dir, "pl_basic.txt")
# polish_output_file = os.path.join(script_dir, "pl_basic_cleaned.txt")
# clean_word_list_with_numbers(polish_input_file, polish_output_file)
# print(f"Cleaned Polish word list saved to {polish_output_file}")

# main_dict_file = os.path.join(script_dir, "pl.txt")
# basic_dict_file = os.path.join(script_dir, "pl_basic.txt")
# output_file = os.path.join(script_dir, "pl_basic_cleaned.txt")
# filter_basic_dictionary(main_dict_file, basic_dict_file, output_file)
