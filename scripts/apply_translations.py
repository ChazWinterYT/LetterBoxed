import json
import os

LANG_DIR = "../frontend/src/languages"
TRANSLATIONS_FILE = "translations.json"

def load_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json(path, data):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def deep_merge(target, source):
    for key, value in source.items():
        if isinstance(value, dict):
            node = target.setdefault(key, {})
            deep_merge(node, value)
        else:
            target[key] = value

def main():
    if not os.path.exists(TRANSLATIONS_FILE):
        print(f"Error: {TRANSLATIONS_FILE} not found.")
        return

    translations_map = load_json(TRANSLATIONS_FILE)

    for filename, translations in translations_map.items():
        file_path = os.path.join(LANG_DIR, filename)
        if not os.path.exists(file_path):
            print(f"Warning: {filename} not found, skipping.")
            continue
        
        try:
            target_data = load_json(file_path)
            
            nested_translations = {}
            for flat_key, value in translations.items():
                parts = flat_key.split('.')
                d = nested_translations
                for part in parts[:-1]:
                    if part not in d:
                        d[part] = {}
                    d = d[part]
                d[parts[-1]] = value
                
            deep_merge(target_data, nested_translations)
            save_json(file_path, target_data)
            print(f"Updated {filename}")
            
        except Exception as e:
            print(f"Error updating {filename}: {e}")

if __name__ == "__main__":
    main()
