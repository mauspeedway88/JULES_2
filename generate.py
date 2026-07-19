import asyncio
import json
import logging
import re
import unicodedata
import os
import wikipedia
import math

wikipedia.set_lang("es")

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

DESTINO_ARCHIVO = "GBX_brain_55B.json"
TEMA_ESPECIFICO = [
    "Imperio Mongol de Gengis Kan", "Civilización china de la antigüedad", "Dinastías guerreras de China antigua",
    "Samuráis de civilización japonesa antigua", "Guerra de Vietnam conflicto bélico", "Guerra de Corea conflicto militar",
    "Guerra del Golfo Pérsico bélica", "Guerra de trincheras primera mundial", "Holocausto de Segunda Guerra Mundial",
    "Batalla de Stalingrado segunda mundial", "Desembarco de Normandía segunda mundial", "Bombardeos atómicos de Japón bélicos",
    "Carrera armamentista de Guerra Fría", "Carrera espacial de Guerra Fría", "Guerra de Afganistán conflicto bélico",
    "Guerra de Siria conflicto moderno", "Guerras yugoslavas de los noventa", "Imperio Bizantino de la antigüedad",
    "Guerras anglobóeres conflicto africano militar", "Guerra del Opio civilización china", "Guerra rusojaponesa conflicto militar oriental",
    "Tácticas militares de civilizaciones antiguas", "Armamento pesado de guerras mundiales", "Tratados de paz de guerras",
    "Civilización sumeria de la antigüedad", "Reino de Kush civilización africana", "Imperio Acadio de guerras antiguas",
    "Civilización hitita de la antigüedad"
]

DIMENSIONES_ONTOLOGICAS = [
    "Definición anatómica o estructural", "Dinámica y funcionamiento físico", "Propiedades químicas o materiales",
    "Errores, fallas y patologías comunes", "Historia, origen y evolución", "Contexto y entorno ecológico",
    "Aplicaciones prácticas en la vida real", "Importancia e impacto social", "Ventajas y desventajas comparativas",
    "Riesgos y medidas de seguridad", "Clasificación taxonómica", "Cálculos y fórmulas asociadas",
    "Mitos y concepciones erróneas", "Relación simbiótica con otros sistemas", "Transformación y ciclos energéticos",
    "Experimentos y demostraciones escolares", "Consecuencias a largo plazo", "Impacto ambiental",
    "Mantenimiento y prevención", "Proyecciones futuras y tecnología"
]

def strip_accents(text):
    text = unicodedata.normalize('NFD', text).encode('ascii', 'ignore').decode("utf-8")
    return str(text)

def generate_intent_id(tema, dimension_index):
    tema_words = [strip_accents(w.lower()) for w in re.findall(r'\b\w+\b', tema) if len(w) > 3]
    tema_str = "_".join(tema_words[:3])
    dim_words = [strip_accents(w.lower()) for w in re.findall(r'\b\w+\b', DIMENSIONES_ONTOLOGICAS[dimension_index]) if len(w) > 3]
    dim_str = "_".join(dim_words[:2])
    intent_id = f"{tema_str}_{dim_str}"
    intent_id = re.sub(r'_\d+$', '', intent_id)
    return intent_id

def clean_text_for_base_response(text):
    text = re.sub(r'={2,}\s*[^=]+\s*={2,}', '', text)  # Eliminar headers ==== Title ====
    text = re.sub(r'\[\d+\]', '', text)
    text = re.sub(r'\[cita requerida\]', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\n+', ' ', text)
    text = re.sub(r' +', ' ', text)
    text = text.replace('"', "'")
    return text.strip()

def get_keywords_from_text(text):
    stop_words = {"el", "la", "los", "las", "un", "una", "unos", "unas", "a", "ante", "bajo", "cabe", "con", "contra", "de", "desde", "en", "entre", "hacia", "hasta", "para", "por", "segun", "sin", "so", "sobre", "tras", "y", "e", "ni", "o", "u", "que", "al", "del", "es", "son", "fue", "fueron", "como", "mas", "sus", "su", "se", "ha", "han", "lo", "este", "esta", "estos", "estas", "habia", "tambien", "aunque", "cuando", "donde", "quien", "porque", "pero", "sino", "si", "ya", "muy", "tan", "asi", "aquel", "aquella", "aquellos", "aquellas", "nos", "les", "me", "te", "os", "mi", "tu", "su", "nuestro", "vuestro", "sus", "sea", "sean", "era", "eran", "sido", "ido", "cual", "cuales", "cada", "todo", "toda", "todos", "todas", "otro", "otra", "otros", "otras", "mismo", "misma", "mismos", "mismas", "algun", "alguna", "algunos", "algunas", "ningun", "ninguna", "nada", "algo", "nadie", "quienes"}

    # Solo mantener palabras compuestas por letras (sin números ni símbolos especiales) y de cierta longitud
    words = re.findall(r'\b[a-zA-ZáéíóúÁÉÍÓÚñÑ]{5,}\b', text)
    cleaned = []

    # Lista estricta de palabras funcionales/adverbios/adjetivos a filtrar adicionalmente
    adverbios_adjetivos_comunes = {"gran", "mayor", "menor", "mejor", "peor", "buen", "mal", "nuevo", "viejo", "alto", "bajo", "largo", "corto", "fuerte", "debil", "grande", "pequeño", "mucho", "poco", "bastante", "demasiado", "casi", "solo", "solamente", "primer", "primera", "segundo", "segunda", "tercer", "tercera", "ultimo", "ultima", "luego", "despues", "antes", "siempre", "nunca", "jamas", "quizas", "talvez", "acaso", "mientras", "durante", "hasta", "hacia", "contra", "desde", "entre", "segun", "sobre", "tras", "mediante", "excepto", "salvo", "incluso", "ademas", "sino", "aunque", "pues", "luego", "entonces", "por", "para", "con", "sin", "aquel", "este", "ese", "aqui", "alli", "alla", "aca", "ahora", "hoy", "mañana", "ayer", "pronto", "tarde", "temprano", "todavia", "aun", "ya"}

    for w in words:
        w_lower = w.lower()
        if w_lower not in stop_words and strip_accents(w_lower) not in adverbios_adjetivos_comunes:
            w_no_accents = strip_accents(w_lower)
            # Intentar asegurar que sean sustantivos o verbos
            if w_no_accents not in cleaned:
                cleaned.append(w_no_accents)

    if len(cleaned) < 4:
        return ["conflicto", "historia", "desarrollo", "sociedad"]
    return cleaned[:6]

def chunk_sentences(text, min_words=35, max_words=50):
    # Separar en oraciones, ignorando abreviaturas comunes si es posible
    sentences = re.split(r'(?<=[.!?])\s+(?=[A-Z])', text)
    valid_chunks = []

    for i in range(len(sentences)):
        chunk = ""
        for j in range(i, len(sentences)):
            temp = chunk + " " + sentences[j] if chunk else sentences[j]
            words = temp.split()
            if min_words <= len(words) <= max_words:
                valid_chunks.append(temp.strip())
            elif len(words) > max_words:
                break

    return valid_chunks

def get_wikipedia_summary(query):
    try:
        search_results = wikipedia.search(query, results=1)
        if search_results:
            page = wikipedia.page(search_results[0])
            return page.content
        return None
    except Exception as e:
        logger.error(f"Error wikipedia para {query}: {e}")
        return None

def extract_concepts_from_wikipedia(wiki_text, tema):
    clean_wiki = clean_text_for_base_response(wiki_text)

    # Extraer chunks válidos (35-50 palabras, oraciones completas)
    valid_chunks = chunk_sentences(clean_wiki)
    if not valid_chunks:
        return []

    # Diccionario de keywords para asociar chunks a dimensiones
    keywords_dim = {
        "Definición anatómica o estructural": ["estructura", "organización", "gobierno", "sistema", "división", "jerarquía", "administración", "estado", "imperio", "reino", "nación", "país"],
        "Dinámica y funcionamiento físico": ["movimiento", "táctica", "funcionamiento", "operación", "maniobra", "despliegue", "combate", "fuerza", "ejército", "tropa", "soldado"],
        "Propiedades químicas o materiales": ["arma", "material", "hierro", "bronce", "acero", "pólvora", "tecnología", "equipamiento", "armadura", "espada", "lanza", "fusil", "cañón", "tanque", "avión"],
        "Errores, fallas y patologías comunes": ["error", "falla", "derrota", "enfermedad", "colapso", "caída", "problema", "crisis", "debacle", "pérdida", "fracaso"],
        "Historia, origen y evolución": ["origen", "historia", "comienzo", "evolución", "desarrollo", "fundación", "surgimiento", "nacimiento", "creación"],
        "Contexto y entorno ecológico": ["geografía", "terreno", "clima", "entorno", "montaña", "río", "valle", "desierto", "llanura", "mar", "océano", "clima"],
        "Aplicaciones prácticas en la vida real": ["aplicación", "práctica", "uso", "estrategia", "logística", "táctica", "método", "técnica"],
        "Importancia e impacto social": ["sociedad", "impacto", "importancia", "población", "cultura", "demografía", "civil', 'pueblo", "ciudadano"],
        "Ventajas y desventajas comparativas": ["ventaja", "superioridad", "desventaja", "comparación", "inferioridad", "beneficio", "perjuicio"],
        "Riesgos y medidas de seguridad": ["riesgo", "peligro", "seguridad", "defensa", "protección", "guardia", "amenaza", "precaución"],
        "Clasificación taxonómica": ["clasificación", "tipo", "clase", "rango", "grado", "categoría", "orden", "familia"],
        "Cálculos y fórmulas asociadas": ["número", "cantidad", "cálculo", "medida", "distancia", "logística", "cifra", "estadística"],
        "Mitos y concepciones erróneas": ["mito", "leyenda", "creencia", "exageración", "propaganda", "falsedad", "error"],
        "Relación simbiótica con otros sistemas": ["relación", "alianza", "comercio", "economía", "intercambio", "diplomacia", "tratado", "pacto"],
        "Transformación y ciclos energéticos": ["recurso", "energía", "producción", "agricultura", "metalurgia", "industria", "economía"],
        "Experimentos y demostraciones escolares": ["estudio", "análisis", "demostración", "maqueta", "simulación", "educación", "enseñanza"],
        "Consecuencias a largo plazo": ["consecuencia", "legado", "futuro", "resultado", "posterioridad", "efecto", "impacto"],
        "Impacto ambiental": ["ambiente", "naturaleza", "bosque", "destrucción", "ecología", "paisaje", "contaminación"],
        "Mantenimiento y prevención": ["mantenimiento", "prevención", "patrulla", "vigilancia", "cuidado", "conservación"],
        "Proyecciones futuras y tecnología": ["futuro", "tecnología", "descubrimiento", "arqueología", "investigación", "ciencia", "avance"]
    }

    # Asignar los mejores chunks a cada dimensión
    concepts = []
    used_chunks = set()

    for idx, dimension in enumerate(DIMENSIONES_ONTOLOGICAS):
        best_chunk = None
        best_score = -1

        target_kws = keywords_dim.get(dimension, [])

        for chunk in valid_chunks:
            if chunk in used_chunks:
                continue

            chunk_lower = chunk.lower()
            score = sum(1 for kw in target_kws if kw in chunk_lower)

            # Penalizar fragmentos extraños
            if chunk_lower.startswith("en ") or chunk_lower.startswith("el ") or chunk_lower.startswith("la "):
                score += 0.1 # Ligero bonus para oraciones normales
            if not chunk.endswith("."):
                score -= 10 # Penalizar fuertemente si no termina en punto

            if score > best_score:
                best_score = score
                best_chunk = chunk

        if best_chunk:
            used_chunks.add(best_chunk)

            intent_id = generate_intent_id(tema, idx)

            # Post-procesamiento final del chunk para asegurar calidad
            chunk_cleaned = best_chunk
            if chunk_cleaned.lower().startswith("esta "):
                chunk_cleaned = "La " + chunk_cleaned[5:]
            if chunk_cleaned.lower().startswith("este "):
                chunk_cleaned = "El " + chunk_cleaned[5:]

            diccionario_acentos = {
                r'\benergia\b': 'energía',
                r'\bvision\b': 'visión',
                r'\bexpansion\b': 'expansión',
                r'\bcivilizacion\b': 'civilización',
                r'\bevolucion\b': 'evolución',
                r'\borigen\b': 'origen',
            }
            for pat, rep in diccionario_acentos.items():
                chunk_cleaned = re.sub(pat, rep, chunk_cleaned, flags=re.IGNORECASE)

            # Verificar restricciones de nuevo
            words = chunk_cleaned.split()
            if 35 <= len(words) <= 50 and not '"' in chunk_cleaned and not '\n' in chunk_cleaned and chunk_cleaned[0].isupper():
                keywords = get_keywords_from_text(chunk_cleaned)
                if keywords and 4 <= len(keywords) <= 6:
                    concepts.append({
                        "intent_id": intent_id,
                        "keywords": keywords,
                        "base_response": chunk_cleaned
                    })

    return concepts

def save_incremental(new_concepts):
    existing = []
    if os.path.exists(DESTINO_ARCHIVO):
        with open(DESTINO_ARCHIVO, "r", encoding="utf-8") as f:
            try:
                existing = json.load(f)
            except:
                pass

    seen_ids = {c["intent_id"] for c in existing}
    seen_resps = {c["base_response"] for c in existing}

    unique_new = []
    for c in new_concepts:
        if c["intent_id"] not in seen_ids and c["base_response"] not in seen_resps:
            unique_new.append(c)
            seen_ids.add(c["intent_id"])
            seen_resps.add(c["base_response"])

    combined = existing + unique_new
    with open(DESTINO_ARCHIVO, "w", encoding="utf-8") as f:
        json.dump(combined, f, ensure_ascii=False, indent=4)

    return len(combined)

def main():
    if os.path.exists(DESTINO_ARCHIVO):
        os.remove(DESTINO_ARCHIVO)

    batch = []

    for tema in TEMA_ESPECIFICO:
        logger.info(f"Scraping Wikipedia for: {tema}")
        wiki_content = get_wikipedia_summary(tema)

        if not wiki_content:
            logger.warning(f"No content for {tema}")
            continue

        concepts = extract_concepts_from_wikipedia(wiki_content, tema)
        batch.extend(concepts)

        if len(batch) >= 20:
            total = save_incremental(batch)
            logger.info(f"Saved {total} concepts")
            batch = []

    if batch:
        total = save_incremental(batch)
        logger.info(f"Saved {total} concepts")

    logger.info("Done generating from Wikipedia.")

if __name__ == "__main__":
    main()
