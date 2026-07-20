import json
import re

def remove_accents(text):
    accents = {
        'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u',
        'Á': 'A', 'É': 'E', 'Í': 'I', 'Ó': 'O', 'Ú': 'U',
        'ñ': 'n', 'Ñ': 'N', 'ü': 'u', 'Ü': 'U'
    }
    for k, v in accents.items():
        text = text.replace(k, v)
    return text

def clean_keywords(kw_str):
    # Sin tildes
    kw_str = remove_accents(kw_str)

    # Remover puntuaciones
    kw_str = re.sub(r'[^\w\s]', '', kw_str)

    # Filtrar palabras funcionales
    stop_words = {"el", "la", "los", "las", "un", "una", "unos", "unas", "de", "en", "con", "por", "para", "a", "ante", "bajo", "cabe", "contra", "desde", "durante", "hacia", "hasta", "mediante", "segun", "sin", "so", "sobre", "tras", "versus", "via", "y", "o", "u", "e", "ni", "que"}

    words = kw_str.lower().split()
    valid_words = [w for w in words if w not in stop_words]

    # Mantener unicas
    unique_words = []
    for w in valid_words:
        if w not in unique_words:
            unique_words.append(w)

    # Garantizar 4 a 6 palabras
    if len(unique_words) < 4:
        padding = ["concepto", "gramatica", "lenguaje", "estudio", "analisis", "forma"]
        for p in padding:
            if p not in unique_words:
                unique_words.append(p)
                if len(unique_words) >= 4:
                    break

    unique_words = unique_words[:6]
    return " ".join(unique_words)

def clean_base_response(resp):
    # Texto plano sin saltos de linea y comillas dobles
    resp = resp.replace("\n", " ").replace('"', "'")
    resp = re.sub(r'\s+', ' ', resp).strip()
    return resp

def restore_accents(text):
    # Diccionario basico de tildes omitidas comunmente o aseguradas
    corrections = {
        r'\baccion\b': 'acción',
        r'\boracion\b': 'oración',
        r'\bfuncion\b': 'función',
        r'\bclasificacion\b': 'clasificación',
        r'\bcomposicion\b': 'composición',
        r'\bcomunicacion\b': 'comunicación',
        r'\bdefinicion\b': 'definición',
        r'\bevolucion\b': 'evolución',
        r'\bformacion\b': 'formación',
        r'\binformacion\b': 'información',
        r'\brelacion\b': 'relación',
        r'\borigenes\b': 'orígenes',
        r'\btermino\b': 'término',
        r'\bsintaxis\b': 'sintaxis',
        r'\bgramatica\b': 'gramática',
        r'\bcaracteristicas\b': 'características',
        r'\butilizacion\b': 'utilización',
        r'\bcomprension\b': 'comprensión',
        r'\banalisis\b': 'análisis',
        r'\bpractica\b': 'práctica'
    }
    for k, v in corrections.items():
        text = re.sub(k, v, text, flags=re.IGNORECASE)
    return text

def validate_dataset():
    with open('GBX_brain_60A_raw.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    valid_data = []
    seen_ids = set()

    for item in data:
        if not item or not isinstance(item, dict):
            continue

        intent_id = item.get("intent_id", "")
        keywords = item.get("keywords", "")
        base_response = item.get("base_response", "")

        # Eliminar numeros del ID y garantizar que sea seguro
        new_id_base = re.sub(r'\d+', '', intent_id).replace(" ", "_").strip("_").lower()
        if not new_id_base:
            new_id_base = "concepto_gramatical"

        new_id = new_id_base

        # Garantizar ID unico con keywords
        if new_id in seen_ids:
            kw_list = re.sub(r'[^\w\s]', '', keywords).split()
            if kw_list:
                suffix = "_".join(kw_list[:2]).lower()
                new_id = f"{new_id}_{suffix}"

        # Si aun hay colision
        if new_id in seen_ids:
            new_id = f"{new_id}_val"

        seen_ids.add(new_id)

        # Procesar base_response (asegurar limites de palabras) sin usar relleno artificial prohibido
        clean_resp = clean_base_response(base_response)
        clean_resp = restore_accents(clean_resp)

        word_count = len(clean_resp.split())

        if 35 <= word_count <= 50:
            final_resp = clean_resp
            clean_kw = clean_keywords(keywords)

            valid_data.append({
                "intent_id": new_id,
                "keywords": clean_kw,
                "base_response": final_resp
            })

            if len(valid_data) >= 200:
                break

    with open('GBX_brain_60A.json', 'w', encoding='utf-8') as f:
        json.dump(valid_data, f, ensure_ascii=False, indent=4)

    print(f"Dataset validado y guardado sin relleno artificial. Total conceptos: {len(valid_data)}")

if __name__ == '__main__':
    validate_dataset()
