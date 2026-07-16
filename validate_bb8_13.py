# -*- coding: utf-8 -*-
import json
import re
import unicodedata
import sys

STOPWORDS = set("""
de la que el en y a los se del las un por con no una su para al lo como
mas pero sus le ya o este si porque esta entre cuando muy sin sobre tambien
me hasta hay donde quien desde todo nos durante todos uno les ni contra otros
ese eso ante ellos e esto mi antes algunos que sus o pero fue fueron ser era
son es han ha sido estan esta habia hecho anos parte tiempo gran forma mayor
solo otras aunque hacia cual cada otros esto luego cual despues vez tan asi
un unas unos de del al con por para en sobre desde hacia hasta para
por sin tras durante mediante o u y e que quien como donde cuando cual cuales
este esta esto estos estas ese esa eso esos esas aquel aquella aquello aquellos
aquellas mi mis tu tus su sus nuestro nuestra nuestros nuestras vuestro vuestra
vuestros vuestras
""".split())

def remove_accents(input_str):
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    return u"".join([c for c in nfkd_form if not unicodedata.combining(c)])

def clean_word(w):
    w = w.lower()
    w = remove_accents(w)
    w = re.sub(r'[^a-z]', '', w)
    return w

def validate():
    file_path = "BB8_brain_13.json"
    print(f"Loading {file_path} for strict validation...")

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"FAIL: Not valid JSON. Error: {e}")
        sys.exit(1)

    print(f"Total concepts found: {len(data)}")
    if len(data) != 600:
        print(f"FAIL: Total concepts is {len(data)}, expected exactly 600.")
        sys.exit(1)

    seen_intents = set()
    seen_responses = set()

    for idx, item in enumerate(data):
        # check keys
        keys = set(item.keys())
        expected_keys = {"intent_id", "keywords", "base_response"}
        if keys != expected_keys:
            print(f"FAIL: Item {idx} has invalid keys: {keys}")
            sys.exit(1)

        intent_id = item["intent_id"]
        keywords = item["keywords"]
        base_response = item["base_response"]

        # Check intent_id
        if not intent_id:
            print(f"FAIL: Item {idx} has empty intent_id.")
            sys.exit(1)
        if intent_id != intent_id.lower():
            print(f"FAIL: Item {idx} has non-lowercase intent_id: {intent_id}")
            sys.exit(1)
        if not re.match(r'^[a-z0-9_]+$', intent_id):
            print(f"FAIL: Item {idx} has non-alphanumeric/underscore intent_id: {intent_id}")
            sys.exit(1)
        if intent_id in seen_intents:
            print(f"FAIL: Duplicate intent_id: {intent_id}")
            sys.exit(1)
        seen_intents.add(intent_id)

        # Check keywords
        if not (4 <= len(keywords) <= 6):
            print(f"FAIL: Item {idx} ({intent_id}) has {len(keywords)} keywords, expected 4 to 6.")
            sys.exit(1)

        for kw in keywords:
            if kw != kw.lower():
                print(f"FAIL: Item {idx} has non-lowercase keyword: '{kw}'")
                sys.exit(1)
            if remove_accents(kw) != kw:
                print(f"FAIL: Item {idx} has keyword with accents/tildes: '{kw}'")
                sys.exit(1)
            if re.sub(r'[^a-z]', '', kw) != kw:
                print(f"FAIL: Item {idx} has keyword with invalid characters: '{kw}'")
                sys.exit(1)
            if kw in STOPWORDS:
                print(f"FAIL: Item {idx} has keyword that is a stopword: '{kw}'")
                sys.exit(1)

        # Check base_response
        words = base_response.split()
        wc = len(words)
        if not (35 <= wc <= 50):
            print(f"FAIL: Item {idx} ({intent_id}) has {wc} words, expected 35 to 50. Text: '{base_response}'")
            sys.exit(1)

        # check greetings and references
        for bad in ["hola", "claro", "recuerda", "segun wikipedia", "en internet"]:
            if bad in base_response.lower():
                print(f"FAIL: Item {idx} has blacklisted word/phrase '{bad}': '{base_response}'")
                sys.exit(1)

        if base_response in seen_responses:
            print(f"FAIL: Duplicate base_response: '{base_response}'")
            sys.exit(1)
        seen_responses.add(base_response)

        # check end punctuation
        if not base_response.endswith(".") and not base_response.endswith("!"):
            print(f"FAIL: Item {idx} does not end with proper punctuation: '{base_response}'")
            sys.exit(1)

    print("SUCCESS: All 600 concepts strictly adhere to all constraints and guidelines!")

if __name__ == "__main__":
    validate()
