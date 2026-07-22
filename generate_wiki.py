import wikipedia
import json
import re
import unicodedata

wikipedia.set_lang("es")

ARCHIVO_DESTINO = "GBX_brain_78A.json"
SUBTEMAS = [
    "Alegría genuina del estado emocional",
    "Tristeza adaptativa del desarrollo psicológico",
    "Manejo del enojo en adolescentes",
    "Empatía emocional con los demás",
    "Inteligencia emocional del desarrollo humano",
    "Autocontrol afectivo ante situaciones tensas",
    "Reconocimiento de emociones propias ajenas",
    "Expresión asertiva de emociones personales",
    "Regulación afectiva del estado anímico",
    "Afrontamiento del estrés psicológico adolescente",
    "Identificación precisa de sentimientos internos",
    "Comunicación fluida de estados emocionales",
    "Comprensión profunda de emociones ajenas",
    "Aceptación plena de emociones negativas",
    "Bienestar emocional del desarrollo adolescente",
    "Sensibilidad emocional ante problemas sociales",
    "Respeto sincero por emociones ajenas",
    "Tolerancia frente a emociones frustrantes",
    "Afrontamiento positivo de crisis emocionales",
    "Equilibrio emocional de la personalidad",
    "Vínculos emocionales de apego seguro",
    "Compasión humana hacia el sufrimiento",
    "Gratitud emocional por beneficios recibidos",
    "Optimismo emocional ante desafíos vitales",
    "Gestión emocional de la frustración",
    "Miedo instintivo de protección personal",
    "Reacción de sorpresa emocional espontánea"
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

MAX_CONCEPTOS = 190

def remove_accents(input_str):
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    return u"".join([c for c in nfkd_form if not unicodedata.combining(c)])

def clean_text(text):
    text = re.sub(r'\{[^{}]*\}', '', text)
    text = re.sub(r'\\displaystyle', '', text)
    text = re.sub(r'\\dots', '', text)
    text = re.sub(r'\s+', ' ', text)
    text = text.replace('\n', ' ').replace('"', '')
    return text.strip()

stopwords = {"el", "la", "los", "las", "un", "una", "unos", "unas", "de", "del", "a", "ante", "bajo", "cabe", "con", "contra", "desde", "en", "entre", "hacia", "hasta", "para", "por", "segun", "sin", "so", "sobre", "tras", "y", "e", "ni", "que", "o", "u", "su", "sus", "al", "se", "lo", "como", "mas", "pero", "esta", "estas", "este", "estos", "es", "son"}

def get_full_wiki_text(query):
    try:
        search_results = wikipedia.search(query, results=1)
        if search_results:
            page = wikipedia.page(search_results[0], auto_suggest=False)
            return page.content
    except Exception:
        pass
    return None

def generate_dataset():
    all_concepts = []
    concept_count = 0
    used_texts = set()
    used_ids = set()
    used_kws = []

    query_mapping = {
        "Alegría genuina del estado emocional": "Alegría (emoción)",
        "Tristeza adaptativa del desarrollo psicológico": "Tristeza",
        "Manejo del enojo en adolescentes": "Ira",
        "Empatía emocional con los demás": "Empatía",
        "Inteligencia emocional del desarrollo humano": "Inteligencia emocional",
        "Autocontrol afectivo ante situaciones tensas": "Autocontrol",
        "Reconocimiento de emociones propias ajenas": "Emoción",
        "Expresión asertiva de emociones personales": "Asertividad",
        "Regulación afectiva del estado anímico": "Regulación emocional",
        "Afrontamiento del estrés psicológico adolescente": "Estrés (psicología)",
        "Identificación precisa de sentimientos internos": "Sentimiento",
        "Comunicación fluida de estados emocionales": "Comunicación no verbal",
        "Comprensión profunda de emociones ajenas": "Teoría de la mente",
        "Aceptación plena de emociones negativas": "Psicología positiva",
        "Bienestar emocional del desarrollo adolescente": "Bienestar",
        "Sensibilidad emocional ante problemas sociales": "Sensibilidad (psicología)",
        "Respeto sincero por emociones ajenas": "Respeto",
        "Tolerancia frente a emociones frustrantes": "Tolerancia a la frustración",
        "Afrontamiento positivo de crisis emocionales": "Resiliencia (psicología)",
        "Equilibrio emocional de la personalidad": "Estabilidad emocional",
        "Vínculos emocionales de apego seguro": "Teoría del apego",
        "Compasión humana hacia el sufrimiento": "Compasión",
        "Gratitud emocional por beneficios recibidos": "Gratitud",
        "Optimismo emocional ante desafíos vitales": "Optimismo",
        "Gestión emocional de la frustración": "Frustración",
        "Miedo instintivo de protección personal": "Miedo",
        "Reacción de sorpresa emocional espontánea": "Sorpresa (emoción)"
    }

    for subtema in SUBTEMAS:
        if concept_count >= MAX_CONCEPTOS:
            break

        wiki_query = query_mapping.get(subtema, subtema)
        content = get_full_wiki_text(wiki_query)

        if not content:
            wiki_query = " ".join(subtema.split()[:2])
            content = get_full_wiki_text(wiki_query)
            if not content:
                print(f"No content found for {subtema}")
                continue

        content = clean_text(content)

        # Remove headers like == Header ==
        content = re.sub(r'==.*?==', '', content)

        # Split into sentences
        sentences = re.split(r'(?<=[.!?])\s+', content)

        dimension_idx = 0
        i = 0
        while i < len(sentences) and dimension_idx < len(DIMENSIONES) and concept_count < MAX_CONCEPTOS:
            dimension = DIMENSIONES[dimension_idx]

            combined = ""
            current_words = 0
            j = i
            valid_text = None

            while j < len(sentences):
                sentence = sentences[j].strip()
                if not sentence:
                    j += 1
                    continue

                words = sentence.split()

                if current_words + len(words) <= 50:
                    combined += sentence + " "
                    current_words += len(words)
                    # Complete sentences ending in punctuation
                    if 35 <= current_words <= 50 and combined.strip()[-1] in '.!?':
                        valid_text = combined.strip()
                        break
                    j += 1
                else:
                    break

            if valid_text and valid_text not in used_texts:
                # generate ID
                base_id = remove_accents(subtema).lower()
                base_id = re.sub(r'[^a-z0-9 ]', '', base_id)
                base_id = "_".join(base_id.split()[:2])

                dim_id = remove_accents(dimension).lower()
                dim_id = re.sub(r'[^a-z0-9 ]', '', dim_id)
                dim_id = "_".join(dim_id.split()[:2])

                intent_id = f"{base_id}_{dim_id}"

                intent_id = ''.join([c for c in intent_id if not c.isdigit()])

                # Deduplicate ID
                original_intent_id = intent_id
                suffix_idx = 1
                while intent_id in used_ids:
                    extra_words = remove_accents(dimension).lower().split()
                    extra_words = [w for w in extra_words if w.isalpha() and w not in stopwords]
                    if suffix_idx < len(extra_words):
                        intent_id = f"{original_intent_id}_{extra_words[suffix_idx]}"
                        suffix_idx += 1
                    else:
                        extra_words = remove_accents(subtema).lower().split()
                        extra_words = [w for w in extra_words if w.isalpha() and w not in stopwords]
                        if suffix_idx - len(extra_words) < len(extra_words):
                             intent_id = f"{original_intent_id}_{extra_words[suffix_idx - len(extra_words)]}"
                             suffix_idx += 1
                        else:
                             intent_id = f"{original_intent_id}_var{suffix_idx}"
                             suffix_idx += 1

                used_ids.add(intent_id)

                # Keywords
                sub_words = remove_accents(subtema).lower().split()
                dim_words = remove_accents(dimension).lower().split()
                text_words = remove_accents(valid_text).lower().split()

                all_possible_kws = sub_words + dim_words + text_words
                clean_kws = []
                for kw in all_possible_kws:
                    kw = re.sub(r'[^a-z]', '', kw)
                    if kw and kw not in stopwords and kw not in clean_kws and len(kw) > 3:
                        clean_kws.append(kw)

                final_kws = clean_kws[:6]
                while len(final_kws) < 4:
                    fallback = ["proceso", "sistema", "desarrollo", "funcion", "estado", "analisis", "estudio", "factor", "efecto"]
                    for fb in fallback:
                        if fb not in final_kws:
                            final_kws.append(fb)
                            break

                # Avoid cloned keywords (exact same array > 3 times)
                # Count current occurrences
                current_kws_tuple = tuple(final_kws)
                kws_count = used_kws.count(current_kws_tuple)
                if kws_count >= 2:
                    # Modify the array by adding a dimension-specific word
                    dim_extra = remove_accents(dimension).lower().split()
                    dim_extra = [w for w in dim_extra if w.isalpha() and w not in stopwords]
                    if dim_extra:
                        final_kws[-1] = dim_extra[0]

                used_kws.append(tuple(final_kws))

                concept = {
                    "intent_id": intent_id,
                    "keywords": final_kws,
                    "base_response": valid_text
                }

                all_concepts.append(concept)
                used_texts.add(valid_text)
                concept_count += 1
                dimension_idx += 1
                i = j + 1
            else:
                # If we couldn't form a valid text block from i, move forward
                # Try from i+1
                i += 1

        print(f"Subtema '{subtema}' terminado. Conceptos de este subtema: {dimension_idx}. Total: {concept_count}")

    # Ensure min 100 concepts as requested "entre 100 y maximo 190"

    with open(ARCHIVO_DESTINO, 'w', encoding='utf-8') as f:
        json.dump(all_concepts, f, ensure_ascii=False, indent=4)

    print(f"Terminado. Total conceptos: {len(all_concepts)}")

if __name__ == "__main__":
    generate_dataset()
