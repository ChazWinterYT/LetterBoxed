import os
import nyt_test_lists as nyt

def check_nyt_words_in_cleaned_list(nyt_dict_obj, cleaned_word_list_file):
    """
    Check if all words in the NYT dictionary are in the cleaned word list.

    Args:
        nyt_dict_obj (dict): Dictionary object containing NYT test list with a "dictionary" key.
        cleaned_word_list_file (str): Path to the cleaned word list file.
    """
    # Extract the list of words from the NYT dictionary object
    nyt_words = nyt_dict_obj.get("dictionary", [])
    
    # Read cleaned word list from file
    with open(cleaned_word_list_file, 'r') as infile:
        cleaned_words = set(line.strip().lower() for line in infile)  # Lowercase for consistent comparison

    # Check for missing words
    missing_words = [word for word in nyt_words if word.lower() not in cleaned_words]

    if missing_words:
        print(f"{len(missing_words)} words are missing from the cleaned word list:")
        print(", ".join(missing_words))
    else:
        print("All words from the NYT dictionary are present in the cleaned word list.")

script_dir = os.path.dirname(os.path.abspath(__file__)) 
output_file = os.path.join(script_dir, "dictionary.txt")

check_nyt_words_in_cleaned_list(nyt.nyt_test_list_2024_11_28, output_file)


