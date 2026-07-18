import json
import time
import asyncio
import g4f
import nest_asyncio
import unidecode
import re
from typing import List, Dict, Any

nest_asyncio.apply()

# --- Configuración Inicial ---
OUTPUT_FILE = "GBX_brain_38B.json"

SUBTEMAS = [
    "uretra excretora de vejiga", "duodeno inicial de intestinos", "yeyuno medio de intestinos",
    "íleon terminal de intestinos", "ciego colónico de intestinos", "apéndice cecal de intestinos",
    "colon ascendente de intestinos", "colon transverso de intestinos", "colon descendente de intestinos",
    "recto digestivo de intestinos", "ano excretor de intestinos", "órgano glandular del páncreas",
    "islotes pancreáticos de páncreas", "órgano linfático del bazo", "pulpa blanca del bazo",
    "glándulas suprarrenales de riñones", "ovarios reproductores de pelvis", "trompas uterinas de ovarios",
    "útero reproductor de gestación", "próstata glandular del varón", "testículos reproductores del varón",
    "vesículas seminales del varón", "miocardio muscular del corazón", "endocardio interno del corazón",
    "pericardio externo del corazón", "lóbulos respiratorios de pulmones", "tejido parenquimatoso de órganos"
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

def clean_text(text: str) -> str:
    # Ensure no unescaped quotes or newlines
    text = text.replace('\n', ' ').replace('\r', '')
    text = text.replace('"', '\\"')
    # Collapse multiple spaces
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def validate_concept(concept: Dict[str, Any]) -> bool:
    try:
        # Validate intent_id
        intent_id = concept.get('intent_id', '')
        if not re.match(r'^[a-z_]+$', intent_id) or re.search(r'\d', intent_id):
            return False

        # Validate keywords
        keywords = concept.get('keywords', [])
        if not isinstance(keywords, list) or not (4 <= len(keywords) <= 6):
            return False
        for kw in keywords:
            if not isinstance(kw, str): return False
            if bool(re.search(r'[áéíóúÁÉÍÓÚñÑ]', kw)): return False # No tildes
            if kw != kw.lower(): return False

        # Validate base_response
        base_response = concept.get('base_response', '')
        words = [w for w in base_response.split() if w.strip()]
        if not (35 <= len(words) <= 50):
            return False

        # Check for tildes (must have at least one or it's likely missing them)
        if not bool(re.search(r'[áéíóúÁÉÍÓÚ]', base_response)):
            return False

        return True
    except Exception:
        return False

def generate_prompt(subtema: str, dimension: str) -> str:
    prompt = f"""
Actúa como un experto en minería de datos educativos. Genera UN SOLO CONCEPTO en formato JSON sobre el subtema "{subtema}" enfocado exclusivamente en la dimensión: "{dimension}".
El público objetivo son estudiantes de Tercer Ciclo (9 a 15 años). Simplifica conceptos universitarios sin perder veracidad científica. No uses muletillas, saludos ni repitas frases.

ESTRUCTURA JSON EXACTA REQUERIDA:
{{
  "intent_id": "identificador_unico_semantico",
  "keywords": ["palabra1", "palabra2", "palabra3", "palabra4"],
  "base_response": "Texto educativo directo, científico, con ortografía perfecta y tildes obligatorias..."
}}

REGLAS ESTRICTAS:
1. `intent_id`: String único, solo minúsculas, separado por guiones bajos (_). CERO NÚMEROS (prohibido _1, _2).
2. `keywords`: Arreglo de 4 a 6 palabras. SOLO sustantivos o verbos nucleares. TODO en minúsculas. ABSOLUTAMENTE SIN TILDES NI ACENTOS. Ninguna palabra funcional (el, la, de, en).
3. `base_response`: String de texto plano, sin saltos de línea (\\n) ni comillas dobles internas (a menos que estén escapadas). LONGITUD EXACTA ENTRE 35 y 50 PALABRAS. ORTOGRAFÍA INMACULADA, DEBES INCLUIR LAS TILDES (á, é, í, ó, ú). Tono instruccional directo, sin introducciones ni saludos.

Solo devuelve el JSON, nada más, sin bloques de código Markdown ```json ```.
"""
    return prompt

async def fetch_concept(subtema: str, dimension: str) -> Dict[str, Any] | None:
    prompt = generate_prompt(subtema, dimension)
    for _ in range(5): # Max 5 retries
        try:
            response = await g4f.ChatCompletion.create_async(
                model=g4f.models.default,
                messages=[{"role": "user", "content": prompt}],
            )

            # Clean up response (sometimes it has markdown or prefix)
            resp_str = str(response)
            match = re.search(r'\{.*\}', resp_str, re.DOTALL)
            if match:
                resp_str = match.group(0)

            data = json.loads(resp_str)

            # Clean text fields
            data['base_response'] = clean_text(data.get('base_response', ''))

            if validate_concept(data):
                return data
        except Exception as e:
            pass # Silently retry
    return None

async def main():
    all_concepts = []
    generated_ids = set()

    # Pre-open array if file doesn't exist
    # Read existing IDs if possible
    try:
        with open(OUTPUT_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
            if content.strip().startswith('['):
                try:
                    data = json.loads(content + (']' if not content.strip().endswith(']') else ''))
                    for item in data:
                        generated_ids.add(item['intent_id'])
                        all_concepts.append(item)
                except Exception:
                    pass
    except Exception:
        pass

    print(f"Starting with {len(generated_ids)} existing items")

    first_item = True

    # Keep track of how many concepts generated in this run
    concepts_generated_this_run = 0

    for subtema in SUBTEMAS:
        for dimension in DIMENSIONES:
            # Skip if we already generated a ton (we want to let the process complete)
            if concepts_generated_this_run > 240:
                break

            concept = await fetch_concept(subtema, dimension)
            if concept:
                # Ensure unique intent_id globally
                base_id = concept['intent_id']
                if base_id in generated_ids:
                    # Append unique string if duplicate (no numbers!)
                    concept['intent_id'] = f"{base_id}_alternativa"
                    if concept['intent_id'] in generated_ids:
                        concept['intent_id'] = f"{base_id}_variante_especial"

                if concept['intent_id'] not in generated_ids:
                    generated_ids.add(concept['intent_id'])
                    all_concepts.append(concept)
                    concepts_generated_this_run += 1

                    # Rewrite entire array incrementally to keep format valid
                    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
                        json.dump(all_concepts, f, ensure_ascii=False, indent=2)

            # Rate limit gracefully
            time.sleep(1)

    print(f"Total concepts generated: {len(all_concepts)}")

if __name__ == "__main__":
    asyncio.run(main())
