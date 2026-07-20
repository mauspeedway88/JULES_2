import json
import re

ARCHIVO_DESTINO = "GBX_brain_63A.json"

# Diccionario para restaurar tildes en base_response
TILDES_COMUNES = {
    r'\bcomprension\b': 'comprensión',
    r'\bleccion\b': 'lección',
    r'\banalisis\b': 'análisis',
    r'\bproposito\b': 'propósito',
    r'\batencion\b': 'atención',
    r'\bfuncion\b': 'función',
    r'\bclasificacion\b': 'clasificación',
    r'\bexploracion\b': 'exploración',
    r'\binformacion\b': 'información',
    r'\bcomunicacion\b': 'comunicación',
    r'\boracion\b': 'oración',
    r'\baccion\b': 'acción',
    r'\bseccion\b': 'sección',
    r'\bconclusion\b': 'conclusión',
    r'\bevaluacion\b': 'evaluación',
    r'\binterpretacion\b': 'interpretación',
    r'\borigenes\b': 'orígenes',
    r'\bterminos\b': 'términos',
    r'\bpracticas\b': 'prácticas',
    r'\bpractica\b': 'práctica',
    r'\btecnica\b': 'técnica',
    r'\btecnicas\b': 'técnicas',
    r'\bmetodo\b': 'método',
    r'\bmetodos\b': 'métodos',
    r'\bbasico\b': 'básico',
    r'\brapida\b': 'rápida',
    r'\brapido\b': 'rápido',
    r'\bexito\b': 'éxito',
    r'\benergia\b': 'energía',
    r'\bsinonimo\b': 'sinónimo',
    r'\btextual\b': 'textual', # No tilde pero aseguramos no romper
    r'\bexploratorio\b': 'exploratorio'
}

# Palabras funcionales (stop words) a eliminar de keywords
STOP_WORDS = {
    'el', 'la', 'los', 'las', 'un', 'una', 'unos', 'unas',
    'de', 'del', 'en', 'a', 'al', 'por', 'para', 'con', 'sin', 'sobre', 'entre',
    'y', 'o', 'u', 'e', 'ni', 'que', 'como', 'cuando', 'donde', 'quien',
    'es', 'son', 'fue', 'eran', 'ser', 'estar'
}

def clean_accents(text):
    text = text.replace('á', 'a').replace('é', 'e').replace('í', 'i').replace('ó', 'o').replace('ú', 'u')
    text = text.replace('Á', 'a').replace('É', 'e').replace('Í', 'i').replace('Ó', 'o').replace('Ú', 'u')
    return text

def procesar_keywords(kw_str):
    # Todo a minúsculas y sin acentos
    kw_str = clean_accents(kw_str.lower())
    # Remover puntuación y comillas
    kw_str = re.sub(r'[^\w\s]', '', kw_str)
    # Extraer palabras
    palabras = kw_str.split()
    # Filtrar palabras funcionales
    palabras_filtradas = [p for p in palabras if p not in STOP_WORDS]
    # Limitar a 4-6 palabras (ajustar si es menos, aseguramos no más de 6)
    palabras_finales = palabras_filtradas[:6]
    return " ".join(palabras_finales)

def procesar_base_response(br_str):
    # Formato de plain text estricto sin saltos de línea ni comillas dobles
    br_str = br_str.replace('\n', ' ').replace('\r', '')
    br_str = br_str.replace('"', "'")
    # Restaurar ortografía si es necesario
    for pat, rep in TILDES_COMUNES.items():
        br_str = re.sub(pat, rep, br_str, flags=re.IGNORECASE)

    # Asegurar longitud (recortar a ~50 palabras o rellenar si es muy corto es complejo con regex,
    # pero al menos nos aseguramos de no tener exceso si el LLM se pasó demasiado).
    # El prompt ya indicaba 35 a 50 palabras.
    palabras = br_str.split()
    if len(palabras) > 50:
        br_str = " ".join(palabras[:50]) + "."

    return br_str

def main():
    try:
        with open(ARCHIVO_DESTINO, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print("Archivo JSON no encontrado.")
        return

    # Post-procesar los elementos
    processed_data = []

    for item in data:
        # Re-generar intent_id sin números secuenciales uniendo keywords
        kw_procesadas = procesar_keywords(item.get('keywords', ''))

        # Crear un id semántico único con las keywords (las 3 primeras)
        partes = kw_procesadas.split()[:3]
        if not partes:
            partes = ['concepto', 'lectura']
        intent_id = "_".join(partes)

        # Validar si ya existe este intent_id (evitar duplicados)
        # Si existe, agregar una palabra más
        suffix_idx = 3
        original_intent_id = intent_id
        while any(d['intent_id'] == intent_id for d in processed_data):
            if suffix_idx < len(kw_procesadas.split()):
                intent_id = original_intent_id + "_" + kw_procesadas.split()[suffix_idx]
                suffix_idx += 1
            else:
                # Si no hay más keywords, generamos algo extra semántico sin números
                intent_id = intent_id + "_alternativo"
                break

        item['intent_id'] = intent_id
        item['keywords'] = kw_procesadas
        item['base_response'] = procesar_base_response(item.get('base_response', ''))
        processed_data.append(item)

    # Asegurar límite máximo de 200 (aunque el generador ya debió cortarlo, no está de más)
    processed_data = processed_data[:200]

    with open(ARCHIVO_DESTINO, 'w', encoding='utf-8') as f:
        json.dump(processed_data, f, ensure_ascii=False, indent=2)

    print(f"Postprocesamiento completado. Total registros: {len(processed_data)}")

if __name__ == "__main__":
    main()
