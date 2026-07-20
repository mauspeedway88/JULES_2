import json
import asyncio
import re
import os
from unidecode import unidecode
from g4f.client import AsyncClient

# Constants
DESTINATION_FILE = "GBX_brain_64B.json"
MAX_CONCEPTS = 235

SUBTEMAS = [
    "Rima consonante de literatura",
    "Rima asonante de literatura",
    "Corrientes de movimientos literarios",
    "Romanticismo de época literaria",
    "Realismo en obras literarias",
    "Vanguardismo de literatura moderna",
    "Modernismo de poesía literaria",
    "Boom de literatura latinoamericana",
    "Narrador omnisciente de literatura",
    "Narrador testigo de literatura",
    "Narrador protagonista de literatura",
    "Personajes principales de literatura",
    "Antagonistas de historias literarias",
    "Personajes secundarios de literatura",
    "Ambiente de trama literaria",
    "Tiempo narrativo de literatura",
    "Espacio escénico de literatura",
    "Clímax de tensión literaria",
    "Desenlace de historia literaria",
    "Prólogo de libros literarios",
    "Epílogo de obras literarias",
    "Literatura juvenil de ficción",
    "Ciencia ficción en literatura",
    "Fantasía épica de literatura",
    "Realismo mágico de literatura",
    "Crónicas de Indias literarias",
    "Literatura medieval de caballería",
    "Renacimiento de época literaria",
    "Siglo de oro español",
    "Premio Nobel de literatura",
    "Antologías de textos literarios"
]

DIMENSIONES = [
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

def clean_response(text):
    text = re.sub(r'\[\[.*?\]\]\(.*?\)', '', text)
    text = re.sub(r'\[\d+\]', '', text)
    text = re.sub(r'\[cita requerida\]', '', text)
    text = text.replace('\n', ' ').replace('"', "'")
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def format_keywords(words):
    words = [unidecode(w.lower()) for w in words]
    stopwords = {"el", "la", "los", "las", "un", "una", "unos", "unas", "de", "en", "por", "para", "con", "sin", "sobre", "a", "ante", "bajo", "cabe", "contra", "desde", "hacia", "hasta", "segun", "tras"}
    filtered_words = [w for w in words if w not in stopwords]
    return filtered_words[:6]

async def generate_concept(client, semaphore, subtema, dimension):
    async with semaphore:
        prompt = f"""
Genera un concepto educativo para estudiantes de Tercer Ciclo (9 a 15 años) en español.
Subtema: {subtema}
Dimensión Ontológica: {dimension}

Instrucciones estrictas:
- Si la dimensión no aplica a este subtema, responde exactamente 'NULL'.
- Genera un JSON con este formato exacto:
{{
  "intent_id": "generado_semanticamente_sin_numeros",
  "keywords": ["exactamente", "entre", "cuatro", "seis", "palabras"],
  "base_response": "Tu respuesta educativa aquí."
}}
- "intent_id": único, en minúsculas, separado por guiones bajos, SIN NÚMEROS SECUENCIALES.
- "keywords": entre 4 y 6 sustantivos o verbos, en minúsculas, SIN tildes ni palabras funcionales.
- "base_response": texto explicativo entre 35 y 50 palabras. DEBE TENER acentos correctos. Sin introducciones ni conclusiones como conteo de palabras. Sin saltos de línea internos ni comillas dobles sin escapar.
- Evita usar la palabra 'esta' al inicio de oraciones para evitar confusiones de tildes.
"""
        try:
            response = await client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}]
            )
            content = response.choices[0].message.content.strip()

            if "NULL" in content or "null" in content.lower():
                return None

            # Extract JSON from markdown
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group(0))
            else:
                data = json.loads(content)

            data['keywords'] = format_keywords(data.get('keywords', []))
            data['base_response'] = clean_response(data.get('base_response', ''))

            words_count = len(data['base_response'].split())
            if 35 <= words_count <= 50 and 4 <= len(data['keywords']) <= 6:
                return data
            return None
        except Exception as e:
            print(f"Error for {subtema} - {dimension}: {e}")
            return None

async def main():
    client = AsyncClient()
    semaphore = asyncio.Semaphore(5)

    concepts = []

    print("Starting generation...")
    for subtema in SUBTEMAS:
        if len(concepts) >= MAX_CONCEPTS:
            break
        print(f"Processing subtema: {subtema}")
        tasks = [generate_concept(client, semaphore, subtema, dim) for dim in DIMENSIONES]
        results = await asyncio.gather(*tasks)

        for r in results:
            if r and len(concepts) < MAX_CONCEPTS:
                concepts.append(r)

        print(f"Accumulated concepts: {len(concepts)}")

        with open(DESTINATION_FILE, "w", encoding="utf-8") as f:
            json.dump(concepts, f, indent=2, ensure_ascii=False)

    print(f"Finished. Total concepts: {len(concepts)}")

if __name__ == "__main__":
    asyncio.run(main())
