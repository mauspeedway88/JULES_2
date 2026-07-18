import json
import re
import os
import subprocess
import unidecode
import wikipedia
import spacy

wikipedia.set_lang("es")
nlp = spacy.load('es_core_news_md')

SUBTOPICS = [
    # skip silbido rápido de altos because it gets bird facts
    "ultrasonido sobre umbral auditivo", "infrasonido bajo registro humano",
    "efecto Doppler por movimiento", "resonancia vibratoria de materiales", "reverberación prolongada en salas",
    "difracción al bordear obstáculos", "refracción por cambio ambiental", "estruendo supersónico de aviones",
    "número de Mach aéreo", "frente esférico de expansión", "patrón estacionario de cuerdas",
    "armónicos de progresión múltiple", "pulsaciones por desfase leve", "absorción amortiguadora de ruido",
    "hertzios de repetición periódica", "acústica arquitectónica moderna", "onda longitudinal en fluidos",
    "velocidad del sonido en sólidos", "interferencia constructiva de ondas", "interferencia destructiva acústica",
    "tono fundamental y sobretonos", "timbre de instrumentos musicales", "umbral de dolor auditivo",
    "decibelios y presión sonora", "audición humana y frecuencias", "ecolocalización en animales marinos",
    "sonar y detección submarina", "onda sonora mecánica", "propagación del sonido", "acústica submarina",
    "eco acústico", "aislamiento acústico", "frecuencia natural", "onda de choque transversal", "barrera del sonido acústico",
    "física de ondas sonoras", "presión acústica", "espectro de frecuencia sonora", "impedancia acústica", "cavitación acústica",
    "onda estacionaria resonante", "oscilación armónica sonora", "nodo y antinodo acústico", "ley de Snell en sonido",
    "efecto Haas acústico", "difracción de Fresnel en sonido", "efecto de proximidad microfónico"
]

TARGET_COUNT = 91
OUTPUT_FILE = "GBX_brain_19B.json"

def get_wiki_content(query):
    try:
        search_results = wikipedia.search(query, results=1)
        if search_results:
            page = wikipedia.page(search_results[0])
            return page.content
        return None
    except Exception as e:
        return None

def search_query_for_topic(subtopic):
    subtopic_lower = subtopic.lower()
    if "doppler" in subtopic_lower: return "Efecto Doppler"
    if "ultrasonido" in subtopic_lower: return "Ultrasonido"
    if "infrasonido" in subtopic_lower: return "Infrasonido"
    if "resonancia" in subtopic_lower: return "Resonancia acústica"
    if "reverberación" in subtopic_lower: return "Reverberación"
    if "difracción" in subtopic_lower: return "Difracción"
    if "refracción" in subtopic_lower: return "Refracción"
    if "mach" in subtopic_lower: return "Número de Mach"
    if "armónicos" in subtopic_lower: return "Armónico"
    if "pulsaciones" in subtopic_lower: return "Pulsación (física)"
    if "acústica arquitectónica" in subtopic_lower: return "Acústica arquitectónica"
    if "velocidad del sonido" in subtopic_lower: return "Velocidad del sonido"
    if "interferencia" in subtopic_lower: return "Interferencia"
    if "timbre" in subtopic_lower: return "Timbre (acústica)"
    if "decibelios" in subtopic_lower: return "Decibelio"
    if "ecolocalización" in subtopic_lower: return "Ecolocalización"
    if "sonar" in subtopic_lower: return "Sonar"
    if "eco" in subtopic_lower: return "Eco"
    if "aislamiento" in subtopic_lower: return "Aislamiento acústico"
    if "choque" in subtopic_lower: return "Onda de choque"
    if "barrera" in subtopic_lower: return "Barrera del sonido"
    if "impedancia" in subtopic_lower: return "Impedancia acústica"
    return subtopic

def fix_keywords(keywords):
    fixed = []
    forbidden = {'el', 'la', 'los', 'las', 'un', 'una', 'unos', 'unas', 'a', 'ante', 'bajo', 'cabe', 'con', 'contra', 'de', 'desde', 'en', 'entre', 'hacia', 'hasta', 'para', 'por', 'segun', 'sin', 'so', 'sobre', 'tras', 'y', 'o', 'u', 'e', 'que', 'su', 'se', 'del', 'las', 'los'}
    for kw in keywords:
        clean_kw = unidecode.unidecode(kw.lower()).replace(',', '').replace('.', '').replace('(', '').replace(')', '').replace('"', '')
        clean_kw = re.sub(r'[^a-z]', '', clean_kw) # strictly only letters
        if len(clean_kw) > 3 and clean_kw not in forbidden:
            fixed.append(clean_kw)

    unique_fixed = []
    for f in fixed:
        if f not in unique_fixed:
            unique_fixed.append(f)

    # Guarantee 4-6 words
    final_kw = unique_fixed[:6]
    fallback = ['onda', 'acustica', 'fisica', 'sonido', 'energia', 'vibracion']
    while len(final_kw) < 4:
        cand = fallback.pop(0)
        if cand not in final_kw:
            final_kw.append(cand)
    return final_kw

def extract_keywords_from_text(text):
    doc = nlp(text)
    nouns = [token.lemma_ for token in doc if token.pos_ in ['NOUN', 'VERB'] and not token.is_stop]
    return fix_keywords(nouns)

def extract_chunks(content):
    doc = nlp(content)
    sentences = [sent.text.strip().replace('\n', ' ').replace('"', "'") for sent in doc.sents if len(sent.text.split()) > 5 and '=' not in sent.text]

    chunks = []
    for i in range(len(sentences)):
        selected = []
        word_count = 0
        for j in range(i, len(sentences)):
            s = sentences[j]
            s_words = s.split()
            if word_count + len(s_words) <= 50:
                selected.append(s)
                word_count += len(s_words)
            else:
                break

        if 35 <= word_count <= 50:
            text = " ".join(selected)
            if any(c in 'áéíóúÁÉÍÓÚ' for c in text):
                chunks.append(text)

    return chunks

def main():
    try:
        with open(OUTPUT_FILE, 'r', encoding='utf-8') as f:
            dataset = json.load(f)
    except:
        dataset = []
    seen_intents = set([d['intent_id'] for d in dataset])

    dimensions = ["definicion", "dinamica", "propiedades", "historia", "aplicaciones", "importancia", "calculos", "interaccion"]

    for subtopic in SUBTOPICS:
        if len(dataset) >= TARGET_COUNT:
            break

        wiki_query = search_query_for_topic(subtopic)
        content = get_wiki_content(wiki_query)
        if not content:
            continue

        chunks = extract_chunks(content)
        if not chunks:
            continue

        unique_chunks = []
        for c in chunks:
            # Simple deduplication based on first few words
            if not any(c[:40] in u[:40] for u in unique_chunks):
                unique_chunks.append(c)

        for i, chunk in enumerate(unique_chunks):
            if i >= len(dimensions) or len(dataset) >= TARGET_COUNT:
                break

            dim_key = dimensions[i]
            intent_id = f"{subtopic.replace(' ', '_').lower()}_{dim_key}".replace(',', '').replace('á','a').replace('é','e').replace('í','i').replace('ó','o').replace('ú','u')
            intent_id = unidecode.unidecode(intent_id)
            intent_id = re.sub(r'[^a-z_]', '', intent_id)

            if intent_id in seen_intents:
                continue

            keywords = extract_keywords_from_text(chunk)

            dataset.append({
                "intent_id": intent_id,
                "keywords": keywords[:6],
                "base_response": chunk
            })
            seen_intents.add(intent_id)
            print(f"Added: {intent_id} ({len(dataset)}/{TARGET_COUNT})")

    # If we fall short, run a second pass through the topics
    if len(dataset) < TARGET_COUNT:
        print(f"Warning: Only {len(dataset)} generated. Running second pass.")
        for subtopic in SUBTOPICS:
             if len(dataset) >= TARGET_COUNT:
                  break
             wiki_query = search_query_for_topic(subtopic)
             content = get_wiki_content(wiki_query)
             if not content: continue
             chunks = extract_chunks(content)
             unique_chunks = []
             for c in chunks:
                 if not any(c[:40] in u[:40] for u in unique_chunks):
                     unique_chunks.append(c)

             if len(unique_chunks) > len(dimensions):
                 for i, chunk in enumerate(unique_chunks[len(dimensions):]):
                     if len(dataset) >= TARGET_COUNT: break
                     intent_id = f"{subtopic.replace(' ', '_').lower()}_extra_{i}".replace(',', '').replace('á','a').replace('é','e').replace('í','i').replace('ó','o').replace('ú','u')
                     intent_id = unidecode.unidecode(intent_id)
                     intent_id = re.sub(r'[^a-z_]', '', intent_id)

                     if intent_id not in seen_intents:
                         dataset.append({
                             "intent_id": intent_id,
                             "keywords": extract_keywords_from_text(chunk)[:6],
                             "base_response": chunk
                         })
                         seen_intents.add(intent_id)
                         print(f"Added: {intent_id} ({len(dataset)}/{TARGET_COUNT})")

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(dataset, f, ensure_ascii=False, indent=2)

    print(f"Finished. Total concepts: {len(dataset)}")

if __name__ == "__main__":
    main()
