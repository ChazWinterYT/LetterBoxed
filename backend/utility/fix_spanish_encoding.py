import os
import codecs

def clean_mojibake(input_file, output_file):
    """
    Replace specific mojibake patterns with correct characters.

    Args:
        input_file (str): Path to the input file with mojibake text.
        output_file (str): Path to save the cleaned text.
    """
    # Define the mapping of mojibake patterns to correct characters
    replacements = {
        "√∫": "ú",  # Example: "s√∫bita" -> "súbita"
        "√©": "é",  # Example: "caf√©" -> "café"
        "√±": "ñ",  # Example: "a√±adir" -> "añadir"
        "√≥": "ó",  # Example: "cam√≥n" -> "camión"
        "√°": "á",  # Example: "c√°lido" -> "cálido"
        "√º": "ü",  # Example: "ping√ºino" -> "pingüino"
        "√ª": "í",  # Example: "√ªndice" -> "índice"
        "√•": "Á",  # Example: "√•rbol" -> "Árbol"
    }

    with open(input_file, 'r', encoding='utf-8') as infile, open(output_file, 'w', encoding='utf-8') as outfile:
        for line in infile:
            # Replace each mojibake pattern in the line
            for mojibake, correct in replacements.items():
                line = line.replace(mojibake, correct)
            outfile.write(line)

# Paths to your files
script_dir = os.path.dirname(os.path.abspath(__file__))

input_file = os.path.join(script_dir, "espanol_basic.txt")
output_file = os.path.join(script_dir, "espanol_basic_fixed.txt")

# Apply the replacement-based fix
clean_mojibake(input_file, output_file)
print(f"Cleaned file saved to: {output_file}")