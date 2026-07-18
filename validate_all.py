import json
import re

def validate_dataset(filename="GBX_brain_33B.json"):
    with open(filename, 'r', encoding='utf-8') as f:
        data = json.load(f)

    if len(data) <= 175:
        print(f"FAIL: Dataset size is {len(data)}, must be > 175")
        return False

    seen_intents = set()
    seen_texts = set()

    for item in data:
        intent_id = item.get("intent_id", "")
        keywords = item.get("keywords", [])
        base_response = item.get("base_response", "")

        # 1. intent_id rules
        if not re.match(r'^[a-z_]+$', intent_id):
            print(f"FAIL: Invalid intent_id format: {intent_id}")
            return False
        if intent_id in seen_intents:
            print(f"FAIL: Duplicate intent_id: {intent_id}")
            return False
        seen_intents.add(intent_id)

        # 2. keywords rules
        if not (4 <= len(keywords) <= 6):
            print(f"FAIL: Invalid keywords length for {intent_id}: {len(keywords)}")
            return False
        for kw in keywords:
            if not re.match(r'^[a-z\s]+$', kw):
                print(f"FAIL: Keyword contains invalid chars in {intent_id}: {kw}")
                return False
            if re.search(r'[áéíóú]', kw):
                print(f"FAIL: Keyword contains tildes in {intent_id}: {kw}")
                return False
            if kw in ['el', 'la', 'los', 'las', 'un', 'una', 'unos', 'unas', 'de', 'en', 'con', 'por', 'para']:
                print(f"FAIL: Keyword is a stop word in {intent_id}: {kw}")
                return False

        # 3. base_response rules
        words = base_response.split()
        if not (35 <= len(words) <= 50):
            print(f"FAIL: base_response word count {len(words)} not 35-50 for {intent_id}")
            return False
        if '\n' in base_response:
            print(f"FAIL: base_response contains newlines in {intent_id}")
            return False
        if '"' in base_response:
            print(f"FAIL: base_response contains double quotes in {intent_id}")
            return False
        if not re.search(r'[áéíóúÁÉÍÓÚ]', base_response):
            print(f"FAIL: base_response missing tildes in {intent_id}")
            return False

        if base_response in seen_texts:
            print(f"FAIL: Duplicate base_response found for {intent_id}")
            return False
        seen_texts.add(base_response)

    print(f"SUCCESS: Validation passed for {len(data)} items!")
    return True

if __name__ == "__main__":
    validate_dataset()
