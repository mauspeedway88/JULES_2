import json
import os
import re
import time
import asyncio
import g4f

subtopics = [
    "extensiones de navegador web",
    "diseño web responsivo móvil",
    "alojamiento de páginas web",
    "transferencia de protocolo FTP",
    "túneles privados virtuales VPN",
    "tecnología de banda ancha",
    "conexión por datos celulares",
    "portal de acceso cautivo",
    "aplicaciones web de internet",
    "indexación de sitios web",
    "plataformas de teletrabajo online",
    "comunidades virtuales de internet",
    "blogs de publicación digital",
    "wikis de información colaborativa",
    "transmisiones de podcast web",
    "almacenamiento remoto en línea",
    "conferencias virtuales por internet",
    "banca electrónica en línea",
    "pasarelas de pago web",
    "moderación de contenido online",
    "neutralidad de la red global",
    "accesibilidad de sitios web",
    "portales de soporte en línea",
    "repositorios de código web",
    "enciclopedias virtuales de internet",
    "mapas interactivos en línea",
    "mensajería instantánea por internet"
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

DEST_FILE = "GBX_brain_40B.json"

def remove_accents(text):
    accents = {'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u', 'ü': 'u', 'ñ': 'n',
               'Á': 'a', 'É': 'e', 'Í': 'i', 'Ó': 'o', 'Ú': 'u', 'Ü': 'u', 'Ñ': 'n'}
    for k, v in accents.items():
        text = text.replace(k, v)
    return text

def validate_concept(data):
    if not isinstance(data, dict): return False

    intent_id = data.get("intent_id", "")
    keywords = data.get("keywords", [])
    base_response = data.get("base_response", "")

    if not isinstance(intent_id, str): return False
    if not re.match(r'^[a-z_]+$', intent_id): return False
    if re.search(r'\d', intent_id): return False

    if not isinstance(keywords, list): return False
    if not (4 <= len(keywords) <= 6): return False
    for kw in keywords:
        if not isinstance(kw, str): return False
        if kw != kw.lower(): return False
        if kw != remove_accents(kw): return False
        if len(kw.split()) > 1: return False

    if not isinstance(base_response, str): return False
    words = [w for w in base_response.split() if w.strip()]
    if not (35 <= len(words) <= 50): return False
    if "\n" in base_response: return False

    return True

def clean_json_string(s):
    match = re.search(r'```json\s*(.*?)\s*```', s, re.DOTALL)
    if match:
        s = match.group(1)

    # ensure it's a list
    s = s.strip()
    if not s.startswith('['):
        s = '[' + s
    if not s.endswith(']'):
        s = s + ']'
    return s

async def generate_batch(subtopic):
    prompt = f"""
Actúa como un experto en minería de información educativa para estudiantes de Tercer Ciclo (9 a 15 años).
Genera 10 conceptos diferentes sobre el subtema "{subtopic}" en formato JSON válido.
El JSON debe ser un arreglo estricto de objetos. No incluyas texto fuera del JSON.

TEMA GENERAL: Tecnología: Internet
SUBTEMA: {subtopic}
Aplica 10 dimensiones distintas de esta lista a los conceptos (1 dimensión por concepto):
- Definición anatómica o estructural
- Dinámica y funcionamiento físico
- Errores, fallas y patologías comunes
- Historia, origen y evolución
- Contexto y entorno ecológico
- Aplicaciones prácticas en la vida real
- Importancia e impacto social
- Ventajas y desventajas comparativas
- Riesgos y medidas de seguridad
- Clasificación taxonómica
- Mitos y concepciones erróneas
- Relación simbiótica con otros sistemas
- Consecuencias a largo plazo
- Proyecciones futuras y tecnología

ESTRUCTURA EXACTA DE CADA OBJETO:
{{
  "intent_id": "identificador_unico_semantico",
  "keywords": ["sustantivo", "verbo", "sustantivo", "verbo"],
  "base_response": "Explicación directa y científica..."
}}

REGLAS ESTRICTAS PARA CADA OBJETO:
1. "intent_id": minúsculas, guiones bajos (_), CERO NÚMEROS O SUFIJOS SECUENCIALES (sin _1). Semántico.
2. "keywords": Array de strings. Entre 4 y 6 términos en total. Todo minúsculas. SIN TILDES O ACENTOS. SIN PALABRAS FUNCIONALES (sin el, la, de, para, un). Solo sustantivos y verbos nucleares únicos. Una palabra por string.
3. "base_response": Entre 35 y 50 palabras exactas. Ortografía inmaculada, INCLUYENDO TILDES. Tono directo, sin saludos. Texto plano, SIN SALTOS DE LÍNEA, sin comillas dobles sin escapar.
4. Valor educativo real.

Responde únicamente con el array JSON.
"""
    try:
        response = await g4f.ChatCompletion.create_async(
            model=g4f.models.default,
            messages=[{"role": "user", "content": prompt}],
        )
        return response
    except Exception as e:
        return None

dataset = []
generated_ids = set()
lock = asyncio.Lock()

async def process_subtopic(subtopic, semaphore):
    async with semaphore:
        for attempt in range(3):
            resp_text = await generate_batch(subtopic)
            if not resp_text:
                await asyncio.sleep(1)
                continue

            resp_text = resp_text.strip()

            try:
                cleaned = clean_json_string(resp_text)
                data_list = json.loads(cleaned)

                if isinstance(data_list, list):
                    added_count = 0
                    async with lock:
                        for data in data_list:
                            if validate_concept(data):
                                if data["intent_id"] not in generated_ids:
                                    dataset.append(data)
                                    generated_ids.add(data["intent_id"])
                                    added_count += 1

                        if added_count > 0:
                            with open(DEST_FILE, "w", encoding="utf-8") as f:
                                json.dump(dataset, f, ensure_ascii=False, indent=2)
                            print(f"Added {added_count} for {subtopic}. Total concepts: {len(dataset)}")
                        return
            except Exception:
                pass
            await asyncio.sleep(1)

async def main():
    global dataset
    if os.path.exists(DEST_FILE):
        with open(DEST_FILE, "r", encoding="utf-8") as f:
            try:
                dataset = json.load(f)
                for item in dataset:
                    generated_ids.add(item["intent_id"])
            except:
                pass

    print(f"Starting with {len(dataset)} concepts.")

    semaphore = asyncio.Semaphore(15)

    tasks = []
    # Doing 2 batches per subtopic to try to reach ~20 per subtopic
    for subtopic in subtopics:
        tasks.append(process_subtopic(subtopic, semaphore))
        tasks.append(process_subtopic(subtopic, semaphore))

    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())
