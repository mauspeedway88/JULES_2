import asyncio
import json
import re
import os
import unicodedata
from g4f.client import AsyncClient

# Inicializar cliente asíncrono sin argumentos (automático)
client = AsyncClient()

SUBTEMAS = [
    "Leyes supremas de la constitucion",
    "Articulos de la constitucion nacional",
    "Asamblea constituyente de leyes civicas",
    "Normativas legales de la constitucion",
    "Deberes ciudadanos constitucionales obligatorios",
    "Garantias constitucionales de educacion civica",
    "Carta magna del ordenamiento juridico",
    "Promulgacion de la constitucion nacional",
    "Reformas constitucionales del estado soberano",
    "Supremacia constitucional del sistema legal",
    "Control de constitucionalidad de leyes",
    "Preambulo de la constitucion estatal",
    "Derechos fundamentales del texto constitucional",
    "Separacion de poderes constitucionales estatales",
    "Organo ejecutivo del mandato constitucional",
    "Organo legislativo de normativas constitucionales",
    "Organo judicial de justicia constitucional",
    "Soberania popular en la constitucion",
    "Estado de derecho constitucional civico",
    "Principios democraticos de la constitucion",
    "Orden constitucional del territorio nacional",
    "Inviolabilidad de la constitucion politica",
    "Justicia social en textos constitucionales",
    "Libertad de expresion constitucional civica",
    "Debido proceso de ley constitucional",
    "Habeas corpus de proteccion constitucional",
    "Amparo legal de derechos constitucionales",
    "Nacionalidad definida en la constitucion"
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

LÍMITE_MÁXIMO = 175
ARCHIVO_DESTINO = "GBX_brain_69A.json"

# Stop words para asegurar que las keywords no tengan palabras funcionales
STOP_WORDS = {"el", "la", "los", "las", "un", "una", "unos", "unas",
              "de", "en", "a", "por", "para", "con", "sin", "sobre", "entre", "hacia", "hasta", "desde",
              "y", "o", "u", "e", "ni", "que"}

# Diccionario de acentos comunes para restaurar
ACCENT_FIXES = {
    r'\bconstitucion\b': 'constitución',
    r'\barticulos\b': 'artículos',
    r'\bcivicas\b': 'cívicas',
    r'\bgarantias\b': 'garantías',
    r'\beducacion\b': 'educación',
    r'\bjuridico\b': 'jurídico',
    r'\bpromulgacion\b': 'promulgación',
    r'\bsupremacia\b': 'supremacía',
    r'\bpreambulo\b': 'preámbulo',
    r'\bseparacion\b': 'separación',
    r'\borgano\b': 'órgano',
    r'\bsoberania\b': 'soberanía',
    r'\bdemocraticos\b': 'democráticos',
    r'\bexpresion\b': 'expresión',
    r'\bproteccion\b': 'protección',
    r'\bnacion\b': 'nación',
    r'\bnacional\b': 'nacional'
}

def clean_text_no_accents(text):
    text = unicodedata.normalize('NFKD', text).encode('ASCII', 'ignore').decode('utf-8')
    return text.lower().strip()

def restore_accents(text):
    for pattern, replacement in ACCENT_FIXES.items():
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    return text

def fix_base_response_format(text):
    text = text.replace('\n', ' ')
    text = text.replace('"', "'")
    text = re.sub(r'\[\[.*?\]\]\(.*?\)', '', text) # Quitar citas raras
    text = re.sub(r'\[\d+\]', '', text) # Quitar citas tipo wikipedia [1]
    text = re.sub(r'\[cita requerida\]', '', text, flags=re.IGNORECASE)
    return text.strip()

def generate_intent_id(subtema, dimension):
    # Generar ID semántico, sin números, combinando partes
    p1 = clean_text_no_accents(subtema).split()
    p2 = clean_text_no_accents(dimension).split()

    # Tomar 2-3 palabras relevantes (sustantivos/verbos)
    p1_filtered = [w for w in p1 if w not in STOP_WORDS][:3]
    p2_filtered = [w for w in p2 if w not in STOP_WORDS][:2]

    return "_".join(p1_filtered + p2_filtered)

async def generate_concept(subtema, dimension, semaphore):
    async with semaphore:
        prompt = f"""
Genera UN concepto educativo único en formato JSON sobre el tema '{subtema}' desde la dimensión '{dimension}'.
Público: Estudiantes de 9 a 15 años.
Directrices estrictas:
- El JSON debe tener exactamente esta estructura: {{"keywords": "palabras clave", "base_response": "texto"}}
- Las 'keywords' deben ser exactamente entre 4 y 6 términos, todos en minúsculas, SIN NINGÚN ACENTO O TILDE. SIN PALABRAS FUNCIONALES (como el, la, de, en, y, etc.). Solo sustantivos y verbos nucleares únicos. Separados por espacios.
- El 'base_response' debe tener exactamente entre 35 y 50 palabras. DEBE TENER ORTOGRAFÍA INMACULADA CON TILDES y mayúsculas adecuadas. Sin saludos, sin muletillas, ir directo al grano con contenido científico real. Formato texto plano sin saltos de línea y sin usar comillas dobles.
Devuelve ÚNICAMENTE el objeto JSON.
        """
        try:
            response = await client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}]
            )
            text = response.choices[0].message.content

            # Extraer JSON de la respuesta (por si hay texto extra)
            json_matches = re.findall(r'\{[^{}]+\}', text)
            if json_matches:
                data = json.loads(json_matches[0])

                # Validar y limpiar
                if "keywords" in data and "base_response" in data:
                    kw = clean_text_no_accents(data["keywords"])
                    kw_list = kw.split()
                    kw_filtered = [w for w in kw_list if w not in STOP_WORDS]

                    if len(kw_filtered) < 4 or len(kw_filtered) > 6:
                        return None # Falla longitud keywords

                    keywords = " ".join(kw_filtered)

                    br = fix_base_response_format(data["base_response"])
                    br = restore_accents(br)
                    word_count = len(br.split())

                    if word_count < 35 or word_count > 50:
                        return None # Falla longitud base_response

                    intent_id = generate_intent_id(subtema, dimension)

                    return {
                        "intent_id": intent_id,
                        "keywords": keywords,
                        "base_response": br
                    }
        except Exception as e:
            # Silenciar errores y retornar None (falla el concepto)
            pass
        return None

async def main():
    semaphore = asyncio.Semaphore(5)
    conceptos_validos = []

    # Cargar si existe para no sobreescribir e ir iterando (aunque empezamos de 0)
    if os.path.exists(ARCHIVO_DESTINO):
        try:
            with open(ARCHIVO_DESTINO, 'r', encoding='utf-8') as f:
                conceptos_validos = json.load(f)
        except Exception:
            conceptos_validos = []

    total_generados = len(conceptos_validos)

    for subtema in SUBTEMAS:
        if total_generados >= LÍMITE_MÁXIMO:
            break

        tasks = [generate_concept(subtema, dim, semaphore) for dim in DIMENSIONES]
        resultados = await asyncio.gather(*tasks)

        nuevos_batch = []
        for res in resultados:
            if res is not None:
                # Comprobar unicidad de intent_id
                if not any(c['intent_id'] == res['intent_id'] for c in conceptos_validos) and not any(c['intent_id'] == res['intent_id'] for c in nuevos_batch):
                    nuevos_batch.append(res)
                    total_generados += 1
                    if total_generados >= LÍMITE_MÁXIMO:
                        break

        if nuevos_batch:
            conceptos_validos.extend(nuevos_batch)
            # Guardar lote incremental
            with open(ARCHIVO_DESTINO, 'w', encoding='utf-8') as f:
                json.dump(conceptos_validos, f, ensure_ascii=False, indent=2)
            print(f"Subtema procesado: {subtema}. Total conceptos guardados: {total_generados}")

        if total_generados >= LÍMITE_MÁXIMO:
            print("Límite máximo alcanzado. Deteniendo generación.")
            break

if __name__ == "__main__":
    asyncio.run(main())
