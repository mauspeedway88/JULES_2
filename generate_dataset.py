import json
import asyncio
import re
import os
from g4f.client import AsyncClient
from unidecode import unidecode

DESTINATION_FILE = "GBX_brain_62B.json"
MAX_CONCEPTS = 235

SUBTEMAS_GUIA = [
    "Párrafos argumentativos de redacción",
    "Párrafos expositivos de redacción",
    "Párrafos descriptivos de redacción",
    "Escritos periodísticos de redacción",
    "Cartas formales de redacción",
    "Correos electrónicos bien redactados",
    "Informes escolares de redacción",
    "Reseñas críticas de redacción",
    "Monografías de investigación redactada",
    "Artículos de opinión redactados",
    "Crónicas narradas por escrito",
    "Noticias redactadas con objetividad",
    "Tesis principal de redacción",
    "Argumentos de apoyo redactados",
    "Contraargumentos del texto redactado",
    "Citas textuales en redacción",
    "Paráfrasis de fuentes redactadas",
    "Bibliografía del texto redactado",
    "Normas APA en redacción",
    "Márgenes del formato redactado",
    "Sangría de párrafos redactados",
    "Interlineado del documento redactado",
    "Títulos de textos redactados",
    "Subtítulos de secciones redactadas",
    "Índices de contenido redactado",
    "Glosarios de términos redactados",
    "Anexos del documento redactado"
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

SYSTEM_PROMPT = """Eres un ingeniero de datos automatizado extrayendo conocimiento educativo sobre {subtema} en su dimensión de '{dimension}'.
ESTRICTAMENTE CONFINADO A ESTUDIANTES DE 9 A 15 AÑOS. Solo español.

VÁLVULA DE ESCAPE OBLIGATORIA: Si la dimensión NO TIENE APLICACIÓN DIRECTA O SENTIDO CIENTÍFICO/EDUCATIVO REAL para este subtema, responde exactamente con la palabra: OMITIR. No alucines, no fuerces historias, no inventes. Solo da información si tiene valor educativo genuino.

Debes devolver la información EXCLUSIVAMENTE en formato JSON plano usando la siguiente estructura, sin formato Markdown, sin comillas alrededor de la respuesta global:

{{
  "intent_id": "<un_id_unico_semantico_con_guiones_bajos_sin_numeros>",
  "keywords": ["palabra1", "palabra2", "palabra3", "palabra4", "palabra5"],
  "base_response": "<respuesta_educativa>"
}}

REGLAS DE FORMATEO (Si no devuelves OMITIR):
- intent_id: debe ser semántico, reflejar el tema y dimensión, sin números secuenciales. (ej: concepto_estructura_parrafo_argumentativo).
- keywords: EXACTAMENTE entre 4 y 6 términos, TODOS EN MINÚSCULAS, SIN TILDES, SIN ACENTOS. EXCLUSIVAMENTE SUSTANTIVOS Y VERBOS NUCLEARES. SIN palabras funcionales (el, la, de, para). (ej: parrafo, estructura, idea, argumentar).
- base_response: EXACTAMENTE entre 35 y 50 palabras. Tono instruccional directo, sin saludos, sin muletillas, sin frases de cierre para rellenar, sin conteos de palabras al final, sin referencias a fuentes. DEBE tener ortografía inmaculada con TILDES donde correspondan. FORMATO DE TEXTO PLANO: Cero saltos de línea (\\n) dentro del texto y usa comillas simples (' ') si necesitas comillas en lugar de dobles. No inicies con palabras ambiguas que causan problemas de tilde al inicio como 'esta'.
"""

def clean_response(text):
    text = text.replace('```json', '').replace('```', '').strip()
    text = re.sub(r'\[\[.*?\]\]\(.*?\)', '', text)
    return text

def format_base_response(text):
    text = text.replace('\n', ' ')
    text = text.replace('"', "'")
    return text.strip()

def process_keywords(kw_list):
    new_kws = []
    for kw in kw_list:
        kw = unidecode(kw.lower().strip())
        new_kws.append(kw)
    return new_kws

async def fetch_concept(client, semaphore, subtema, dimension):
    async with semaphore:
        prompt = SYSTEM_PROMPT.format(subtema=subtema, dimension=dimension)
        try:
            response = await client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
            )
            content = response.choices[0].message.content.strip()

            if "OMITIR" in content.upper()[:10]:
                return None

            content = clean_response(content)
            data = json.loads(content)

            # Validation
            intent_id = data.get('intent_id', '')
            if any(char.isdigit() for char in intent_id):
                return None

            keywords = data.get('keywords', [])
            if not (4 <= len(keywords) <= 6):
                return None
            keywords = process_keywords(keywords)

            base_response = format_base_response(data.get('base_response', ''))
            word_count = len(base_response.split())
            if not (35 <= word_count <= 50):
                return None

            return {
                "intent_id": intent_id,
                "keywords": keywords,
                "base_response": base_response
            }
        except Exception as e:
            # Ignore failures, let the loop handle skips
            return None

async def main():
    client = AsyncClient()
    semaphore = asyncio.Semaphore(15)

    generated_concepts = []
    total_generated = 0

    # Initialize file empty
    with open(DESTINATION_FILE, 'w', encoding='utf-8') as f:
        f.write('[')

    first_item = True

    tasks = []
    concept_combos = [(s, d) for s in SUBTEMAS_GUIA for d in DIMENSIONES]

    # Process in batches to write incrementally
    batch_size = 40
    for i in range(0, len(concept_combos), batch_size):
        if total_generated >= MAX_CONCEPTS:
            break

        batch_combos = concept_combos[i:i+batch_size]
        batch_tasks = [fetch_concept(client, semaphore, s, d) for s, d in batch_combos]
        results = await asyncio.gather(*batch_tasks)

        valid_results = [r for r in results if r is not None]

        # Write batch incrementally
        with open(DESTINATION_FILE, 'a', encoding='utf-8') as f:
            for item in valid_results:
                if total_generated >= MAX_CONCEPTS:
                    break

                if not first_item:
                    f.write(',\n')
                else:
                    f.write('\n')
                    first_item = False

                json.dump(item, f, ensure_ascii=False, indent=2)
                total_generated += 1

        print(f"Lote procesado. Conceptos acumulados: {total_generated}/{MAX_CONCEPTS}")

    with open(DESTINATION_FILE, 'a', encoding='utf-8') as f:
        f.write('\n]')

    print(f"Finalizado. Total de conceptos generados: {total_generated}")

if __name__ == "__main__":
    asyncio.run(main())
