import json
import re

def validate_dataset(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"FAILED: Could not parse JSON from {filepath}. Error: {e}")
        return False

    print(f"Total entries loaded: {len(data)}")

    if len(data) < 90:
        print(f"FAILED: Insufficient entries. Expected >= 90, got {len(data)}")
        return False

    seen_ids = set()
    all_responses = []

    for idx, entry in enumerate(data):
        intent_id = entry.get('intent_id')
        keywords = entry.get('keywords')
        base_response = entry.get('base_response')

        # 1. intent_id validation
        if not intent_id:
            print(f"FAILED [Entry {idx}]: Missing intent_id")
            return False
        if intent_id in seen_ids:
            print(f"FAILED [Entry {idx}]: Duplicate intent_id '{intent_id}'")
            return False
        seen_ids.add(intent_id)
        if any(c.isdigit() for c in intent_id):
            print(f"FAILED [Entry {idx}]: intent_id '{intent_id}' contains numbers")
            return False
        if not re.match(r'^[a-z_]+$', intent_id):
            print(f"FAILED [Entry {idx}]: intent_id '{intent_id}' contains invalid characters (only lowercase and underscores allowed)")
            return False

        # 2. keywords validation
        if not isinstance(keywords, list):
            print(f"FAILED [Entry {idx}]: keywords is not a list")
            return False
        if not (4 <= len(keywords) <= 6):
            print(f"FAILED [Entry {idx}]: keywords length must be between 4 and 6, got {len(keywords)}")
            return False
        for kw in keywords:
            if not kw.islower():
                print(f"FAILED [Entry {idx}]: keyword '{kw}' is not lowercase")
                return False
            if any(c in 'áéíóúÁÉÍÓÚñÑ' for c in kw):
                print(f"FAILED [Entry {idx}]: keyword '{kw}' contains accents or tildes")
                return False

        # 3. base_response validation
        if not base_response:
            print(f"FAILED [Entry {idx}]: Missing base_response")
            return False
        if '\n' in base_response or '\r' in base_response:
            print(f"FAILED [Entry {idx}]: base_response contains line breaks")
            return False

        words = base_response.split()
        if not (35 <= len(words) <= 50):
            print(f"FAILED [Entry {idx}]: base_response word count {len(words)} is outside the 35-50 range")
            return False

        if not any(c in 'áéíóúÁÉÍÓÚ' for c in base_response):
            print(f"FAILED [Entry {idx}]: base_response must contain valid Spanish accents/tildes")
            return False

        all_responses.append(base_response)

    print("SUCCESS: Dataset passed all validations.")
    return True

if __name__ == "__main__":
    validate_dataset('GBX_brain_19B.json')
