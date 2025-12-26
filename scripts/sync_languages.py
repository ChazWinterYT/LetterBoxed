import json
import os

LANG_DIR = "../frontend/src/languages"
EN_FILE = os.path.join(LANG_DIR, "en.json")
REPORT_FILE = "missing_translations.json"

def load_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json(path, data):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def sync_dict(source, target, path="", missing_report=None):
    """
    Recursively syncs target dict to match source dict structure.
    Populates missing keys with source values.
    """
    new_target = {}
    
    for key, value in source.items():
        current_path = f"{path}.{key}" if path else key
        
        if key not in target:
            # Key missing, use source value
            new_target[key] = value
            if missing_report is not None:
                if isinstance(value, dict):
                     # If it's a dict, we need to traverse it to mark all sub-keys as missing
                     flatten_and_report(value, current_path, missing_report)
                else:
                    missing_report[current_path] = value
        else:
            # Key exists
            if isinstance(value, dict):
                # If source is dict, target must be dict
                if not isinstance(target[key], dict):
                    # Structure mismatch, overwrite with source
                    new_target[key] = value
                    flatten_and_report(value, current_path, missing_report)
                else:
                    # Both are dicts, recurse
                    new_target[key] = sync_dict(value, target[key], current_path, missing_report)
            else:
                # Source is value
                if isinstance(target[key], dict):
                     # Structure mismatch, overwrite with source
                    new_target[key] = value
                    missing_report[current_path] = value
                else:
                    # Both are values, keep target value
                    new_target[key] = target[key]
                    
    return new_target

def flatten_and_report(data, path, report):
    if isinstance(data, dict):
        for k, v in data.items():
            flatten_and_report(v, f"{path}.{k}", report)
    else:
        report[path] = data

def main():
    if not os.path.exists(EN_FILE):
        print(f"Error: {EN_FILE} not found.")
        return

    en_data = load_json(EN_FILE)
    missing_translations = {}

    for filename in os.listdir(LANG_DIR):
        if filename == "en.json" or not filename.endswith(".json"):
            continue
        
        file_path = os.path.join(LANG_DIR, filename)
        try:
            target_data = load_json(file_path)
            print(f"Syncing {filename}...")
            
            file_missing = {}
            synced_data = sync_dict(en_data, target_data, missing_report=file_missing)
            
            if file_missing:
                missing_translations[filename] = file_missing
            
            save_json(file_path, synced_data)
            
        except Exception as e:
            print(f"Error processing {filename}: {e}")

    save_json(REPORT_FILE, missing_translations)
    print(f"Sync complete. Missing translations report saved to {REPORT_FILE}")

if __name__ == "__main__":
    main()
