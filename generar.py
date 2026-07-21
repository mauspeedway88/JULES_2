import asyncio
import json
import re
import unicodedata
import os
from g4f.client import AsyncClient

DESTINATION_FILE = "GBX_brain_66A.json"
MAX_CONCEPTS = 175

SUBTHEMES = [
    "Estructura oracional gramática inglesa",
    "Sujeto sintáctico gramática inglesa",
    "Predicado verbal gramática inglesa",
    "Objeto directo gramática inglesa",
    "Objeto indirecto gramática inglesa",
    "Oraciones afirmativas gramática inglesa",
    "Oraciones negativas gramática inglesa",
    "Oraciones interrogativas gramática inglesa",
    "Oraciones imperativas gramática inglesa",
    "Oraciones condicionales gramática inglesa",
    "Oraciones compuestas gramática inglesa",
    "Oraciones complejas gramática inglesa",
    "Voz activa gramática inglesa",
    "Voz pasiva gramática inglesa",
    "Discurso directo gramática inglesa",
    "Discurso indirecto gramática inglesa",
    "Genitivo sajón gramática inglesa",
    "Cuantificadores nominales gramática inglesa",
    "Modificadores sustantivo gramática inglesa",
    "Concordancia nominal gramática inglesa",
    "Partículas interrogativas gramática inglesa",
    "Etiquetas interrogativas gramática inglesa",
    "Contracciones formales gramática inglesa",
    "Sufijos derivativos gramática inglesa",
    "Prefijos formativos gramática inglesa",
    "Sustantivos colectivos gramática inglesa",
    "Sustantivos abstractos gramática inglesa",
    "Casos gramaticales idioma inglés"
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

STOP_WORDS = {'el', 'la', 'los', 'las', 'un', 'una', 'unos', 'unas', 'de', 'del', 'al', 'en', 'por', 'para', 'con', 'sin', 'sobre', 'y', 'o', 'u', 'e', 'a', 'su', 'sus', 'es', 'son', 'que', 'como', 'se'}

def remove_accents(input_str):
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    return u"".join([c for c in nfkd_form if not unicodedata.combining(c)])

def clean_base_response(text):
    text = re.sub(r'\[\[.*?\]\]\(.*?\)', '', text)
    text = re.sub(r'\[\d+\]', '', text)
    text = text.replace('\n', ' ').replace('"', "'")
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def clean_keywords(keywords_raw):
    words = keywords_raw.lower().replace(',', ' ').split()
    cleaned = []
    for w in words:
        w_clean = remove_accents(re.sub(r'[^a-záéíóúüñ]', '', w.strip()))
        if w_clean and w_clean not in STOP_WORDS:
            cleaned.append(w_clean)

    unique_words = list(dict.fromkeys(cleaned))
    if len(unique_words) >= 4:
        return " ".join(unique_words[:6])
    return None

def validate_word_count(text):
    words = text.split()
    return 35 <= len(words) <= 50

async def generate_concept(client, sem, subtheme, dimension):
    prompt = f"""
Eres un especialista en educación elaborando un dataset para estudiantes de 9 a 15 años.
Tema principal: {subtheme}
Dimensión analítica: {dimension}

Extrae conocimiento valioso y responde ÚNICAMENTE con un JSON estrictamente válido:
{{
  "keywords": "4 a 6 sustantivos o verbos clave separados por espacio, ABSOLUTAMENTE SIN ACENTOS NI TILDES y SIN PALABRAS FUNCIONALES (artículos o preposiciones).",
  "base_response": "Texto educativo que empiece con el conocimiento sin saludos ni introducciones. DEBE tener entre 35 y 50 palabras exactas. DEBE tener ORTOGRAFÍA INMACULADA CON TILDES. SIN COMILLAS DOBLES INTERNAS, SIN SALTOS DE LÍNEA."
}}
IMPORTANTE: Las keywords NO DEBEN tener tildes, pero base_response SÍ DEBE tener tildes.
"""

    async with sem:
        try:
            response = await client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=300,
            )
            content = response.choices[0].message.content
            match = re.search(r'\{[^{}]+\}', content)
            if match:
                data = json.loads(match.group(0))
                return data
            return None
        except Exception as e:
            return None

async def main():
    client = AsyncClient()
    sem = asyncio.Semaphore(4)

    results = []
    count = 0

    with open(DESTINATION_FILE, "w", encoding="utf-8") as f:
        json.dump([], f)

    for subtheme in SUBTHEMES:
        if count >= MAX_CONCEPTS:
            break

        tasks = [generate_concept(client, sem, subtheme, dim) for dim in DIMENSIONS]
        responses = await asyncio.gather(*tasks)

        for resp in responses:
            if count >= MAX_CONCEPTS:
                break

            if resp and isinstance(resp, dict) and "keywords" in resp and "base_response" in resp:
                kw_clean = clean_keywords(resp["keywords"])
                if kw_clean:
                    br_clean = clean_base_response(resp["base_response"])
                    if validate_word_count(br_clean):
                        kw_list = kw_clean.split()
                        intent_id = "_".join(kw_list[:4])

                        if not re.search(r'\d', intent_id):
                            if not any(r["intent_id"] == intent_id for r in results):
                                concept = {
                                    "intent_id": intent_id,
                                    "keywords": kw_clean,
                                    "base_response": br_clean
                                }
                                results.append(concept)
                                count += 1
                                print(f"Concepto valido agregado. Total: {count}")

                                with open(DESTINATION_FILE, "w", encoding="utf-8") as f:
                                    json.dump(results, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    asyncio.run(main())
