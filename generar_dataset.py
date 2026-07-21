import json
import asyncio
import re
from g4f.client import AsyncClient

# Configuration
OUTPUT_FILE = "GBX_brain_68A.json"
MAX_ITEMS = 175
SUBTEMAS = [
    "Verbo ser estar inglés",
    "Presente simple tiempos ingleses",
    "Pasado simple tiempos ingleses",
    "Futuro continuo tiempos ingleses",
    "Verbos irregulares léxico inglés",
    "Verbos regulares léxico inglés",
    "Presente continuo tiempos ingleses",
    "Presente perfecto tiempos ingleses",
    "Pasado continuo tiempos ingleses",
    "Pasado perfecto tiempos ingleses",
    "Futuro simple tiempos ingleses",
    "Futuro perfecto tiempos ingleses",
    "Condicional simple tiempos ingleses",
    "Condicional perfecto tiempos ingleses",
    "Presente perfecto continuo inglés",
    "Pasado perfecto continuo inglés",
    "Futuro perfecto continuo inglés",
    "Verbo tener poseer inglés",
    "Verbo hacer realizar inglés",
    "Verbos modales capacidad inglés",
    "Verbos modales obligación inglés",
    "Verbos modales posibilidad inglés",
    "Infinitivos verbales tiempos ingleses",
    "Gerundios verbales tiempos ingleses",
    "Participios pasados tiempos ingleses",
    "Participios presentes tiempos ingleses",
    "Verbos transitivos tiempos ingleses",
    "Verbos intransitivos tiempos ingleses"
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

STOP_WORDS = ['el', 'la', 'los', 'las', 'un', 'una', 'unos', 'unas', 'de', 'en', 'a', 'ante', 'bajo', 'cabe', 'con', 'contra', 'desde', 'durante', 'entre', 'hacia', 'hasta', 'mediante', 'para', 'por', 'segun', 'sin', 'so', 'sobre', 'tras', 'versus', 'via', 'y', 'e', 'ni', 'o', 'u', 'pero', 'mas', 'sino']

def normalize_intent_id(text):
    text = text.lower()
    text = re.sub(r'[áäâà]', 'a', text)
    text = re.sub(r'[éëêè]', 'e', text)
    text = re.sub(r'[íïîì]', 'i', text)
    text = re.sub(r'[óöôò]', 'o', text)
    text = re.sub(r'[úüûù]', 'u', text)
    text = re.sub(r'ñ', 'n', text)
    text = re.sub(r'[^a-z0-9\s]', '', text)
    text = re.sub(r'\s+', '_', text.strip())
    # Remove sequential numbers
    text = re.sub(r'\d+', '', text)
    text = text.strip('_')
    return text

def normalize_keywords(text):
    text = text.lower()
    text = re.sub(r'[áäâà]', 'a', text)
    text = re.sub(r'[éëêè]', 'e', text)
    text = re.sub(r'[íïîì]', 'i', text)
    text = re.sub(r'[óöôò]', 'o', text)
    text = re.sub(r'[úüûù]', 'u', text)
    text = re.sub(r'ñ', 'n', text)
    text = re.sub(r'[^a-z\s]', '', text)
    words = text.split()
    filtered_words = [w for w in words if w not in STOP_WORDS]
    # Filter non-functional words, take exactly 4 to 6 unique words
    unique_words = []
    for w in filtered_words:
        if w not in unique_words:
            unique_words.append(w)

    if len(unique_words) < 4:
        return None # Invalid
    return unique_words[:6]

def generate_intent_id(subtema, dimension, keywords):
    base_id = normalize_intent_id(subtema + " " + dimension)
    if keywords:
        # Avoid simple sequential ids, make it semantic
        unique_suffix = "_".join(keywords[:2])
        return f"{base_id}_{unique_suffix}"
    return base_id

def sanitize_response(text):
    # Plain text, no newlines, no unescaped double quotes, proper orthography
    text = text.replace('\n', ' ')
    text = text.replace('"', "'")
    text = re.sub(r'\[\[.*?\]\]\(.*?\)', '', text) # Remove citations
    text = text.strip()
    return text

async def generate_concept(client, subtema, dimension, semaphore):
    async with semaphore:
        prompt = f"""
Eres un Ingeniero de Datos Autónomo y Especialista en Minería de Información Educativa.
Genera un concepto educativo sobre el subtema "{subtema}" analizado desde la dimensión "{dimension}".
RESTRICCIÓN DE NIVEL ACADÉMICO: Estudiantes de Tercer Ciclo (9 a 15 años). Simplifica conceptos universitarios sin perder veracidad científica.
RESTRICCIONES ESTRICTAS DE SALIDA:
Debes responder ÚNICAMENTE con un objeto JSON válido. Nada de markdown, nada de explicaciones antes o después del JSON.
El objeto JSON debe tener exactamente esta estructura:
{{
  "keywords": "lista de 4 a 6 sustantivos o verbos nucleares clave. SIN acentos ni tildes. TODO minúsculas. SIN artículos ni preposiciones (ej. sin 'el', 'la', 'de', 'en'). Solo español.",
  "base_response": "Explicación académica en formato de texto plano. Exactamente entre 35 y 50 palabras. Ortografía inmaculada, CON tildes y acentos. Tono instruccional directo, sin saludos ni despedidas ni referencias a fuentes. Inicia directamente con la carga de conocimiento. SIN saltos de línea internos."
}}

¡Importante!
- Si la dimensión no aplica a este subtema con base científica, devuelve un JSON vacío {{}}
- NO alucines.
- NO uses frases repetitivas de cierre.
- SOLO JSON.
"""
        try:
            response = await client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}]
            )
            text = response.choices[0].message.content

            # Extract JSON
            match = re.search(r'\{.*\}', text, re.DOTALL)
            if match:
                json_str = match.group(0)
                data = json.loads(json_str)
                if not data:
                    return None

                # Validation & Post-processing
                if 'keywords' not in data or 'base_response' not in data:
                    return None

                raw_keywords = data['keywords']
                if isinstance(raw_keywords, list):
                    raw_keywords = " ".join(raw_keywords)

                processed_keywords = normalize_keywords(raw_keywords)
                if not processed_keywords:
                    return None

                raw_response = sanitize_response(data['base_response'])
                word_count = len(raw_response.split())

                if not (35 <= word_count <= 50):
                    return None # Strict word count enforcement

                intent_id = generate_intent_id(subtema, dimension, processed_keywords)

                return {
                    "intent_id": intent_id,
                    "keywords": processed_keywords,
                    "base_response": raw_response
                }
            return None
        except Exception as e:
            # print(f"Error: {e}")
            return None

async def main():
    client = AsyncClient()
    semaphore = asyncio.Semaphore(5)

    results = []
    generated_ids = set()

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write('[\n')

    for subtema in SUBTEMAS:
        if len(results) >= MAX_ITEMS:
            break

        tasks = []
        for dimension in DIMENSIONES:
            tasks.append(generate_concept(client, subtema, dimension, semaphore))

        batch_results = await asyncio.gather(*tasks)

        for item in batch_results:
            if item and item['intent_id'] not in generated_ids:
                generated_ids.add(item['intent_id'])

                # Add to results and append to file
                prefix = '  ' if len(results) == 0 else ',\n  '
                with open(OUTPUT_FILE, 'a', encoding='utf-8') as f:
                    json.dump(item, f, ensure_ascii=False)
                    # We have to handle formatting manually because we stream
                    # Actually, json.dumps is better here
                    if len(results) > 0:
                        f.write(',\n  ')
                    else:
                        f.write('  ')
                    f.write(json.dumps(item, ensure_ascii=False))

                results.append(item)
                print(f"Generated {len(results)}/{MAX_ITEMS}: {item['intent_id']}")

                if len(results) >= MAX_ITEMS:
                    break

    with open(OUTPUT_FILE, 'a', encoding='utf-8') as f:
        f.write('\n]\n')

    print(f"Completed! Generated {len(results)} concepts.")

if __name__ == "__main__":
    asyncio.run(main())
