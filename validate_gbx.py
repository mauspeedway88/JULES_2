import json
import re
import sys

# Blacklisted conversational words or phrases
BLACKLIST = [
    "hola", "claro", "recuerda", "segun wikipedia", "en internet", "wikipedia",
    "como sabemos", "como sabras", "como ya sabes", "por supuesto", "bienvenido"
]

# Stop words in Spanish that are strictly forbidden in keywords
STOP_WORDS = {
    # Articles
    "el", "la", "los", "las", "un", "una", "unos", "unas", "lo", "al", "del",
    # Prepositions
    "a", "ante", "bajo", "cabe", "con", "contra", "de", "desde", "durante", "en", "entre", "hacia", "hasta", "mediante", "para", "por", "segun", "sin", "so", "sobre", "tras", "versus", "via",
    # Conjunctions
    "y", "o", "u", "e", "ni", "que", "pero", "sino", "aunque", "porque", "como", "cuando", "donde", "quien", "cual", "cuyo",
    # Pronouns & determiners
    "yo", "tu", "el", "ella", "ello", "nosotros", "nosotras", "vosotros", "vosotras", "ellos", "ellas", "este", "esta", "esto", "estos", "estas", "ese", "esa", "eso", "esos", "esas", "aquel", "aquella", "aquello", "aquellos", "aquellas", "mi", "mis", "tu", "tus", "su", "sus", "nuestro", "nuestra", "nuestros", "nuestras", "vuestro", "vuestra", "vuestros", "vuestras", "me", "te", "se", "nos", "os", "le", "les", "lo", "la", "los", "las",
    # Adverbs & others (commonly function words)
    "si", "no", "mas", "muy", "tan", "tambien", "tampoco", "ya", "aun", "ahora", "despues", "entonces", "luego", "asi", "bien", "mal", "siempre", "nunca", "jamas"
}

def clean_word(word):
    # Strip punctuation
    return re.sub(r'[^\w]', '', word).lower()

def validate_dataset(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: File {filepath} not found.")
        return False
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON in {filepath}: {e}")
        return False

    if not isinstance(data, list):
        print("Error: Dataset root must be a list of concepts.")
        return False

    print(f"Loaded {len(data)} concepts from {filepath}.")

    intent_ids = set()
    errors = []

    for idx, item in enumerate(data):
        concept_ref = f"Concept #{idx+1}"

        # Check required keys
        for key in ["intent_id", "keywords", "base_response"]:
            if key not in item:
                errors.append(f"{concept_ref} is missing required key '{key}'")
                continue

        if len(errors) > len(data) * 2: # Stop early if completely broken
            break

        intent_id = item.get("intent_id", "")
        keywords = item.get("keywords", [])
        base_response = item.get("base_response", "")

        concept_ref = f"Concept '{intent_id}' at index {idx}"

        # 1. Validate intent_id
        if not isinstance(intent_id, str):
            errors.append(f"{concept_ref}: 'intent_id' must be a string")
        else:
            # Must be unique
            if intent_id in intent_ids:
                errors.append(f"{concept_ref}: 'intent_id' '{intent_id}' is not unique")
            intent_ids.add(intent_id)

            # Lowercase, separated by underscores
            if not re.match(r'^[a-z_]+$', intent_id):
                errors.append(f"{concept_ref}: 'intent_id' '{intent_id}' must only contain lowercase letters and underscores")

            # Zero sequential or suffix numbers (no numeric digits at all)
            if any(char.isdigit() for char in intent_id):
                errors.append(f"{concept_ref}: 'intent_id' '{intent_id}' contains numeric characters (forbidden)")

        # 2. Validate keywords
        if not isinstance(keywords, list):
            errors.append(f"{concept_ref}: 'keywords' must be a list")
        else:
            # Exactly 4-6 words
            if len(keywords) < 4 or len(keywords) > 6:
                errors.append(f"{concept_ref}: 'keywords' length is {len(keywords)}, must be exactly 4-6 words")

            # Unique words in the keywords list
            if len(keywords) != len(set(keywords)):
                errors.append(f"{concept_ref}: 'keywords' contains duplicate words")

            for kw in keywords:
                if not isinstance(kw, str):
                    errors.append(f"{concept_ref}: keyword '{kw}' is not a string")
                    continue

                # Lowercase only
                if kw != kw.lower():
                    errors.append(f"{concept_ref}: keyword '{kw}' is not lowercase")

                # Absence of accents/tildes
                if any(char in "áéíóúüñ" for char in kw):
                    # Check for accents/tildes specifically
                    if any(char in "áéíóúü" for char in kw):
                        errors.append(f"{concept_ref}: keyword '{kw}' contains accents/tildes")

                # Absence of stop words
                if kw in STOP_WORDS:
                    errors.append(f"{concept_ref}: keyword '{kw}' is a forbidden stop word")

        # 3. Validate base_response
        if not isinstance(base_response, str):
            errors.append(f"{concept_ref}: 'base_response' must be a string")
        else:
            # Word count: exactly 35-50 words
            words = base_response.strip().split()
            word_count = len(words)
            if word_count < 35 or word_count > 50:
                errors.append(f"{concept_ref}: 'base_response' word count is {word_count}, must be exactly 35-50 words. Response: '{base_response}'")

            # Flat text with no internal line breaks
            if "\n" in base_response or "\r" in base_response:
                errors.append(f"{concept_ref}: 'base_response' contains internal line breaks")

            # Check blacklist
            base_lower = base_response.lower()
            for forbidden in BLACKLIST:
                if forbidden in base_lower:
                    errors.append(f"{concept_ref}: 'base_response' contains blacklisted conversational word/phrase '{forbidden}'")

    if errors:
        print(f"\nValidation failed with {len(errors)} errors:")
        for err in errors[:50]:
            print(f" - {err}")
        if len(errors) > 50:
            print(f" ... and {len(errors) - 50} more errors.")
        return False
    else:
        print("\nValidation passed successfully! All rules are strictly obeyed.")
        return True

if __name__ == "__main__":
    target = "GBX_brain_02A.json"
    if len(sys.argv) > 1:
        target = sys.argv[1]
    success = validate_dataset(target)
    sys.exit(0 if success else 1)
