import json
import re

def validate_json(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        try:
            data = json.load(f)
        except Exception as e:
            print(f"ERROR: Invalid JSON file - {e}")
            return False

    if not isinstance(data, list):
        print("ERROR: Root must be a JSON array.")
        return False

    if len(data) != 900:
        print(f"ERROR: Expected 900 items, got {len(data)}")
        return False

    print(f"Validating {len(data)} items...")

    for i, item in enumerate(data):
        # Check keys
        if "intent_id" not in item or "keywords" not in item or "base_response" not in item:
            print(f"ERROR: Missing keys in item {i}: {item}")
            return False

        # Check intent_id format
        intent_id = item["intent_id"]
        if not re.match(r'^[a-z0-9_]+$', intent_id):
            print(f"ERROR: Invalid intent_id format in item {i}: {intent_id}")
            return False

        # Check keywords
        keywords = item["keywords"]
        if not isinstance(keywords, list) or not (4 <= len(keywords) <= 6):
            print(f"ERROR: Invalid keywords length in item {i}: {len(keywords)} keywords - {keywords}")
            return False

        for kw in keywords:
            if not kw.islower() or not kw.isalpha() or re.search(r'[áéíóúü]', kw):
                print(f"ERROR: Invalid keyword format in item {i}: '{kw}'")
                return False

        # Check base_response words count
        resp = item["base_response"]
        words = re.findall(r'\b\w+\b', resp)
        if not (35 <= len(words) <= 50):
            print(f"ERROR: Invalid base_response word count in item {i}: {len(words)} words - {resp}")
            return False

    print("SUCCESS: JSON structure, item count, and all rules are valid!")
    return True

if __name__ == "__main__":
    if not validate_json('MM_brain_39.json'):
        exit(1)
