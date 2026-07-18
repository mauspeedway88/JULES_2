import json
import os
import re
import time
import asyncio
import unicodedata
from string import digits

# Inicializar asyncio anidado
import nest_asyncio
nest_asyncio.apply()

from g4f.client import Client

SUBTEMAS = [
    "arquitectura de bits del procesador",
    "disipador térmico del microprocesador",
    "zócalo de conexión principal",
    "ranuras de expansión PCIe",
    "interfaz firmware del BIOS",
    "caché interna del procesador",
    "latencia de respuesta informática",
    "ancho de banda de buses",
    "formato de placa microATX",
    "pines de conexión electrónica",
    "sensores de temperatura internos",
    "gestión de energía del sistema",
    "controladores de dispositivos físicos",
    "particiones del disco local",
    "sistema de archivos informáticos",
    "desfragmentación de unidades magnéticas",
    "conectores de audio analógico",
    "puerto ethernet de red",
    "adaptador inalámbrico de computadora",
    "lector de tarjetas multimedia",
    "botón de reinicio del chasis",
    "panel frontal de conexiones",
    "luces LED de actividad",
    "formato de almacenamiento emedós",
    "memoria ROM de solo lectura",
    "unidad óptica de lectura",
    "pasta térmica de refrigeración",
    "actualización física de componentes"
]

DIMENSIONES = [
    "Definición anatómica o estructural.",
    "Dinámica y funcionamiento físico.",
    "Propiedades químicas o materiales.",
    "Errores, fallas y patologías comunes.",
    "Historia, origen y evolución.",
    "Contexto y entorno ecológico.",
    "Aplicaciones prácticas en la vida real.",
    "Importancia e impacto social.",
    "Ventajas y desventajas comparativas.",
    "Riesgos y medidas de seguridad.",
    "Clasificación taxonómica.",
    "Cálculos y fórmulas asociadas.",
    "Mitos y concepciones erróneas.",
    "Relación simbiótica con otros sistemas.",
    "Transformación y ciclos energéticos.",
    "Experimentos y demostraciones escolares.",
    "Consecuencias a largo plazo.",
    "Impacto ambiental.",
    "Mantenimiento y prevención.",
    "Proyecciones futuras y tecnología."
]

ARCHIVO_DESTINO = "GBX_brain_39B.json"

client = Client()

def quitar_acentos(texto):
    texto = unicodedata.normalize('NFD', texto)
    texto = texto.encode('ascii', 'ignore').decode('utf-8')
    return str(texto)

def generar_prompt(subtema, dimension):
    return f"""
Escribe en formato JSON estrictamente válido, sin markdown, sobre el siguiente subtema y dimensión.
Nivel educativo: Tercer Ciclo (9 a 15 años).

Subtema: "{subtema}"
Dimensión: "{dimension}"

Estructura obligatoria JSON:
{{
  "intent_id": "cadena_texto",
  "keywords": ["palabra1", "palabra2", "palabra3", "palabra4"],
  "base_response": "texto descriptivo"
}}

Reglas estrictas de los campos:
1. "intent_id": ID único, semántico, en minúsculas, palabras separadas por guiones bajos. ESTRICTAMENTE PROHIBIDO INCLUIR NÚMEROS O SUFIJOS NUMÉRICOS.
2. "keywords": Exactamente entre 4 y 6 palabras. Solo sustantivos y verbos nucleares (sin artículos ni preposiciones). Todo en minúsculas. ESTRICTAMENTE PROHIBIDO incluir tildes o acentos en este array.
3. "base_response": Exactamente entre 35 y 50 palabras. Tono instruccional directo, sin saludos ni despedidas, sin comillas dobles internas y sin saltos de línea. ORTOGRAFÍA INMACULADA, DEBES INCLUIR LAS TILDES en español.

Genera solo el JSON, nada más. Si no aplica, devuelve un JSON con intent_id: "omite".
"""

def procesar_respuesta(texto_respuesta):
    try:
        # Extraer JSON de la respuesta
        inicio = texto_respuesta.find('{')
        fin = texto_respuesta.rfind('}') + 1
        if inicio == -1 or fin == 0:
            return None

        json_str = texto_respuesta[inicio:fin]
        datos = json.loads(json_str)

        if "omite" in datos.get("intent_id", "").lower():
            return "OMITE"

        # Validar intent_id
        intent_id = datos.get("intent_id", "")
        intent_id = re.sub(r'\d+', '', intent_id) # Eliminar números
        intent_id = intent_id.strip('_')

        # Validar keywords
        keywords = datos.get("keywords", [])
        if not isinstance(keywords, list):
            return None
        keywords = [quitar_acentos(str(k).lower().strip()) for k in keywords]
        keywords = [k for k in keywords if len(k) > 2 and k not in ['el', 'la', 'los', 'las', 'un', 'una', 'unos', 'unas', 'de', 'del', 'a', 'en', 'con', 'por', 'para', 'y', 'o']]
        if len(keywords) < 4:
            return None
        if len(keywords) > 6:
            keywords = keywords[:6]

        # Validar base_response
        base_response = datos.get("base_response", "").strip()
        base_response = base_response.replace('\n', ' ').replace('"', "'")
        conteo_palabras = len(base_response.split())
        if not (35 <= conteo_palabras <= 50):
            return None

        datos["intent_id"] = intent_id
        datos["keywords"] = keywords
        datos["base_response"] = base_response

        return datos
    except Exception as e:
        return None

async def generar_concepto(subtema, dimension):
    prompt = generar_prompt(subtema, dimension)
    for _ in range(3):
        try:
            respuesta = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
            )
            texto_respuesta = respuesta.choices[0].message.content
            parseado = procesar_respuesta(texto_respuesta)
            if parseado:
                return parseado
        except Exception as e:
            time.sleep(2)
    return None

def guardar_datos(datos):
    if os.path.exists(ARCHIVO_DESTINO):
        with open(ARCHIVO_DESTINO, 'r', encoding='utf-8') as f:
            existentes = json.load(f)
    else:
        existentes = []

    existentes.append(datos)

    with open(ARCHIVO_DESTINO, 'w', encoding='utf-8') as f:
        json.dump(existentes, f, ensure_ascii=False, indent=2)

async def principal():
    if not os.path.exists(ARCHIVO_DESTINO):
        with open(ARCHIVO_DESTINO, 'w', encoding='utf-8') as f:
            json.dump([], f)

    conteo = 0
    # Aleatorizar orden para asegurar variedad si falla
    for subtema in SUBTEMAS:
        for dimension in DIMENSIONES:
            print(f"Generando para: {subtema} - {dimension}")
            datos = await generar_concepto(subtema, dimension)
            if datos and datos != "OMITE":
                guardar_datos(datos)
                conteo += 1
                print(f"¡Éxito! Conceptos totales: {conteo}")
                # Commit progresivo cada 30 conceptos
                if conteo % 30 == 0:
                    os.system(f"git add {ARCHIVO_DESTINO}")
                    os.system(f"git commit -m 'Commit incremental: {conteo} conceptos'")
            elif datos == "OMITE":
                print("Omitido (no aplicable).")
            else:
                print("Fallido o formato inválido.")

            # Retraso simple para evitar problemas de límite de solicitudes
            time.sleep(1)

            if False:
                print("Conteo objetivo alcanzado.")
                return

if __name__ == "__main__":
    asyncio.run(principal())
