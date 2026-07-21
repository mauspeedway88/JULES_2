import json
import asyncio
import re
from g4f.client import AsyncClient

SUBTEMAS = [
    "Mapas conceptuales de lectura", "Cuadros sinópticos de textos", "Vocabulario por contexto lector",
    "Significado de palabras leídas", "Estrategias de lectura veloz", "Retención de información leída",
    "Interpretación de textos complejos", "Deducciones de comprensión lectora", "Conclusiones derivadas de lectura",
    "Puntos de vista leídos", "Hechos verificables del texto", "Opiniones subjetivas de lectura",
    "Tono emocional del texto", "Ironía en textos leídos", "Sarcasmo en comprensión lectora",
    "Doble sentido del texto", "Lectura inferencial de documentos", "Lectura literal de textos",
    "Metacognición de comprensión lectora", "Automonitoreo durante la lectura", "Relectura de párrafos confusos",
    "Preguntas sobre textos leídos", "Conocimientos previos de lectura", "Síntesis de información leída",
    "Evaluación de fuentes leídas", "Fiabilidad del texto leído", "Sesgos del autor leído",
    "Falacias en textos argumentativos", "Contraste de textos leídos", "Tipología textual de lectura",
    "Lectura silenciosa de comprensión", "Lectura en voz alta"
]

DIMENSIONES = [
    "Definición anatómica o estructural", "Dinámica y funcionamiento físico", "Propiedades químicas o materiales",
    "Errores, fallas y patologías comunes", "Historia, origen y evolución", "Contexto y entorno ecológico",
    "Aplicaciones prácticas en la vida real", "Importancia e impacto social", "Ventajas y desventajas comparativas",
    "Riesgos y medidas de seguridad", "Clasificación taxonómica", "Cálculos y fórmulas asociadas",
    "Mitos y concepciones erróneas", "Relación simbiótica con otros sistemas", "Transformación y ciclos energéticos",
    "Experimentos y demostraciones escolares", "Consecuencias a largo plazo", "Impacto ambiental",
    "Mantenimiento y prevención", "Proyecciones futuras y tecnología"
]

PROMPT_TEMPLATE = """
MANDATO OPERATIVO PRINCIPAL: Eres un generador estricto de conceptos académicos para estudiantes de Tercer Ciclo (9 a 15 años). Simplifica pero mantén la veracidad científica.
Genera un concepto sobre el subtema "{subtema}" en la dimensión taxonómica "{dimension}".

Debes devolver EXCLUSIVAMENTE UN OBJETO JSON con la siguiente estructura y formato. ¡NINGUNA OTRA PALABRA FUERA DEL JSON!:
{{
  "intent_id": "identificador_unico_semantico_sin_numeros",
  "keywords": ["palabra", "otra", "mas", "otra"],
  "base_response": "Explicación directa sin saludos, ortografía perfecta, entre 35 y 50 palabras, sin comillas dobles internas ni saltos de línea."
}}

REGLAS ESTRICTAS QUE DEBES CUMPLIR (O FALLARÁS):
1. `intent_id`: único, semántico, minúsculas, separado por guiones bajos, ¡SIN NÚMEROS! Solo el concepto central.
2. `keywords`: exactamente entre 4 y 6 términos, TODO minúsculas, SIN TILDES, SIN ACENTOS. ¡SIN PALABRAS FUNCIONALES! (no uses artículos, no uses preposiciones, sin 'el', 'la', 'de', 'en', 'para', etc.). Solo sustantivos y verbos nucleares únicos.
3. `base_response`: exactamente entre 35 y 50 palabras. Ortografía INMACULADA con tildes y acentos donde correspondan. Tono instruccional directo, arranca directo con el concepto (sin "Hola" o "Te explico"). Texto plano total (sin \n, sin comillas dobles, sin enlaces, sin Markdown).

¡Devuelve SÓLO EL JSON!
"""

stop_words = {'el', 'la', 'los', 'las', 'un', 'una', 'unos', 'unas', 'de', 'del', 'a', 'al', 'en', 'por', 'para', 'con', 'sin', 'sobre', 'y', 'o', 'pero', 'es', 'son', 'se', 'su', 'sus'}

def remove_accents(text):
    import unicodedata
    return ''.join(c for c in unicodedata.normalize('NFD', text) if unicodedata.category(c) != 'Mn')

def validate_and_clean_keywords(keywords):
    if not isinstance(keywords, list):
        return None
    if not (4 <= len(keywords) <= 6):
        return None

    cleaned = []
    for kw in keywords:
        kw_clean = remove_accents(kw.lower().strip())
        if kw_clean and kw_clean not in stop_words:
            cleaned.append(kw_clean)

    if not (4 <= len(cleaned) <= 6):
        return None
    return cleaned

def validate_base_response(response):
    words = response.split()
    if not (35 <= len(words) <= 50):
        return None
    response = response.replace('\n', ' ').replace('"', "'")
    response = re.sub(r'\[\[.*?\]\]\(.*?\)', '', response)
    return response.strip()

def fix_intent_id(intent_id, subtema, dimension):
    intent_id = re.sub(r'\d+', '', intent_id)
    intent_id = intent_id.strip('_')

    if not intent_id or intent_id == '_':
         intent_id = f"{remove_accents(subtema).replace(' ', '_').lower()}_{remove_accents(dimension).replace(' ', '_').lower()}"
    return intent_id

async def generate_concept(client, sem, subtema, dimension):
    async with sem:
        prompt = PROMPT_TEMPLATE.format(subtema=subtema, dimension=dimension)
        try:
            response = await client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=250
            )
            content = response.choices[0].message.content

            match = re.search(r'\{.*\}', content, re.DOTALL)
            if not match:
                return None

            data = json.loads(match.group(0))

            intent_id = fix_intent_id(data.get('intent_id', ''), subtema, dimension)
            keywords = validate_and_clean_keywords(data.get('keywords', []))
            base_response = validate_base_response(data.get('base_response', ''))

            if not keywords or not base_response:
                return None

            return {
                "intent_id": intent_id,
                "keywords": keywords,
                "base_response": base_response
            }

        except Exception as e:
            print(f"Error generating {subtema} - {dimension}: {e}")
            return None

async def main():
    client = AsyncClient()
    sem = asyncio.Semaphore(5)

    results = []
    total_concepts = 0
    seen_ids = set()

    for subtema in SUBTEMAS:
        if total_concepts >= 200:
            break

        tasks = []
        for dimension in DIMENSIONES:
            tasks.append(generate_concept(client, sem, subtema, dimension))

        batch_results = await asyncio.gather(*tasks)

        for item in batch_results:
            if item and item['intent_id'] not in seen_ids:
                seen_ids.add(item['intent_id'])
                results.append(item)
                total_concepts += 1

                if total_concepts >= 200:
                    break

        print(f"Subtema processed: {subtema}. Total concepts so far: {total_concepts}")

        with open('GBX_brain_63B.json', 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"Finished generating {len(results)} concepts.")

if __name__ == "__main__":
    asyncio.run(main())