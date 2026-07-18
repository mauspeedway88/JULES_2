import json
import re

with open("GBX_brain_46B.json", "r", encoding="utf-8") as f:
    data = json.load(f)

errors = []
for i, item in enumerate(data):
    intent_id = item.get("intent_id", "")
    if re.search(r'\d+$', intent_id) or re.search(r'_\d+', intent_id):
        errors.append(f"Row {i}: Invalid intent_id {intent_id}")

    kws = item.get("keywords", [])
    if not (4 <= len(kws) <= 6):
        errors.append(f"Row {i}: Invalid keywords length {len(kws)}")

    base_response = item.get("base_response", "")
    word_count = len(re.findall(r'\b\w+\b', base_response))
    if not (35 <= word_count <= 50):
        errors.append(f"Row {i}: Invalid base_response word count {word_count}")
    if "\n" in base_response:
        errors.append(f"Row {i}: Newlines in base_response")

    seen = set()
    for kw in kws:
        if kw in seen:
            errors.append(f"Row {i}: Duplicate keyword {kw}")
        seen.add(kw)

if errors:
    print(f"Validation failed with {len(errors)} errors:")
    for err in errors[:10]:
        print(err)
    exit(1)
else:
    print(f"All {len(data)} requirements met.")
