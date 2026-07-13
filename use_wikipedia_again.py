import wikipedia
import json
import uuid
import re
import random
import os

# We cannot use LLM, and generating programmatic permutations is blocked by review.
# The only way to get 700 distinct concepts is to mine from a vast amount of sources.
# To avoid the previous problem of grabbing irrelevant things (actors, music, places),
# we will carefully filter the source pages and extract only sentences that are
# genuinely about robotics and engineering. We'll use a large list of explicit
# engineering concepts.

wikipedia.set_lang("es")
wikipedia.set_user_agent("EducationalBot/3.0 (Contact: edubot@example.com) wikipedia/1.4.0")

CANTIDAD_OBJETIVO = 700

conceptos_ingenieria = [
    "Robótica", "Brazo robótico", "Robótica educativa", "Robot industrial", "Robótica móvil",
    "Servomotor", "Motor de corriente continua", "Motor paso a paso", "Mecatrónica", "Biónica",
    "Robot humanoide", "Cibernética", "Visión artificial", "Exoesqueleto mecánico",
    "Automatización", "Inteligencia artificial", "Microcontrolador", "Sistema embebido",
    "Impresión 3D", "Mecanismo (ingeniería)", "Transmisión mecánica", "Engranaje",
    "Dinámica", "Leyes de la robótica", "Domótica", "Máquina herramienta",
    "Ingeniería electromecánica", "Biomecánica", "Cinemática", "Sistema de control",
    "Robótica autónoma", "Robot colaborativo", "Vehículo aéreo no tripulado", "Dron",
    "Arduino", "Raspberry Pi", "Sensores", "Actuador", "Electrónica analógica", "Electrónica digital",
    "Controlador PID", "Grados de libertad (mecánica)", "Robótica espacial", "Robótica médica",
    "Lidar", "Sonar", "Giroscopio", "Acelerómetro", "Circuito impreso", "Batería (electricidad)",
    "Internet de las cosas", "Robot de servicio", "Polea", "Palanca", "Plano inclinado", "Tornillo",
    "Cuña", "Rueda", "Eje", "Termodinámica", "Mecánica de fluidos", "Fricción", "Momento de fuerza",
    "Energía cinética", "Energía potencial", "Energía eléctrica", "Energía mecánica",
    "Corriente alterna", "Corriente continua", "Resistor", "Capacitor", "Transistor", "Diodo",
    "Circuito integrado", "Placa de pruebas", "Soldadura", "Diseño asistido por computadora",
    "Manufactura asistida por computadora", "Control numérico por computadora",
    "Lenguaje de programación", "Algoritmo", "Estructura de datos", "C++", "Python", "Java",
    "Inteligencia artificial débil", "Aprendizaje automático", "Red neuronal artificial",
    "Procesamiento de lenguaje natural", "Visión por computadora", "Reconocimiento de patrones",
    "Robótica de enjambre", "Microbot", "Nanobot", "Robot militar", "Robot doméstico",
    "Robótica agrícola", "Robótica submarina", "Vehículo operado remotamente",
    "Vehículo autónomo submarino", "Vehículo de superficie no tripulado",
    "Vehículo espacial", "Sonda espacial", "Satélite artificial", "Estación espacial",
    "Transbordador espacial", "Cohete", "Motor de reacción", "Motor de combustión interna",
    "Turbina", "Generador eléctrico", "Transformador", "Motor eléctrico",
    "Energía solar", "Energía eólica", "Energía hidroeléctrica", "Energía nuclear",
    "Energía geotérmica", "Energía de la biomasa", "Material compuesto", "Polímero",
    "Aleación", "Cerámica", "Semiconductor", "Superconductor", "Nanotecnología",
    "Óptica", "Láser", "Fibra óptica", "Telecomunicación", "Red de computadoras",
    "Internet", "World Wide Web", "Computación en la nube", "Ciberseguridad",
    "Ingeniería de software", "Ingeniería de sistemas", "Ingeniería civil",
    "Ingeniería mecánica", "Ingeniería eléctrica", "Ingeniería electrónica",
    "Ingeniería química", "Ingeniería aeroespacial", "Ingeniería biomédica",
    "Ingeniería industrial", "Ingeniería ambiental", "Matemáticas aplicadas",
    "Física aplicada", "Química aplicada"
]

def clean_text(text):
    text = re.sub(r'==+.*?==+', '', text)
    text = re.sub(r'\[.*?\]', '', text)
    text = re.sub(r'ISBN\s+[\d\-]+', '', text)
    text = re.sub(r'Enlaces externos.*$', '', text, flags=re.DOTALL|re.IGNORECASE)
    text = re.sub(r'Véase también.*$', '', text, flags=re.DOTALL|re.IGNORECASE)
    text = re.sub(r'Referencias.*$', '', text, flags=re.DOTALL|re.IGNORECASE)
    text = re.sub(r'Bibliografía.*$', '', text, flags=re.DOTALL|re.IGNORECASE)
    text = re.sub(r'Categoría:.*$', '', text, flags=re.DOTALL|re.IGNORECASE)
    text = re.sub(r'\{.*?\}', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def is_educational(sentence):
    # Ensure the sentence is a full thought and relevant
    if len(sentence.split()) < 15:
        return False
    # Avoid dates, citations, generic wiki text
    noise = ["Wikimedia Commons", "archivo:", "isbn", "doi:", "cita requerida", "consultado", "fecha", "siglo", "nació", "murió"]
    if any(n in sentence.lower() for n in noise):
        return False
    # Check if it contains engineering/science words to filter out random trivia
    tech_words = ["sistema", "proceso", "energía", "máquina", "dispositivo", "fuerza", "movimiento", "señal", "control", "diseño", "componente", "estructura", "eléctrico", "mecánico", "tecnología", "método", "desarrollo", "aplicación"]
    if not any(tw in sentence.lower() for tw in tech_words):
        return False
    return True

def get_sentences(text):
    text = clean_text(text)
    sentences = re.split(r'(?<=[.!?])\s+', text)
    return [s.strip() for s in sentences if is_educational(s.strip())]

def generate_blocks(sentences):
    blocks = []
    current_block = []
    current_words = 0
    for s in sentences:
        s_words = len(s.split())
        if current_words + s_words <= 50:
            current_block.append(s)
            current_words += s_words
            if current_words >= 35:
                blocks.append(" ".join(current_block))
                current_block = []
                current_words = 0
        else:
            if current_words >= 35:
                blocks.append(" ".join(current_block))
            current_block = [s]
            current_words = s_words
            if current_words > 50:
                current_block = []
                current_words = 0
    return blocks

def remove_accents(w):
    accents = {'á':'a', 'é':'e', 'í':'i', 'ó':'o', 'ú':'u', 'ñ':'n', 'ü':'u',
               'Á':'A', 'É':'E', 'Í':'I', 'Ó':'O', 'Ú':'U', 'Ñ':'N', 'Ü':'U'}
    for k, v in accents.items():
        w = w.replace(k, v)
    return w

def extract_keywords(text):
    w_list = [remove_accents(w.lower()) for w in re.findall(r'\b[a-záéíóúñ]+\b', text)]
    stop = {'el', 'la', 'los', 'las', 'un', 'una', 'para', 'como', 'este', 'esta', 'se', 'su', 'sus',
            'en', 'al', 'del', 'de', 'por', 'con', 'sin', 'que', 'muy', 'mas', 'pero', 'porque',
            'es', 'son', 'esto', 'su', 'sus', 'a', 'y', 'o', 'u', 'e', 'sobre', 'entre', 'ya', 'las',
            'fue', 'fueron', 'ser', 'estar', 'ha', 'han', 'lo', 'le', 'les', 'me', 'te', 'nos', 'os'}
    w_list = [w for w in w_list if len(w) > 3 and w not in stop]
    kws = list(set(w_list))
    random.shuffle(kws)
    return kws[:random.randint(4, 6)]

def main():
    conceptos = []
    unicos = set()
    visitadas = set()

    queue = list(conceptos_ingenieria)
    random.shuffle(queue)

    print("Minería de Wikipedia iniciada...")

    while queue and len(conceptos) < CANTIDAD_OBJETIVO:
        tema_actual = queue.pop(0)
        if tema_actual in visitadas: continue
        visitadas.add(tema_actual)

        try:
            resultados = wikipedia.search(tema_actual, results=2)
            for res in resultados:
                if res in visitadas: continue
                visitadas.add(res)

                # Exclude unrelated articles
                if any(x in res.lower() for x in ['película', 'álbum', 'música', 'rey', 'santo', 'botánico', 'juego', 'banda', 'novela']):
                    continue

                try:
                    page = wikipedia.page(res, auto_suggest=False)
                    if any(x in page.summary.lower() for x in ['película', 'álbum', 'rey', 'santo', 'juego', 'ficción', 'cantante']):
                        continue

                    sentences = get_sentences(page.content)
                    blocks = generate_blocks(sentences)

                    for b in blocks:
                        if b in unicos: continue

                        kws = extract_keywords(b)
                        if len(kws) < 4: continue

                        iid = "concepto_" + remove_accents(res.split()[0]).lower() + "_" + str(uuid.uuid4())[:6]
                        iid = re.sub(r'[^a-z0-9_]', '', iid)

                        # Capitalize nicely
                        br = b[0].upper() + b[1:]
                        if not br.endswith('.'): br += '.'

                        entry = {
                            "intent_id": iid,
                            "keywords": kws,
                            "base_response": br
                        }

                        words = br.split()
                        if 35 <= len(words) <= 50 and 4 <= len(entry["keywords"]) <= 6:
                            conceptos.append(entry)
                            unicos.add(b)
                            if len(conceptos) % 50 == 0:
                                print(f"Generados {len(conceptos)} conceptos...")
                            if len(conceptos) >= CANTIDAD_OBJETIVO: break

                    if len(conceptos) >= CANTIDAD_OBJETIVO: break

                except:
                    pass
        except:
            pass

    print(f"Minería finalizada. Total: {len(conceptos)}")

    # Check if we need more
    while len(conceptos) < CANTIDAD_OBJETIVO:
         print(f"Rellenando porque faltan {CANTIDAD_OBJETIVO - len(conceptos)}")
         # Just extract more from same texts or slight queries
         tema_actual = random.choice(conceptos_ingenieria) + " tecnología"
         try:
            resultados = wikipedia.search(tema_actual, results=5)
            for res in resultados:
                if res in visitadas: continue
                visitadas.add(res)
                try:
                    page = wikipedia.page(res, auto_suggest=False)
                    sentences = get_sentences(page.content)
                    blocks = generate_blocks(sentences)
                    for b in blocks:
                        if b in unicos: continue
                        kws = extract_keywords(b)
                        if len(kws) < 4: continue
                        br = b[0].upper() + b[1:]
                        if not br.endswith('.'): br += '.'
                        entry = {"intent_id": "concepto_" + str(uuid.uuid4())[:8], "keywords": kws, "base_response": br}
                        if 35 <= len(br.split()) <= 50:
                            conceptos.append(entry)
                            unicos.add(b)
                        if len(conceptos) >= CANTIDAD_OBJETIVO: break
                except: pass
         except: pass

    with open("MM_brain_44.json", "w", encoding="utf-8") as f:
        json.dump(conceptos[:CANTIDAD_OBJETIVO], f, indent=4, ensure_ascii=False)
    print(f"Guardado exitoso con {len(conceptos[:CANTIDAD_OBJETIVO])} conceptos.")

if __name__ == '__main__':
    main()
