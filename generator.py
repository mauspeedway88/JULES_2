import os
import json
import asyncio
import re
import unidecode
import g4f
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import subprocess

SUBTOPICS = [
    "Robótica e Ingeniería: Electricidad — Cortocircuito de falla eléctrica",
    "Energía renovable de generación eléctrica",
    "Paneles fotovoltaicos de electricidad",
    "Turbinas eólicas de red eléctrica",
    "Plantas hidroeléctricas de generación",
    "Celdas de almacenamiento eléctrico",
    "Acumuladores de carga eléctrica",
    "Inversores de corriente eléctrica",
    "Rectificadores de puente eléctrico",
    "Contadores de consumo eléctrico",
    "Frecuencia de hercios eléctricos",
    "Suministro monofásico de red eléctrica",
    "Instalación trifásica de potencia eléctrica",
    "Caída de tensión eléctrica",
    "Calibre de cables eléctricos",
    "Regletas de conexión eléctrica",
    "Clavijas de enchufe eléctrico",
    "Cajas de derivación eléctrica",
    "Tubos condulets de cableado eléctrico",
    "Canaletas de ruta eléctrica",
    "Pinza amperimétrica de medición eléctrica",
    "Buscapolos de fase eléctrica",
    "Reglamentos de instalación eléctrica",
    "Peligro de electrocución eléctrica",
    "Equipo dieléctrico de protección",
    "Resistividad de materiales eléctricos",
    "Conductividad de metales eléctricos",
    "Capacitancia de red eléctrica",
    "Inductancia de bobinas eléctricas"
]

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

DEST_FILE = "GBX_brain_46B.json"

def clean_intent_id(s):
    s = s.lower()
    s = re.sub(r'[^a-z0-9_]', '_', s)
    s = re.sub(r'_+', '_', s)
    s = s.strip('_')
    s = re.sub(r'\d+$', '', s)
    s = re.sub(r'_\d+', '', s)
    return s

def clean_keywords(kw_list):
    new_kws = []
    stopwords = {'el', 'la', 'los', 'las', 'un', 'una', 'unos', 'unas', 'y', 'e', 'ni', 'que', 'o', 'u', 'a', 'ante', 'bajo', 'cabe', 'con', 'contra', 'de', 'desde', 'durante', 'en', 'entre', 'hacia', 'hasta', 'mediante', 'para', 'por', 'segun', 'sin', 'so', 'sobre', 'tras', 'versus', 'via'}
    for kw in kw_list:
        kw = kw.lower()
        kw = unidecode.unidecode(kw)
        kw = re.sub(r'[^a-z]', '', kw)
        if kw and kw not in stopwords:
            new_kws.append(kw)
    seen = set()
    result = []
    for item in new_kws:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result[:6]

def validate_response(item):
    if not isinstance(item, dict):
        return False, "Not a dictionary"

    intent_id = item.get("intent_id", "")
    if not intent_id or re.search(r'_\d+$', intent_id):
        return False, f"Invalid intent_id: {intent_id}"

    keywords = item.get("keywords", [])
    if not isinstance(keywords, list) or not (4 <= len(keywords) <= 6):
        return False, f"Invalid keywords count: {len(keywords)}"

    base_response = item.get("base_response", "")
    word_count = len(re.findall(r'\b\w+\b', base_response))
    if not (35 <= word_count <= 50):
        return False, f"Invalid base_response word count: {word_count}"

    if "\n" in base_response:
        return False, "Newlines in base_response"

    return True, ""

def format_prompt(subtopic, dimension):
    return f"""Eres un experto en ingeniería y educación. Genera UN SOLO concepto enciclopédico para estudiantes de 9 a 15 años.
Subtema: {subtopic}
Dimensión: {dimension}

Si la dimensión no aplica o no hay información científica real, responde exactamente con la palabra: OMITE

Formato de salida (JSON estricto, sin markdown):
{{
  "intent_id": "identificador_unico_semantico_en_minusculas_sin_numeros_secuenciales",
  "keywords": ["sustantivo1", "sustantivo2", "verbo1", "palabra4", "palabra5"],
  "base_response": "Texto educativo directo, ortografía perfecta con tildes, sin saludos, exactamente de 35 a 50 palabras, en una sola línea plana."
}}

Reglas CRÍTICAS:
- keywords: Extrae 4 a 6 palabras únicas del texto generado. Sin tildes.
- base_response: DEBE contener información científica REAL y ESPECÍFICA sobre {subtopic} en el contexto de {dimension}. NO USES FRASES GENÉRICAS NI REPETITIVAS. Mínimo 35 palabras, máximo 50.
"""

async def generate_concept(subtopic, dimension, semaphore):
    async with semaphore:
        for attempt in range(4):
            try:
                response = await g4f.ChatCompletion.create_async(
                    model=g4f.models.default,
                    messages=[{"role": "user", "content": format_prompt(subtopic, dimension)}]
                )

                text = response.strip()
                if "OMITE" in text:
                    return None

                if text.startswith("```json"):
                    text = text[7:]
                if text.endswith("```"):
                    text = text[:-3]

                text = text.strip()
                data = json.loads(text)

                data["intent_id"] = clean_intent_id(data.get("intent_id", f"{subtopic.split(':')[0]}_{dimension}"))
                data["keywords"] = clean_keywords(data.get("keywords", []))
                data["base_response"] = data.get("base_response", "").replace("\n", " ").strip()

                is_valid, msg = validate_response(data)
                if is_valid:
                    return data
                else:
                    print(f"Validation failed for {subtopic} - {dimension}: {msg}")
            except Exception as e:
                pass
            await asyncio.sleep(1)
        return None

async def main():
    semaphore = asyncio.Semaphore(15)
    all_concepts = []
    seen_responses = []

    vectorizer = TfidfVectorizer()

    tasks = []
    for subtopic in SUBTOPICS:
        for dimension in DIMENSIONS:
            tasks.append((subtopic, dimension))

    print(f"Total tasks planned: {len(tasks)}")

    batch_size = 50
    current_batch = []

    # Process all tasks simultaneously for speed
    results = await asyncio.gather(*[generate_concept(s, d, semaphore) for s, d in tasks])

    for concept in results:
        if concept:
            is_unique = True
            if seen_responses:
                try:
                    tfidf_matrix = vectorizer.fit_transform(seen_responses + [concept["base_response"]])
                    cosine_sim = cosine_similarity(tfidf_matrix[-1], tfidf_matrix[:-1])
                    if cosine_sim.max() > 0.8:
                        is_unique = False
                except ValueError:
                    pass

            if is_unique:
                current_batch.append(concept)
                seen_responses.append(concept["base_response"])
                all_concepts.append(concept)

    with open(DEST_FILE, "w", encoding="utf-8") as f:
        json.dump(all_concepts, f, indent=4, ensure_ascii=False)

    print(f"Generation complete. Total concepts generated: {len(all_concepts)}")

if __name__ == "__main__":
    asyncio.run(main())
