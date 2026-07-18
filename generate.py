import json
import re
import os
import time
import wikipedia
import unicodedata
from g4f.client import Client
import g4f

wikipedia.set_lang("es")

subtopics = [
    "extremidades superiores o brazos",
    "extremidades inferiores o piernas",
    "extremidad distal de manos",
    "extremidad distal de pies",
    "hueso principal del fémur",
    "hueso braquial del húmero",
    "uniones móviles de articulaciones",
    "hueso radio del brazo",
    "hueso cúbito del brazo",
    "huesos carpianos de manos",
    "metacarpianos óseos de manos",
    "falanges digitales de manos",
    "hueso tibia de pierna",
    "hueso peroné de pierna",
    "hueso rótula de pierna",
    "huesos tarsianos de pies",
    "metatarsianos óseos de pies",
    "falanges digitales de pies",
    "hueso calcáneo del pie",
    "músculo bíceps del brazo",
    "músculo tríceps del brazo",
    "músculo deltoides del brazo",
    "músculo cuádriceps de pierna",
    "músculos isquiotibiales de pierna",
    "músculos gemelos de pierna",
    "músculo glúteo de pierna"
]

dimensions = [
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

def remove_accents(input_str):
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    return u"".join([c for c in nfkd_form if not unicodedata.combining(c)])

def get_wikipedia_context(topic):
    try:
        results = wikipedia.search(topic, results=1)
        if results:
            summary = wikipedia.summary(results[0], sentences=5, auto_suggest=False)
            return summary
    except Exception as e:
        pass
    return ""

def validate_intent_id(intent_id):
    if not isinstance(intent_id, str): return False
    if any(char.isdigit() for char in intent_id): return False
    if not re.match(r"^[a-z_]+$", intent_id): return False
    return True

stop_words = {"el", "la", "los", "las", "un", "una", "unos", "unas", "de", "del", "a", "ante", "bajo", "cabe", "con", "contra", "desde", "en", "entre", "hacia", "hasta", "para", "por", "segun", "sin", "sobre", "tras", "y", "e", "o", "u", "ni", "que", "es", "son"}

def validate_keywords(keywords):
    if not isinstance(keywords, list): return False
    if len(keywords) < 4 or len(keywords) > 6: return False
    for kw in keywords:
        if not isinstance(kw, str): return False
        if any(c.isupper() for c in kw): return False
        if kw != remove_accents(kw): return False
        if any(char.isdigit() for char in kw): return False
        if kw in stop_words: return False
        if len(kw.split()) > 1: return False # single words only
    return len(set(keywords)) == len(keywords) # all unique

def validate_base_response(response):
    if not isinstance(response, str): return False
    words = [w for w in response.split() if re.search(r'\w', w)]
    if len(words) < 35 or len(words) > 50: return False
    # Check for tildes (acentos) to ensure orthography
    if not re.search(r'[áéíóúÁÉÍÓÚ]', response): return False
    if '\n' in response: return False
    if '"' in response: return False
    return True

client = Client()

output_file = "GBX_brain_37A.json"
generated_data = []

# If file exists, load existing data
if os.path.exists(output_file):
    with open(output_file, 'r', encoding='utf-8') as f:
        try:
            generated_data = json.load(f)
        except:
            pass

generated_intent_ids = {item["intent_id"] for item in generated_data}

print(f"Starting generation. Existing concepts: {len(generated_data)}")

batch_size = 5
current_batch_count = 0

for subtopic in subtopics:
    context = get_wikipedia_context(subtopic)

    for dimension in dimensions:
        # Prompt definition
        prompt = f"""
Actúa como un experto en anatomía y educación para estudiantes de 9 a 15 años.
Subtema: {subtopic}
Dimensión: {dimension}
Contexto de Wikipedia: {context}

Instrucciones estrictas:
Genera un objeto JSON puro (SIN bloques de código markdown, SIN etiquetas ```json) con los siguientes campos:
1. "intent_id": Un identificador único, semántico, estrictamente en minúsculas y separado por guiones bajos. NO DEBE CONTENER NÚMEROS (ejemplo: anatomia_brazo_dinamica).
2. "keywords": Un arreglo de entre 4 y 6 palabras clave. Estrictamente en minúsculas, SIN tildes (sin acentos), SIN palabras funcionales (sin artículos, ni preposiciones). Solo sustantivos y verbos nucleares únicos.
3. "base_response": Exactamente entre 35 y 50 palabras en español. Debe tener ortografía perfecta (DEBE INCLUIR TILDES, ASEGÚRATE DE INCLUIR LAS TILDES). Tono instruccional directo, sin saludos. Inicia directamente con la carga de conocimiento real. Texto plano sin saltos de línea ni comillas dobles. Sin relleno ni frases repetitivas.

VÁLVULA DE ESCAPE: Si la dimensión NO APLICA lógicamente al subtema o no tiene información científica real (por ejemplo, 'Mantenimiento y prevención' para un hueso abstracto si no aplica, o 'Mitos' si no hay), debes responder exactamente con el texto "OMITE" en lugar del JSON.

Responde únicamente con el JSON o con la palabra OMITE.
"""
        max_retries = 3
        success = False

        for attempt in range(max_retries):
            try:
                response = client.chat.completions.create(
                    model=g4f.models.default,
                    messages=[{"role": "user", "content": prompt}],
                )
                content = response.choices[0].message.content.strip()

                if "OMITE" in content or "omite" in content:
                    print(f"OMITTED: {subtopic} - {dimension}")
                    success = True
                    break

                # Clean up markdown formatting if any
                if content.startswith("```json"):
                    content = content[7:]
                if content.startswith("```"):
                    content = content[3:]
                if content.endswith("```"):
                    content = content[:-3]

                content = content.strip()
                data = json.loads(content)

                # Format fixing
                intent_id = data.get("intent_id", "").lower().replace("-", "_")
                intent_id = "".join([c for c in intent_id if not c.isdigit()])

                keywords = data.get("keywords", [])
                if isinstance(keywords, list):
                    keywords = [remove_accents(str(kw).lower()) for kw in keywords]

                base_response = data.get("base_response", "").replace("\n", " ").replace('"', '')

                # Validations
                if validate_intent_id(intent_id) and intent_id not in generated_intent_ids and validate_keywords(keywords) and validate_base_response(base_response):
                    concept = {
                        "intent_id": intent_id,
                        "keywords": keywords,
                        "base_response": base_response
                    }
                    generated_data.append(concept)
                    generated_intent_ids.add(intent_id)
                    print(f"SUCCESS: {intent_id} ({len(generated_data)} total)")
                    current_batch_count += 1
                    success = True
                    break
                else:
                    pass
            except Exception as e:
                pass
            time.sleep(2)

        # Save batch incrementally
        if current_batch_count >= batch_size:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(generated_data, f, ensure_ascii=False, indent=2)
            current_batch_count = 0

# Final save
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(generated_data, f, ensure_ascii=False, indent=2)

print(f"Generation complete. Total concepts: {len(generated_data)}")
