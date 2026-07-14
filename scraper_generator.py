import urllib.request
import urllib.parse
import json
import re
import random
import unicodedata
import spacy
import time

nlp = spacy.load("es_core_news_sm")

topics = [
    "Robótica", "Automatización industrial", "Sensor infrarrojo", "Sensor ultrasónico",
    "Sensor de temperatura", "Termopar", "Termistor", "Actuador", "Servomotor",
    "Motor paso a paso", "Sistema de control", "Controlador PID", "Microcontrolador",
    "Domótica", "Mecatrónica", "Cibernética", "Visión artificial", "Lidar",
    "Radar", "Sonar", "Cinemática", "Grados de libertad (ingeniería)",
    "Neumática", "Hidráulica", "Cobot", "Robot industrial", "Controlador lógico programable",
    "Sensor de proximidad", "Efecto Hall", "Acelerómetro", "Giroscopio",
    "Sistemas embebidos", "Sistema de tiempo real", "Vehículo aéreo no tripulado",
    "Ingeniería de control", "Sistema de lazo cerrado", "Sistema de lazo abierto",
    "Biónica", "Inteligencia artificial", "Redes neuronales artificiales",
    "Procesamiento de señales", "Filtro de Kalman", "Teoría de control",
    "Sensor de presión", "Sensor de fuerza", "Sensor capacitivo", "Sensor inductivo",
    "Motor de corriente continua", "Motor sin escobillas", "Control predictivo",
    "Transductor", "Control automático", "Robótica autónoma", "Brazo robótico",
    "Codificador rotatorio", "Placa de circuito impreso", "Corte por láser",
    "Impresión 3D", "Control numérico por computadora", "Microprocesador",
    "Ingeniería electrónica", "Señal analógica", "Señal digital", "Lógica difusa",
    "Reconocimiento de patrones", "Aprendizaje automático", "Algoritmo genético",
    "Dinámica", "Sistemas dinámicos", "Telecomunicación", "Cinta transportadora",
    "Industria 4.0", "Internet de las cosas", "Autómata programable", "Microbotica",
    "Control óptimo", "Control robusto", "Diagrama de bloques", "Ingeniería de sistemas",
    "Procesador de señales digitales", "Microarquitectura", "Electrónica analógica",
    "Robot", "Robot de servicio", "Robot doméstico", "Robot militar", "Robot médico",
    "Vehículo autónomo", "Ciborg", "Androide", "Ginoide", "Exoesqueleto mecánico",
    "Automatización", "SCADA", "Sistema de control distribuido", "Interfaz hombre-máquina",
    "Sensor", "Sensor de luz", "Fotodiodo", "Fotorresistencia", "Fototransistor",
    "Termómetro", "Pirómetro", "Sensor magnético", "Interruptor de lengüeta",
    "Relé", "Contactor", "Válvula solenoide", "Cilindro neumático", "Cilindro hidráulico",
    "Bomba hidráulica", "Compresor", "Motor eléctrico", "Motor asíncrono", "Motor síncrono",
    "Variador de frecuencia", "Control de movimiento", "Servoaccionamiento",
    "Arduino", "Raspberry Pi", "ESP32", "ESP8266", "Sistema en un chip",
    "Arquitectura ARM", "Arquitectura x86", "Microcontrolador PIC", "AVR",
    "Bluetooth", "Wi-Fi", "Zigbee", "Z-Wave", "LoRa", "Sigfox", "NFC", "RFID",
    "MQTT", "CoAP", "HTTP", "AMQP", "Protocolo de comunicación", "Bus CAN",
    "Modbus", "Profibus", "Profinet", "EtherCAT", "EtherNet/IP", "IO-Link"
]

def clean_text(text):
    text = re.sub(r'\[.*?\]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    text = text.replace('"', "'")
    return text

def remove_accents(input_str):
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    return u"".join([c for c in nfkd_form if not unicodedata.combining(c)])

def count_words(text):
    doc = nlp(text)
    return len([token for token in doc if not token.is_punct and not token.is_space])

results = []
intent_counter = 1
seen_texts = set()

def fetch_wikipedia_content(title):
    url = f"https://es.wikipedia.org/w/api.php?action=query&format=json&prop=extracts&explaintext=1&redirects=1&titles={urllib.parse.quote(title)}"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            pages = data.get("query", {}).get("pages", {})
            for page_id, page_data in pages.items():
                if page_id == "-1":
                    return ""
                return page_data.get("extract", "")
    except Exception as e:
        print(f"Error fetching {title}: {e}")
    return ""

def fetch_search_title(title):
    url = f"https://es.wikipedia.org/w/api.php?action=opensearch&format=json&search={urllib.parse.quote(title)}&limit=1"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            if len(data) > 1 and len(data[1]) > 0:
                return data[1][0]
    except Exception as e:
        pass
    return ""

for topic in topics:
    if len(results) >= 400:
        break
    print(f"Procesando: {topic}")

    content = fetch_wikipedia_content(topic)
    if not content:
        suggested_title = fetch_search_title(topic)
        if suggested_title:
            content = fetch_wikipedia_content(suggested_title)

    if not content:
        print(f"No se encontró contenido para {topic}")
        continue

    content = clean_text(content)

    content = content.split("== Referencias ==")[0]
    content = content.split("== Bibliografía ==")[0]
    content = content.split("== Véase también ==")[0]
    content = content.split("== Enlaces externos ==")[0]
    content = content.split("== Notas ==")[0]

    doc = nlp(content)
    sentences = [sent.text.strip() for sent in doc.sents if len(sent.text.split()) > 4]

    current_response = ""

    for sent in sentences:
        if "==" in sent or len(sent) < 10:
            continue

        test_response = current_response + " " + sent if current_response else sent
        test_response = test_response.strip()

        c_words = count_words(test_response)

        if c_words <= 50:
            current_response = test_response
            if 35 <= c_words <= 50:
                if current_response not in seen_texts:
                    seen_texts.add(current_response)

                    doc_resp = nlp(current_response)
                    valid_words = []
                    for token in doc_resp:
                        if token.pos_ in ["NOUN", "VERB"] and not token.is_stop and token.is_alpha:
                            clean_word = remove_accents(token.text.lower())
                            if len(clean_word) > 2 and clean_word not in valid_words:
                                valid_words.append(clean_word)

                    if len(valid_words) >= 4:
                        num_keywords = min(len(valid_words), random.randint(4, 6))
                        keywords = random.sample(valid_words, num_keywords)

                        clean_topic = remove_accents(topic.lower().replace(" ", "_").replace("(", "").replace(")", "").replace("/", "_"))
                        intent_id = f"{clean_topic}_{intent_counter:03d}"

                        results.append({
                            "intent_id": intent_id,
                            "keywords": keywords,
                            "base_response": current_response
                        })
                        intent_counter += 1

                        if len(results) >= 400:
                            break
                current_response = ""
        else:
            c_words_sent = count_words(sent)
            if c_words_sent <= 50:
                current_response = sent
                if 35 <= c_words_sent <= 50:
                    if current_response not in seen_texts:
                        seen_texts.add(current_response)
                        doc_resp = nlp(current_response)
                        valid_words = []
                        for token in doc_resp:
                            if token.pos_ in ["NOUN", "VERB"] and not token.is_stop and token.is_alpha:
                                clean_word = remove_accents(token.text.lower())
                                if len(clean_word) > 2 and clean_word not in valid_words:
                                    valid_words.append(clean_word)

                        if len(valid_words) >= 4:
                            num_keywords = min(len(valid_words), random.randint(4, 6))
                            keywords = random.sample(valid_words, num_keywords)

                            clean_topic = remove_accents(topic.lower().replace(" ", "_").replace("(", "").replace(")", "").replace("/", "_"))
                            intent_id = f"{clean_topic}_{intent_counter:03d}"

                            results.append({
                                "intent_id": intent_id,
                                "keywords": keywords,
                                "base_response": current_response
                            })
                            intent_counter += 1

                            if len(results) >= 400:
                                break
                    current_response = ""
            else:
                current_response = ""

    time.sleep(0.1)

with open('MM_brain_47.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print(f"Generados {len(results)} conceptos en MM_brain_47.json")
