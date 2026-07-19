import asyncio
import json
import re
import os
from g4f.client import AsyncClient
from unidecode import unidecode

# VARIABLES DE EJECUCIÓN
ARCHIVO_DESTINO = "GBX_brain_54A.json"
MAX_CONCEPTOS = 275

SUBTEMAS_GUIA = [
    "Historia de El Salvador",
    "Época Prehispánica de El Salvador",
    "Conquista española de El Salvador",
    "Independencia nacional de El Salvador",
    "República inicial de El Salvador",
    "Conflicto Armado de El Salvador",
    "Acuerdos de Paz salvadoreños históricos",
    "Señorío de Cuzcatlán en Salvador",
    "Ruinas de Tazumal El Salvador",
    "Sitio arqueológico Joya de Cerén",
    "Rebelión campesina salvadoreña del treintaydós",
    "Dinastía Meléndez Quiñónez en Salvador",
    "Cultivo del añil salvadoreño histórico",
    "Auge cafetalero de El Salvador",
    "Dictadura de Maximiliano Hernández Martínez",
    "Guerra de las Cien Horas",
    "Ofensiva final salvadoreña del ochentaynueve",
    "Masacre del Mozote El Salvador",
    "Constitución política salvadoreña del ochentaytrés",
    "Asesinato de Monseñor Romero salvadoreño",
    "Terremotos históricos de El Salvador",
    "Migración salvadoreña hacia Estados Unidos",
    "Dolarización económica de El Salvador",
    "Provincia de San Salvador colonial",
    "Firma de independencia de Salvador",
    "Federación Centroamericana y El Salvador",
    "Batalla de Arada El Salvador",
    "Introducción del telégrafo en Salvador",
    "Ferrocarril salvadoreño de época republicana"
]

DIMENSIONES_TAXONOMICAS = [
    "Definición anatómica o estructural.",
    "Dinámica y funcionamiento físico.",
    "Propiedades químicas o materiales.",
    "Errores, fallas y patologías comunes.",
    "Historia, origen y evolución.",
    "Contexto y entorno ecológico.",
    "Aplicaciones prácticas en la vida real.",
    "Importancia e impacto social.",
    "Ventajas y desventajas comparativas.",
    "Riesgos y medidas de seguridad.",
    "Clasificación taxonómica.",
    "Cálculos y fórmulas asociadas.",
    "Mitos y concepciones erróneas.",
    "Relación simbiótica con otros sistemas.",
    "Transformación y ciclos energéticos.",
    "Experimentos y demostraciones escolares.",
    "Consecuencias a largo plazo.",
    "Impacto ambiental.",
    "Mantenimiento y prevención.",
    "Proyecciones futuras y tecnología."
]

def sanitize_text(text):
    text = text.replace('\n', ' ')
    text = text.replace('"', "'")
    return text.strip()

def process_keywords(keywords_list):
    processed = []
    stopwords = {'el', 'la', 'los', 'las', 'un', 'una', 'unos', 'unas', 'y', 'o', 'de', 'del', 'en', 'a', 'ante', 'bajo', 'con', 'contra', 'desde', 'hacia', 'hasta', 'para', 'por', 'segun', 'sin', 'sobre', 'tras', 'al', 'que', 'como', 'cual', 'quien', 'donde', 'cuando', 'porque', 'aunque'}
    for kw in keywords_list:
        kw = unidecode(kw.lower()).strip()
        kw = re.sub(r'[^a-z0-9\s]', '', kw)
        words = [w for w in kw.split() if w not in stopwords and len(w) > 1]
        processed.extend(words)
    return list(dict.fromkeys(processed))[:6]

async def generate_concept(client, sem, subtema, dimension):
    prompt = f"""
    Genera un único concepto educativo estrictamente enfocado en la dimensión "{dimension}" del subtema "{subtema}".

    REGLAS ESTRICTAS Y OBLIGATORIAS:
    - Audiencia: Estudiantes de 9 a 15 años (simplifica conceptos sin perder veracidad científica).
    - VÁLVULA DE ESCAPE: Si la dimensión no aplica o no tiene información científica real para este subtema, responde exactamente con la palabra "OMITIR". No intentes forzar una respuesta o inventar datos.
    - No uses trampas: no clones palabras clave, no uses sufijos o secuencias numéricas, no agregues frases de relleno ni saludos ni conteo de palabras.

    El resultado DEBE SER ÚNICAMENTE UN JSON VÁLIDO con esta estructura exacta y escapando las llaves con doble llave si fuera necesario para string format:
    {{
      "intent_id": "identificador_unico_semantico",
      "keywords": ["palabra1", "palabra2", "palabra3", "palabra4", "palabra5"],
      "base_response": "La respuesta de 35 a 50 palabras exactas..."
    }}

    Reglas adicionales del JSON:
    - intent_id: En minúsculas, palabras separadas por guiones bajos, SEMÁNTICO (por ejemplo: "historia_evolucion_sitio_joya_ceren"), y CERO números secuenciales al final.
    - keywords: Entre 4 y 6 términos exactos. TODO en minúsculas, SIN TILDES y SIN ACENTOS. Ninguna palabra funcional (ni el, la, de, en, y, etc.). Solo sustantivos y verbos nucleares.
    - base_response: DEBE tener exactamente entre 35 y 50 palabras. Ortografía inmaculada (CON TILDES donde correspondan). Sin saltos de línea internos (texto plano continuo), usar comillas simples (') en lugar de comillas dobles (") adentro del texto. Tono instruccional directo, sin introducciones ni metatexto, ni conteo de palabras al final.
    - Evita empezar la frase de base_response con la palabra "esta" o ambiguas para evitar problemas de tildes.
    """

    async with sem:
        try:
            response = await client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
            )

            content = response.choices[0].message.content.strip()

            if "OMITIR" in content:
                return None

            # Extract JSON from potential markdown formatting
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                content = json_match.group(0)

            data = json.loads(content)

            intent_id = data.get("intent_id", "")
            if not intent_id or re.search(r'_[0-9]+$', intent_id) or re.search(r'_[a-z]$', intent_id):
                base_id = re.sub(r'[^a-z0-9]+', '_', unidecode(subtema.lower()))
                dim_id = re.sub(r'[^a-z0-9]+', '_', unidecode(dimension.split()[0].lower()))
                intent_id = f"{base_id}_{dim_id}"

            raw_keywords = data.get("keywords", [])
            keywords = process_keywords(raw_keywords)
            if len(keywords) < 4:
                keywords.extend(process_keywords([intent_id.replace('_', ' ')]))
                keywords = list(dict.fromkeys(keywords))[:6]
                if len(keywords) < 4:
                    return None

            base_response = sanitize_text(data.get("base_response", ""))
            word_count = len(re.findall(r'\b\w+\b', base_response))

            if word_count < 35 or word_count > 50:
                return None

            # Anti-foreign words check (simple heuristic for English)
            if re.search(r'\b(the|and|is|are|of|in|to)\b', base_response.lower()):
                return None

            return {
                "intent_id": intent_id,
                "keywords": keywords,
                "base_response": base_response
            }

        except Exception as e:
            # print(f"Error generating concept for {subtema} - {dimension}: {e}")
            return None

async def main():
    client = AsyncClient()
    sem = asyncio.Semaphore(5)

    all_concepts = []
    concept_count = 0
    seen_intents = set()

    print("Iniciando generacion de conceptos...")

    for subtema in SUBTEMAS_GUIA:
        if concept_count >= MAX_CONCEPTOS:
            break

        print(f"Procesando subtema: {subtema}")
        tasks = [generate_concept(client, sem, subtema, dimension) for dimension in DIMENSIONES_TAXONOMICAS]
        results = await asyncio.gather(*tasks)

        for res in results:
            if res and res["intent_id"] not in seen_intents:
                # Add validation for keywords without accents
                res["keywords"] = [unidecode(kw) for kw in res["keywords"]]

                all_concepts.append(res)
                seen_intents.add(res["intent_id"])
                concept_count += 1

                if concept_count % 10 == 0:
                    print(f"Generados {concept_count} conceptos validados.")
                    with open(ARCHIVO_DESTINO, 'w', encoding='utf-8') as f:
                        json.dump(all_concepts, f, ensure_ascii=False, indent=2)

                if concept_count >= MAX_CONCEPTOS:
                    break

    print(f"Finalizado. Se generaron {concept_count} conceptos.")

    with open(ARCHIVO_DESTINO, 'w', encoding='utf-8') as f:
        json.dump(all_concepts, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    asyncio.run(main())
