# -*- coding: utf-8 -*-
import json
import re
import urllib.request
import urllib.error
import time
import sys
import subprocess

API_KEY = "AIzaSyB8bKP9j36keoht6Gxg08c3uO2ZOeYNnkM"
MODEL_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={API_KEY}"

SUBTHEMES = [
    "Sustancias puras metálicas",
    "Componentes puros no metales",
    "Gases nobles inertes",
    "Grupos o familias periódicas",
    "Periodos o filas horizontales",
    "Identificador protónico principal",
    "Organización periódica de Mendeleyev",
    "Bloques de clasificación periódica",
    "Metales alcalinos reactivos",
    "Metales alcalinotérreos ligeros",
    "Elementos halógenos formadores",
    "Metales de transición central",
    "Elementos lantánidos tierras raras",
    "Elementos actínidos radiactivos",
    "Metaloides con atributos intermedios",
    "Símbolo alfabético identificador",
    "Radio elemental periódico",
    "Potencial para ionización periódica",
    "Electronegatividad de escala Pauling",
    "Afinidad electrónica periódica",
    "Carácter metálico de elementos",
    "Elementos sintéticos artificiales",
    "Ley periódica de Moseley",
    "Valencia elemental típica",
    "Clasificación periódica moderna",
    "Familias representativas principales",
    "Elementos transuránicos pesados",
    "Configuración electrónica terminal",
    "Triadas periódicas de Dobereiner",
    "Octavas periódicas de Newlands"
]

STOP_WORDS = {
    'el', 'la', 'los', 'las', 'un', 'una', 'unos', 'unas',
    'de', 'del', 'con', 'en', 'por', 'para', 'y', 'o', 'que', 'como',
    'a', 'al', 'ante', 'bajo', 'cabe', 'contra', 'desde', 'durante',
    'entre', 'hacia', 'hasta', 'mediante', 'para', 'por', 'segun',
    'sin', 'so', 'sobre', 'tras', 'versus', 'via', 'e', 'u', 'pero', 'mas'
}

def remove_accents(text):
    import unicodedata
    # Normalized text to decompose accents, then filter out non-spacing marks
    normalized = unicodedata.normalize('NFD', text)
    result = "".join(c for c in normalized if unicodedata.category(c) != 'Mn')
    # Manual fallback for common Spanish characters just in case
    replacements = {
        'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u',
        'Á': 'a', 'É': 'e', 'Í': 'i', 'Ó': 'o', 'Ú': 'u',
        'ñ': 'n', 'Ñ': 'n', 'ü': 'u', 'Ü': 'u'
    }
    for k, v in replacements.items():
        result = result.replace(k, v)
    return result.lower()

def count_words(text):
    # Split by spaces and punctuation, but keeping hyphens or contractions together if needed
    # We want a standard word count (split by spaces/punctuation)
    words = re.findall(r'[a-zA-Z0-9áéíóúÁÉÍÓÚñÑüÜ]+', text)
    return len(words)

def validate_concept(concept):
    """
    Validates a concept against the strict guidelines.
    Returns (True, None) or (False, error_reason).
    """
    # 1. Structure Check
    if not isinstance(concept, dict):
        return False, "Not a dictionary"

    for key in ["intent_id", "keywords", "base_response"]:
        if key not in concept:
            return False, f"Missing key: {key}"

    intent_id = concept["intent_id"]
    keywords = concept["keywords"]
    base_response = concept["base_response"]

    # 2. intent_id format
    if not isinstance(intent_id, str):
        return False, "intent_id must be a string"
    if not intent_id:
        return False, "intent_id is empty"
    if intent_id != intent_id.lower():
        return False, "intent_id must be strictly lowercase"
    if not re.match(r'^[a-z0-9_]+$', intent_id):
        return False, f"intent_id contains invalid characters: '{intent_id}' (only a-z, 0-9, and underscore are allowed)"
    # Avoid sequential patterns
    if re.search(r'concepto_\d+', intent_id) or re.search(r'tema_\d+', intent_id) or re.search(r'concept_\d+', intent_id):
        return False, f"intent_id has restricted sequential/generic pattern: '{intent_id}'"

    # 3. keywords rules
    if not isinstance(keywords, list):
        return False, "keywords must be a list"
    if len(keywords) < 4 or len(keywords) > 6:
        return False, f"keywords list must have exactly 4 to 6 terms, got {len(keywords)}"

    for kw in keywords:
        if not isinstance(kw, str):
            return False, f"keyword {kw} is not a string"
        if kw != kw.lower():
            return False, f"keyword '{kw}' is not strictly lowercase"
        # Check accents / tildes
        no_acc = remove_accents(kw)
        if kw != no_acc:
            return False, f"keyword '{kw}' contains accents/tildes (must be: '{no_acc}')"
        # Check stop words
        words_in_kw = re.findall(r'[a-z0-9]+', kw)
        for w in words_in_kw:
            if w in STOP_WORDS:
                return False, f"keyword '{kw}' contains function/stop word '{w}'"

    # 4. base_response rules
    if not isinstance(base_response, str):
        return False, "base_response must be a string"

    # Word count (exactly 35 to 50 words)
    words_count = count_words(base_response)
    if words_count < 35 or words_count > 50:
        return False, f"base_response word count is {words_count}, must be between 35 and 50 words"

    # Forbidden greetings or intros
    lower_res = base_response.lower().strip()
    forbidden_starters = ["hola", "claro", "recuerda", "segun", "en internet", "wikipedia"]
    for fs in forbidden_starters:
        if lower_res.startswith(fs):
            return False, f"base_response starts with forbidden word/phrase: '{fs}'"

    # Formats (no newlines, no unescaped double quotes)
    if "\n" in base_response or "\r" in base_response:
        return False, "base_response contains line breaks"

    return True, None

def call_gemini_api(prompt):
    data = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.3,
            "responseMimeType": "application/json"
        }
    }
    req = urllib.request.Request(
        MODEL_URL,
        data=json.dumps(data).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    try:
        with urllib.request.urlopen(req, timeout=45) as response:
            res_data = json.loads(response.read().decode("utf-8"))
            return res_data["candidates"][0]["content"]["parts"][0]["text"]
    except Exception as e:
        print(f"Error calling Gemini API: {e}")
        time.sleep(5)
        return None

def generate_concepts_for_subtheme(subtheme, existing_ids, count_needed=20):
    prompt = f"""
Eres un Ingeniero de Datos y Especialista en Minería de Información Educativa Química.
Genera un lote de exactamente {count_needed} conceptos educativos únicos sobre el subtema: "{subtheme}" dentro del tema general "Química: Tabla Periódica".

Cada concepto debe estar enfocado en un nivel cognitivo de Tercer Ciclo (estudiantes de 12 a 15 años). Simplifica las explicaciones pero mantén la precisión científica. El tono debe ser directo, instruccional y pedagógico, como un tutor explicándole a un alumno de 13 años.

Debes responder estrictamente con un objeto JSON que contenga una clave llamada "concepts" que es una lista de objetos, donde cada objeto sigue EXACTAMENTE esta estructura:
{{
  "intent_id": "identificador_unico_y_semantico",
  "keywords": ["palabra1", "palabra2", "palabra3", "palabra4"],
  "base_response": "La explicacion educativa directa..."
}}

REGLAS CRÍTICAS DE CONTROL DE CALIDAD:
1. intent_id:
   - Debe ser único, semántico, en minúsculas y separado por guiones bajos (ejemplo: "bloques_clasificacion_s").
   - NO uses patrones repetitivos o secuenciales de relleno como "concepto_01", "subtema_3", etc.
   - Estos IDs existentes ya están ocupados, NO los repitas: {list(existing_ids)[:30]}...

2. keywords:
   - Debe haber EXACTAMENTE entre 4 y 6 términos en la lista.
   - Todos los términos deben estar en minúsculas.
   - AUSENCIA TOTAL DE TILDES O ACENTOS (escribe "quimica" en vez de "química", "periodo" en vez de "período", "mendeleiev" en vez de "mendeléyev").
   - AUSENCIA TOTAL DE PALABRAS FUNCIONALES (absolutamente nada de artículos, preposiciones o conjunciones como: el, la, los, las, un, una, de, del, con, en, por, para, y, o, que, como, a, al). Usa solo sustantivos o verbos nucleares.

3. base_response:
   - Debe tener EXACTAMENTE entre 35 y 50 palabras. ¡Mídete y cuenta muy bien! Ni una palabra menos de 35, ni una más de 50.
   - ORTOGRAFÍA INMACULADA: Las tildes y acentos SÍ van en el base_response (escribe "química", "período", "átomo" correctamente).
   - El texto DEBE iniciar directamente con la explicación. PROHIBIDO incluir saludos ("Hola", "Claro", "Recuerda que"), muletillas, introducciones, o referencias a fuentes ("Según Wikipedia", "En internet").
   - Formato de texto plano en una sola línea: CERO saltos de línea (\\n) internos. CERO comillas dobles sin escapar.

Asegúrate de que el JSON retornado sea totalmente válido y esté bien estructurado.
"""
    raw_response = call_gemini_api(prompt)
    if not raw_response:
        return []

    # Try parsing the JSON
    try:
        # Clean potential markdown wrappers
        cleaned = raw_response.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        cleaned = cleaned.strip()

        data = json.loads(cleaned)
        concepts = data.get("concepts", [])
        return concepts
    except Exception as e:
        print(f"Error parsing JSON response for subtheme '{subtheme}': {e}")
        # Print a small preview of raw response
        print("Raw response preview:", raw_response[:200])
        return []
