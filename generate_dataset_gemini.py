import asyncio
import json
import os
import re
from google import genai
from google.genai import types
from unidecode import unidecode

SUBTEMAS = [
    "Ideas principales de lectura",
    "Inferencias de comprensión lectora",
    "Resumen de textos leídos",
    "Análisis de comprensión lectora",
    "Lectura crítica de textos",
    "Contexto de comprensión lectora",
    "Ideas secundarias de lectura",
    "Detalles específicos del texto",
    "Propósito del autor leído",
    "Intención comunicativa de lectura",
    "Público objetivo del texto",
    "Mensaje implícito de lectura",
    "Información explícita de textos",
    "Tema central de lectura",
    "Argumento principal del texto",
    "Estructura textual de lectura",
    "Hipótesis de comprensión lectora",
    "Anticipación de contenidos leídos",
    "Predicciones durante la lectura",
    "Lectura exploratoria de textos",
    "Lectura analítica de documentos",
    "Subrayado de textos leídos",
    "Esquemas de comprensión lectora"
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

MAX_CONCEPTOS = 235
ARCHIVO_DESTINO = "GBX_brain_63A.json"

SEMAFORO = asyncio.Semaphore(5) # Lower concurrency for Gemini

PROMPT_TEMPLATE = """
Eres un ingeniero de datos autónomo experto en educación para estudiantes de Tercer Ciclo (9 a 15 años). Solo en español. NUNCA escribir en inglés.
Tu objetivo es generar UN SOLO concepto educativo.
Tema: Lenguaje: Comprensión Lectora
Subtema: {subtema}
Dimensión a analizar: {dimension}

Instrucciones estrictas para la salida JSON:
1. `intent_id`: Identificador único y semántico, en minúsculas, separado por guiones bajos y con cero números secuenciales. Que represente el tema y dimensión.
2. `keywords`: Arreglo de exactamente 4 a 6 términos, TODO en minúsculas, SIN NINGUNA tilde o acento (usa la vocal normal), SIN palabras funcionales (como artículos o preposiciones), usa SOLAMENTE sustantivos y verbos nucleares únicos. Ejemplo: ["idea", "principal", "texto", "identificacion", "lectura"]
3. `base_response`: Texto plano de exactamente 35 a 50 palabras. DEBE TENER ortografía inmaculada INCLUYENDO TILDES. Tono instruccional directo, sin saludos ni muletillas ni referencias a fuentes. Inicia directamente con la carga de conocimiento real. Sin saltos de línea internos ni comillas dobles sin escapar que corrompan el JSON. NUNCA incluyas tu conteo de palabras al final. No menciones (XX palabras).
4. VÁLVULA DE ESCAPE: Si la dimensión no aplica científicamente a este subtema (ej. fórmulas para subrayado), responde exactamente con el texto NULO.
5. Usa como base de conocimiento primero Wikipedia, luego fuentes educativas, luego tu conocimiento.

Salida EXACTAMENTE en este formato JSON, nada más, sin bloques Markdown (como ```json):
{{
  "intent_id": "...",
  "keywords": ["...", "..."],
  "base_response": "..."
}}
"""

def clean_base_response(text):
    text = text.replace('\n', ' ').replace('"', "'")
    text = re.sub(r'\[\[.*?\]\]\(.*?\)', '', text)
    text = re.sub(r'\[\d+\]', '', text)
    text = re.sub(r'\[cita requerida\]', '', text)
    text = re.sub(r'\(\d+ palabras\)', '', text)
    return text.strip()

def process_keywords(keywords_list):
    new_kw = []
    for kw in keywords_list:
        clean = unidecode(kw).lower().strip()
        if clean:
            new_kw.append(clean)
    return new_kw

async def generate_concept(client, subtema, dimension):
    prompt = PROMPT_TEMPLATE.format(subtema=subtema, dimension=dimension)
    async with SEMAFORO:
        try:
            # We are using Gemini Sync API in a wrapper to emulate async execution.
            # In a real environment we would use AsyncClient for Gemini if available,
            # but to be sure we just use the event loop here.

            def run_gemini():
                return client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=prompt
                )

            response = await asyncio.get_running_loop().run_in_executor(None, run_gemini)

            raw_text = response.text.strip()
            if raw_text == "NULO":
                return None
            if raw_text.startswith("```json"):
                raw_text = raw_text[7:]
            if raw_text.endswith("```"):
                raw_text = raw_text[:-3]
            raw_text = raw_text.strip()

            data = json.loads(raw_text)

            # Post-procesamiento
            base_res = clean_base_response(data.get("base_response", ""))
            words = base_res.split()
            if not (30 <= len(words) <= 55): # slightly relaxed to allow post processing
                return None

            keywords = process_keywords(data.get("keywords", []))
            if not (4 <= len(keywords) <= 6):
                return None

            intent_id = data.get("intent_id", "")
            if any(char.isdigit() for char in intent_id):
                return None

            return {
                "intent_id": intent_id,
                "keywords": keywords,
                "base_response": base_res
            }
        except Exception as e:
            return None

async def main():
    api_key = os.environ.get('API_KEY')
    if not api_key:
        print("API_KEY environment variable not set.")
        return

    client = genai.Client(api_key=api_key)
    all_concepts = []

    tasks = []
    for subtema in SUBTEMAS:
        for dimension in DIMENSIONES:
            tasks.append(generate_concept(client, subtema, dimension))

    print(f"Total tasks created: {len(tasks)}")

    # Run in batches to save to file incrementally
    batch_size = 20
    current_count = 0

    with open(ARCHIVO_DESTINO, "w", encoding="utf-8") as f:
        f.write("[\n")

    for i in range(0, len(tasks), batch_size):
        batch = tasks[i:i+batch_size]
        results = await asyncio.gather(*batch)

        valid_results = [r for r in results if r is not None]

        for item in valid_results:
            if current_count >= MAX_CONCEPTOS:
                break

            prefix = "" if current_count == 0 else ",\n"
            with open(ARCHIVO_DESTINO, "a", encoding="utf-8") as f:
                f.write(prefix + json.dumps(item, ensure_ascii=False, indent=2))
            current_count += 1

        print(f"Batch {i//batch_size + 1} processed. Total concepts so far: {current_count}")

        if current_count >= MAX_CONCEPTOS:
            print("Maximum concept limit reached. Stopping.")
            break

    with open(ARCHIVO_DESTINO, "a", encoding="utf-8") as f:
        f.write("\n]")

    print(f"Finished generating concepts. Total: {current_count}")

if __name__ == "__main__":
    asyncio.run(main())
