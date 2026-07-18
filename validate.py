import json
import re

def validate_dataset(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    print(f"Total concepts: {len(data)}")

    intent_ids = set()

    for item in data:
        intent_id = item.get("intent_id")
        keywords = item.get("keywords")
        base_response = item.get("base_response")

        # Check intent_id
        assert isinstance(intent_id, str), f"Invalid intent_id type: {intent_id}"
        assert intent_id not in intent_ids, f"Duplicate intent_id: {intent_id}"
        assert re.match(r"^[a-z_]+$", intent_id), f"Invalid intent_id format (must be lowercase and underscores only): {intent_id}"
        assert not any(c.isdigit() for c in intent_id), f"intent_id contains numbers: {intent_id}"
        intent_ids.add(intent_id)

        # Check keywords
        assert isinstance(keywords, list), f"Keywords must be a list: {intent_id}"
        assert 4 <= len(keywords) <= 6, f"Keywords must be between 4 and 6 words: {intent_id}"
        for kw in keywords:
            assert isinstance(kw, str), f"Keyword must be string: {kw} in {intent_id}"
            assert kw.islower(), f"Keyword must be lowercase: {kw} in {intent_id}"
            assert not re.search(r'[áéíóúÁÉÍÓÚ]', kw), f"Keyword contains accents: {kw} in {intent_id}"
            assert len(kw.split()) == 1, f"Keyword must be a single word: {kw} in {intent_id}"
            assert not any(c.isdigit() for c in kw), f"Keyword contains numbers: {kw} in {intent_id}"
        assert len(set(keywords)) == len(keywords), f"Keywords must be unique: {intent_id}"

        # Check base_response
        assert isinstance(base_response, str), f"Base response must be string: {intent_id}"
        words = [w for w in base_response.split() if re.search(r'\w', w)]
        assert 35 <= len(words) <= 50, f"Base response must be 35-50 words (got {len(words)}): {intent_id}"
        assert re.search(r'[áéíóúÁÉÍÓÚ]', base_response), f"Base response missing accents (tildes): {intent_id}"
        assert '\n' not in base_response, f"Base response contains newlines: {intent_id}"
        assert '"' not in base_response, f"Base response contains unescaped quotes: {intent_id}"

    # Target requirement (240 unique minimum)
    if len(data) >= 240:
        print("Success: Total concepts >= 240.")
    else:
        print(f"Warning: Total concepts is {len(data)}, expected at least 240.")

    print("All validation checks passed.")

if __name__ == "__main__":
    validate_dataset("GBX_brain_37A.json")
