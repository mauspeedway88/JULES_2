import json
import re
import os
import time
import unidecode
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import g4f
import nest_asyncio

nest_asyncio.apply()

# 23 biological subtopics
SUBTOPICS = [
    "camuflaje protector de especies",
    "mimetismo engañoso de apariencia",
    "ectotermos de sangre fría",
    "endotermos de sangre caliente",
    "animales vivíparos de vientre",
    "animales ovovivíparos de huevos internos",
    "respiración cutánea de ranas",
    "respiración traqueal de insectos",
    "exoesqueleto de quitina protector",
    "sistema ambulacral de estrellas",
    "línea lateral de peces",
    "vejiga natatoria de flotación",
    "glándulas mamarias de alimentación",
    "dimorfismo sexual de formas",
    "feromonas de comunicación química",
    "cortejo reproductivo de parejas",
    "migración estacional de aves",
    "estivación de letargo cálido",
    "nematodos gusanos cilíndricos lisos",
    "platelmintos gusanos planos parásitos",
    "apéndices articulados de artrópodos",
    "bioluminiscencia animal de luz",
    "placenta nutritiva de fetos"
]

# 20 ontological dimensions
DIMENSIONS = [
    "Definición anatómica o estructural",
    "Dinámica y funcionamiento físico",
    "Propiedades químicas o materiales",
    "Errores, fallas y patologías comunes",
    "Historia, origen y evolución",
    "Contexto y entorno ecológico",
    "Aplicaciones prácticas en la vida real",
    "Importancia e impacto social",
    "Ventajas y desventajas comparativas",
    "Riesgos y medidas de seguridad",
    "Clasificación taxonómica",
    "Cálculos y fórmulas asociadas",
    "Mitos y concepciones erróneas",
    "Relación simbiótica con otros sistemas",
    "Transformación y ciclos energéticos",
    "Experimentos y demostraciones escolares",
    "Consecuencias a largo plazo",
    "Impacto ambiental",
    "Mantenimiento y prevención",
    "Proyecciones futuras y tecnología"
]

DEST_FILE = "GBX_brain_33B.json"

def clean_json_string(s):
    # Remove markdown formatting if any
    s = re.sub(r'```json\n|\n```|```', '', s)
    return s.strip()

def validate_concept(data):
    if not isinstance(data, dict):
        return False, "Not a dictionary"

    intent_id = data.get("intent_id", "")
    keywords = data.get("keywords", [])
    base_response = data.get("base_response", "")

    # intent_id rules
    if not isinstance(intent_id, str) or not intent_id:
        return False, "intent_id empty or not string"
    if not re.match(r'^[a-z_]+$', intent_id):
        return False, "intent_id must be lowercase, underscores, no numbers"

    # keywords rules
    if not isinstance(keywords, list):
        return False, "keywords must be a list"
    if not (4 <= len(keywords) <= 6):
        return False, "keywords length must be 4 to 6"
    for kw in keywords:
        if not isinstance(kw, str) or not kw:
            return False, "keyword must be a non-empty string"
        if not re.match(r'^[a-z\s]+$', kw):
            return False, f"keyword '{kw}' contains non-lowercase-alpha chars"
        if re.search(r'[áéíóú]', kw):
            return False, f"keyword '{kw}' contains tildes"
        # basic stopword check
        if kw in ['el', 'la', 'los', 'las', 'un', 'una', 'unos', 'unas', 'de', 'en', 'con', 'por', 'para']:
            return False, f"keyword '{kw}' is a stopword"

    # base_response rules
    if not isinstance(base_response, str):
        return False, "base_response must be a string"
    base_response = base_response.strip()
    words = base_response.split()
    if not (35 <= len(words) <= 50):
        return False, f"base_response length ({len(words)} words) not in 35-50 range"
    if '\n' in base_response:
        return False, "base_response contains newlines"
    if '"' in base_response:
        return False, "base_response contains double quotes"
    if not re.search(r'[áéíóúÁÉÍÓÚ]', base_response):
        return False, "base_response missing tildes (acentos)"

    return True, "Valid"

def generate_concept(subtopic, dimension, existing_intents):
    prompt = f"""
    Eres un especialista en minería de datos educativos.
    Genera un concepto educativo para estudiantes de 9 a 15 años.
    Tema: {subtopic}
    Dimensión: {dimension}

    Reglas:
    - Si esta dimensión NO aplica o no tiene información científica real para este tema, responde exactamente con la palabra: OMITE
    - En caso contrario, responde ÚNICAMENTE con un JSON válido. NINGÚN texto antes o después.

    Estructura JSON:
    {{
        "intent_id": "identificador_unico_semantico_del_tema_y_dimension",
        "keywords": ["sustantivo", "verbo", "sustantivo_dos", "verbo_dos"],
        "base_response": "Texto educativo directo."
    }}

    Restricciones ESTRICTAS:
    - intent_id: Todo minúscula, separado por guiones bajos, CERO NÚMEROS. Único en el contexto. No uses un id que ya exista: {', '.join(list(existing_intents)[-5:]) if existing_intents else 'ninguno_todavia'}.
    - keywords: Exactamente de 4 a 6 palabras. Todo minúscula, SIN TILDES, SIN ACENTOS. SOLO sustantivos y verbos relevantes. NADA de artículos o preposiciones (no uses "el", "de", etc).
    - base_response: Exactamente entre 35 y 50 palabras de longitud. NO uses comillas dobles ("). NO uses saltos de línea. ASEGÚRATE DE INCLUIR LAS TILDES (á, é, í, ó, ú) con ortografía inmaculada. Tono instruccional directo, sin saludos ni despedidas, entra directo a la carga de conocimiento real. No uses frases de cierre repetitivas ni relleno.

    Genera ahora:
    """

    try:
        response = g4f.ChatCompletion.create(
            model=g4f.models.default,
            messages=[{"role": "user", "content": prompt}]
        )
        if not response:
            return None, "Empty response"

        if "OMITE" in response.upper()[:20]:
            return None, "Dimension not applicable (OMITE)"

        json_str = clean_json_string(response)
        data = json.loads(json_str)
        return data, "Success"
    except Exception as e:
        return None, str(e)

def main():
    dataset = []
    existing_intents = set()
    existing_texts = []

    if os.path.exists(DEST_FILE):
        with open(DEST_FILE, 'r', encoding='utf-8') as f:
            try:
                dataset = json.load(f)
                for item in dataset:
                    existing_intents.add(item['intent_id'])
                    existing_texts.append(item['base_response'])
            except:
                pass

    vectorizer = TfidfVectorizer()

    print(f"Starting generation. Found {len(dataset)} existing items.")

    for subtopic in SUBTOPICS:
        for dimension in DIMENSIONS:
            print(f"Processing: {subtopic} - {dimension}")

            # Simple check to see if we already covered something very similar
            id_guess_base = unidecode.unidecode(f"{subtopic}_{dimension}").lower().replace(' ', '_')
            id_guess_base = re.sub(r'[^a-z_]', '', id_guess_base)

            # Try a few times per combination
            success = False
            for attempt in range(3):
                data, msg = generate_concept(subtopic, dimension, existing_intents)

                if data is None:
                    if msg == "Dimension not applicable (OMITE)":
                        print("  -> Skipped (OMITE)")
                        break # Go to next dimension
                    else:
                        print(f"  -> Attempt {attempt+1} failed: {msg}")
                        time.sleep(1)
                        continue

                is_valid, val_msg = validate_concept(data)
                if not is_valid:
                    print(f"  -> Validation failed: {val_msg}")
                    continue

                # Deduplication check
                if existing_texts:
                    texts_to_check = existing_texts + [data['base_response']]
                    tfidf_matrix = vectorizer.fit_transform(texts_to_check)
                    similarities = cosine_similarity(tfidf_matrix[-1:], tfidf_matrix[:-1])
                    max_sim = similarities[0].max() if len(similarities[0]) > 0 else 0
                    if max_sim > 0.8:
                        print(f"  -> Text too similar to existing (sim: {max_sim:.2f})")
                        continue

                if data['intent_id'] in existing_intents:
                    print(f"  -> Intent ID collision: {data['intent_id']}")
                    data['intent_id'] = data['intent_id'] + "_" + unidecode.unidecode(subtopic.split()[0].lower())
                    if data['intent_id'] in existing_intents:
                        continue

                # All good
                dataset.append(data)
                existing_intents.add(data['intent_id'])
                existing_texts.append(data['base_response'])
                print(f"  -> Added {data['intent_id']} (Total: {len(dataset)})")

                # Save incrementally
                with open(DEST_FILE, 'w', encoding='utf-8') as f:
                    json.dump(dataset, f, ensure_ascii=False, indent=4)

                success = True
                break

            time.sleep(0.5)

    print(f"Finished generation. Total concepts: {len(dataset)}")

if __name__ == "__main__":
    main()
