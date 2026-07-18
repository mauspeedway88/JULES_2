import json
import re
import os
import time
import unidecode
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import urllib.request
import urllib.parse
from bs4 import BeautifulSoup
import g4f

SUBTOPICS = [
    "camuflaje protector de especies",
    "mimetismo engañoso de apariencia",
    "ectotermos de sangre fría",
    "endotermos de sangre caliente",
    "animales vivíparos de vientre",
    "animales ovovivíparos de huevos internos",
    "respiración cutánea de ranas",
    "respiración traqueal de insectos",
    "exoesqueleto de quitina protector",
    "sistema ambulacral de estrellas",
    "línea lateral de peces",
    "vejiga natatoria de flotación",
    "glándulas mamarias de alimentación",
    "dimorfismo sexual de formas",
    "feromonas de comunicación química",
    "cortejo reproductivo de parejas",
    "migración estacional de aves",
    "estivación de letargo cálido",
    "nematodos gusanos cilíndricos lisos",
    "platelmintos gusanos planos parásitos",
    "apéndices articulados de artrópodos",
    "bioluminiscencia animal de luz",
    "placenta nutritiva de fetos"
]

DIMENSIONS = [
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

DEST_FILE = "GBX_brain_33B.json"

def get_wiki_summary(query):
    try:
        url = "https://es.wikipedia.org/wiki/Especial:Buscar?search=" + urllib.parse.quote(query.split()[0] + " " + query.split()[1])
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        html = urllib.request.urlopen(req).read()
        soup = BeautifulSoup(html, 'html.parser')
        p_tags = soup.find_all('p')
        content = ""
        for p in p_tags:
            text = p.get_text().strip()
            if len(text) > 50:
                content += text + " "
                if len(content) > 500:
                    break
        return content
    except:
        return ""

def validate_concept(data):
    if not isinstance(data, dict): return False, "Not a dictionary"

    intent_id = data.get("intent_id", "")
    keywords = data.get("keywords", [])
    base_response = data.get("base_response", "")

    if not intent_id or not re.match(r'^[a-z_]+$', intent_id):
        return False, "intent_id invalid"
    if not (4 <= len(keywords) <= 6):
        return False, "keywords length invalid"
    for kw in keywords:
        if not re.match(r'^[a-z\s]+$', kw) or re.search(r'[áéíóú]', kw) or kw in ['el', 'la', 'los', 'las', 'un', 'una', 'de', 'en', 'con', 'por', 'para']:
            return False, f"keyword {kw} invalid"

    words = base_response.strip().split()
    if not (35 <= len(words) <= 50):
        return False, f"base_response length {len(words)} not in 35-50"
    if '\n' in base_response or '"' in base_response:
        return False, "base_response has newline or quotes"
    if not re.search(r'[áéíóúÁÉÍÓÚ]', base_response):
        return False, "base_response missing tildes"
    return True, "Valid"

def main():
    dataset = []
    existing_ids = set()
    existing_texts = []
    vectorizer = TfidfVectorizer()

    if os.path.exists(DEST_FILE):
        with open(DEST_FILE, 'r', encoding='utf-8') as f:
            dataset = json.load(f)
            for d in dataset:
                existing_ids.add(d['intent_id'])
                existing_texts.append(d['base_response'])

    for subtopic in SUBTOPICS:
        context = get_wiki_summary(subtopic)
        for dimension in DIMENSIONS:
            base_id = unidecode.unidecode(f"{subtopic}_{dimension}").lower().replace(' ', '_')
            base_id = re.sub(r'[^a-z_]', '', base_id)[:40]
            if base_id in existing_ids: continue

            prompt = f"""
            Basado en esta información biológica: "{context[:400]}"
            Genera un concepto educativo (para 9-15 años) aportando valor científico real.
            Tema biológico: {subtopic}
            Dimensión: {dimension}

            Si no hay información científica real, responde exactamente: OMITE

            Genera SÓLO un JSON válido:
            {{
                "intent_id": "{base_id}",
                "keywords": ["sustantivo", "verbo", "celula", "funcion", "organo"],
                "base_response": "Texto educativo directo y científico de exactamente 35 a 50 palabras."
            }}
            Reglas: keywords (4-6 palabras, TODO minúscula sin tildes ni acentos). base_response (35-50 palabras, CON TILDES, ortografía perfecta, sin comillas, sin saltos de línea).
            """

            for _ in range(3):
                try:
                    response = g4f.ChatCompletion.create(model=g4f.models.default, messages=[{"role": "user", "content": prompt}])
                    if "OMITE" in response.upper()[:20]:
                        break
                    json_str = re.sub(r'```json\n|\n```|```', '', response).strip()
                    data = json.loads(json_str)

                    is_valid, msg = validate_concept(data)
                    if is_valid:
                        if existing_texts:
                            sims = cosine_similarity(vectorizer.fit_transform(existing_texts + [data['base_response']])[-1:], vectorizer.fit_transform(existing_texts + [data['base_response']])[:-1])
                            if sims[0].max() > 0.8: continue
                        dataset.append(data)
                        existing_ids.add(data['intent_id'])
                        existing_texts.append(data['base_response'])
                        with open(DEST_FILE, 'w', encoding='utf-8') as f:
                            json.dump(dataset, f, ensure_ascii=False, indent=4)
                        print(f"Added {base_id} (Total: {len(dataset)})")
                        break
                except Exception as e:
                    pass
            if len(dataset) >= 180: break
        if len(dataset) >= 180: break

main()
