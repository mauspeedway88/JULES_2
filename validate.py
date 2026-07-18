import json
import re

def validate_dataset(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON format. {e}")
        return False

    print(f"Total entries: {len(data)}")

    intent_ids = set()
    errors = 0

    for i, item in enumerate(data):
        # Check keys
        if set(item.keys()) != {'intent_id', 'keywords', 'base_response'}:
            print(f"[{i}] Error: Missing or invalid keys.")
            errors += 1

        intent_id = item.get('intent_id', '')
        if not re.match(r'^[a-z_]+$', intent_id) or re.search(r'\d', intent_id):
            print(f"[{i}] Error: Invalid intent_id format: {intent_id}")
            errors += 1

        if intent_id in intent_ids:
            print(f"[{i}] Error: Duplicate intent_id: {intent_id}")
            errors += 1
        intent_ids.add(intent_id)

        keywords = item.get('keywords', [])
        if not (4 <= len(keywords) <= 6):
            print(f"[{i}] Error: Keywords length must be 4-6, got {len(keywords)}")
            errors += 1

        for kw in keywords:
            if kw != kw.lower() or re.search(r'[áéíóúÁÉÍÓÚñÑ]', kw):
                print(f"[{i}] Error: Invalid keyword format: {kw}")
                errors += 1

        base_response = item.get('base_response', '')
        words = [w for w in base_response.split() if w.strip()]
        if not (35 <= len(words) <= 50):
            print(f"[{i}] Error: base_response word count {len(words)} not in 35-50 range")
            errors += 1

        if not re.search(r'[áéíóúÁÉÍÓÚ]', base_response):
            print(f"[{i}] Error: base_response missing tildes.")
            errors += 1

    if errors == 0:
        print("Validation passed!")
        return True
    else:
        print(f"Validation failed with {errors} errors.")
        return False

if __name__ == '__main__':
    validate_dataset('GBX_brain_38B.json')
