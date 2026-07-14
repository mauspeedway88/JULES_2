import json
import sys

def run_tests():
    try:
        with open("MM_brain_56.json", "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error loading JSON: {e}")
        sys.exit(1)

    if not isinstance(data, list):
        print("Root is not a list")
        sys.exit(1)

    for i, item in enumerate(data):
        if "intent_id" not in item:
            print(f"Item {i} missing intent_id")
            sys.exit(1)
        if "keywords" not in item:
            print(f"Item {i} missing keywords")
            sys.exit(1)
        if "base_response" not in item:
            print(f"Item {i} missing base_response")
            sys.exit(1)

        intent_id = item["intent_id"]
        if not intent_id.islower() or not all(c.isalnum() or c == '_' for c in intent_id):
            print(f"Item {i} intent_id invalid format: {intent_id}")
            sys.exit(1)

        keywords = item["keywords"]
        if not isinstance(keywords, list):
            print(f"Item {i} keywords is not list")
            sys.exit(1)
        if not (4 <= len(keywords) <= 6):
            print(f"Item {i} keywords length invalid: {len(keywords)}")
            sys.exit(1)
        for kw in keywords:
            if not kw.islower() or not kw.isalpha():
                print(f"Item {i} invalid keyword: {kw}")
                sys.exit(1)

        base_response = item["base_response"]
        words = base_response.split()
        if not (35 <= len(words) <= 50):
            print(f"Item {i} base_response length invalid: {len(words)} words. text: {base_response}")
            sys.exit(1)

    print("All tests passed!")
    sys.exit(0)

if __name__ == "__main__":
    run_tests()
