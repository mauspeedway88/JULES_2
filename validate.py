import json
import re
import sys
import unicodedata

def test_json():
    try:
        with open("NET_brain_01.json", "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error loading JSON: {e}")
        return False

    if len(data) != 50:
        print(f"Error: Se esperaban 50 elementos, se encontraron {len(data)}")
        return False

    stopwords = {'el', 'la', 'los', 'las', 'un', 'una', 'unos', 'unas', 'de', 'del', 'a', 'ante', 'bajo', 'con', 'contra', 'desde', 'en', 'entre', 'hacia', 'hasta', 'para', 'por', 'segun', 'sin', 'sobre', 'tras', 'y', 'e', 'ni', 'o', 'u', 'pero', 'mas', 'sino', 'que'}

    for item in data:
        intent_id = item.get("intent_id", "")
        keywords = item.get("keywords", [])
        base_response = item.get("base_response", "")

        # Validar intent_id
        if not re.match(r'^[a-z_]+$', intent_id):
            print(f"Error en intent_id: {intent_id}")
            return False

        # Validar keywords
        if not (4 <= len(keywords) <= 6):
            print(f"Error en cantidad de keywords para {intent_id}: {keywords}")
            return False

        for kw in keywords:
            if not kw.isalpha() or not kw.islower():
                print(f"Error en keyword no alfabético o no minúscula: '{kw}' en {intent_id}")
                return False

            kw_clean = ''.join(c for c in unicodedata.normalize('NFD', kw) if unicodedata.category(c) != 'Mn')
            if kw != kw_clean:
                print(f"Error en keyword con tilde: '{kw}' en {intent_id}")
                return False

            if kw in stopwords:
                print(f"Error, keyword es una stopword: '{kw}' en {intent_id}")
                return False

        # Validar conteo de palabras base_response
        words = re.findall(r'\b\w+\b', base_response)
        if len(words) < 35 or len(words) > 50:
            print(f"Error en conteo de palabras ({len(words)}) para {intent_id}:\n{base_response}")
            return False

    print("Todas las validaciones pasaron exitosamente.")
    return True

if __name__ == "__main__":
    if not test_json():
        sys.exit(1)
    sys.exit(0)
