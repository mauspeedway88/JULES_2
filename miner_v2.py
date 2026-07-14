import urllib.request
import urllib.parse
import json
import re
import unicodedata
import random
import spacy

# Load spanish model
nlp = spacy.load("es_core_news_sm")

def remove_accents(input_str):
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    return u"".join([c for c in nfkd_form if not unicodedata.combining(c)])

def extract_keywords(text):
    doc = nlp(text)
    # Collect only Nouns and Verbs, longer than 3 chars, removing accents, lowercasing.
    valid_words = []
    for token in doc:
        if token.pos_ in ["NOUN", "VERB"] and not token.is_stop and token.is_alpha:
            clean_word = remove_accents(token.text.lower())
            if len(clean_word) > 3:
                valid_words.append(clean_word)

    # frequency
    freq = {}
    for w in valid_words:
        freq[w] = freq.get(w, 0) + 1

    sorted_words = sorted(freq.keys(), key=lambda w: (-freq[w], -len(w)))

    kws = sorted_words[:random.randint(4, 6)]
    if len(kws) < 4:
        for w in valid_words:
            if w not in kws:
                kws.append(w)
            if len(kws) >= 4:
                break
    return kws[:6]

def clean_text(text):
    # Remove Wikipedia sections like References, Bibliography, etc.
    # We truncate the text when we see these headers.
    sections_to_drop = [
        "== Referencias ==", "== Bibliografía ==", "== Véase también ==",
        "== Enlaces externos ==", "== Notas =="
    ]
    for sec in sections_to_drop:
        if sec in text:
            text = text.split(sec)[0]

    # Remove any remaining section headers == Header ==
    text = re.sub(r'==+[^=]+==+', '', text)

    # Remove HTML tags if any
    text = re.sub(r'<[^>]+>', '', text)
    # Remove references [1], [2a], [cita requerida]
    text = re.sub(r'\[\d+[a-z]*\]', '', text)
    text = re.sub(r'\[cita requerida\]', '', text)

    # Remove extra spaces
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def get_wikipedia_extract(title):
    try:
        url = f"https://es.wikipedia.org/w/api.php?action=query&prop=extracts&explaintext=1&titles={urllib.parse.quote(title)}&format=json"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            pages = data['query']['pages']
            for page_id in pages:
                return pages[page_id].get('extract', '')
    except Exception as e:
        print(f"Error fetching {title}: {e}")
        return ""

def process_text(text, prefix, concepts):
    text = clean_text(text)

    # Better sentence splitting using spacy
    doc = nlp(text)
    sentences = [sent.text.strip() for sent in doc.sents if sent.text.strip()]

    buffer = ""
    buffer_word_count = 0

    for sentence in sentences:
        if not sentence: continue

        words = sentence.split()
        word_count = len(words)

        if buffer_word_count + word_count >= 35 and buffer_word_count + word_count <= 50:
            final_text = (buffer + " " + sentence).strip()
            # check limits strictly
            final_wc = len(final_text.split())
            if 35 <= final_wc <= 50:
                kws = extract_keywords(final_text)
                if len(kws) >= 4:
                    intent_id = f"hist_{prefix}_{len(concepts)+1:04d}"
                    concepts.append({
                        "intent_id": intent_id,
                        "keywords": kws,
                        "base_response": final_text
                    })
            buffer = ""
            buffer_word_count = 0
        elif buffer_word_count + word_count > 50:
            # Drop current buffer, start with this sentence if it fits or is small enough
            if 35 <= word_count <= 50:
                kws = extract_keywords(sentence)
                if len(kws) >= 4:
                    intent_id = f"hist_{prefix}_{len(concepts)+1:04d}"
                    concepts.append({
                        "intent_id": intent_id,
                        "keywords": kws,
                        "base_response": sentence
                    })
                buffer = ""
                buffer_word_count = 0
            elif word_count < 35:
                buffer = sentence
                buffer_word_count = word_count
            else:
                buffer = ""
                buffer_word_count = 0
        else:
            if buffer:
                buffer += " " + sentence
            else:
                buffer = sentence
            buffer_word_count += word_count

titles = [
    "Historia de América", "América precolombina", "Descubrimiento de América",
    "Colonización europea de América", "Descolonización de América",
    "Independencia de Hispanoamérica", "Revoluciones hispanoamericanas",
    "Civilización maya", "Imperio azteca", "Imperio incaico", "Conquista de América",
    "Conquista de México", "Conquista del Perú", "Virreinato del Perú",
    "Virreinato de Nueva España", "Virreinato del Río de la Plata",
    "Revolución de Mayo", "Independencia de México", "Independencia de Centroamérica",
    "Independencia de los Estados Unidos", "Guerra de Secesión",
    "Revolución cubana", "Revolución haitiana", "Revolución mexicana",
    "Poblamiento de América", "Cultura olmeca", "Cultura tolteca",
    "Cultura zapoteca", "Cultura mixteca", "Civilización andina",
    "Cultura chavín", "Cultura moche", "Cultura nazca", "Cultura tiahuanaco",
    "Cristóbal Colón", "Hernán Cortés", "Francisco Pizarro", "Simón Bolívar",
    "José de San Martín", "Guerra de Independencia de Cuba", "Mesoamérica",
    "Guerras de independencia hispanoamericanas", "Guerra hispano-estadounidense",
    "Tratado de Tordesillas", "Virreinato de Nueva Granada", "Virreinato de Nueva Andalucía",
    "Capitanía General de Guatemala", "Capitanía General de Chile", "Capitanía General de Venezuela",
    "Guerra del Pacífico", "Guerra de la Triple Alianza", "Guerra del Chaco",
    "Revolución Sandinista", "Revolución de 1952 (Bolivia)", "Guerra Cristera",
    "Periodo posclásico mesoamericano", "Periodo clásico mesoamericano", "Periodo preclásico mesoamericano",
    "Civilización zapoteca", "Imperio purépecha", "Cultura huari", "Imperio chimú",
    "Guerra de los Mil Días", "Guerra civil estadounidense", "Fiebre del oro de California",
    "Trece Colonias", "Nueva Francia", "Guerra franco-india", "Revolución de las Trece Colonias",
    "Cultura maya", "Cultura azteca", "Mitología maya", "Mitología azteca", "Mitología incaica",
    "Historia de Argentina", "Historia de Bolivia", "Historia de Brasil", "Historia de Chile",
    "Historia de Colombia", "Historia de Costa Rica", "Historia de Cuba", "Historia de Ecuador",
    "Historia de El Salvador", "Historia de Guatemala", "Historia de Honduras", "Historia de México",
    "Historia de Nicaragua", "Historia de Panamá", "Historia de Paraguay", "Historia de Perú",
    "Historia de República Dominicana", "Historia de Uruguay", "Historia de Venezuela",
    "Historia de Canadá", "Historia de Estados Unidos", "Reconquista española de América"
]

concepts = []

for title in titles:
    print(f"Buscando: {title}")
    text = get_wikipedia_extract(title)
    if text:
        process_text(text, "".join(random.choices("abcdefghijklmnopqrstuvwxyz", k=3)), concepts)
    if len(concepts) >= 450:
        break

print(f"Conceptos obtenidos: {len(concepts)}")

with open("MM_brain_53.json", "w", encoding="utf-8") as f:
    json.dump(concepts, f, ensure_ascii=False, indent=2)
