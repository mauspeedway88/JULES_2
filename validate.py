import json
import re

INPUT_FILE = "GBX_brain_60B.json"
OUTPUT_FILE = "GBX_brain_60B.json"

# Stop words a eliminar
STOP_WORDS = {'el', 'la', 'los', 'las', 'un', 'una', 'unos', 'unas', 'de', 'en', 'a', 'ante', 'bajo', 'con', 'contra', 'desde', 'durante', 'entre', 'hacia', 'hasta', 'mediante', 'para', 'por', 'segun', 'sin', 'so', 'sobre', 'tras', 'y', 'e', 'ni', 'o', 'u', 'pero', 'mas', 'sino', 'aunque'}

def remove_accents(text):
    accents = {
        'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u',
        'Á': 'A', 'É': 'E', 'Í': 'I', 'Ó': 'O', 'Ú': 'U',
        'ñ': 'n', 'Ñ': 'N', 'ü': 'u', 'Ü': 'U'
    }
    for k, v in accents.items():
        text = text.replace(k, v)
    return text

def fix_accents(text):
    # Solucionamos algunos acentos comunes que puedan faltar
    replacements = {
        r'\bcomprension\b': 'comprensión',
        r'\bexplicacion\b': 'explicación',
        r'\bfuncion\b': 'función',
        r'\baccion\b': 'acción',
        r'\boracion\b': 'oración',
        r'\boraciones\b': 'oraciones',
        r'\bmas\b': 'más',
        r'\btambien\b': 'también',
        r'\bsintactica\b': 'sintáctica',
        r'\bsemantica\b': 'semántica',
        r'\banalisis\b': 'análisis',
        r'\bclasificacion\b': 'clasificación'
    }
    for pattern, repl in replacements.items():
        text = re.sub(pattern, repl, text, flags=re.IGNORECASE)
    return text

def clean_response(text):
    # Limpiamos el response
    # Quitamos markdown artifacts si hay
    text = re.sub(r'\[\[.*?\]\]\(.*?\)', '', text)
    text = text.replace('\n', ' ').replace('"', "'")
    text = re.sub(r'\s+', ' ', text).strip()
    return fix_accents(text)

def clean_keywords(kw_str):
    if not isinstance(kw_str, str):
        kw_str = " ".join(kw_str) if isinstance(kw_str, list) else str(kw_str)
    # Reemplazamos guiones bajos por espacios en caso de que aún haya alguno
    kw_str = kw_str.replace('_', ' ')
    kw_str = remove_accents(kw_str.lower())
    words = [w for w in re.split(r'\W+', kw_str) if w and w not in STOP_WORDS]
    # Si es muy largo truncamos
    if len(words) > 6:
        words = words[:6]
    return words

def clean_intent_id(intent_str, keywords_list):
    intent_str = remove_accents(intent_str.lower())
    intent_str = re.sub(r'[^a-z_]', '_', intent_str)
    # Evitar números secuenciales o repeticiones de intent_ids
    # Como la restricción dice "0 números secuenciales", no le ponemos números
    intent_str = re.sub(r'\d+', '', intent_str)
    intent_str = re.sub(r'_+', '_', intent_str).strip('_')
    return intent_str

def main():
    try:
        with open(INPUT_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        print("No se encontró el archivo de entrada.")
        return

    valid_data = []
    seen_ids = set()

    for item in data:
        intent_id = item.get("intent_id", "")
        keywords = item.get("keywords", "")
        base_response = item.get("base_response", "")

        kw_list = clean_keywords(keywords)

        # Generar un ID único semántico basado en parte en los keywords para asegurar no repetidos
        base_id = clean_intent_id(intent_id, kw_list)
        if base_id in seen_ids or not base_id:
            base_id = f"{base_id}_{'_'.join(kw_list[:2])}"
            if base_id in seen_ids:
                base_id = f"{base_id}_{'_'.join(kw_list[2:4])}"

        # Asegurarnos de que el ID final no tenga _ repetidos
        base_id = re.sub(r'_+', '_', base_id).strip('_')

        seen_ids.add(base_id)

        c_response = clean_response(base_response)

        # Validar conteo de palabras en base_response (35 a 50)
        word_count = len(c_response.split())

        # Filtramos estrictamente a los que cumplen TODAS las condiciones:
        # - base_response entre 35 y 50 palabras
        # - keywords list debe tener entre 4 y 6 palabras sin rellenar con basura
        if 35 <= word_count <= 50 and 4 <= len(kw_list) <= 6:
             valid_data.append({
                 "intent_id": base_id,
                 "keywords": " ".join(kw_list),
                 "base_response": c_response
             })

    # Enforzar el límite estricto de máximo 200.
    final_data = valid_data[:200]

    print(f"Total de conceptos válidos tras filtrado estricto: {len(final_data)}")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(final_data, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()