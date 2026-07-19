import asyncio
import json
import re
import os
from g4f.client import AsyncClient
import nest_asyncio
from unidecode import unidecode

nest_asyncio.apply()

# Archivo de salida
OUTPUT_FILE = "GBX_brain_53A.json"

# Subtemas y dimensiones
SUBTEMAS = [
    "Historia de América — Descubrimiento europeo de América histórica",
    "Colonización española en continente americano",
    "Pueblos precolombinos de América histórica",
    "Independencias nacionales de América Latina",
    "Revoluciones sociales en América histórica",
    "Virreinatos coloniales de historia americana",
    "Civilización Maya en América precolombina",
    "Imperio Azteca de historia americana",
    "Imperio Inca en América histórica",
    "Conquista de México historia americana",
    "Conquista del Perú en América",
    "Esclavitud africana en América colonial",
    "Mestizaje cultural de historia americana",
    "Reformas borbónicas en América española",
    "Doctrina Monroe de historia americana",
    "Revolución Cubana en América contemporánea",
    "Guerra civil estadounidense historia americana",
    "Caudillismo político en América Latina",
    "Dictaduras militares de América Latina",
    "Plan Cóndor en historia americana",
    "Crisis de misiles en Cuba",
    "Tratados de libre comercio americanos",
    "Civilización Olmeca en América precolombina",
    "Cultura Teotihuacana de historia americana",
    "Expansión territorial de Estados Unidos",
    "Fiebre del oro americana histórica",
    "Revolución Mexicana en historia americana",
    "Guerra del Pacífico en Sudamérica",
    "Guerra de Secesión americana histórica"
]

DIMENSIONES = [
    "1. Definición anatómica o estructural",
    "2. Dinámica y funcionamiento físico",
    "3. Propiedades químicas o materiales",
    "4. Errores, fallas y patologías comunes",
    "5. Historia, origen y evolución",
    "6. Contexto y entorno ecológico",
    "7. Aplicaciones prácticas en la vida real",
    "8. Importancia e impacto social",
    "9. Ventajas y desventajas comparativas",
    "10. Riesgos y medidas de seguridad",
    "11. Clasificación taxonómica",
    "12. Cálculos y fórmulas asociadas",
    "13. Mitos y concepciones erróneas",
    "14. Relación simbiótica con otros sistemas",
    "15. Transformación y ciclos energéticos",
    "16. Experimentos y demostraciones escolares",
    "17. Consecuencias a largo plazo",
    "18. Impacto ambiental",
    "19. Mantenimiento y prevención",
    "20. Proyecciones futuras y tecnología"
]

MAX_CONCEPTS = 275
BATCH_SIZE = 15

client = AsyncClient()
semaphore = asyncio.Semaphore(5)

def clean_json_string(s):
    # Intentar limpiar la respuesta de la IA en caso de que venga con bloques markdown
    s = s.strip()
    if s.startswith("```json"):
        s = s[7:]
    elif s.startswith("```"):
        s = s[3:]
    if s.endswith("```"):
        s = s[:-3]
    return s.strip()

def process_keywords(keywords_list):
    processed = []
    # stopwords simples para filtrar si el LLM las incluyó
    stopwords = {"el", "la", "los", "las", "un", "una", "unos", "unas", "de", "en", "a", "y", "o", "por", "para", "con"}
    for kw in keywords_list:
        kw_clean = unidecode(kw.lower().strip())
        if kw_clean and kw_clean not in stopwords:
            processed.append(kw_clean)
    return processed[:6] # Asegurar max 6

async def generate_concept(subtema, dimension):
    async with semaphore:
        prompt = f"""
Eres un especialista en minería de información educativa para estudiantes de Tercer Ciclo (9 a 15 años).
Tu objetivo es extraer un concepto científico/histórico real sobre el subtema '{subtema}', enfocado ESTRICTAMENTE en la dimensión '{dimension}'.
VÁLVULA DE ESCAPE: Si la dimensión NO TIENE APLICACIÓN REAL O SENTIDO HISTÓRICO/CIENTÍFICO para este subtema, devuelve EXACTAMENTE el string: SKIP.

Restricciones para el JSON si decides responder:
1. "intent_id": un ID único semántico que combine el tema y dimensión, en minúsculas, con guiones bajos, SIN NÚMEROS SECUENCIALES.
2. "keywords": un arreglo de EXACTAMENTE entre 4 y 6 palabras clave. Todas en minúsculas, SIN NINGUNA TILDE, SIN PALABRAS FUNCIONALES (artículos, preposiciones), SOLO SUSTANTIVOS O VERBOS.
3. "base_response": un texto de EXACTAMENTE entre 35 y 50 palabras. Texto plano sin saltos de línea internos, ortografía perfecta (con tildes), tono instruccional directo, iniciando con la información real sin saludos.

Devuelve ÚNICAMENTE un JSON válido con las claves "intent_id", "keywords" (array de strings) y "base_response" (string). No agregues ningún otro texto o comentario.
"""
        try:
            response = await client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}]
            )
            content = response.choices[0].message.content
            if "SKIP" in content:
                return None

            cleaned_content = clean_json_string(content)
            data = json.loads(cleaned_content)

            # Validar y procesar datos
            intent_id = data.get("intent_id", "").lower().replace("-", "_")
            intent_id = re.sub(r'[0-9]+', '', intent_id) # Sin números

            keywords = data.get("keywords", [])
            keywords = process_keywords(keywords)
            if len(keywords) < 4:
                return None # No cumple la regla mínima de keywords

            base_response = data.get("base_response", "")
            base_response = base_response.replace('\n', ' ').replace('"', "'")

            # Validar conteo de palabras
            word_count = len(base_response.split())
            if word_count < 35 or word_count > 50:
                return None # No cumple conteo de palabras

            return {
                "intent_id": intent_id,
                "keywords": keywords,
                "base_response": base_response
            }
        except Exception as e:
            # print(f"Error generando: {e}")
            return None

async def main():
    generated_concepts = []
    total_generated = 0

    # Crear/abrir archivo JSON y empezar el array
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("[\n")

    for subtema in SUBTEMAS:
        if total_generated >= MAX_CONCEPTS:
            break

        tasks = []
        for dimension in DIMENSIONES:
            tasks.append(generate_concept(subtema, dimension))

        results = await asyncio.gather(*tasks)

        valid_results = [res for res in results if res is not None]

        # Filtrar duplicados (por intent_id simple)
        seen_ids = {c["intent_id"] for c in generated_concepts}
        new_valid = []
        for r in valid_results:
            if r["intent_id"] not in seen_ids:
                new_valid.append(r)
                seen_ids.add(r["intent_id"])

        # Asegurar no pasarse del límite
        for concept in new_valid:
            if total_generated >= MAX_CONCEPTS:
                break
            generated_concepts.append(concept)

            # Anexar al archivo
            with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
                json_str = json.dumps(concept, ensure_ascii=False)
                if total_generated == 0:
                    f.write(f"  {json_str}")
                else:
                    f.write(f",\n  {json_str}")

            total_generated += 1
            print(f"Generados: {total_generated}/{MAX_CONCEPTS} - Último añadido: {concept['intent_id']}")

            # Realizar commit incremental cada cierto lote si es necesario (no bloquearemos el loop para esto,
            # lo dejaremos como un solo commit grande por simplicidad o unos pocos si el proceso es muy largo,
            # pero por ahora lo más seguro y rápido es generar todo y hacer commit final, para no interrumpir el AsyncClient).

    # Cerrar el array JSON
    with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
        f.write("\n]\n")

    print(f"Generación finalizada con {total_generated} conceptos.")

if __name__ == "__main__":
    asyncio.run(main())
