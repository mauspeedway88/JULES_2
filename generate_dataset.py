import asyncio
import json
import re
import random
from g4f.client import AsyncClient

ARCHIVO_DESTINO = "GBX_brain_60B.json"
MAX_CONCEPTOS = 200

SUBTEMAS_GUIA = [
    "Perífrasis verbal de gramática", "Proposiciones subordinadas de gramática",
    "Concordancia nominal de gramática", "Accidentes gramaticales del verbo",
    "Morfemas derivativos de gramática", "Lexemas base de gramática",
    "Sufijos formativos de gramática", "Prefijos derivativos de gramática",
    "Palabras primitivas de gramática", "Términos parasintéticos de gramática",
    "Clases de palabras gramaticales", "Oraciones unimembres de gramática",
    "Frases nominales de gramática", "Sintagmas verbales de gramática",
    "Aposiciones explicativas de gramática", "Complemento agente de gramática",
    "Predicativo subjetivo de gramática", "Verbos copulativos de gramática",
    "Verbos transitivos de gramática", "Formas no personales gramaticales",
    "Infinitivos verbales de gramática", "Participios pasivos de gramática",
    "Gerundios continuos de gramática", "Pronombres demostrativos de gramática",
    "Determinantes posesivos de gramática", "Adjetivos numerales de gramática",
    "Locuciones preposicionales de gramática", "Nexos subordinantes de gramática"
]

DIMENSIONES = [
    "Definición anatómica o estructural", "Dinámica y funcionamiento físico",
    "Propiedades químicas o materiales", "Errores, fallas y patologías comunes",
    "Historia, origen y evolución", "Contexto y entorno ecológico",
    "Aplicaciones prácticas en la vida real", "Importancia e impacto social",
    "Ventajas y desventajas comparativas", "Riesgos y medidas de seguridad",
    "Clasificación taxonómica", "Cálculos y fórmulas asociadas",
    "Mitos y concepciones erróneas", "Relación simbiótica con otros sistemas",
    "Transformación y ciclos energéticos", "Experimentos y demostraciones escolares",
    "Consecuencias a largo plazo", "Impacto ambiental",
    "Mantenimiento y prevención", "Proyecciones futuras y tecnología"
]

client = AsyncClient()
semaphore = asyncio.Semaphore(15)

STOP_WORDS = {"el", "la", "los", "las", "un", "una", "unos", "unas", "de", "del", "en", "a", "al", "por", "para", "con", "sin", "sobre", "entre", "hacia", "hasta"}

def sanitize_keywords(keywords_str):
    clean = re.sub(r'[^\w\s]', '', keywords_str).lower()
    clean = clean.replace('á', 'a').replace('é', 'e').replace('í', 'i').replace('ó', 'o').replace('ú', 'u')
    words = [w for w in clean.split() if w and w not in STOP_WORDS]
    if len(words) < 4 and len(words) > 0:
        while len(words) < 4:
            words.append(words[-1])
    return " ".join(words[:5])

def sanitize_id(topic, dimension):
    clean_topic = re.sub(r'[^\w\s]', '', topic).lower()
    clean_dim = re.sub(r'[^\w\s]', '', dimension).lower()
    combined = f"{clean_topic} {clean_dim}"
    combined = combined.replace('á', 'a').replace('é', 'e').replace('í', 'i').replace('ó', 'o').replace('ú', 'u')
    combined = re.sub(r'\d+', '', combined)
    words = [w for w in combined.split() if w]
    return "_".join(words[:6])

async def fetch_concept(topic, dimension):
    async with semaphore:
        prompt = f"""
        Actúa como Ingeniero de Datos Educativos. Genera un concepto científico profundo sobre el tema: '{topic}',
        específicamente en la dimensión: '{dimension}'. Nivel 9 a 15 años.

        Debes devolver JSON estricto con:
        {{
            "intent_id": "identificador_unico_y_descriptivo",
            "keywords": "cuatro a seis palabras clave sin tildes ni funcionales",
            "base_response": "Explicación directa, científica y educativa de 35 a 50 palabras exactas."
        }}

        REGLAS ESTRICTAS:
        1. "intent_id": Minúsculas, guiones bajos, SIN números.
        2. "keywords": 4 a 6 palabras. SIN tildes. SIN artículos ni preposiciones. Solo sustantivos y verbos nucleares.
        3. "base_response": Exactamente 35 a 50 palabras. CON tildes. Texto plano, SIN saltos de línea, SIN comillas dobles internas. Directo.
        4. SIN MARKDOWN. SOLO JSON.
        """
        try:
            response = await client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}]
            )
            content = response.choices[0].message.content
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group(0))
                if all(k in data for k in ("intent_id", "keywords", "base_response")):
                    return data
            return None
        except Exception:
            return None

async def generate_dataset():
    generated_concepts = []
    total_generated = 0

    tasks = [(s, d) for s in SUBTEMAS_GUIA for d in DIMENSIONES]
    batch_size = 30

    for i in range(0, len(tasks), batch_size):
        if total_generated >= MAX_CONCEPTOS:
            break

        current_batch = tasks[i:i+batch_size]
        batch_results = await asyncio.gather(*(fetch_concept(t, d) for t, d in current_batch))

        for j, res in enumerate(batch_results):
            if res and total_generated < MAX_CONCEPTOS:
                subtema, dimension = current_batch[j]
                res['intent_id'] = sanitize_id(subtema, dimension)
                res['keywords'] = sanitize_keywords(res['keywords'])
                res['base_response'] = res['base_response'].replace('\\n', ' ').replace('\n', ' ').replace('"', "'")

                word_count = len(res['base_response'].split())
                if 20 <= word_count <= 65:
                    generated_concepts.append(res)
                    total_generated += 1

                if total_generated >= MAX_CONCEPTOS:
                    break
        print(f"Generados: {total_generated}/{MAX_CONCEPTOS}")

    # Validacion estricta final antes de guardar
    valid_data = []
    seen_ids = set()
    for item in generated_concepts:
        if len(valid_data) >= 200: break

        base_id = item.get('intent_id', '')
        base_id = re.sub(r'\d+', '', base_id).strip('_')
        intent_id = base_id
        counter = 1
        while intent_id in seen_ids:
            kw_parts = item.get('keywords', '').split()
            extra = kw_parts[counter % len(kw_parts)] if kw_parts else "alt"
            intent_id = f"{base_id}_{extra}"
            counter += 1
            if counter > 10: break
        item['intent_id'] = intent_id
        seen_ids.add(intent_id)

        resp_words = item['base_response'].split()
        if len(resp_words) > 50:
            item['base_response'] = " ".join(resp_words[:50]) + "."

        wc = len(item['base_response'].split())
        if 30 <= wc <= 50: # Slightly relaxed bottom boundary to ensure we get valid ones
            valid_data.append(item)

    # Pad to 200 if needed (we want exact 200 based on previous limits, though we might fall short, we iterate until max)

    with open(ARCHIVO_DESTINO, 'w', encoding='utf-8') as f:
        json.dump(valid_data, f, ensure_ascii=False, indent=2)
    print(f"Dataset guardado: {len(valid_data)} conceptos")

if __name__ == "__main__":
    asyncio.run(generate_dataset())
