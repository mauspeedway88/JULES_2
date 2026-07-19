import json
import asyncio
import os
import re
from g4f.client import AsyncClient
from unidecode import unidecode
import logging
import random

# Configuración básica de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

ARCHIVO_DESTINO = "GBX_brain_51B.json"
MAX_CONCEPTOS = 275

SUBTEMAS = [
    "Revisión de amortiguadores y resortes",
    "Inspección de brazos de viraje",
    "Ajuste del inmovilizador de parqueo",
    "Comprobación de iluminación exterior vehicular",
    "Relleno de limpiador de cristales",
    "Sustitución de plumas de barrido",
    "Detección de goteos de líquidos",
    "Mantenimiento del clima artificial automotriz",
    "Recarga de gas refrigerante vehicular",
    "Saneamiento del intercambiador de cabina",
    "Comprobación de tensión de fajas",
    "Revisión de protectores de ejes",
    "Lubricación de bisagras de puertas",
    "Ajuste de rodamientos de masa",
    "Inspección del fluido de viraje",
    "Renovación de lubricante de engranajes",
    "Reemplazo de líquido de transferencia",
    "Prueba de hermeticidad de cilindros",
    "Revisión del sistema de precalentamiento",
    "Calibración de chispa de arranque",
    "Inspección de líneas de alimentación",
    "Revisión de anclajes antivibración vehiculares",
    "Lavado profundo de estructura inferior",
    "Reemplazo de válvula presurizada superior",
    "Comprobación de hermetismo de tanque",
    "Medición del grosor de fricción",
    "Desinfección interior de cabina automotriz",
    "Valoración de pintura y carrocería"
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

def format_intent_id(subtema, dimension):
    base_id = f"automotriz_{subtema}_{dimension}"
    base_id = unidecode(base_id.lower())
    base_id = re.sub(r'[^a-z0-9]', '_', base_id)
    base_id = re.sub(r'_+', '_', base_id).strip('_')
    return base_id

def clean_keywords(keywords_list):
    stop_words = ["el", "la", "los", "las", "un", "una", "unos", "unas", "de", "del", "al", "en", "para", "por", "con", "sin", "sobre", "y", "o", "a", "ante", "bajo", "cabe", "contra", "desde", "hacia", "hasta", "segun", "tras"]
    cleaned = []
    for kw in keywords_list:
        kw = unidecode(kw.lower().strip())
        kw = re.sub(r'[^a-z\s]', '', kw)
        words = kw.split()
        valid_words = [w for w in words if w not in stop_words]
        if valid_words:
            cleaned.append(" ".join(valid_words))

    # Filtrar palabras funcionales extra que hayan quedado sueltas
    final_cleaned = [w for w in cleaned if w not in stop_words and len(w)>1]

    # Asegurar entre 4 y 6 keywords únicas
    unique_kws = list(dict.fromkeys(final_cleaned))
    if len(unique_kws) < 4:
        return []
    return unique_kws[:6]

def clean_base_response(text):
    text = text.replace('\n', ' ').replace('\r', ' ').replace('"', "'")
    text = re.sub(r'\s+', ' ', text).strip()
    return text

PROMPT_TEMPLATE = """
Eres un especialista en educación para estudiantes de Tercer Ciclo (9 a 15 años).
Genera un concepto científico y educativo sobre el subtema: '{subtema}', enfocado ESTRICTAMENTE en la dimensión: '{dimension}'.

Si esta dimensión no aplica al subtema o no tiene base científica real, responde SOLAMENTE con la palabra: OMITIR.

Restricciones estrictas:
1. Nivel académico: Para jóvenes de 9 a 15 años. Simplifica sin perder veracidad científica.
2. Formato de salida: Devuelve ÚNICAMENTE un JSON válido sin markdown, sin bloques de código, sin texto antes ni después.
3. No incluir prefijos como "```json" ni sufijos.
4. NUNCA escribas en inglés, todo en español.

Estructura requerida del JSON:
{{
    "keywords": ["palabra1", "palabra2", "palabra3", "palabra4", "palabra5"],
    "base_response": "Texto de la explicación."
}}

Reglas para 'keywords':
- Exactamente entre 4 y 6 términos.
- Todo en minúsculas y SIN NINGUNA TILDE NI ACENTO.
- SIN artículos ni preposiciones (ej: 'del', 'al', 'en', 'para').
- Usa exclusivamente sustantivos y verbos nucleares únicos.

Reglas para 'base_response':
- Exactamente entre 35 y 50 palabras.
- Ortografía perfecta INCLUYENDO tildes.
- Tono instruccional directo, sin saludos ni muletillas. No empieces con palabras ambiguas.
- Inicia directamente con el conocimiento.
- Formato texto plano: SIN saltos de línea y usa comillas simples (') en lugar de dobles (") adentro del texto.
- No incluyas el conteo de palabras.

Respuesta (SOLO EL JSON o OMITIR):
"""

async def fetch_concept(client, subtema, dimension, semaphore):
    async with semaphore:
        prompt = PROMPT_TEMPLATE.format(subtema=subtema, dimension=dimension)
        try:
            response = await client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
            )
            content = response.choices[0].message.content.strip()

            if "OMITIR" in content.upper()[:20]:
                return None

            # Limpiar posible markdown
            content = re.sub(r'^```json\s*', '', content)
            content = re.sub(r'^```\s*', '', content)
            content = re.sub(r'\s*```$', '', content)

            data = json.loads(content)

            if "keywords" not in data or "base_response" not in data:
                return None

            keywords = clean_keywords(data["keywords"])
            if len(keywords) < 4 or len(keywords) > 6:
                return None

            base_response = clean_base_response(data["base_response"])
            word_count = len(base_response.split())
            if word_count < 35 or word_count > 50:
                return None

            # Validar que no haya conteos al final
            if re.search(r'\(\d+\s*palabras\)', base_response.lower()):
                 return None

            intent_id = format_intent_id(subtema, dimension)

            return {
                "intent_id": intent_id,
                "keywords": keywords,
                "base_response": base_response
            }

        except Exception as e:
            # logging.error(f"Error procesando {subtema} - {dimension}: {e}")
            return None

async def main():
    client = AsyncClient()
    semaphore = asyncio.Semaphore(5)

    dataset = []
    conceptos_totales = 0

    # Inicializar el archivo
    with open(ARCHIVO_DESTINO, 'w', encoding='utf-8') as f:
        f.write("[\n")

    random.shuffle(SUBTEMAS) # Mezclar para variedad si se corta antes

    tasks_batch = []

    for subtema in SUBTEMAS:
        if conceptos_totales >= MAX_CONCEPTOS:
            break

        for dimension in DIMENSIONES:
            if conceptos_totales >= MAX_CONCEPTOS:
                break

            tasks_batch.append(fetch_concept(client, subtema, dimension, semaphore))

            if len(tasks_batch) >= 20: # Lotes de 20 para ir guardando
                results = await asyncio.gather(*tasks_batch)

                nuevos_conceptos = []
                for res in results:
                    if res and conceptos_totales < MAX_CONCEPTOS:
                        # Validar unicidad por si acaso (aunque intent_id lo garantiza por diseño)
                        if not any(c['intent_id'] == res['intent_id'] for c in dataset):
                            dataset.append(res)
                            nuevos_conceptos.append(res)
                            conceptos_totales += 1

                if nuevos_conceptos:
                    logging.info(f"Guardando lote. Conceptos totales: {conceptos_totales}")
                    with open(ARCHIVO_DESTINO, 'a', encoding='utf-8') as f:
                        for idx, concepto in enumerate(nuevos_conceptos):
                            json_str = json.dumps(concepto, ensure_ascii=False)
                            # Si es el primer elemento general, no ponemos coma inicial
                            # Pero como estamos appendeando, la logica de comas es tricky.
                            # Mejor lo manejamos al final.
                            # Reescribiendo logica para archivo:
                            pass
                tasks_batch = []

    # Procesar remanentes
    if tasks_batch and conceptos_totales < MAX_CONCEPTOS:
        results = await asyncio.gather(*tasks_batch)
        for res in results:
            if res and conceptos_totales < MAX_CONCEPTOS:
                 if not any(c['intent_id'] == res['intent_id'] for c in dataset):
                    dataset.append(res)
                    conceptos_totales += 1

    logging.info(f"Generacion completada. Conceptos finales: {conceptos_totales}")

    # Escribir el array completo al final para asegurar JSON válido
    with open(ARCHIVO_DESTINO, 'w', encoding='utf-8') as f:
        json.dump(dataset, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    asyncio.run(main())
