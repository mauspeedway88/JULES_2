import json
import re

TARGET_FILE = "GBX_brain_34B.json"

def validate_dataset():
    with open(TARGET_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    print(f"Total entries: {len(data)}")
    if len(data) <= 200:
        print(f"ERROR: Dataset size {len(data)} is not >200.")

    seen_intents = set()
    seen_responses = set()

    errors = 0
    for item in data:
        intent_id = item.get('intent_id')
        keywords = item.get('keywords')
        base_response = item.get('base_response')

        # Unique constraints
        if intent_id in seen_intents:
            print(f"ERROR: Duplicate intent_id: {intent_id}")
            errors += 1
        seen_intents.add(intent_id)

        if base_response in seen_responses:
            print(f"ERROR: Duplicate base_response: {intent_id}")
            errors += 1
        seen_responses.add(base_response)

        # Intent ID rules
        if not re.match(r'^[a-z_]+$', intent_id):
            print(f"ERROR: Invalid intent_id format: {intent_id}")
            errors += 1
        if any(char.isdigit() for char in intent_id):
            print(f"ERROR: intent_id contains numbers: {intent_id}")
            errors += 1

        # Keywords rules
        if not isinstance(keywords, list) or not (4 <= len(keywords) <= 6):
            print(f"ERROR: Invalid keywords length: {intent_id}")
            errors += 1

        for kw in keywords:
            if not re.match(r'^[a-z]+$', kw):
                print(f"ERROR: Invalid keyword format (must be unaccented lowercase): '{kw}' in {intent_id}")
                errors += 1

        # Base Response rules
        words = base_response.split()
        if not (35 <= len(words) <= 50):
            print(f"ERROR: Invalid base_response length ({len(words)} words): {intent_id}")
            errors += 1

        if '"' in base_response or '\n' in base_response:
            print(f"ERROR: Invalid characters in base_response: {intent_id}")
            errors += 1

    print(f"Validation complete. Found {errors} errors.")
    return errors

if __name__ == "__main__":
    import sys
    if validate_dataset() > 0:
        sys.exit(1)
    sys.exit(0)
