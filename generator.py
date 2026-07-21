import json
import asyncio
import re
from g4f.client import AsyncClient

# Constants
DESTINATION_FILE = "GBX_brain_63B.json"
MAX_CONCEPTS = 175
# Semantic ID combination subset rule: "_".join(keywords[:4])

SUBTHEMES = [
    "Mapas conceptuales de lectura",
    "Cuadros sinópticos de textos",
    "Vocabulario por contexto lector",
    "Significado de palabras leídas",
    "Estrategias de lectura veloz",
    "Retención de información leída",
    "Interpretación de textos complejos",
    "Deducciones de comprensión lectora",
    "Conclusiones derivadas de lectura",
    "Puntos de vista leídos",
    "Hechos verificables del texto",
    "Opiniones subjetivas de lectura",
    "Tono emocional del texto",
    "Ironía en textos leídos",
    "Sarcasmo en comprensión lectora",
    "Doble sentido del texto",
    "Lectura inferencial de documentos",
    "Lectura literal de textos",
    "Metacognición de comprensión lectora",
    "Automonitoreo durante la lectura",
    "Relectura de párrafos confusos",
    "Preguntas sobre textos leídos",
    "Conocimientos previos de lectura",
    "Síntesis de información leída",
    "Evaluación de fuentes leídas",
    "Fiabilidad del texto leído",
    "Sesgos del autor leído",
    "Falacias en textos argumentativos",
    "Contraste de textos leídos",
    "Tipología textual de lectura",
    "Lectura silenciosa de comprensión",
    "Lectura en voz alta"
]

DIMENSIONS = [
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

STOP_WORDS = {'el', 'la', 'los', 'las', 'un', 'una', 'unos', 'unas', 'de', 'del', 'en', 'a', 'al', 'con', 'por', 'para', 'y', 'o', 'su', 'sus'}

PROMPT_TEMPLATE = """
Eres un especialista en Minería de Información Educativa. Genera 1 concepto independiente sobre "{subtheme}" desde la siguiente dimensión taxonómica: "{dimension}".
RESTRICCIÓN DE NIVEL ACADÉMICO: El dataset está estrictamente confinado a estudiantes de Tercer Ciclo (9 a 15 años). Simplifica conceptos universitarios sin perder veracidad científica.
DIRECTRIZ SUPREMA DE CALIDAD: Prohibido clonar arreglos de palabras clave. Prohibido crear secuencias o sufijos numéricos en los identificadores. Prohibido pegar frases repetitivas de cierre. Prohibido alucinar profesiones o historias para fingir variedad. Cada concepto debe aportar valor científico real y diferenciado.
VÁLVULA DE ESCAPE: Si la dimensión no aplica o no tiene información científica real, responde "OMITIR".

ESTRUCTURA DE DATOS REQUERIDA (devolver SOLO formato JSON, sin bloques de código, referencias ni citaciones de estilo markdown, todo texto plano en el base_response):
{{
    "keywords": ["sustantivo1", "verbo1", "sustantivo2", "verbo2", "sustantivo3"],
    "base_response": "Carga de conocimiento directo, entre 35 y 50 palabras, con ortografía inmaculada, sin saltos de linea, sin dobles comillas sin escapar."
}}

REGLAS DE FORMATEO ESTRICTO:
- Las keywords deben ser exactamente entre 4 y 6 términos, todo en minúsculas, AUSENCIA TOTAL de tildes o acentos, AUSENCIA TOTAL de palabras funcionales como artículos o preposiciones (ej. el, la, de, en), usando exclusivamente sustantivos y verbos nucleares únicos.
- El base_response debe tener EXACTAMENTE entre 35 y 50 palabras, con ortografía inmaculada INCLUYENDO TILDES en el texto hablado, tono instruccional directo, sin saludos ni muletillas ni referencias a fuentes, iniciando directamente con la carga de conocimiento real, en formato de texto plano sin saltos de línea internos ni comillas dobles sin escapar que corrompan el JSON.
- NUNCA usar formato markdown, ni bloques ` ```json `, SOLO el JSON raw en texto.
"""

def clean_response(text):
    text = re.sub(r'\[\[.*?\]\]\(.*?\)', '', text)
    text = re.sub(r'\[\d+\]', '', text)
    text = re.sub(r'\[cita requerida\]', '', text)
    text = text.replace('\n', ' ')
    text = text.replace('"', "'")
    return text.strip()

def process_keywords(keywords):
    cleaned = []
    for kw in keywords:
        kw = kw.lower()
        # Remove accents
        kw = kw.replace('á', 'a').replace('é', 'e').replace('í', 'i').replace('ó', 'o').replace('ú', 'u')
        if kw not in STOP_WORDS:
            cleaned.append(kw)
    return cleaned

def check_word_count(text):
    words = text.split()
    return 35 <= len(words) <= 50

def generate_intent_id(keywords):
    return "_".join(keywords[:4])

def append_to_json(filepath, item, count):
    try:
        with open(filepath, 'r+', encoding='utf-8') as f:
            content = f.read()
            if content.strip() == "":
                f.seek(0)
                json.dump([item], f, ensure_ascii=False, indent=4)
            else:
                data = json.loads(content)
                data.append(item)
                f.seek(0)
                f.truncate()
                json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"[{count}/{MAX_CONCEPTS}] Añadido {item['intent_id']}")
    except FileNotFoundError:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump([item], f, ensure_ascii=False, indent=4)
        print(f"[{count}/{MAX_CONCEPTS}] Añadido {item['intent_id']}")

async def worker(sem, client, subtheme, dimension, count_container):
    if count_container[0] >= MAX_CONCEPTS:
        return

    async with sem:
        if count_container[0] >= MAX_CONCEPTS:
            return

        prompt = PROMPT_TEMPLATE.format(subtheme=subtheme, dimension=dimension)

        try:
            response = await client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}]
            )

            raw_text = response.choices[0].message.content

            if "OMITIR" in raw_text:
                return

            # Extract JSON
            match = re.search(r'\{[^{}]+\}', raw_text)
            if not match:
                return

            try:
                data = json.loads(match.group(0))
            except json.JSONDecodeError:
                return

            if "keywords" not in data or "base_response" not in data:
                return

            keywords = process_keywords(data["keywords"])

            if not (4 <= len(keywords) <= 6):
                return

            base_response = clean_response(data["base_response"])

            if not check_word_count(base_response):
                return

            intent_id = generate_intent_id(keywords)

            item = {
                "intent_id": intent_id,
                "keywords": keywords,
                "base_response": base_response
            }

            if count_container[0] < MAX_CONCEPTS:
                count_container[0] += 1
                append_to_json(DESTINATION_FILE, item, count_container[0])

        except Exception as e:
            # print(f"Error: {e}")
            pass

async def main():
    client = AsyncClient()
    sem = asyncio.Semaphore(5)
    count_container = [0]

    tasks = []
    for subtheme in SUBTHEMES:
        for dimension in DIMENSIONS:
            if count_container[0] >= MAX_CONCEPTS:
                break
            tasks.append(worker(sem, client, subtheme, dimension, count_container))

    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())
