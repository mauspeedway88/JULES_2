import requests
from bs4 import BeautifulSoup
import json
import re
from unidecode import unidecode
import uuid
import urllib.parse
import time
import spacy

nlp = spacy.load('es_core_news_sm')

def fetch_wikipedia_text(topic):
    encoded_topic = urllib.parse.quote(topic)
    url = f"https://es.wikipedia.org/wiki/{encoded_topic}"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    try:
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            return ""

        soup = BeautifulSoup(response.text, 'html.parser')
        paragraphs = soup.find_all('p')
        text = " ".join([p.get_text() for p in paragraphs if p.get_text().strip()])
        return text
    except Exception as e:
        print(f"Error fetching {topic}: {e}")
        return ""

def clean_text(text):
    # Remove citations like [1], [cita requerida], [nota 1], etc.
    text = re.sub(r'\[.*?\]', '', text)
    # Remove parenthesis that might contain citations or extra noise if they are long
    # text = re.sub(r'\(.*?\)', '', text) # Maybe too aggressive, let's just keep words
    # Remove extra spaces
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def split_into_responses(text, min_words=35, max_words=50):
    doc = nlp(text)
    sentences = [sent.text.strip() for sent in doc.sents if sent.text.strip()]

    responses = []
    current_chunk = []
    current_len = 0

    # Words to avoid starting a new independent concept with
    bad_starters = {'él', 'ella', 'ellos', 'ellas', 'esto', 'eso', 'aquello', 'estos', 'estas',
                    'además', 'también', 'asimismo', 'sin embargo', 'por lo tanto', 'por consiguiente',
                    'luego', 'entonces', 'este', 'esta', 'estos', 'estas', 'su', 'sus'}

    for sent in sentences:
        words = sent.split()
        if not words:
            continue

        first_word_lower = words[0].lower().strip(',.')

        if current_len == 0 and first_word_lower in bad_starters:
            # Skip this sentence entirely as it cannot start a valid pedagogical chunk
            continue

        if current_len + len(words) <= max_words:
            current_chunk.append(sent)
            current_len += len(words)
        else:
            if current_len >= min_words:
                responses.append(" ".join(current_chunk))

            # Try to start a new chunk with the current sentence
            if first_word_lower not in bad_starters and len(words) <= max_words:
                current_chunk = [sent]
                current_len = len(words)
            else:
                current_chunk = []
                current_len = 0

    if min_words <= current_len <= max_words:
        responses.append(" ".join(current_chunk))

    return responses

def extract_keywords(text, num_keywords=6):
    doc = nlp(text)
    invalid_lemmas = {'ser', 'estar', 'haber', 'tener', 'hacer', 'ir', 'poder', 'deber', 'querer', 'decir', 'ver', 'dar', 'saber'}
    keywords = []

    for token in doc:
        # Strictly Noun or Verb
        if token.pos_ in ['NOUN', 'VERB'] and not token.is_stop and token.is_alpha:
            lemma = token.lemma_.lower()
            if lemma not in invalid_lemmas:
                word = unidecode(lemma)
                if len(word) > 2:
                    keywords.append(word)

    freq = {}
    for w in keywords:
        freq[w] = freq.get(w, 0) + 1

    # Sort by frequency and then length
    sorted_words = sorted(freq.keys(), key=lambda k: (-freq[k], -len(k)))

    return sorted_words[:num_keywords]

def generate_concepts(topics, target_count=700):
    all_concepts = []
    seen_responses = set()

    for topic in topics:
        if len(all_concepts) >= target_count:
            break

        print(f"Buscando tema: {topic}")
        raw_text = fetch_wikipedia_text(topic)
        if not raw_text:
            continue

        cleaned_text = clean_text(raw_text)
        responses = split_into_responses(cleaned_text)

        added = 0
        for base_response in responses:
            if len(all_concepts) >= target_count:
                break

            word_count = len(base_response.split())
            if not (35 <= word_count <= 50):
                continue

            if base_response in seen_responses:
                continue

            seen_responses.add(base_response)

            keywords = extract_keywords(base_response)
            if len(keywords) < 4:
                continue # Require at least 4 valid NOUN/VERB keywords

            keywords = keywords[:6]

            intent_id = f"anatomia_{uuid.uuid4().hex[:8]}"

            concept = {
                "intent_id": intent_id,
                "keywords": keywords,
                "base_response": base_response
            }
            all_concepts.append(concept)
            added += 1

        print(f"  - Añadidos {added} conceptos de {topic}")
        time.sleep(0.5)

    return all_concepts

if __name__ == "__main__":
    topics = [
        "Tronco_(anatomía)", "Tórax", "Abdomen", "Columna_vertebral", "Costilla", "Pelvis", "Diafragma_(anatomía)",
        "Esternón", "Clavícula", "Escápula", "Músculos_intercostales", "Músculo_pectoral_mayor",
        "Músculo_recto_del_abdomen", "Músculo_oblicuo_externo_del_abdomen", "Músculo_transverso_del_abdomen",
        "Músculo_dorsal_ancho", "Músculo_trapecio", "Vértebra", "Médula_espinal", "Disco_intervertebral",
        "Costillas_verdaderas", "Costillas_falsas", "Costillas_flotantes", "Hueso_coxal", "Sacro", "Cóccix",
        "Cavidad_torácica", "Cavidad_abdominal", "Cavidad_pélvica", "Peritoneo", "Pleura", "Mediastino",
        "Corazón", "Pulmón", "Hígado", "Estómago", "Intestino_delgado", "Intestino_grueso", "Bazo", "Páncreas",
        "Riñón", "Vejiga_urinaria", "Arteria_aorta", "Vena_cava_inferior", "Vena_cava_superior",
        "Sistema_respiratorio", "Sistema_digestivo", "Sistema_cardiovascular", "Sistema_urinario",
        "Anatomía_humana", "Esqueleto_humano", "Aparato_locomotor", "Osteología", "Miología",
        "Músculo_serrato_anterior", "Músculo_cuadrado_lumbar", "Músculo_iliopsoas",
        "Caja_torácica", "Articulación_costovertebral", "Articulación_sacroilíaca", "Sínfisis_púbica",
        "Ligamento_inguinal", "Línea_alba_(anatomía)", "Ombligo", "Conducto_inguinal", "Retroperitoneo",
        "Glándula_suprarrenal", "Duodeno", "Yeyuno", "Íleon", "Ciego_(anatomía)", "Apéndice_vermiforme",
        "Colon_ascendente", "Colon_transverso", "Colon_descendente", "Colon_sigmoideo", "Recto", "Ano",
        "Aparato_reproductor", "Fisiología", "Tejido_muscular", "Aparato_circulatorio", "Aorta_abdominal",
        "Arteria_ilíaca_común", "Cerebro", "Nervio_vago", "Músculo_liso", "Metabolismo",
        "Sistema_nervioso", "Hormona", "Esternocleidomastoideo", "Médula_ósea", "Capilar_sanguíneo",
        "Célula_sanguínea", "Glóbulo_rojo", "Leucocito", "Plaqueta", "Sangre",
        "Sistema_inmunitario", "Linfocito", "Antígeno", "Anticuerpo", "Sistema_linfático",
        "Glándula_tiroides", "Glándula_paratiroides", "Glándula_pituitaria", "Hipófisis", "Hipotálamo",
        "Cerebelo", "Tronco_del_encéfalo", "Sistema_nervioso_periférico", "Sistema_nervioso_autónomo",
        "Sistema_nervioso_simpático", "Sistema_nervioso_parasimpático", "Ojo_humano", "Oído",
        "Piel_humana", "Epidermis", "Dermis", "Folículo_piloso", "Glándula_sudorípara", "Uña",
        "Cráneo", "Mandíbula", "Húmero", "Cúbito", "Radio_(hueso)", "Carpo", "Metacarpo", "Falange",
        "Fémur", "Tibia", "Peroné", "Rótula", "Tarso", "Metatarso", "Falange_del_pie",
        "Articulación_(anatomía)", "Sinovial", "Cartílago", "Tendón", "Ligamento",
        "Sistema_endocrino", "Órgano_(biología)", "Tejido_(biología)", "Célula", "Epitelio",
        "Glándula_salival", "Faringe", "Esófago", "Vesícula_biliar", "Válvula_cardíaca",
        "Bronquio", "Bronquiolo", "Alvéolo", "Uréter", "Uretra", "Ovario", "Útero", "Trompas_de_Falopio",
        "Vagina", "Testículo", "Próstata", "Vesícula_seminal", "Pene",
        "Respiración", "Digestión", "Circulación_sanguínea", "Excreción", "Reproducción_humana",
        "Biología_humana", "Médico", "Cirugía", "Gastroenterología", "Neurología", "Cardiología"
    ]

    print("Iniciando extracción de conceptos...")
    concepts = generate_concepts(topics, target_count=700)
    print(f"Conceptos generados tras primer ciclo: {len(concepts)}")

    if len(concepts) < 700:
        print("Ampliando búsqueda para llegar a 700...")
        def search_wikipedia(query):
            url = f"https://es.wikipedia.org/w/api.php?action=query&list=search&srsearch={urllib.parse.quote(query)}&utf8=&format=json&srlimit=50"
            try:
                response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
                data = response.json()
                return [item['title'] for item in data['query']['search']]
            except Exception as e:
                print(f"Error search: {e}")
                return []

        extra_queries = ["órgano anatomía", "hueso cuerpo humano", "músculo humano", "enfermedad sistema digestivo",
                         "arterias cuerpo humano", "venas cuerpo humano", "nervios anatomía", "tejidos histología",
                         "articulaciones humanas", "glándulas del cuerpo humano", "fisiología humana",
                         "aparato reproductor", "sistema esquelético", "biología humana", "salud humana",
                         "medicina anatomía", "neuroanatomía", "cardioanatomía", "osteología", "miología", "esplacnología"]

        for query in extra_queries:
            if len(concepts) >= 700:
                break
            print(f"Buscando artículos extra para: {query}")
            new_topics = search_wikipedia(query)
            for new_topic in new_topics:
                if new_topic not in topics:
                    topics.append(new_topic)

        print("Continuando generación con temas extra...")
        extra_concepts = generate_concepts(topics[len(topics)-len(extra_queries)*50:], target_count=700 - len(concepts))
        concepts.extend(extra_concepts)

    print(f"Conceptos totales finales: {len(concepts)}")

    with open('MM_brain_36.json', 'w', encoding='utf-8') as f:
        json.dump(concepts[:700], f, ensure_ascii=False, indent=2)

    print("Archivo MM_brain_36.json guardado con éxito.")
