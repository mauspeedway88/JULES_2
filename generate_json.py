import urllib.request
import urllib.parse
import json
import re
import unicodedata

def remove_accents(input_str):
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    return u"".join([c for c in nfkd_form if not unicodedata.combining(c)])

STOPWORDS = {
    "el", "la", "los", "las", "un", "una", "unos", "unas",
    "y", "e", "ni", "o", "u", "pero", "mas", "sino",
    "a", "ante", "bajo", "cabe", "con", "contra", "de", "desde",
    "durante", "en", "entre", "hacia", "hasta", "mediante", "para",
    "por", "segun", "sin", "so", "sobre", "tras", "versus", "via",
    "como", "cuando", "donde", "quien", "que", "cual", "cuales",
    "este", "esta", "estos", "estas", "ese", "esa", "esos", "esas",
    "aquel", "aquella", "aquellos", "aquellas",
    "mi", "tu", "su", "mis", "tus", "sus", "nuestro", "nuestra",
    "vuestro", "vuestra", "su", "sus",
    "al", "del", "lo", "se", "me", "te", "nos", "os",
    "ser", "estar", "es", "son", "fue", "fueron", "ha", "han",
    "tiene", "tienen", "puede", "pueden", "hace", "hacen",
    "mas", "muy", "tambien", "asi", "solo", "ya", "hoy", "ayer",
    "hay", "parte", "forma", "tipo", "tipos", "medio", "vez"
}

TOPICS = [
    "Embrague", "Caja de cambios", "Engranaje", "Tracción (mecánica)", "Eje",
    "Diferencial (mecánica)", "Transmisión mecánica", "Transmisión automática",
    "Transmisión manual", "Par motor", "Relación de transmisión", "Caja de transferencia",
    "Árbol de transmisión", "Palier", "Junta homocinética", "Embrague hidráulico",
    "Convertidor de par", "Transmisión variable continua", "Piñón (mecanismo)",
    "Cremallera (mecanismo)", "Diferencial autoblocante", "Tracción delantera",
    "Tracción trasera", "Tracción en las cuatro ruedas", "Doble embrague",
    "Volante de inercia", "Plato de presión", "Marcha atrás", "Sobremarcha",
    "Engranaje helicoidal", "Engranaje recto", "Engranaje cónico", "Tornillo sin fin",
    "Tren de engranajes", "Engranaje epicicloidal", "Diferencial Torsen", "Junta Cardán",
    "Lubricación", "Fricción", "Cojinete", "Rodamiento", "Sincronizador (automoción)",
    "Tracción integral", "Acoplamiento mecánico", "Embrague centrífugo",
    "Embrague electromagnético", "Transmisión secuencial", "Eje motriz",
    "Eje rígido", "Par cónico", "Reductor de velocidad", "Caja reductora",
    "Transmisión por cadena", "Transmisión por correa", "Vehículo híbrido",
    "Coche eléctrico", "Motor de combustión interna", "Mecánica automotriz",
    "Ingeniería automotriz", "Chasis", "Cinemática", "Dinámica de vehículos",
    "Fuerza motriz", "Potencia (física)", "Torque", "Momento de fuerza",
    "Inercia", "Aceleración", "Velocidad angular", "Frenado", "Transmisión robotizada",
    "Volante bimasa", "Transeje", "Grupo cónico", "Bloqueo del diferencial",
    "Diferencial de deslizamiento limitado", "Control de tracción", "Mantenimiento automotriz",
    "Eficiencia mecánica", "Desgaste", "Fatiga de materiales", "Acero aleado"
]

def fetch_wikipedia_text(title):
    url = f"https://es.wikipedia.org/w/api.php?action=query&prop=extracts&explaintext=1&titles={urllib.parse.quote(title)}&format=json"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            pages = data['query']['pages']
            for page_id in pages:
                return pages[page_id].get('extract', '')
    except Exception as e:
        print(f"Error fetching {title}: {e}")
        return ""

def clean_text(text):
    text = re.sub(r'==.*?==', '', text)
    text = re.sub(r'\[\d+\]', '', text)
    text = text.replace('\n', ' ')
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def split_sentences(text):
    sentences = re.split(r'(?<=[.!?])\s+', text)
    return [s.strip() for s in sentences if len(s.split()) > 3]

def get_keywords(text):
    words = re.findall(r'\b[a-záéíóúüñ]+\b', text.lower())
    clean_words = []
    for w in words:
        w_clean = remove_accents(w)
        if w_clean not in STOPWORDS and len(w_clean) > 3:
            clean_words.append(w_clean)

    word_counts = {}
    for w in clean_words:
        word_counts[w] = word_counts.get(w, 0) + 1

    sorted_words = sorted(word_counts.keys(), key=lambda x: (-word_counts[x], -len(x)))
    return sorted_words[:5]

def generate_responses():
    results = []
    count = 0
    seen_responses = set()

    for topic in TOPICS:
        if count >= 300:
            break
        print(f"Processing topic: {topic}")
        raw_text = fetch_wikipedia_text(topic)
        if not raw_text:
            continue

        clean = clean_text(raw_text)
        sentences = split_sentences(clean)

        current_chunk = []
        current_words = 0

        for sentence in sentences:
            if count >= 300:
                break
            words_in_sentence = len(sentence.split())
            if current_words + words_in_sentence > 50:
                # Check if current chunk is between 35 and 50 words
                if 35 <= current_words <= 50:
                    response_text = " ".join(current_chunk)

                    if response_text not in seen_responses:
                        seen_responses.add(response_text)
                        keywords = get_keywords(response_text)
                        if len(keywords) >= 4:
                            # Adjust keywords length
                            keywords = keywords[:6]

                            topic_id = remove_accents(topic.lower().replace(" ", "_").replace("(", "").replace(")", "").replace("__", "_").strip("_"))
                            intent_id = f"concepto_{topic_id}_{count+1}"

                            # Ensure it doesn't contain invalid characters or mentions of wikipedia
                            if "wikipedia" not in response_text.lower():
                                results.append({
                                    "intent_id": intent_id,
                                    "keywords": keywords,
                                    "base_response": response_text
                                })
                                count += 1

                # Start new chunk
                current_chunk = [sentence]
                current_words = words_in_sentence
            else:
                current_chunk.append(sentence)
                current_words += words_in_sentence

    return results

if __name__ == "__main__":
    concepts = generate_responses()
    print(f"Generated {len(concepts)} concepts.")

    with open("MM_brain_50.json", "w", encoding="utf-8") as f:
        json.dump(concepts, f, ensure_ascii=False, indent=2)
