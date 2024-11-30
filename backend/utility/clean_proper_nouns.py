import os

def filter_proper_nouns(input_file, proper_nouns_file, output_file):
    """
    Filters out proper nouns from the input file using the proper nouns list.

    Args:
        input_file (str): Path to the file containing the main word list.
        proper_nouns_file (str): Path to the file containing proper nouns.
        output_file (str): Path to save the filtered word list.
    """
    # Load proper nouns into a set for quick lookup
    with open(proper_nouns_file, 'r') as pn_file:
        proper_nouns = set(line.strip().lower() for line in pn_file)

    # Open files for reading and writing
    with open(input_file, 'r') as infile, open(output_file, 'w') as outfile:
        for line in infile:
            word = line.strip().lower()
            if word not in proper_nouns:
                outfile.write(word + '\n')

script_dir = os.path.dirname(os.path.abspath(__file__))
input_file = os.path.join(script_dir, "cleaned_word_list.txt")
proper_nouns_file = os.path.join(script_dir, "proper_nouns.txt")
output_file = os.path.join(script_dir, "filtered_word_list.txt")

filter_proper_nouns(input_file, proper_nouns_file, output_file)
print(f"Filtered word list saved to {output_file}")