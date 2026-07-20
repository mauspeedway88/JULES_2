import asyncio
import json
import logging
import sys
import re
from g4f.client import AsyncClient

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

SUBTEMAS = [
    "Sustantivos de la gramática española",
    "Adjetivos calificativos de gramática",
    "Verbos conjugados en gramática",
    "Adverbios modificadores de gramática",
    "Preposiciones de enlaces gramaticales",
    "Sintaxis de oraciones gramaticales",
    "Oraciones compuestas de gramática",
    "Pronombres personales de gramática",
    "Artículos definidos de gramática",
    "Conjunciones coordinantes de gramática",
    "Interjecciones expresivas de gramática",
    "Sujeto expreso de gramática",
    "Predicado verbal de gramática",
    "Núcleo del sujeto gramatical",
    "Modificador directo de gramática",
    "Objeto directo de gramática",
    "Complemento indirecto de gramática",
    "Circunstancial de tiempo gramatical",
    "Atributo del predicado nominal",
    "Voz activa de gramática",
    "Voz pasiva de gramática",
    "Modo indicativo de gramática",
    "Tiempo pretérito de gramática",
    "Persona gramatical del verbo",
    "Número singular de gramática",
    "Género femenino de gramática",
    "Grado superlativo del adjetivo"
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

LIMIT_MAX = 200

def get_prompt(subtema, dimension):
    return f"""
    Eres un experto en lingüística y gramática hispánica, creando contenido educativo para estudiantes de Tercer Ciclo (9 a 15 años).
    Debes generar exactamente UN concepto educativo que relacione el subtema "{subtema}" analizado desde la perspectiva de la dimensión "{dimension}" (adaptando la dimensión al contexto gramatical).

    INSTRUCCIONES DE FORMATO:
    Debes devolver ÚNICAMENTE un objeto JSON válido con la siguiente estructura y reglas estrictas, sin ningún texto adicional o Markdown (ni ```json).

    Estructura JSON requerida:
    {{
        "intent_id": "Un identificador único en minúsculas, palabras separadas por guiones bajos. NO USES NÚMEROS SECUENCIALES.",
        "keywords": "Exactamente entre 4 y 6 palabras clave en minúsculas. ESTRICTAMENTE SIN TILDES Y SIN ACENTOS. ESTRICTAMENTE SIN PALABRAS FUNCIONALES (el, la, los, las, un, una, de, en, con, por, para, etc.). Usa sustantivos y verbos nucleares únicos separados por espacios.",
        "base_response": "Un texto educativo de exactamente entre 35 y 50 palabras. ESTRICTAMENTE CON ORTOGRAFÍA INMACULADA INCLUYENDO TILDES. Tono instruccional directo, sin saludos ni muletillas. Inicia directamente con el conocimiento. Texto plano sin saltos de línea y usando solo comillas simples si es necesario."
    }}

    IMPORTANTE: Si la dimensión no aplica o no tiene sentido científico/gramatical, devuelve un JSON vacío: {{}}.
    """

async def fetch_concept(client, sem, subtema, dimension):
    async with sem:
        try:
            # Quitamos PollinationsAI para que intente con otros providers
            response = await client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": get_prompt(subtema, dimension)}]
            )
            content = response.choices[0].message.content.strip()

            # Limpiar posible markdown
            if content.startswith("```"):
                content = re.sub(r"^```(?:json)?\s*|\s*```$", "", content)

            data = json.loads(content)
            if not data or not all(k in data for k in ["intent_id", "keywords", "base_response"]):
                return None

            return data
        except Exception as e:
            logging.error(f"Error generando para {subtema} - {dimension}: {e}")
            return None

async def main():
    # Inicialización del cliente sin argumentos
    client = AsyncClient()
    # Menos concurrencia
    sem = asyncio.Semaphore(5)

    results = []
    count = 0

    tasks = []
    for subtema in SUBTEMAS:
        for dimension in DIMENSIONES:
            tasks.append(fetch_concept(client, sem, subtema, dimension))

    for chunk in [tasks[i:i + 15] for i in range(0, len(tasks), 15)]:
        if count >= LIMIT_MAX:
            break

        chunk_results = await asyncio.gather(*chunk)
        for r in chunk_results:
            if r and count < LIMIT_MAX:
                results.append(r)
                count += 1
                logging.info(f"Concepto {count}/{LIMIT_MAX} agregado.")

        # Guardar progreso incremental
        with open("GBX_brain_60A_raw.json", "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=4)

        logging.info(f"Guardado lote. Total: {count}")
        await asyncio.sleep(1) # Pausa ligera entre lotes

if __name__ == "__main__":
    asyncio.run(main())
