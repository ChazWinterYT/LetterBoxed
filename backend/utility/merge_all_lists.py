import os
import shutil  # Import shutil for file copy
import nyt_test_lists as nyt

def clean_word(word):
    """Normalize and clean a word."""
    return word.strip().upper()

def merge_word_lists(output_file, *word_lists):
    """
    Merge multiple word lists into a single cleaned and deduplicated list.
    
    Args:
        output_file (str): Path to the output file.
        *word_lists (list): Lists of words to merge.
    """
    unique_words = set()

    for word_list in word_lists:
        if isinstance(word_list, str) and os.path.isfile(word_list):
            # If word_list is a file path, load it
            with open(word_list, 'r') as infile:
                for line in infile:
                    word = clean_word(line)
                    if len(word) >= 3 and word.isalpha():
                        unique_words.add(word)
        elif isinstance(word_list, list):
            # If word_list is a Python list, process it directly
            for word in word_list:
                word = clean_word(word)
                if len(word) >= 3 and word.isalpha():
                    unique_words.add(word)

    # Write sorted unique words to output file
    with open(output_file, 'w') as outfile:
        for word in sorted(unique_words):
            outfile.write(word + '\n')

def copy_to_target_directory(source_file, target_directory):
    """
    Copy a file to a target directory.

    Args:
        source_file (str): The path to the source file.
        target_directory (str): The path to the target directory.
    """
    if not os.path.exists(target_directory):
        os.makedirs(target_directory)  # Create the directory if it doesn't exist

    target_file = os.path.join(target_directory, os.path.basename(source_file))
    shutil.copy(source_file, target_file)
    print(f"Copied {source_file} to {target_file}")

# Example Usage
script_dir = os.path.dirname(os.path.abspath(__file__))

# File paths
cleaned_word_list_path = os.path.join(script_dir, 'cleaned_word_list.txt')
scrabble_cleaned_path = os.path.join(script_dir, 'cleaned_scrabble.txt')
enable_cleaned_path = os.path.join(script_dir, 'enable1.txt')
stolen_list_path = os.path.join(script_dir, 'cleaned_stolen_list.txt')
output_file = os.path.join(script_dir, "esdictionary.txt")
esbasic = os.path.join(script_dir, "esbasic")
esfull = os.path.join(script_dir, "esfull")

# Target directory for copying the dictionary
target_directory = r"C:\Users\chas\Documents\JS Projects\chazwinter.com\LetterBoxed\backend\dictionaries\en"

# Merge and save
merge_word_lists(
    output_file,
    esbasic,
    esfull
)

# Copy the merged dictionary to the target directory
copy_to_target_directory(output_file, target_directory)

print("All lists merged and copied successfully.")
