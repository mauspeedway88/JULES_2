import json
import re
import asyncio
import g4f
import os

TARGET_FILE = "GBX_brain_40B.json"

subtemas = [
    "extensiones de navegador web", "diseño web responsivo móvil", "alojamiento de páginas web",
    "transferencia de protocolo FTP", "túneles privados virtuales VPN", "tecnología de banda ancha",
    "conexión por datos celulares", "portal de acceso cautivo", "aplicaciones web de internet",
    "indexación de sitios web", "plataformas de teletrabajo online", "comunidades virtuales de internet",
    "blogs de publicación digital", "wikis de información colaborativa", "transmisiones de podcast web",
    "almacenamiento remoto en línea", "conferencias virtuales por internet", "banca electrónica en línea",
    "pasarelas de pago web", "moderación de contenido online", "neutralidad de la red global",
    "accesibilidad de sitios web", "portales de soporte en línea", "repositorios de código web",
    "enciclopedias virtuales de internet", "mapas interactivos en línea", "mensajería instantánea por internet"
]

dimensiones = [
    "Definición anatómica o estructural", "Dinámica y funcionamiento físico", "Propiedades químicas o materiales",
    "Errores, fallas y patologías comunes", "Historia, origen y evolución", "Contexto y entorno ecológico",
    "Aplicaciones prácticas en la vida real", "Importancia e impacto social", "Ventajas y desventajas comparativas",
    "Riesgos y medidas de seguridad", "Clasificación taxonómica", "Cálculos y fórmulas asociadas",
    "Mitos y concepciones erróneas", "Relación simbiótica con otros sistemas", "Transformación y ciclos energéticos",
    "Experimentos y demostraciones escolares", "Consecuencias a largo plazo", "Impacto ambiental",
    "Mantenimiento y prevención", "Proyecciones futuras y tecnología"
]

def clean_json_response(raw_text):
    try:
        start_idx = raw_text.find("{")
        end_idx = raw_text.rfind("}")
        if start_idx != -1 and end_idx != -1:
            json_str = raw_text[start_idx:end_idx+1]
            return json.loads(json_str)
    except:
        pass
    return None

def normalize_intent_id(subtema, dimension):
    # Combine subtema and dimension for uniqueness, remove accents, space to underscore
    text = f"{subtema} {dimension}".lower()
    text = re.sub(r'[áéíóúñ]', lambda m: {'á':'a', 'é':'e', 'í':'i', 'ó':'o', 'ú':'u', 'ñ':'n'}[m.group(0)], text)
    text = re.sub(r'[^a-z\s]', '', text)
    text = re.sub(r'\s+', '_', text.strip())
    return text

def normalize_keywords(keywords):
    if isinstance(keywords, list):
        kw_str = " ".join(keywords)
    else:
        kw_str = str(keywords)

    kw_str = kw_str.lower()
    kw_str = re.sub(r'[^a-záéíóúñ\s]', '', kw_str)

    stop_words = ["el", "la", "los", "las", "un", "una", "unos", "unas", "de", "del", "en", "por", "para", "con", "sin", "sobre", "a", "ante", "bajo", "cabe", "contra", "desde", "hacia", "hasta", "segun", "y", "o", "u", "ni", "que", "como", "su", "sus", "al"]
    words = [w for w in kw_str.split() if w not in stop_words and len(w) > 2]

    clean_words = []
    for w in words:
        w_clean = re.sub(r'[áéíóúñ]', lambda m: {'á':'a', 'é':'e', 'í':'i', 'ó':'o', 'ú':'u', 'ñ':'n'}[m.group(0)], w)
        clean_words.append(w_clean)

    return clean_words[:6]

async def generate_concept(subtema, dimension):
    prompt = f"""
Genera un concepto educativo sobre "{subtema}" desde la perspectiva de "{dimension}".
RESTRICCIONES ESTRICTAS:
1. Idioma: SOLO ESPAÑOL.
2. Público: Estudiantes de Tercer Ciclo (9 a 15 años). Simplifica pero mantén rigor científico. Si la dimensión no tiene sentido (ej: propiedades químicas de una web), inventa una analogía válida, o concéntrate en los servidores físicos.
3. Formato: JSON estricto con las siguientes claves:
   - "intent_id": Cadena en minúsculas. Usa esto exacto: "{normalize_intent_id(subtema, dimension)}". No lo cambies.
   - "keywords": Array de exactamente 5 palabras clave (sustantivos o verbos unicos), TODO en minúsculas, SIN TILDES, sin la letra ñ, SIN palabras funcionales (ej: ["encriptacion", "datos", "privacidad", "red", "seguridad"]).
   - "base_response": Texto plano de EXACTAMENTE 40 palabras (ni una más ni una menos, intenta que sea 40 a 45). DEBE incluir tildes en el texto. Tono instruccional directo, sin saludos ni conclusiones. Nada de comillas dobles. No incluir saltos de linea.

Responde SOLO con el JSON válido.
"""
    for attempt in range(3):
        try:
            response = await g4f.ChatCompletion.create_async(
                model=g4f.models.default,
                messages=[{"role": "user", "content": prompt}]
            )

            data = clean_json_response(response)
            if data and "intent_id" in data and "keywords" in data and "base_response" in data:
                intent_id = normalize_intent_id(subtema, dimension) # Force exact ID

                keywords = normalize_keywords(data["keywords"])
                if len(keywords) < 4:
                    continue

                base_response = data["base_response"].strip().replace('\n', ' ').replace('"', "'")
                word_count = len(base_response.split())

                if 35 <= word_count <= 50:
                    return {
                        "intent_id": intent_id,
                        "keywords": keywords,
                        "base_response": base_response
                    }
        except Exception as e:
            await asyncio.sleep(1)
    return None

async def main():
    if os.path.exists(TARGET_FILE):
        with open(TARGET_FILE, "r") as f:
            all_concepts = json.load(f)

        # Deduplicate and filter out bad intent_ids
        valid_concepts = {}
        for c in all_concepts:
            if "_" in c["intent_id"]: # only keep the new format if we resume
                valid_concepts[c["intent_id"]] = c
        all_concepts = list(valid_concepts.values())
    else:
        all_concepts = []

    existing_ids = set([c["intent_id"] for c in all_concepts])

    semaphore = asyncio.Semaphore(15)

    async def worker(subtema, dim):
        intent_id = normalize_intent_id(subtema, dim)
        if intent_id in existing_ids:
            return None

        async with semaphore:
            result = await generate_concept(subtema, dim)
            return result

    tasks = []
    for subtema in subtemas:
        for dim in dimensiones:
            tasks.append(worker(subtema, dim))

    batch_size = 50
    for i in range(0, len(tasks), batch_size):
        batch_tasks = tasks[i:i+batch_size]
        print(f"Procesando lote {i//batch_size + 1}/{(len(tasks)+batch_size-1)//batch_size}...")
        results = await asyncio.gather(*batch_tasks)

        valid_results = [r for r in results if r is not None]
        all_concepts.extend(valid_results)

        # Guardado incremental
        with open(TARGET_FILE, "w", encoding="utf-8") as f:
            json.dump(all_concepts, f, ensure_ascii=False, indent=2)

        print(f"Total conceptos guardados: {len(all_concepts)}")

if __name__ == "__main__":
    asyncio.run(main())
