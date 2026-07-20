import asyncio
import json
import logging
import os
import re
from g4f.client import AsyncClient
from g4f.models import gpt_4o
from unidecode import unidecode

# Setup logging
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
    "1. Definición anatómica o estructural.",
    "2. Dinámica y funcionamiento físico.",
    "3. Propiedades químicas o materiales.",
    "4. Errores, fallas y patologías comunes.",
    "5. Historia, origen y evolución.",
    "6. Contexto y entorno ecológico.",
    "7. Aplicaciones prácticas en la vida real.",
    "8. Importancia e impacto social.",
    "9. Ventajas y desventajas comparativas.",
    "10. Riesgos y medidas de seguridad.",
    "11. Clasificación taxonómica.",
    "12. Cálculos y fórmulas asociadas.",
    "13. Mitos y concepciones erróneas.",
    "14. Relación simbiótica con otros sistemas.",
    "15. Transformación y ciclos energéticos.",
    "16. Experimentos y demostraciones escolares.",
    "17. Consecuencias a largo plazo.",
    "18. Impacto ambiental.",
    "19. Mantenimiento y prevención.",
    "20. Proyecciones futuras y tecnología."
]

PROMPT_TEMPLATE = """MANDATO OPERATIVO PRINCIPAL:
Genera un (1) concepto para el subtema '{subtema}' respondiendo a la dimensión taxonómica '{dimension}'.
RESTRICCIÓN DE NIVEL ACADÉMICO: Confina la respuesta estrictamente a estudiantes de Tercer Ciclo (9 a 15 años). Simplifica conceptos universitarios sin perder veracidad científica.
DIRECTRIZ SUPREMA DE CALIDAD: Cada concepto debe aportar valor científico real y diferenciado.

VÁLVULA DE ESCAPE: Si la dimensión '{dimension}' no aplica de ninguna forma realista, científica o razonable al subtema '{subtema}', devuelve EXACTAMENTE la cadena vacía y nada más. No fuerces conocimiento.

Si decides generar el concepto, devuélvelo obligatoriamente en formato JSON estricto con la siguiente estructura:
{{
  "intent_id": "identificador_unico_semantico",
  "keywords": ["palabra1", "palabra2", "palabra3", "palabra4", "palabra5"],
  "base_response": "Tu respuesta aquí..."
}}

REGLAS DE FORMATEO ESTRICTO:
- `intent_id`: único, semántico (que combine el tema y dimensión, sin acentos), en minúsculas, separado por guiones bajos, y CERO números secuenciales.
- `keywords`: exactamente entre 4 y 6 términos, todo en minúsculas. Ausencia total de tildes o acentos. Ausencia total de palabras funcionales como artículos, preposiciones, etc (solo sustantivos y verbos nucleares únicos).
- `base_response`: exactamente entre 35 y 50 palabras, ortografía inmaculada (con tildes), tono instruccional directo, sin saludos ni referencias. Evita usar la palabra 'esta' al inicio. Formato de texto plano, sin saltos de línea ni comillas dobles sin escapar. NUNCA incluyas tu conteo de palabras al final.
Idioma: Solo español. NUNCA en inglés."""

MAX_CONCEPTOS = 225

def sanitize_json(text):
    text = re.sub(r'```json', '', text)
    text = re.sub(r'```', '', text)
    return text.strip()

async def generate_concept(client, semaphore, subtema, dimension):
    async with semaphore:
        prompt = PROMPT_TEMPLATE.format(subtema=subtema, dimension=dimension)
        try:
            response = await client.chat.completions.create(
                model=gpt_4o,
                messages=[{"role": "user", "content": prompt}]
            )
            content = response.choices[0].message.content.strip()

            if not content or len(content) < 10: # Válvula de escape
                return None

            content = sanitize_json(content)
            try:
                data = json.loads(content)
                if 'intent_id' in data and 'keywords' in data and 'base_response' in data:
                    return data
            except json.JSONDecodeError as e:
                logging.error(f"JSON Parse Error for {subtema} - {dimension}: {e}\nContent: {content}")
        except Exception as e:
            logging.error(f"Error fetching {subtema} - {dimension}: {e}")

    return None

async def main():
    client = AsyncClient()
    semaphore = asyncio.Semaphore(5)

    conceptos = []

    for subtema in SUBTEMAS:
        if len(conceptos) >= MAX_CONCEPTOS:
            break

        tasks = [generate_concept(client, semaphore, subtema, dim) for dim in DIMENSIONES]
        results = await asyncio.gather(*tasks)

        for res in results:
            if res is not None:
                conceptos.append(res)
                if len(conceptos) >= MAX_CONCEPTOS:
                    break

        logging.info(f"Generados {len(conceptos)} conceptos acumulados...")

        # Save incremental
        with open("GBX_brain_60A.json", "w", encoding="utf-8") as f:
            json.dump(conceptos, f, ensure_ascii=False, indent=2)

    logging.info(f"Finalizado. Total conceptos: {len(conceptos)}")

if __name__ == "__main__":
    asyncio.run(main())
