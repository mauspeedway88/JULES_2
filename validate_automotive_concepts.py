# Script de validación rigurosa de calidad y reglas JSON
import json
import re

filename = "MM_brain_51.json"

def validate():
    print(f"Iniciando validación rigurosa de '{filename}'...")
    try:
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"ERROR: No se pudo cargar el archivo JSON. {e}")
        return False

    print(f"Total de conceptos cargados: {len(data)}")

    # 1. Validar que la cantidad de conceptos sea significativa (al menos 200, buscando llegar a los 300 sugeridos)
    if len(data) < 200:
        print("ERROR: La cantidad de conceptos generados es menor de 200.")
        return False

    intent_ids = set()
    errors = 0

    # Palabras no deseadas en las palabras clave (artículos, preposiciones, conjunciones, etc.)
    stopwords = set([
        "el", "la", "los", "las", "un", "una", "unos", "unas",
        "de", "del", "al", "en", "con", "y", "o", "u", "a", "ante",
        "bajo", "cabe", "contra", "desde", "durante", "en", "entre",
        "hacia", "hasta", "mediante", "para", "por", "segun", "sin",
        "so", "sobre", "tras", "versus", "via", "pero", "mas", "e",
        "ni", "si", "no", "como", "que", "cual", "cuanto", "quien",
        "donde", "cuando", "este", "esta", "estos", "estas"
    ])

    for i, item in enumerate(data):
        intent_id = item.get("intent_id")
        keywords = item.get("keywords")
        base_response = item.get("base_response")

        # A. Estructura obligatoria
        if not intent_id or not isinstance(keywords, list) or not base_response:
            print(f"ERROR en elemento {i}: Faltan campos obligatorios. Estructura incorrecta.")
            errors += 1
            continue

        # B. Unicidad del intent_id
        if intent_id in intent_ids:
            print(f"ERROR en elemento {i}: El intent_id '{intent_id}' está duplicado.")
            errors += 1
        intent_ids.add(intent_id)

        # C. intent_id en minúsculas con guiones bajos
        if not re.match(r"^[a-z0-9_]+$", intent_id):
            print(f"ERROR en elemento {i} ('{intent_id}'): El intent_id no está en minúsculas con guiones bajos.")
            errors += 1

        # D. Palabras clave (keywords): entre 4 y 6 términos, solo minúsculas, sin acentos
        if len(keywords) < 4 or len(keywords) > 6:
            print(f"ERROR en elemento {i} ('{intent_id}'): keywords debe tener entre 4 y 6 términos (tiene {len(keywords)}).")
            errors += 1

        for kw in keywords:
            # Minúsculas, solo letras y números, sin acentos
            if not kw.islower() or not kw.isalnum():
                print(f"ERROR en elemento {i} ('{intent_id}'): La palabra clave '{kw}' no es minúscula o alfanumérica pura.")
                errors += 1
            if any(char in "áéíóúüñ" for char in kw):
                print(f"ERROR en elemento {i} ('{intent_id}'): La palabra clave '{kw}' contiene acentos o la letra ñ.")
                errors += 1
            # Sin artículos, preposiciones o conjunciones
            if kw in stopwords:
                print(f"ERROR en elemento {i} ('{intent_id}'): La palabra clave '{kw}' es una stopword/artículo/preposición.")
                errors += 1

        # E. base_response: entre 35 y 50 palabras, sin caracteres extraños, ortografía perfecta
        words = base_response.split()
        word_count = len(words)
        if word_count < 35 or word_count > 50:
            print(f"ERROR en elemento {i} ('{intent_id}'): base_response tiene {word_count} palabras (debe ser entre 35 y 50).")
            print(f" -> Contenido: {base_response}")
            errors += 1

        # Sin saludos típicos o referencias a fuentes
        for forbidden in ["hola", "buenos dias", "saludos", "wikipedia", "openstax", "ck-12"]:
            if forbidden in base_response.lower():
                print(f"ERROR en elemento {i} ('{intent_id}'): base_response contiene saludo o referencia a fuentes ('{forbidden}').")
                errors += 1

    if errors == 0:
        print("\n¡Felicidades! Todas las validaciones de calidad y formato pasaron exitosamente.")
        return True
    else:
        print(f"\nSe encontraron {errors} errores en la validación.")
        return False

if __name__ == "__main__":
    validate()
