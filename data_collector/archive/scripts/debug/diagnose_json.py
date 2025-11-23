import json
import os

file_path = "processed_data/bangkok_pois.json"

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

try:
    decoder = json.JSONDecoder()
    obj, idx = decoder.raw_decode(content)
    print(f"Successfully decoded object of length {len(obj)}")
    print(f"Stopped at index {idx}")
    print(f"Total length: {len(content)}")
    print(f"Remaining content: {content[idx:idx+100]!r}...")
    
    # If successful, save the clean object
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False)
    print("Fixed file!")
    
except Exception as e:
    print(f"Decode failed: {e}")
