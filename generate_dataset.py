import asyncio
import json
import re
from google import genai
from google.genai import types

# Simulación de la API configurada por la variable de entorno o instanciación vacía.
# No exponemos la API key en el código final por seguridad.
client = genai.Client()

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

PROMPT_TEMPLATE = """
Eres un especialista en Minería de Información Educativa. Genera 1 concepto académico sobre el tema '{subtema}', estrictamente enfocado en la dimensión taxonómica '{dimension}'.

ESTRICTAMENTE OBLIGATORIO:
- El público objetivo son estudiantes de Tercer Ciclo (9 a 15 años). Simplifica conceptos universitarios sin perder veracidad científica.
- NO uses información repetitiva, NO uses secuencias numéricas, aporta valor científico real y diferenciado.
- NO incluyas fuentes, ni saludos, ni despedidas.
- Genera la respuesta en formato JSON estrictamente válido, sin markdown, con la siguiente estructura:
{{
  "intent_id": "<identificador semantico unico en minusculas, separado por guiones bajos y con CERO NUMEROS SEQUENCIALES, ni letras secunciales>",
  "keywords": "<generame exactamente una oracion de 4 a 6 palabras sueltas separadas por espacios. Las palabras deben ser TODO EN MINUSCULAS, AUSENCIA TOTAL DE TILDES O ACENTOS, AUSENCIA TOTAL DE PALABRAS FUNCIONALES COMO ARTICULOS O PREPOSICIONES. USA EXCLUSIVAMENTE SUSTANTIVOS Y VERBOS NUCLEARES. EJEMPLO CORRECTO: sustantivo verbo accion estado predicativo>",
  "base_response": "<un texto de exactamente entre 35 y 50 palabras. DEBE TENER ORTOGRAFIA INMACULADA INCLUYENDO TILDES. Inicia directamente con el conocimiento real, en formato de texto plano sin saltos de linea internos ni comillas dobles que corrompan el JSON.>"
}}
"""

MAX_CONCEPTOS = 200
OUTPUT_FILE = "GBX_brain_60B.json"

sem = asyncio.Semaphore(5)

async def generate_concept(subtema, dimension, lock, context_list):
    async with sem:
        if len(context_list) >= MAX_CONCEPTOS:
            return

        prompt = PROMPT_TEMPLATE.format(subtema=subtema, dimension=dimension)

        try:
            response = await client.aio.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt,
            )
            raw_text = response.text
            json_match = re.search(r'\{[^{}]+\}', raw_text)
            if json_match:
                json_str = json_match.group(0)
                data = json.loads(json_str)
                words = len(data.get("base_response", "").split())
                if 30 <= words <= 55:
                    async with lock:
                        if len(context_list) < MAX_CONCEPTOS:
                            context_list.append(data)
                            print(f"Concepto generado: {len(context_list)}/{MAX_CONCEPTOS}")
        except Exception as e:
            print(f"Error generando {subtema} - {dimension}: {e}")

async def main():
    lock = asyncio.Lock()
    conceptos_generados = []

    tasks = []
    for subtema in SUBTEMAS_GUIA:
        for dimension in DIMENSIONES:
            if len(tasks) > MAX_CONCEPTOS * 2:
                break
            tasks.append(generate_concept(subtema, dimension, lock, conceptos_generados))
        if len(tasks) > MAX_CONCEPTOS * 2:
            break

    await asyncio.gather(*tasks)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(conceptos_generados[:MAX_CONCEPTOS], f, ensure_ascii=False, indent=2)

    print(f"Generación completa. Total guardado: {len(conceptos_generados[:MAX_CONCEPTOS])}")

if __name__ == "__main__":
    asyncio.run(main())