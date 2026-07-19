import os
import json
import asyncio
import re
from unidecode import unidecode
from g4f.client import AsyncClient

# Constants
DESTINATION_FILE = 'GBX_brain_52B.json'
MAX_CONCEPTS = 275
BATCH_SIZE = 30
CONCURRENCY_LIMIT = 5

# Subtopics array
SUBTOPICS = [
    "Historia Universal - Revolución Rusa",
    "Crisis económica del veintinueve universal",
    "Fin del mundo bipolar universal",
    "Revolución Neolítica de historia universal",
    "Surgimiento del Estado moderno universal",
    "Mercantilismo económico en historia universal",
    "Humanismo filosófico de historia universal",
    "Reformas protestantes de historia universal",
    "Descubrimientos geográficos en historia universal",
    "Tratado de Versalles historia universal",
    "Surgimiento del fascismo historia universal",
    "Era de los imperios coloniales",
    "Independencias asiáticas en historia universal",
    "Revolución China en historia universal",
    "Pandemias globales de historia universal",
    "Exploración espacial de historia universal",
    "Avances médicos en historia universal",
    "Movimientos obreros en historia universal",
    "Derechos humanos en historia universal",
    "Cambio climático en historia contemporánea",
    "Formación de Naciones Unidas universal",
    "Revoluciones atlánticas de historia universal",
    "Crisis de entreguerras historia universal",
    "Desarrollo del capitalismo histórico universal",
    "Era de la información universal"
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

STOP_WORDS = {"el", "la", "los", "las", "un", "una", "unos", "unas", "de", "del", "a", "ante", "bajo", "cabe", "con", "contra", "desde", "en", "entre", "hacia", "hasta", "para", "por", "segun", "sin", "sobre", "tras", "y", "o", "u", "e"}

def sanitize_keywords(keyword_list):
    sanitized = []
    for kw in keyword_list:
        kw = unidecode(kw.lower())
        words = kw.split()
        filtered = [w for w in words if w not in STOP_WORDS]
        sanitized.extend(filtered)
    return sanitized[:6] if len(sanitized) >= 4 else sanitized

def validate_base_response(text):
    text = text.replace('\n', ' ').replace('"', "'")
    word_count = len(text.split())
    if 35 <= word_count <= 50:
        return text
    return None

async def generate_concept(client, semaphore, subtopic, dimension):
    async with semaphore:
        prompt = f"""Eres un experto educativo creando contenido científico e histórico riguroso para estudiantes de Tercer Ciclo (9 a 15 años). Solo español. NUNCA escribir en inglés.

        Genera un concepto sobre el subtema: '{subtopic}', enfocado ESTRICTAMENTE en la dimensión: '{dimension}'.
        VÁLVULA DE ESCAPE: Si la dimensión NO aplica al subtema o carece de valor científico real e histórico diferenciado, devuelve exactamente esto: {{"skip": true}}

        Si aplica, genera un objeto JSON con esta estructura exacta, sin markdown, solo el texto plano del JSON.

        {{
            "intent_id": "identificador_unico_semantico_en_minusculas_con_guiones_bajos",
            "keywords": ["palabra1", "palabra2", "palabra3", "palabra4", "palabra5"],
            "base_response": "Explicación del concepto que inicie directamente con la carga de conocimiento, con tono instruccional directo, sin saludos ni muletillas. Exactamente entre 35 y 50 palabras. Ortografía inmaculada, incluyendo tildes. Sin comillas dobles internas ni saltos de línea. NUNCA incluyas conteos de palabras al final."
        }}

        Reglas estrictas para el JSON:
        - intent_id: sin números secuenciales, solo palabras descriptivas.
        - keywords: exactamente 4 a 6 palabras. TODO en minúsculas, SIN tildes ni acentos, SIN palabras funcionales (el, la, de, y, con...). Usa solo sustantivos y verbos nucleares.
        - base_response: debe cumplir el conteo y reglas.
        """

        try:
            response = await client.chat.completions.create(
                model="gpt-4", # using standard routing
                messages=[{"role": "user", "content": prompt}],
            )
            content = response.choices[0].message.content

            # extract JSON
            match = re.search(r'\{.*\}', content, re.DOTALL)
            if match:
                json_str = match.group(0)
                data = json.loads(json_str)
                if data.get("skip"):
                    return None

                # validation
                intent_id = data.get("intent_id", "")
                if any(char.isdigit() for char in intent_id) or not intent_id:
                    return None

                kws = data.get("keywords", [])
                sanitized_kws = sanitize_keywords(kws)
                if not (4 <= len(sanitized_kws) <= 6):
                    return None

                base_resp = data.get("base_response", "")
                valid_resp = validate_base_response(base_resp)
                if not valid_resp:
                    return None

                return {
                    "intent_id": intent_id,
                    "keywords": sanitized_kws,
                    "base_response": valid_resp
                }
            return None
        except Exception as e:
            # print(f"Error generating concept: {e}")
            return None

async def main():
    client = AsyncClient()
    semaphore = asyncio.Semaphore(CONCURRENCY_LIMIT)

    concepts_generated = 0

    with open(DESTINATION_FILE, 'w', encoding='utf-8') as f:
        f.write('[\n')

    is_first = True

    for subtopic in SUBTOPICS:
        if concepts_generated >= MAX_CONCEPTS:
            break

        tasks = []
        for dim in DIMENSIONS:
            if concepts_generated + len(tasks) >= MAX_CONCEPTS:
                break
            tasks.append(generate_concept(client, semaphore, subtopic, dim))

        results = await asyncio.gather(*tasks)

        valid_results = [r for r in results if r is not None]

        if valid_results:
            with open(DESTINATION_FILE, 'a', encoding='utf-8') as f:
                for idx, result in enumerate(valid_results):
                    if concepts_generated >= MAX_CONCEPTS:
                        break

                    if not is_first:
                        f.write(',\n')
                    is_first = False

                    json.dump(result, f, ensure_ascii=False, indent=4)
                    concepts_generated += 1

            print(f"Subtopic '{subtopic}' processed. Total valid concepts: {concepts_generated}")
            # Incremental commit (simulate or direct git commands could be run, but doing it in bash later is safer to avoid blocking)

        if concepts_generated >= MAX_CONCEPTS:
            print(f"Maximum limit of {MAX_CONCEPTS} reached. Stopping.")
            break

    with open(DESTINATION_FILE, 'a', encoding='utf-8') as f:
        f.write('\n]')

    print(f"Finished generating dataset. Total concepts: {concepts_generated}")

if __name__ == "__main__":
    asyncio.run(main())
