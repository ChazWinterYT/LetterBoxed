import os

# Print the current working directory
print("Current working directory:", os.getcwd())

# Print files in the current directory to verify
print("Files in current directory:", os.listdir())

# Define file paths
main_dictionary_path = "cleaned_stolen_list.txt"
proper_nouns_path = "proper_nouns.txt"
filtered_dictionary_path = "cleaned_stolen_list_no_proper_nouns.txt"

# Read and normalize the main dictionary
with open(main_dictionary_path, "r") as main_file:
    main_words = set(word.strip().upper() for word in main_file)

# Read and normalize the proper nouns
with open(proper_nouns_path, "r") as proper_file:
    proper_nouns = set(word.strip().upper() for word in proper_file)

# Remove proper nouns from the main dictionary
filtered_words = main_words - proper_nouns

# Write the filtered dictionary to a new file
with open(filtered_dictionary_path, "w") as filtered_file:
    for word in sorted(filtered_words):  # Sorting is optional
        filtered_file.write(word + "\n")

print(f"Filtered dictionary saved to {filtered_dictionary_path}")