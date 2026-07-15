import json
import re

def validate_data(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
        return False

    errors = 0
    ids = set()

    for i, item in enumerate(data):
        intent_id = item.get("intent_id", "")
        keywords = item.get("keywords", [])
        base_response = item.get("base_response", "")

        # Validate intent_id
        if not re.match(r'^[a-z_]+$', intent_id):
            print(f"[{intent_id}] Error: Invalid intent_id format.")
            errors += 1

        if intent_id in ids:
            print(f"[{intent_id}] Error: Duplicate intent_id.")
            errors += 1
        ids.add(intent_id)

        # Validate keywords
        if not (4 <= len(keywords) <= 6):
            print(f"[{intent_id}] Error: Keywords array must have 4-6 items (found {len(keywords)}).")
            errors += 1

        for kw in keywords:
            if not re.match(r'^[a-z]+$', kw):
                print(f"[{intent_id}] Error: Invalid keyword format '{kw}'. Must be unaccented alphabetical lowercase.")
                errors += 1

        # Validate base_response word count
        word_count = len(re.findall(r'\b\w+\b', base_response, re.UNICODE))
        if not (35 <= word_count <= 50):
            print(f"[{intent_id}] Error: Base response has {word_count} words (must be 35-50).")
            errors += 1

    if errors == 0:
        print("Validation successful. No errors found.")
        return True
    else:
        print(f"Validation failed with {errors} errors.")
        return False

if __name__ == "__main__":
    validate_data("MM_brain_01.json")