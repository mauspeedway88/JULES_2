import json
import re

def validate_dataset(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error loading JSON: {e}")
        return False

    print(f"Dataset has {len(data)} concepts.")

    intent_ids = set()

    for idx, item in enumerate(data):
        intent_id = item.get("intent_id", "")
        if not re.match(r'^[a-z_]+$', intent_id):
            print(f"Error at index {idx}: Invalid intent_id format '{intent_id}'.")
            return False
        if intent_id in intent_ids:
            print(f"Error at index {idx}: Duplicate intent_id '{intent_id}'.")
            return False
        intent_ids.add(intent_id)

        keywords = item.get("keywords", [])
        if len(keywords) < 4 or len(keywords) > 6:
            print(f"Error at index {idx}: Keyword count out of bounds. Found {len(keywords)}.")
            return False
        for kw in keywords:
            if not re.match(r'^[a-z]+$', kw):
                print(f"Error at index {idx}: Invalid keyword format '{kw}'.")
                return False

        base_response = item.get("base_response", "")
        words = len(re.findall(r'\b\w+\b', base_response))
        if words < 35 or words > 50:
            print(f"Error at index {idx}: Word count {words} out of bounds (35-50). Text: {base_response}")
            return False

        if not re.search(r'[áéíóúÁÉÍÓÚ]', base_response):
            print(f"Error at index {idx}: No accents found in base_response.")
            return False

    print(f"Validation successful! Checked {len(data)} concepts.")
    return True

if __name__ == '__main__':
    validate_dataset("GBX_brain_19B.json")