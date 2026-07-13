import json
import wikipedia
import re
import uuid
from unidecode import unidecode
import random
import nltk
from nltk.tokenize import sent_tokenize
import time
import requests

nltk.download('punkt', quiet=True)
nltk.download('punkt_tab', quiet=True)

wikipedia.set_lang("es")

# Configurar User-Agent personalizado para evitar bloqueos
USER_AGENT = "GeneradorAnatomia/1.0 (https://github.com/usuario/repo; correo@ejemplo.com) wikipedia/1.4.0"
import wikipedia.wikipedia
wikipedia.wikipedia.HEADERS = {'User-Agent': USER_AGENT}

def limpiar_texto(texto):
    # Eliminar referencias tipo [1], [2], etc.
    texto = re.sub(r'\[\d+\]', '', texto)
    # Eliminar dobles espacios y saltos de línea innecesarios
    texto = re.sub(r'\s+', ' ', texto)
    return texto.strip()

def extraer_keywords(texto):
    # En un entorno real se usaría un analizador morfológico más avanzado (como spacy).
    # Como solo buscamos sustantivos/verbos, usamos un enfoque simplificado
    # extrayendo palabras de más de 4 letras que no sean stop words evidentes.
    stopwords_es = {'para', 'como', 'entre', 'sobre', 'desde', 'hasta', 'hacia', 'donde', 'cuando', 'porque', 'aunque', 'mientras', 'luego', 'entonces', 'tambien', 'ademas', 'sino', 'pero', 'este', 'esta', 'estos', 'estas', 'aquel', 'aquella', 'aquellos', 'aquellas', 'cada', 'todo', 'toda', 'todos', 'todas', 'otro', 'otra', 'otros', 'otras', 'algo', 'nada', 'alguien', 'nadie', 'algun', 'alguna', 'algunos', 'algunas', 'ningun', 'ninguna', 'ningunos', 'ningunas', 'aqui', 'alla', 'alli', 'cerca', 'lejos', 'antes', 'despues', 'ahora', 'siempre', 'nunca', 'jamas', 'quizas', 'acaso', 'tiene', 'tienen', 'estan', 'esta', 'este', 'esto', 'estos', 'estas', 'este', 'puede', 'pueden'}

    palabras = [unidecode(p.lower()) for p in re.findall(r'\b[a-záéíóúüñ]{5,}\b', texto.lower())]

    # Filtrar stopwords
    palabras_filtradas = [p for p in palabras if p not in stopwords_es]

    # Eliminar duplicados manteniendo orden
    keywords_unicas = list(dict.fromkeys(palabras_filtradas))

    if len(keywords_unicas) >= 6:
        return random.sample(keywords_unicas, 6)
    elif len(keywords_unicas) >= 4:
        return keywords_unicas
    else:
        # Añadir algunas palabras más cortas si no llegamos a 4
        palabras_cortas = [unidecode(p.lower()) for p in re.findall(r'\b[a-záéíóúüñ]{3,4}\b', texto.lower())]
        palabras_cortas = [p for p in palabras_cortas if p not in stopwords_es and p not in {'las', 'los', 'del', 'que', 'con', 'por', 'una', 'uno', 'son', 'sin', 'sus'}]
        todas = keywords_unicas + list(dict.fromkeys(palabras_cortas))
        if len(todas) > 6:
            return random.sample(todas, 6)
        else:
            return todas[:6]

def procesar_articulo(titulo, limite=100):
    conceptos = []
    try:
        page = wikipedia.page(titulo)
        texto = limpiar_texto(page.content)
        oraciones = sent_tokenize(texto)

        buffer_oraciones = ""
        for oracion in oraciones:
            if "==" in oracion:  # Saltar títulos de sección
                continue

            buffer_oraciones += oracion + " "
            palabras = buffer_oraciones.split()

            if 35 <= len(palabras) <= 50:
                intent_id = f"anat_{uuid.uuid4().hex[:8]}"
                keywords = extraer_keywords(buffer_oraciones)

                # Asegurar longitud de base_response
                base_response = buffer_oraciones.strip()

                # Asegurar que no acabe en coma
                if base_response.endswith(','):
                    base_response = base_response[:-1] + '.'

                conceptos.append({
                    "intent_id": intent_id,
                    "keywords": keywords,
                    "base_response": base_response
                })
                buffer_oraciones = ""

                if len(conceptos) >= limite:
                    break
            elif len(palabras) > 50:
                # Si se pasó, intentamos recortar a un tamaño válido buscando el último punto
                recortado = " ".join(palabras[:48])
                if '.' in recortado:
                    partes = recortado.rsplit('.', 1)
                    base_response = partes[0] + '.'
                    palabras_finales = base_response.split()
                    if 35 <= len(palabras_finales) <= 50:
                        intent_id = f"anat_{uuid.uuid4().hex[:8]}"
                        keywords = extraer_keywords(base_response)
                        conceptos.append({
                            "intent_id": intent_id,
                            "keywords": keywords,
                            "base_response": base_response
                        })
                buffer_oraciones = ""
    except Exception as e:
        print(f"Error procesando '{titulo}': {e}")

    return conceptos

def main():
    temas = [
        "Cráneo", "Hueso frontal", "Hueso parietal", "Hueso temporal", "Hueso occipital",
        "Esfenoides", "Etmoides", "Maxilar", "Mandíbula", "Hueso cigomático",
        "Hueso nasal", "Hueso palatino", "Vómer", "Hioides", "Columna vertebral",
        "Atlas (hueso)", "Axis (hueso)", "Vértebra cervical", "Músculos faciales",
        "Músculo occipitofrontal", "Músculo orbicular de los párpados", "Músculo orbicular de la boca",
        "Músculo buccinador", "Músculo masetero", "Músculo temporal", "Músculo pterigoideo medial",
        "Músculo pterigoideo lateral", "Músculo esternocleidomastoideo", "Músculo escaleno",
        "Glándula tiroides", "Glándula paratiroides", "Faringe", "Laringe",
        "Cartílago tiroides", "Cartílago cricoides", "Tráquea", "Esófago",
        "Arteria carótida común", "Arteria carótida interna", "Arteria carótida externa",
        "Vena yugular interna", "Vena yugular externa", "Nervio craneal", "Nervio trigémino",
        "Nervio facial", "Nervio vago", "Nervio espinal (accesorio)", "Nervio hipogloso",
        "Sistema nervioso central", "Encéfalo", "Cerebro", "Cerebelo", "Tronco del encéfalo",
        "Bulbo raquídeo", "Puente troncoencefálico", "Mesencéfalo", "Líquido cefalorraquídeo",
        "Meninges", "Duramadre", "Aracnoides", "Piamadre", "Médula espinal",
        "Cabeza", "Cuello", "Fascia cervical",
        "Músculo platisma", "Músculos suprahioideos", "Músculos infrahioideos",
        "Músculo digástrico", "Músculo milohioideo", "Músculo estilohioideo",
        "Músculo geniohioideo", "Músculo esternohioideo", "Músculo omohioideo",
        "Músculo esternotiroideo", "Músculo tirohioideo", "Glándulas salivales",
        "Glándula parótida", "Glándula submandibular", "Glándula sublingual",
        "Boca", "Paladar", "Lengua (anatomía)", "Diente", "Encía",
        "Nariz", "Seno paranasal", "Seno frontal", "Seno maxilar",
        "Seno esfenoidal", "Celdillas etmoidales", "Ojo", "Órbita (anatomía)",
        "Oído", "Oído externo", "Oído medio", "Oído interno", "Tímpano",
        "Martillo (anatomía)", "Yunque (anatomía)", "Estribo (anatomía)",

        # Subtemas, conceptos relacionados y aplicaciones para llegar a los 700
        "Sistema nervioso periférico", "Ganglio linfático", "Amígdala palatina",
        "Sistema respiratorio", "Aparato digestivo", "Fonación", "Masticación",
        "Deglución", "Respiración", "Visión", "Audición", "Olfato", "Gusto",
        "Sistema esquelético", "Articulación temporomandibular", "Sistema muscular",
        "Hueso", "Cartílago", "Músculo esquelético", "Tejido nervioso", "Neurona",
        "Sinapsis", "Neurotransmisor", "Arteria", "Vena", "Capilar sanguíneo",
        "Sistema circulatorio", "Sangre", "Plasma sanguíneo", "Glóbulo rojo",
        "Glóbulo blanco", "Plaqueta", "Corazón", "Sistema linfático", "Linfa",
        "Sistema inmunológico", "Anticuerpo", "Antígeno", "Vacuna", "Enfermedad",
        "Salud", "Higiene", "Nutrición", "Dieta", "Vitamina", "Mineral",
        "Proteína", "Carbohidrato", "Lípido", "Agua", "Metabolismo",
        "Célula", "Núcleo celular", "Membrana plasmática", "Citoplasma",
        "Orgánulo", "Mitocondria", "Ribosoma", "Retículo endoplasmático",
        "Aparato de Golgi", "Lisosoma", "Citoesqueleto", "División celular",
        "Mitosis", "Meiosis", "ADN", "ARN", "Gen", "Cromosoma",
        "Tejido epitelial", "Tejido conectivo", "Tejido muscular", "Piel",
        "Epidermis", "Dermis", "Hipodermis", "Pelo", "Uña",
        "Glándula sebácea", "Glándula sudorípara", "Melanina", "Queratina"
    ]

    todos_conceptos = []
    objetivo = 700

    print(f"Iniciando extracción para {objetivo} conceptos...")

    for tema in temas:
        if len(todos_conceptos) >= objetivo:
            break

        print(f"Procesando: {tema}")
        conceptos_tema = procesar_articulo(tema)

        # Añadir asegurando que no nos pasamos
        for concepto in conceptos_tema:
            # Validación estricta final
            palabras = concepto['base_response'].split()
            if 35 <= len(palabras) <= 50 and 4 <= len(concepto['keywords']) <= 6:
                todos_conceptos.append(concepto)

            if len(todos_conceptos) >= objetivo:
                break

        print(f"Conceptos acumulados: {len(todos_conceptos)}")
        time.sleep(2) # Aumentar pausa para evitar límite de tasa

    # Validar y truncar si es necesario
    if len(todos_conceptos) > objetivo:
        todos_conceptos = todos_conceptos[:objetivo]

    print(f"Total de conceptos validados a guardar: {len(todos_conceptos)}")

    with open('MM_brain_35.json', 'w', encoding='utf-8') as f:
        json.dump(todos_conceptos, f, ensure_ascii=False, indent=2)

    print("Archivo MM_brain_35.json generado exitosamente.")

if __name__ == "__main__":
    main()
