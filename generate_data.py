import os
import json
import time
from google import genai
from google.genai import types

# Variables from prompt
API_KEY = "AIzaSyB8bKP9j36keoht6Gxg08c3uO2ZOeYNnkM"
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
client = genai.Client(api_key=API_KEY)

def generate_concepts():
    all_concepts = []

    prompt_template = """
    Eres un especialista en educación científica para adolescentes de 9 a 15 años.
    Tu objetivo es generar EXACTAMENTE UN concepto educativo en JSON sobre el tema "{subtema}" enfocado estrictamente en la dimensión "{dimension}".

    REGLAS ESTRICTAS:
    - Valor educativo máximo, lenguaje adaptado a adolescentes, sin alucinaciones, basado en hechos verificables científicamente (Biología, Psicología, Neurociencia).
    - El ID (intent_id) debe ser único, semántico (relacionado al tema y dimensión), en minúsculas, separado por guiones bajos y con CERO números secuenciales. Ejemplo: "alegria_genuina_dinamica_fisica". NO USAR NÚMEROS.
    - Keywords (keywords): EXACTAMENTE entre 4 y 6 palabras, todo en minúsculas, CERO tildes o acentos, CERO palabras funcionales (sin "el", "la", "de", "con", "y", "en", "para", "los", "las", etc.). SOLO sustantivos y verbos nucleares únicos. Ejemplo: ["alegria", "cerebro", "liberar", "endorfina"].
    - Respuesta base (base_response): EXACTAMENTE entre 35 y 50 palabras. Ortografía perfecta con tildes. Tono instruccional directo. SIN saludos. SIN referencias a fuentes. Texto plano continuo. SIN saltos de línea (\\n).

    Devuelve ÚNICAMENTE un objeto JSON válido con las claves intent_id, keywords y base_response. NINGÚN texto extra.
    Si la dimensión no aplica al tema o no hay información científica real, devuelve un JSON vacío: {{}}
    """

    concept_count = 0
    batch = []

    for subtema in SUBTEMAS:
        if concept_count >= MAX_CONCEPTOS:
            break

        for dimension in DIMENSIONES:
            if concept_count >= MAX_CONCEPTOS:
                break

            print(f"Generando: {subtema} - {dimension}")
            try:
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=prompt_template.format(subtema=subtema, dimension=dimension),
                    config=types.GenerateContentConfig(
                        temperature=0.4,
                        response_mime_type="application/json"
                    )
                )

                content = response.text.strip()
                if not content:
                    continue

                try:
                    data = json.loads(content)
                    if not data or 'intent_id' not in data:
                        continue

                    # Validations and formatting
                    # ID
                    intent_id = data['intent_id'].lower().replace(" ", "_")
                    intent_id = ''.join([i for i in intent_id if not i.isdigit()])
                    data['intent_id'] = intent_id

                    # Keywords
                    if isinstance(data['keywords'], str):
                         data['keywords'] = data['keywords'].split()

                    cleaned_kws = []
                    for kw in data['keywords']:
                        kw = kw.lower()
                        # Remove accents
                        replacements = (("á", "a"), ("é", "e"), ("í", "i"), ("ó", "o"), ("ú", "u"))
                        for a, b in replacements:
                            kw = kw.replace(a, b)
                        # Basic stopword filter
                        stopwords = {"el", "la", "los", "las", "un", "una", "unos", "unas", "de", "del", "a", "ante", "bajo", "cabe", "con", "contra", "desde", "en", "entre", "hacia", "hasta", "para", "por", "segun", "sin", "so", "sobre", "tras", "y", "e", "ni", "que", "o", "u"}
                        if kw not in stopwords and kw.isalpha():
                            cleaned_kws.append(kw)

                    # force 4-6 keywords (if too few add subtema words, if too many slice)
                    if len(cleaned_kws) > 6:
                        cleaned_kws = cleaned_kws[:6]
                    while len(cleaned_kws) < 4:
                         # try to extract more from subtema
                         sub_words = subtema.lower().split()
                         added = False
                         for sw in sub_words:
                             # remove accents
                             for a, b in replacements:
                                 sw = sw.replace(a, b)
                             if sw not in stopwords and sw not in cleaned_kws and sw.isalpha():
                                 cleaned_kws.append(sw)
                                 added = True
                                 if len(cleaned_kws) >=4: break
                         if not added:
                             # fallback
                             fallback = ["concepto", "estudio", "analisis", "proceso", "sistema", "funcion", "desarrollo", "efecto", "reaccion", "estado"]
                             for fb in fallback:
                                 if fb not in cleaned_kws:
                                     cleaned_kws.append(fb)
                                     break

                    data['keywords'] = cleaned_kws

                    # Base Response
                    words = data['base_response'].split()
                    if len(words) < 35:
                        print(f"Skipping: too short ({len(words)} words)")
                        continue
                    if len(words) > 50:
                        data['base_response'] = " ".join(words[:50]) + "."

                    data['base_response'] = data['base_response'].replace("\\n", " ").replace("\n", " ")

                    # ensure intent_id is unique
                    suffix = "_".join(cleaned_kws[:2])
                    if any(item.get('intent_id') == data['intent_id'] for item in all_concepts):
                        data['intent_id'] = f"{data['intent_id']}_{suffix}"

                    all_concepts.append(data)
                    batch.append(data)
                    concept_count += 1
                    print(f"Success! Count: {concept_count}")

                    # Write batch every 30 concepts
                    if len(batch) >= 30:
                        with open(ARCHIVO_DESTINO, 'w', encoding='utf-8') as f:
                            json.dump(all_concepts, f, ensure_ascii=False, indent=4)
                        print(f"Batch saved. Total: {len(all_concepts)}")
                        batch = []

                except json.JSONDecodeError as e:
                    print(f"JSON Error: {e}")
                    continue

            except Exception as e:
                print(f"API Error: {e}")
                time.sleep(5)
                continue

            time.sleep(2) # rate limit prevention

    # Final save
    with open(ARCHIVO_DESTINO, 'w', encoding='utf-8') as f:
        json.dump(all_concepts, f, ensure_ascii=False, indent=4)
    print(f"Finished! Total concepts: {len(all_concepts)}")

if __name__ == "__main__":
    generate_concepts()
