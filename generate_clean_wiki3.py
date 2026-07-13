import requests
import json
import re
from unidecode import unidecode
import spacy
import random

nlp = spacy.load("es_core_news_sm")

def clean_text(text):
    text = re.sub(r'\[\d+\]', '', text)
    text = re.sub(r'\[cita requerida\]', '', text)
    text = re.sub(r'\s*\([^)]*\)', '', text)
    text = re.sub(r'(?i)(Archivado desde el original|Wayback Machine|doi:|http://|https://|Consultado el).*', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def sanitize_response(text):
    text = text.strip()
    if not text.endswith(('.', '!', '?')):
        text += '.'
    text = text.replace('"', "'").replace('\n', ' ').replace('\r', ' ')
    text = text.replace('  ', ' ')
    return text

def get_keywords(text):
    doc = nlp(text)
    valid = []
    for token in doc:
        if token.pos_ in ["NOUN", "VERB"] and token.is_alpha and len(token.text) >= 4:
            clean = unidecode(token.text.lower())
            if clean not in valid:
                valid.append(clean)
    valid.sort(key=len, reverse=True)
    if len(valid) < 4: return None
    return valid[:random.randint(4,6)]

def is_pedagogical(text):
    noise = ['= ', ' =', '{', '}', '<', '>', 'isbn', 'http', 'www', 'doi', 'archivo', 'consultado', 'wayback', 'machine', 'referencias', 'vease', 'tambien', 'enlaces', 'externos']
    low = text.lower()
    for nm in noise:
        if nm in low: return False
    # Evitar oraciones demasiado cortas o que parezcan títulos o fragmentos de listas
    if len(text.split()) < 5: return False
    return True

cats = [
    "Hardware", "Tipos_de_computadoras", "Sistemas_operativos", "Software_de_sistema",
    "Componentes_de_computadora", "Microprocesadores", "Periféricos_de_computadora",
    "Lenguajes_de_programación", "Dispositivos_de_almacenamiento", "Bases_de_datos",
    "Inteligencia_artificial", "Redes_informáticas", "Programación", "Seguridad_informática",
    "Internet", "Navegadores_web", "Videojuegos", "Aplicaciones_informáticas",
    "Ingeniería_de_software", "Criptografía", "Estructuras_de_datos", "Algoritmos",
    "Historia_de_la_informática", "Protocolos_de_red", "Telefonía_móvil", "Televisión_digital",
    "Informática", "Teoría_de_la_computación", "Gráficos_por_computadora", "Robótica"
]

all_titles = set()

# Get broader set of titles by querying these categories and their subcategories
for cat in cats:
    try:
        r = requests.get("https://es.wikipedia.org/w/api.php", params={'action': 'query', 'list': 'categorymembers', 'cmtitle': f'Categoría:{cat}', 'cmlimit': 'max', 'format': 'json', 'cmtype': 'page'})
        all_titles.update([m['title'] for m in r.json().get('query', {}).get('categorymembers', []) if m['ns'] == 0])

        # Subcategories
        r2 = requests.get("https://es.wikipedia.org/w/api.php", params={'action': 'query', 'list': 'categorymembers', 'cmtitle': f'Categoría:{cat}', 'cmlimit': 'max', 'format': 'json', 'cmtype': 'subcat'})
        subcats = [m['title'] for m in r2.json().get('query', {}).get('categorymembers', [])]
        for subcat in subcats[:3]: # limit to 3 subcats per cat to save time
             r3 = requests.get("https://es.wikipedia.org/w/api.php", params={'action': 'query', 'list': 'categorymembers', 'cmtitle': subcat, 'cmlimit': 'max', 'format': 'json', 'cmtype': 'page'})
             all_titles.update([m['title'] for m in r3.json().get('query', {}).get('categorymembers', []) if m['ns'] == 0])

        if len(all_titles) > 5000: break
    except: pass

all_titles = list(all_titles)
random.shuffle(all_titles)

print(f"Titles to process: {len(all_titles)}")
concepts = []
seen_texts = set()

# We will read chunks of pages to speed up processing
batch_size = 20
for i in range(0, len(all_titles), batch_size):
    if len(concepts) >= 900: break

    batch = all_titles[i:i+batch_size]
    titles_str = "|".join(batch)

    # explaintext gets plain text, without exintro we get the whole page so we have rich pedagogical material
    params = {'action': 'query', 'prop': 'extracts', 'titles': titles_str, 'format': 'json', 'explaintext': True}

    try:
        r = requests.get("https://es.wikipedia.org/w/api.php", params=params, timeout=10)
        pages = r.json().get('query', {}).get('pages', {})
    except: continue

    for page_id, page_data in pages.items():
        if len(concepts) >= 900: break

        title = page_data.get('title', '')
        text = clean_text(page_data.get('extract', ''))
        if not text: continue

        # Avoid pages that are just disambiguations or too short
        if "puede referirse a" in text.lower() or len(text) < 200: continue

        sentences = re.split(r'(?<=[.!?]) +', text)
        valid_sentences = [s.strip() for s in sentences if len(s.strip()) > 20 and is_pedagogical(s)]

        j = 0
        while j < len(valid_sentences):
            if len(concepts) >= 900: break

            block = []
            words = 0
            used = 0

            for k in range(j, min(j+6, len(valid_sentences))):
                s = valid_sentences[k]
                s_words = len(re.findall(r'\b\w+\b', s))
                if words + s_words <= 50:
                    block.append(s)
                    words += s_words
                    used += 1
                else: break

            # Check length exactly
            if 35 <= words <= 50:
                btext = sanitize_response(" ".join(block))
                if btext not in seen_texts:
                    kws = get_keywords(btext)
                    if kws and len(kws) >= 4:
                        intent_base = unidecode(title.lower())
                        intent_base = re.sub(r'[^a-z0-9_]', '_', intent_base)
                        intent_id = re.sub(r'_+', '_', intent_base).strip('_') + f"_{len(concepts)}"

                        concepts.append({
                            "intent_id": intent_id,
                            "keywords": kws,
                            "base_response": btext
                        })
                        seen_texts.add(btext)
                # Avanzamos exactamente la cantidad de oraciones que usamos para este bloque,
                # así extraemos un concepto distinto de la siguiente parte del artículo sin superposición.
                j += used
            else:
                j += 1

    if len(concepts) % 50 == 0 and len(concepts) > 0:
        print(f"Generated {len(concepts)} unique educational concepts...")

with open('MM_brain_39.json', 'w', encoding='utf-8') as f:
    json.dump(concepts[:900], f, ensure_ascii=False, indent=2)

print(f"Finished extracting {len(concepts[:900])} concepts from distinct wikipedia segments.")
