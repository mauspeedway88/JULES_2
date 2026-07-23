import os
import json
import re
import requests
import spacy
import unicodedata
import random

def remove_accents(input_str):
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    return u"".join([c for c in nfkd_form if not unicodedata.combining(c)])

def clean_text(text):
    text = re.sub(r'==+.*?==+', '', text)
    text = re.sub(r'===+.*?===+', '', text)
    text = re.sub(r'\[.*?\]', '', text)
    text = re.sub(r'\{.*?\}', '', text)
    text = re.sub(r'\(.*?\)', '', text)
    text = re.sub(r'\u200b|\u200c', '', text)
    text = re.sub(r'Bibliografía.*', '', text, flags=re.IGNORECASE)
    text = re.sub(r'Enlaces externos.*', '', text, flags=re.IGNORECASE)
    text = re.sub(r'Véase también.*', '', text, flags=re.IGNORECASE)
    text = re.sub(r'Referencias.*', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\s+', ' ', text)
    text = text.replace('"', "'")
    return text.strip()

def get_wikipedia_text(topic):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) JulesBot/1.0'}
    search_url = f'https://es.wikipedia.org/w/api.php?action=query&list=search&srsearch={requests.utils.quote(topic)}&format=json'
    text_content = ""
    try:
        resp = requests.get(search_url, headers=headers).json()
        if not resp.get('query', {}).get('search'):
            # try with fewer words
            words = topic.split()
            if len(words) > 2:
                shorter_topic = " ".join(words[:2])
                search_url = f'https://es.wikipedia.org/w/api.php?action=query&list=search&srsearch={requests.utils.quote(shorter_topic)}&format=json'
                resp = requests.get(search_url, headers=headers).json()

        search_results = resp.get('query', {}).get('search', [])
        for res in search_results[:2]: # Get top 2 articles
            title = res['title']
            url = f'https://es.wikipedia.org/w/api.php?action=query&prop=extracts&explaintext=1&titles={requests.utils.quote(title)}&format=json'
            resp2 = requests.get(url, headers=headers).json()
            pages = resp2.get('query', {}).get('pages', {})
            for k, v in pages.items():
                extract = v.get('extract', '')
                text_content += extract + " "
    except Exception as e:
        print(f"Error fetching {topic}: {e}")
    return text_content

nlp = spacy.load("es_core_news_sm")

SUBTOPICS = [
    "Música Memoria auditiva",
    "Apreciación crítica audición musical",
    "Clave de sol musical",
    "Clave de fa bajos",
    "Instrumentos de percusión",
    "Instrumentos de viento madera",
    "Instrumentos de viento metal",
    "Instrumentos de cuerda frotada",
    "Pulso constante ritmo musical",
    "Síncopa rítmica tiempos débiles",
    "Alteraciones musicales sostenido bemol",
    "Tonalidad musical obras sonoras",
    "Solfeo cantado de notas",
    "Fraseo expresivo interpretación musical",
    "Repertorio musical coros",
    "Matices expresión musical",
    "Rango de tesitura vocal",
    "Canto a capela",
    "Música folclórica",
    "Instrumentos musicales electrónicos",
    "Altura sonido musical",
    "Forma musical estrofa estribillo",
    "Contrapunto melodías simultáneas",
    "Acústica sonido aulas",
    "Dictado musical entrenamiento",
    "Dirección orquestal",
    "Improvisación musical rítmica"
]

DIMENSIONS = [
    "definicion",
    "funcionamiento",
    "propiedades",
    "errores",
    "historia",
    "contexto",
    "aplicaciones",
    "impacto",
    "ventajas",
    "riesgos",
    "clasificacion",
    "calculos",
    "mitos",
    "relacion",
    "transformacion",
    "experimentos",
    "consecuencias",
    "ambiente",
    "mantenimiento",
    "proyecciones"
]

def get_last_sentence(text):
    sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', text) if s.strip()]
    return sentences[-1] if sentences else ""

def is_valid_spanish_content(text):
    # Reject texts with English words or weird author names
    english_words = ["the", "and", "pitch", "double", "flat", "half", "steps", "raised", "lowered"]
    words = text.lower().split()
    for w in words:
        if w in english_words:
            return False
    # Check length again just in case
    word_count = len(words)
    if not (35 <= word_count <= 50):
        return False
    return True

def generate_concepts():
    dataset = []
    global_kws = set()
    global_last_sentences = set()

    total_concepts = 0
    max_total = 100

    for subtopic in SUBTOPICS:
        if total_concepts >= max_total:
            break

        print(f"Processing: {subtopic}")
        raw_text = get_wikipedia_text(subtopic)
        cleaned_text = clean_text(raw_text)

        doc = nlp(cleaned_text)
        sentences = [sent.text.strip() for sent in doc.sents if len(sent.text.split()) > 5]

        concepts_for_subtopic = 0
        dim_idx = 0

        i = 0
        while i < len(sentences) and concepts_for_subtopic < 20 and total_concepts < max_total:
            chunk = []
            word_count = 0
            j = i
            while j < len(sentences) and word_count < 35:
                words = sentences[j].split()
                if word_count + len(words) <= 50:
                    chunk.append(sentences[j])
                    word_count += len(words)
                    j += 1
                else:
                    break

            if 35 <= word_count <= 50:
                base_response = " ".join(chunk)

                if not is_valid_spanish_content(base_response):
                    i += 1
                    continue

                last_sentence = get_last_sentence(base_response)

                # Check robotic templates
                if last_sentence in global_last_sentences:
                    i += 1
                    continue

                # Extract keywords
                chunk_doc = nlp(base_response)
                valid_words = []
                for token in chunk_doc:
                    if token.pos_ in ["NOUN", "VERB"] and token.is_alpha:
                        w = remove_accents(token.text.lower())
                        if len(w) > 3 and w not in valid_words:
                            valid_words.append(w)

                if len(valid_words) < 4:
                    i += 1
                    continue

                keywords = valid_words[:random.randint(4, 6)]
                keywords_tuple = tuple(sorted(keywords))

                # Check cloned keywords
                if keywords_tuple in global_kws:
                    i += 1
                    continue

                # Semantic dimension matching
                dimension = DIMENSIONS[dim_idx % len(DIMENSIONS)]

                base_response = base_response.strip()
                if not base_response[0].isupper():
                    base_response = base_response.capitalize()
                if not base_response[-1] in ['.', '!', '?']:
                    base_response += '.'

                subtopic_clean = remove_accents(subtopic.lower().replace(" ", "_"))
                kw_str = "_".join(keywords[:2])
                intent_id = f"{subtopic_clean}_{dimension}_{kw_str}"
                intent_id = re.sub(r'\d+', '', intent_id)
                intent_id = re.sub(r'_+', '_', intent_id).strip('_')

                dataset.append({
                    "intent_id": intent_id,
                    "keywords": keywords,
                    "base_response": base_response
                })

                global_kws.add(keywords_tuple)
                global_last_sentences.add(last_sentence)

                concepts_for_subtopic += 1
                total_concepts += 1
                dim_idx += 1
                i = j
            else:
                i += 1

        print(f"  Got {concepts_for_subtopic} concepts. Total so far: {total_concepts}")

    with open("GBX_brain_83B.json", "w", encoding="utf-8") as f:
        json.dump(dataset, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    generate_concepts()
    print("Finished generating dataset.")
