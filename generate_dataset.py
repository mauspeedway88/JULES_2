import json
import asyncio
import os
import re
from g4f.client import AsyncClient
import unidecode

SUBTEMAS = [
    "Geografía: El Salvador — Volcanes activos del territorio salvadoreño",
    "Valles fértiles de geografía salvadoreña",
    "Ríos principales del mapa salvadoreño",
    "Clima estacional de geografía salvadoreña",
    "Fauna autóctona del territorio salvadoreño",
    "Flora endémica de geografía salvadoreña",
    "Lagos naturales de tierras salvadoreñas",
    "Departamentos administrativos de geografía salvadoreña",
    "Clima tropical del territorio salvadoreño",
    "Fronteras limítrofes de geografía salvadoreña",
    "Relieve nacional del territorio salvadoreño",
    "Cordillera del Bálsamo geografía salvadoreña",
    "Cordillera Apaneca Ilamatepec territorio salvadoreño",
    "Volcán Ilamatepec de Santa Ana",
    "Volcán Izalco de geografía salvadoreña",
    "Volcán Quezaltepeque de San Salvador",
    "Volcán Chaparrastique de geografía salvadoreña",
    "Volcán Chinchontepec del territorio salvadoreño",
    "Río Lempa de geografía salvadoreña",
    "Río Goascorán limítrofe oriental salvadoreño",
    "Río Paz del territorio occidental",
    "Río Sumpul de geografía salvadoreña",
    "Río Torola del mapa salvadoreño",
    "Lago de Coatepeque geografía salvadoreña",
    "Lago de Ilopango territorio salvadoreño",
    "Lago de Güija geografía salvadoreña",
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

MAX_CONCEPTOS = 275
ARCHIVO_DESTINO = "GBX_brain_59A.json"
STOP_WORDS = ["el", "la", "los", "las", "un", "una", "unos", "unas", "de", "del", "al", "a", "ante", "bajo", "cabe", "con", "contra", "desde", "en", "entre", "hacia", "hasta", "para", "por", "segun", "sin", "so", "sobre", "tras"]

client = AsyncClient()
semaphore = asyncio.Semaphore(5)

def clean_text(text):
    text = text.replace('"', "'")
    text = text.replace('\n', ' ')
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def process_keywords(keywords_raw):
    # Split by comma or space
    words = []
    if isinstance(keywords_raw, list):
        words = keywords_raw
    elif isinstance(keywords_raw, str):
         words = re.split(r'[,\s]+', keywords_raw)

    clean_words = []
    for w in words:
        w = unidecode.unidecode(w.lower().strip())
        w = re.sub(r'[^a-z]', '', w)
        if w and w not in STOP_WORDS:
            clean_words.append(w)

    # keep only 4 to 6 terms
    if len(clean_words) < 4:
        return [] # invalid
    return clean_words[:6]

async def generate_concept(subtema, dimension):
    prompt = f"""
    Eres un experto en educación geográfica de El Salvador para estudiantes de Tercer Ciclo (9 a 15 años).
    Debes extraer un concepto científico sobre el subtema "{subtema}" desde la dimensión "{dimension}".
    Si esta dimensión no aplica al subtema o no tiene base científica real, responde exactamente con la palabra "NULL".

    Requisitos OBLIGATORIOS:
    1. ID: Crea un intent_id único y semántico en minúsculas, separado por guiones bajos y sin números. Ejemplo: "geografia_salvador_lempa_origen".
    2. KEYWORDS: Entre 4 y 6 palabras clave exactas. Todas en minúsculas, SIN NINGÚN ACENTO O TILDE, usando SOLO sustantivos y verbos únicos. NO USES preposiciones ni artículos (de, el, la, etc.).
    3. BASE_RESPONSE: Texto explicativo de EXACTAMENTE entre 35 y 50 palabras. Tono instruccional directo, sin saludos. DEBE TENER ortografía perfecta con tildes. NO incluyas saltos de línea ni comillas dobles. No incluyas el conteo de palabras al final.

    Responde ÚNICAMENTE con un JSON válido con esta estructura, sin markdown, sin texto adicional:
    {{
        "intent_id": "tu_id_aqui",
        "keywords": ["palabra1", "palabra2", "palabra3", "palabra4"],
        "base_response": "Tu texto aqui con ortografía perfecta."
    }}
    """

    try:
        async with semaphore:
            response = await client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}]
            )
            content = response.choices[0].message.content.strip()

            if "NULL" in content or "null" in content:
                return None

            # Remove markdown JSON blocks if present
            if content.startswith("```json"):
                content = content[7:-3].strip()
            elif content.startswith("```"):
                content = content[3:-3].strip()

            data = json.loads(content)

            if "intent_id" not in data or "keywords" not in data or "base_response" not in data:
                return None

            if any(char.isdigit() for char in data["intent_id"]):
                 return None # No numbers allowed

            keywords = process_keywords(data["keywords"])
            if not keywords:
                 return None

            base_response = clean_text(data["base_response"])
            word_count = len(base_response.split())
            if word_count < 35 or word_count > 50:
                 return None

            # Ensure no "XX palabras" at the end
            if re.search(r'\(\d+\s+palabras\)$', base_response, re.IGNORECASE):
                return None

            return {
                "intent_id": data["intent_id"].lower(),
                "keywords": keywords,
                "base_response": base_response
            }
    except Exception as e:
        print(f"Error generando {subtema} - {dimension}: {e}")
        return None

async def main():
    dataset = []

    for subtema in SUBTEMAS:
        if len(dataset) >= MAX_CONCEPTOS:
            break
        print(f"Procesando subtema: {subtema}")
        tasks = []
        for dimension in DIMENSIONES:
             tasks.append(generate_concept(subtema, dimension))

        results = await asyncio.gather(*tasks)
        for r in results:
             if r:
                 # Check for duplicate intent_ids
                 if not any(item["intent_id"] == r["intent_id"] for item in dataset):
                     dataset.append(r)
                     if len(dataset) >= MAX_CONCEPTOS:
                         break

        print(f"Conceptos válidos acumulados: {len(dataset)}")

        # Incremental save
        with open(ARCHIVO_DESTINO, 'w', encoding='utf-8') as f:
            json.dump(dataset, f, ensure_ascii=False, indent=2)

    print(f"Generación completa. Total conceptos: {len(dataset)}")

if __name__ == "__main__":
    asyncio.run(main())
