import json
import spacy

nlp = spacy.load("es_core_news_sm")

def count_words(text):
    doc = nlp(text)
    return len([token for token in doc if not token.is_punct and not token.is_space])

with open('MM_brain_47.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

valid = True
for idx, item in enumerate(data):
    # Validar intent_id
    if not item['intent_id'] or item['intent_id'].isspace():
        print(f"[{idx}] intent_id invalido: {item['intent_id']}")
        valid = False

    # Validar keywords
    if len(item['keywords']) < 4 or len(item['keywords']) > 6:
        print(f"[{idx}] Número incorrecto de keywords ({len(item['keywords'])})")
        valid = False

    for kw in item['keywords']:
        if not kw.islower() or any(c in 'áéíóú' for c in kw):
            print(f"[{idx}] Keyword invalida (mayusculas o tildes): {kw}")
            valid = False

    # Validar base_response
    resp = item['base_response']
    w_count = count_words(resp)
    if not (35 <= w_count <= 50):
        print(f"[{idx}] base_response length invalido: {w_count} palabras")
        valid = False

if valid:
    print("El JSON es válido y cumple los requisitos de conteo de palabras y keywords.")
else:
    print("Existen errores en el JSON.")
