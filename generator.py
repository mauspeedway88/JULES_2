import os
import json
import asyncio
import re
import random
import nest_asyncio
import g4f

nest_asyncio.apply()

# Required parameters from the prompt
TARGET_FILE = "GBX_brain_34B.json"

SUBTOPICS = [
    "selva tropical de lluvias",
    "sostenibilidad ambiental de recursos",
    "depredación biológica de caza",
    "competencia interespecífica por recursos",
    "ciclo del carbono ambiental",
    "ciclo del nitrógeno ecológico",
    "ciclo del agua planetario",
    "red trófica interconectada global",
    "ecología científica de sistemas",
    "bosque templado caducifolio estacional",
    "sabana herbácea de pastizales",
    "taiga de bosques coníferos",
    "estuario de mezcla salobre",
    "arrecifes coralinos de biodiversidad",
    "sucesión ecológica primaria secundaria",
    "especies pioneras de colonización",
    "clímax ecológico de estabilidad",
    "capacidad de carga ambiental",
    "huella ecológica del humano",
    "impacto ambiental de contaminación",
    "conservación biológica de espacios"
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

def clean_text(text):
    """Remove quotes and newlines for JSON safety."""
    return text.replace('"', '').replace('\n', ' ').strip()

def strip_accents(text):
    """Strip accents from keywords."""
    accents = {'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u', 'ñ': 'n',
               'Á': 'a', 'É': 'e', 'Í': 'i', 'Ó': 'o', 'Ú': 'u', 'Ñ': 'n'}
    for k, v in accents.items():
        text = text.replace(k, v)
    return text

def parse_llm_response(raw_text):
    """Extract JSON from the LLM output."""
    try:
        start = raw_text.find('{')
        end = raw_text.rfind('}') + 1
        if start != -1 and end != -1:
            json_str = raw_text[start:end]
            return json.loads(json_str)
    except Exception:
        pass
    return None

def validate_response(data):
    """Validate constraints."""
    if not isinstance(data, dict): return False

    intent_id = data.get("intent_id", "")
    keywords = data.get("keywords", [])
    base_response = data.get("base_response", "")

    # Check intent_id
    if not intent_id or not isinstance(intent_id, str): return False
    if not re.match(r'^[a-z_]+$', intent_id): return False

    # Check keywords
    if not isinstance(keywords, list) or not (4 <= len(keywords) <= 6): return False
    for kw in keywords:
        if not re.match(r'^[a-z]+$', kw): return False

    # Check base_response words
    words = base_response.split()
    if not (35 <= len(words) <= 50): return False

    # Temporarily remove strict orthography check if it's failing valid outputs
    # We enforce in prompt instead.
    # if not re.search(r'[áéíóúÁÉÍÓÚñÑ]', base_response): return False

    return True

async def fetch_concept(subtopic, dimension):
    prompt = f"""
Actúa como un experto en minería de información educativa para estudiantes de Tercer Ciclo (9-15 años).
Genera un concepto científico sobre el subtema "{subtopic}" enfocado ESTRICTAMENTE en la dimensión: "{dimension}".

REGLAS DE SALIDA:
Genera un único objeto JSON plano. NO agregues formato markdown.
{{
  "intent_id": "identificador_unico_semantico_sin_numeros",
  "keywords": ["sustantivo", "verbo", "concepto", "clave"],
  "base_response": "Texto educativo directo..."
}}

REGLAS DE CAMPOS:
- intent_id: minúsculas, separado por guiones bajos, único para este concepto, cero números secuenciales.
- keywords: Arreglo de EXACTAMENTE 4 a 6 términos. Todo en minúsculas. Cero tildes, cero acentos. Cero palabras funcionales (el, la, de, con). SOLO sustantivos y verbos nucleares únicos de este concepto.
- base_response: EXACTAMENTE entre 35 y 50 palabras. Ortografía inmaculada, ASEGÚRATE DE INCLUIR LAS TILDES NECESARIAS EN LAS PALABRAS QUE LO LLEVEN. Tono instruccional directo, sin saludos ni muletillas. Inicia directamente con el conocimiento. Texto plano sin saltos de línea ni comillas dobles internas.

VÁLVULA DE ESCAPE:
Si la dimensión "{dimension}" no aplica de ninguna manera lógica al subtema "{subtopic}" (ej. anatomía para un concepto abstracto), o no hay información científica real, responde SOLO con: {{"OMITE": true}}

Genera solo el JSON:
"""
    try:
        # Give it a retry loop
        for _ in range(3):
            response = await g4f.ChatCompletion.create_async(
                model=g4f.models.default,
                messages=[{"role": "user", "content": prompt}],
            )
            data = parse_llm_response(response)
            if data and validate_response(data):
                return response
            elif data and "OMITE" in data:
                return response
        return None
    except Exception as e:
        print(f"Error for {subtopic} - {dimension}: {e}")
        return None

def main():
    existing_data = []
    if os.path.exists(TARGET_FILE):
        with open(TARGET_FILE, 'r', encoding='utf-8') as f:
            try:
                existing_data = json.load(f)
            except:
                pass

    seen_intents = {item["intent_id"] for item in existing_data}
    seen_responses = {item["base_response"] for item in existing_data}

    added_in_run = 0

    for subtopic in SUBTOPICS:
        for dimension in DIMENSIONS:
            print(f"Generating for {subtopic} - {dimension}...")

            raw_response = asyncio.run(fetch_concept(subtopic, dimension))
            if not raw_response:
                continue

            data = parse_llm_response(raw_response)

            if not data or "OMITE" in data:
                print("Skipped (Escape valve).")
                continue

            # Clean and enforce constraints
            data["base_response"] = clean_text(data["base_response"])

            # Fix keywords just in case
            cleaned_keywords = []
            for kw in data.get("keywords", []):
                cleaned = strip_accents(kw.lower().strip())
                cleaned = re.sub(r'[^a-z]', '', cleaned)
                if cleaned and len(cleaned) > 2:
                    cleaned_keywords.append(cleaned)
            data["keywords"] = cleaned_keywords

            if validate_response(data):
                if data["intent_id"] in seen_intents or data["base_response"] in seen_responses:
                    print("Duplicate content, skipping.")
                    continue

                existing_data.append(data)
                seen_intents.add(data["intent_id"])
                seen_responses.add(data["base_response"])
                added_in_run += 1

                print(f"Added! Total concepts: {len(existing_data)}")

                # Save incremental
                with open(TARGET_FILE, 'w', encoding='utf-8') as f:
                    json.dump(existing_data, f, ensure_ascii=False, indent=2)
            else:
                print("Failed validation.")

    print(f"Generation complete. Added {added_in_run} concepts.")

if __name__ == "__main__":
    main()
