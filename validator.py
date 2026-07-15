import json
import re

def validate_json_file(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        data = json.load(f)

    print(f"Total de conceptos: {len(data)}")

    errors = 0
    for i, item in enumerate(data):
        intent = item.get("intent_id", "")
        keywords = item.get("keywords", [])
        response = item.get("base_response", "")

        # Validar intent_id
        if not re.match(r'^[a-z0-9_]+$', intent):
            print(f"Error [{i}]: intent_id inválido -> {intent}")
            errors += 1

        # Validar keywords
        if not (4 <= len(keywords) <= 6):
            print(f"Error [{i}]: Cantidad de keywords inválida ({len(keywords)}) -> {keywords}")
            errors += 1

        for kw in keywords:
            if not re.match(r'^[a-z0-9]+$', kw):
                print(f"Error [{i}]: keyword contiene caracteres inválidos o mayúsculas -> {kw}")
                errors += 1

        # Validar base_response (35 a 50 palabras)
        word_count = len(re.findall(r'\b\w+\b', response))
        if not (35 <= word_count <= 50):
            print(f"Error [{i}]: base_response tiene cantidad de palabras inválida ({word_count}) -> {response}")
            errors += 1

    if errors == 0:
        print("¡Validación exitosa! Todos los conceptos cumplen las reglas.")
    else:
        print(f"Se encontraron {errors} errores.")

if __name__ == "__main__":
    validate_json_file("MM_brain_73.json")
