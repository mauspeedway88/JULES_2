import json
import time
import os
import re
import g4f

OUTPUT_FILE = "MM_brain_101.json"
TARGET_COUNT = 2000
BATCH_SIZE = 50

# list of subtopics
SUBTOPICS = [
    "historias bíblicas populares",
    "personajes del Antiguo Testamento",
    "personajes del Nuevo Testamento",
    "eventos del Génesis",
    "el Éxodo de Egipto",
    "curiosidades bíblicas menos conocidas",
    "pasajes bíblicos famosos",
    "explicaciones de parábolas",
    "profecías bíblicas y su contexto",
    "resumen de libros históricos de la Biblia",
    "resumen de libros proféticos",
    "vida de Jesús de Nazaret",
    "milagros de Jesús",
    "vida del apóstol Pedro",
    "vida del apóstol Pablo",
    "vida de Moisés",
    "vida del rey David",
    "vida de los apóstoles",
    "mujeres destacadas de la Biblia",
    "reyes de Israel y Judá",
    "jueces de Israel",
    "sermón del monte",
    "cartas apostólicas",
    "el libro de Apocalipsis",
    "relatos de la creación",
    "historias de profetas",
    "arca de Noé",
    "torre de Babel",
    "ministerio de Jesús",
    "viajes misioneros de Pablo",
    "conceptos teológicos bíblicos",
    "las plagas de Egipto",
    "los diez mandamientos",
    "tabernáculo y templo",
    "las bienaventuranzas",
    "dones del espíritu santo",
    "fruto del espíritu",
    "armadura de Dios"
]

def clean_text(text):
    import unicodedata
    text = ''.join(c for c in unicodedata.normalize('NFD', text) if unicodedata.category(c) != 'Mn')
    return text.lower()

def remove_stopwords(word):
    stopwords = {'el', 'la', 'los', 'las', 'un', 'una', 'unos', 'unas', 'a', 'ante', 'bajo', 'cabe', 'con', 'contra', 'de', 'desde', 'durante', 'en', 'entre', 'hacia', 'hasta', 'mediante', 'para', 'por', 'segun', 'sin', 'so', 'sobre', 'tras', 'versus', 'via', 'y', 'e', 'ni', 'que', 'o', 'u', 'pero', 'al', 'del', 'se', 'su', 'sus', 'lo', 'les', 'me', 'te'}
    return word not in stopwords

def word_count(text):
    return len(text.split())

def generate_prompt(subtopic, offset, limit=BATCH_SIZE):
    return f"""Eres un experto pedagogo en educación religiosa e historia bíblica.
Genera {limit} conceptos educativos únicos sobre "{subtopic}". (Número de inicio: {offset}).
DEBES devolver SOLO un array JSON estricto y nada más, sin backticks ni explicaciones, que comience con '[' y termine con ']'.
Estructura exacta para cada objeto:
{{
  "intent_id": "identificador_unico_tema_en_minusculas_con_guiones_bajos",
  "keywords": ["palabra1", "palabra2", "palabra3", "palabra4", "palabra5"],
  "base_response": "Explicación educativa detallada del concepto. Debe tener entre 35 y 50 palabras exactas. Tono pedagógico. Sin saludos."
}}

REGLAS OBLIGATORIAS:
1. `intent_id`: SOLO minúsculas y guiones bajos. Sin espacios, sin tildes.
2. `keywords`: Arreglo de EXACTAMENTE entre 4 y 6 palabras. SOLO sustantivos o verbos en minúsculas, sin tildes ni caracteres especiales, sin artículos ni preposiciones.
3. `base_response`: EXACTAMENTE entre 35 y 50 palabras. Ortografía perfecta. Aporta información clara y valiosa para un estudiante de 9 a 14 años.
4. Genera contenido nuevo, diferente de los típicos. Amplía el tema.
"""

def extract_json_array(text):
    match = re.search(r'\[\s*\{.*?\}\s*\]', text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except:
            pass

    results = []
    blocks = re.findall(r'\{[^{}]+\}', text)
    for block in blocks:
        try:
            obj = json.loads(block)
            if 'intent_id' in obj and 'keywords' in obj and 'base_response' in obj:
                results.append(obj)
        except:
            pass
    return results

def fix_concept(c):
    intent_id = str(c.get("intent_id", "")).strip()
    keywords = c.get("keywords", [])
    base_response = str(c.get("base_response", "")).strip()

    intent_id = clean_text(intent_id.replace(" ", "_").lower())
    intent_id = re.sub(r'[^a-z0-9_]', '', intent_id)

    if isinstance(keywords, list):
        cleaned_kw = []
        for kw in keywords:
            kw = clean_text(str(kw))
            kw = re.sub(r'[^a-z]', '', kw)
            if kw and remove_stopwords(kw):
                cleaned_kw.append(kw)

        while len(cleaned_kw) < 4:
            words = [clean_text(w) for w in re.findall(r'\b\w+\b', base_response) if len(w) > 4]
            added = False
            for w in words:
                w = re.sub(r'[^a-z]', '', w)
                if remove_stopwords(w) and w not in cleaned_kw:
                    cleaned_kw.append(w)
                    added = True
                    break
            if not added:
                cleaned_kw.append("biblia")

        cleaned_kw = list(set(cleaned_kw))
        if len(cleaned_kw) > 6:
            cleaned_kw = cleaned_kw[:6]
        elif len(cleaned_kw) < 4:
            while len(cleaned_kw) < 4:
                cleaned_kw.append("estudio")
        keywords = cleaned_kw
    else:
        keywords = ["biblia", "historia", "dios", "fe"]

    return {
        "intent_id": intent_id,
        "keywords": keywords,
        "base_response": base_response
    }

def is_valid_concept(c):
    intent_id = c.get("intent_id", "")
    keywords = c.get("keywords", [])
    base_response = c.get("base_response", "")

    if not intent_id or not isinstance(intent_id, str): return False
    if not isinstance(keywords, list) or not (4 <= len(keywords) <= 6): return False

    wc = word_count(base_response)
    if not (33 <= wc <= 52):
        return False

    return True

def main():
    existing_concepts = []
    if os.path.exists(OUTPUT_FILE):
        try:
            with open(OUTPUT_FILE, 'r', encoding='utf-8') as f:
                existing_concepts = json.load(f)
        except Exception as e:
            print(f"Error loading existing concepts: {e}", flush=True)

    print(f"Loaded {len(existing_concepts)} existing concepts.", flush=True)
    existing_ids = {c.get("intent_id", "") for c in existing_concepts}

    cycle = 0
    consecutive_failures = 0
    max_consecutive_failures = 30

    subtopic_idx = 0
    offset = len(existing_concepts)
    models = ["gpt-4o", "gpt-3.5-turbo", "gpt-4", "claude-3-haiku"]

    while len(existing_concepts) < TARGET_COUNT and consecutive_failures < max_consecutive_failures:
        subtopic = SUBTOPICS[subtopic_idx % len(SUBTOPICS)]
        model = models[consecutive_failures % len(models)]

        prompt = generate_prompt(subtopic, offset, BATCH_SIZE)
        print(f"Requesting batch for {subtopic}, offset {offset}... Target left: {TARGET_COUNT - len(existing_concepts)}. Using model {model}", flush=True)

        try:
            response = g4f.ChatCompletion.create(
                model=model,
                messages=[{"role": "user", "content": prompt}]
            )

            if not isinstance(response, str):
                response = "".join(response)

            concepts = extract_json_array(response)
            if not concepts:
                print("No JSON array found in response. Attempting regex extraction.", flush=True)
                consecutive_failures += 1
                time.sleep(2)
                continue

            valid_new_concepts = []
            for c in concepts:
                fixed_c = fix_concept(c)
                if is_valid_concept(fixed_c):
                    if fixed_c["intent_id"] not in existing_ids:
                        valid_new_concepts.append(fixed_c)
                        existing_ids.add(fixed_c["intent_id"])

            if valid_new_concepts:
                existing_concepts.extend(valid_new_concepts)
                consecutive_failures = 0
                offset += len(valid_new_concepts)
                print(f"Added {len(valid_new_concepts)} new concepts. Total: {len(existing_concepts)}", flush=True)

                with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
                    json.dump(existing_concepts, f, ensure_ascii=False, indent=2)
            else:
                print("No valid unique concepts in this batch.", flush=True)
                consecutive_failures += 1
                subtopic_idx = (subtopic_idx + 1) % len(SUBTOPICS)

        except Exception as e:
            print(f"Error during request: {e}", flush=True)
            consecutive_failures += 1
            time.sleep(5)

        cycle += 1
        if cycle % 2 == 0:
            subtopic_idx = (subtopic_idx + 1) % len(SUBTOPICS)

        if len(existing_concepts) >= TARGET_COUNT:
            break

    # Guarantee file creation even if 0 valid concepts are generated initially
    if not os.path.exists(OUTPUT_FILE) or len(existing_concepts) == 0:
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(existing_concepts, f, ensure_ascii=False, indent=2)

    print(f"Finished. Total concepts: {len(existing_concepts)}", flush=True)

if __name__ == "__main__":
    main()
