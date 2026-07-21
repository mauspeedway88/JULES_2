import json
import re

ARCHIVO_DESTINO = "GBX_brain_68A.json"

# Stop words a eliminar en las keywords
STOP_WORDS = {"el", "la", "los", "las", "un", "una", "unos", "unas", "de", "del", "a", "al", "en", "por", "para", "con", "sin", "sobre", "entre", "hacia", "hasta", "desde"}

# Mapeo simple para quitar tildes
def remove_accents(text):
    text = text.replace('á', 'a').replace('é', 'e').replace('í', 'i').replace('ó', 'o').replace('ú', 'u')
    return text.replace('Á', 'a').replace('É', 'e').replace('Í', 'i').replace('Ó', 'o').replace('Ú', 'u')

# Mapeo simple de correcciones ortográficas (acentos faltantes mas comunes)
# (Si bien le pedimos a GPT que los ponga, a veces falla. Usamos regex para asegurar)
CORRECTIONS = {
    r'\bcomprension\b': 'comprensión',
    r'\bcomunicacion\b': 'comunicación',
    r'\boracion\b': 'oración',
    r'\baccion\b': 'acción',
    r'\bexplicacion\b': 'explicación',
    r'\bfuncion\b': 'función',
    r'\bclasificacion\b': 'clasificación',
    r'\bconjugacion\b': 'conjugación',
    r'\bingles\b': 'inglés',
    r'\bingleses\b': 'ingleses',
    r'\braiz\b': 'raíz',
    r'\bterminacion\b': 'terminación',
    r'\berronea\b': 'errónea',
    r'\bpractica\b': 'práctica',
    r'\btecnologica\b': 'tecnológica',
    r'\basociacion\b': 'asociación',
    r'\bformacion\b': 'formación',
    r'\baplicacion\b': 'aplicación'
}

def clean_base_response(text):
    # Formateo general sin saltos de linea ni comillas dobles sin escapar (sustituidas por simples)
    text = text.replace('\n', ' ').replace('"', "'")
    # Restaurar algunas tildes comunes
    for pattern, replacement in CORRECTIONS.items():
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    return text.strip()

def clean_keywords(text):
    words = text.lower().split()
    # Filtrar stopwords
    words = [w for w in words if w not in STOP_WORDS]
    # Quitar comas y caracteres raros, y tildes
    words = [remove_accents(re.sub(r'[^a-zñ]', '', w)) for w in words]
    words = [w for w in words if w]
    return ' '.join(words[:6]) # Limitar a 6

def clean_intent_id(text, keywords_str):
    # Sin secuencias, solo minusculas y guiones bajos
    text = text.lower()
    text = re.sub(r'[0-9]', '', text)
    text = remove_accents(text)
    # Reconstruir un ID unico en caso de que sea el mismo
    return text.strip('_')

def validate_and_clean():
    try:
        with open(ARCHIVO_DESTINO, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error cargando JSON: {e}")
        return

    validated_data = []
    seen_ids = set()

    for item in data:
        # Validación y limpieza de campos
        kw = clean_keywords(item.get('keywords', ''))
        br = clean_base_response(item.get('base_response', ''))

        # Validar conteo de palabras 35-50 (permitiendo algo flexible por calidad, pero filtrando muy cortos)
        word_count = len(br.split())
        if word_count < 30:
            continue

        # Procesar intent_id
        iid = clean_intent_id(item.get('intent_id', ''), kw)

        # Garantizar que el ID es unico sin usar numeros
        if iid in seen_ids or not iid:
            kw_parts = kw.split()
            if len(kw_parts) >= 2:
                iid = f"{iid}_{kw_parts[0]}_{kw_parts[1]}"
            if iid in seen_ids:
                continue # Saltar si aun asi es duplicado

        seen_ids.add(iid)

        validated_data.append({
            "intent_id": iid,
            "keywords": kw,
            "base_response": br
        })

        if len(validated_data) >= 175:
            break

    # Escribir el nuevo JSON limpio
    with open(ARCHIVO_DESTINO, 'w', encoding='utf-8') as f:
        json.dump(validated_data, f, ensure_ascii=False, indent=4)

    print(f"Post-procesamiento completado. Total de conceptos validados: {len(validated_data)}")

if __name__ == "__main__":
    validate_and_clean()
