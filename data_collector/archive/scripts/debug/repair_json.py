import json
import os

file_path = "processed_data/bangkok_pois.json"
if not os.path.exists(file_path):
    print(f"File not found: {file_path}")
    exit(1)

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# Find the last ']'
last_bracket = content.rfind("]")
if last_bracket != -1:
    valid_json = content[:last_bracket+1]
    try:
        data = json.loads(valid_json)
        print(f"Successfully recovered {len(data)} items.")
        
        # Backup original
        os.rename(file_path, file_path + ".bak")
        
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print("Saved repaired file.")
    except Exception as e:
        print(f"Failed to parse recovered JSON: {e}")
else:
    print("Could not find closing bracket.")
