import g4f
import json
import os
import re
import time
from g4f.client import Client

SUBTOPICS = [
    "cavidad anatómica del tórax", "región anatómica del abdomen", "estructura de columna vertebral",
    "estructura ósea de costillas", "estructura ósea de pelvis", "músculo respiratorio del diafragma",
    "hueso esternón del tórax", "vértebras dorsales del tronco", "vértebras lumbares del tronco",
    "hueso sacro de pelvis", "hueso cóccix del tronco", "costillas verdaderas del tórax",
    "costillas falsas del tórax", "costillas flotantes del tórax", "cartílagos costales del tórax",
    "músculo pectoral del tronco", "músculos intercostales del tórax", "músculo recto del abdomen",
    "músculos oblicuos del abdomen", "músculo transverso del abdomen", "músculo dorsal ancho torácico",
    "músculo trapecio del tronco", "músculo romboides del tronco", "región umbilical del abdomen",
    "región epigástrica del abdomen", "región hipogástrica del abdomen"
]

DIMENSIONS = [
    ("Definición anatómica o estructural", "definicion"),
    ("Dinámica y funcionamiento físico", "dinamica"),
    ("Propiedades químicas o materiales", "quimica"),
    ("Errores, fallas y patologías comunes", "patologias"),
    ("Historia, origen y evolución", "evolucion"),
    ("Aplicaciones prácticas en la vida real", "aplicaciones"),
    ("Importancia e impacto social", "impacto"),
    ("Ventajas y desventajas comparativas", "ventajas"),
    ("Riesgos y medidas de seguridad", "riesgos"),
    ("Relación simbiótica con otros sistemas", "simbiosis"),
    ("Mantenimiento y prevención", "mantenimiento"),
    ("Contexto y entorno ecológico", "ecologia"),
    ("Mitos y concepciones erróneas", "mitos")
]

OUTPUT_FILE = "GBX_brain_36A.json"

def clean_text(text):
    text = text.replace('"', '\\"')
    text = text.replace('\n', ' ')
    return text.strip()

def strip_accents(s):
    replacements = (
        ("á", "a"), ("é", "e"), ("í", "i"), ("ó", "o"), ("ú", "u"),
        ("Á", "a"), ("É", "e"), ("Í", "i"), ("Ó", "o"), ("Ú", "u"),
        ("ñ", "n"), ("Ñ", "n")
    )
    for a, b in replacements:
        s = s.replace(a, b)
    return s

def remove_stopwords(words):
    stopwords = {"el", "la", "los", "las", "un", "una", "unos", "unas", "de", "del", "a", "al", "en", "por", "para", "con", "sin", "sobre", "y", "o", "u", "e", "que", "como", "su", "sus", "son"}
    return [w for w in words if w not in stopwords and len(w) > 2]

def get_base_intent_id(subtopic, dim_key):
    sub = strip_accents(subtopic.lower()).replace(" ", "_")
    return f"anatomia_{sub}_{dim_key}"

def generate_entry(client, subtopic, dimension_name, dimension_key):
    prompt = f"""
    Eres un experto en anatomía educativa para adolescentes. Escribe 1 concepto.
    Tema: "{subtopic}"
    Dimensión: "{dimension_name}"

    Reglas estrictas:
    - SI ESTA DIMENSIÓN NO TIENE SENTIDO (ej: propiedades químicas de un músculo), RESPONDE ÚNICAMENTE CON LA PALABRA "OMITIR". No intentes forzarla.
    - RESPUESTA EN FORMATO JSON EXACTO:
    {{
        "keywords": ["palabra_uno", "palabra_dos", "palabra_tres", "palabra_cuatro", "palabra_cinco"],
        "base_response": "Texto aquí."
    }}

    1. keywords: Entre 4 y 6 palabras. MINÚSCULAS. SIN TILDES. SIN ARTÍCULOS O PREPOSICIONES. Sustantivos/verbos.
    2. base_response: EXACTAMENTE ENTRE 35 Y 50 PALABRAS. INCLUYE LAS TILDES NECESARIAS. Texto plano sin saltos de línea ni comillas dobles internas. Directo al punto.

    Escribe únicamente el JSON, nada más.
    """

    try:
        response = client.chat.completions.create(
            model=g4f.models.default,
            messages=[{"role": "user", "content": prompt}]
        )
        content = response.choices[0].message.content.strip()

        if "OMITIR" in content.upper() or "omitir" in content.lower():
            return None

        match = re.search(r'\{.*\}', content, re.DOTALL)
        if match:
            json_str = match.group(0)
            data = json.loads(json_str)

            words = data["base_response"].split()
            if 35 <= len(words) <= 50:
                kws = [strip_accents(k.lower()) for k in data["keywords"]]
                kws = remove_stopwords(kws)
                if 4 <= len(kws) <= 6:
                    # Enforce accents check programmatically
                    if not re.search(r'[áéíóúÁÉÍÓÚ]', data["base_response"]):
                        # Retry if missing accents
                        return None
                    return {
                        "intent_id": get_base_intent_id(subtopic, dimension_key),
                        "keywords": kws,
                        "base_response": clean_text(data["base_response"])
                    }
    except Exception as e:
        pass
    return None

def main():
    client = Client()
    dataset = []

    if os.path.exists(OUTPUT_FILE):
        try:
            with open(OUTPUT_FILE, 'r', encoding='utf-8') as f:
                dataset = json.load(f)
            print(f"Loaded {len(dataset)} existing entries.")
        except json.JSONDecodeError:
            pass

    existing_intents = {item["intent_id"] for item in dataset}

    count = len(dataset)
    retries = 3

    for subtopic in SUBTOPICS:
        for dimension_name, dimension_key in DIMENSIONS:
            intent = get_base_intent_id(subtopic, dimension_key)
            if intent in existing_intents:
                continue

            print(f"Generating: {subtopic} - {dimension_name}...")
            data = None
            for r in range(retries):
                data = generate_entry(client, subtopic, dimension_name, dimension_key)
                if data:
                    break
                time.sleep(1)

            if data:
                if data["intent_id"] in existing_intents:
                    data["intent_id"] += "_variante"
                existing_intents.add(data["intent_id"])

                dataset.append(data)
                count += 1
                print(f"Success! Total: {count}")

                if count % 5 == 0:
                    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
                        json.dump(dataset, f, ensure_ascii=False, indent=4)

            time.sleep(1)

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(dataset, f, ensure_ascii=False, indent=4)
    print(f"Generation complete. Total entries: {len(dataset)}")

if __name__ == "__main__":
    main()
