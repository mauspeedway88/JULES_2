import json
import re
import asyncio
from g4f.client import AsyncClient

# Matriz Ontológica de Expansión Multidimensional
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

SUBTEMAS = [
    "Géneros de obras literarias",
    "Novela narrativa de literatura",
    "Poesía lírica de literatura",
    "Cuento breve de literatura",
    "Figuras literarias de retórica",
    "Autores clásicos de literatura",
    "Fábulas morales de literatura",
    "Mitos antiguos de literatura",
    "Leyendas populares de literatura",
    "Epopeyas heroicas de literatura",
    "Ensayos literarios de reflexión",
    "Dramaturgia de teatro literario",
    "Tragedias griegas de literatura",
    "Comedias clásicas de literatura",
    "Metáforas de textos literarios",
    "Símiles de poesía literaria",
    "Hipérboles de lenguaje literario",
    "Personificaciones en cuentos literarios",
    "Anáforas de rima literaria",
    "Onomatopeyas de textos literarios",
    "Aliteraciones de sonido literario",
    "Versos libres de literatura",
    "Estrofas de poemas literarios",
    "Métrica de composición literaria"
]

MAX_CONCEPTOS = 200
ARCHIVO_DESTINO = "GBX_brain_64A.json"

async def generar_concepto(cliente, semaforo, subtema, dimension):
    async with semaforo:
        prompt = f"""
Genera un concepto educativo para el subtema '{subtema}' abordando la dimensión: '{dimension}'.
El concepto debe ser dirigido a estudiantes de Tercer Ciclo (9 a 15 años).
Aporta valor científico o académico real y diferenciado.
Prohibido usar frases de cierre repetitivas o alucinar datos.

Responde ÚNICAMENTE en el siguiente formato JSON estricto:
{{
    "intent_id": "identificador_unico_y_semantico",
    "keywords": "palabra1 palabra2 palabra3 palabra4",
    "base_response": "Texto educativo directo sin saludos, ortografía perfecta."
}}

Reglas del JSON:
1. 'intent_id': Solo minúsculas, guiones bajos, único (usa palabras del subtema y dimensión), CERO números.
2. 'keywords': EXACTAMENTE de 4 a 6 términos, minúsculas, SIN NINGUNA TILDE, sin artículos (el, la, los) ni preposiciones (de, en, con), solo sustantivos y verbos nucleares únicos separados por espacios.
3. 'base_response': EXACTAMENTE de 35 a 50 palabras, ortografía inmaculada, incluye tildes, formato texto plano SIN saltos de línea internos ni dobles comillas sin escapar, directo a la instrucción. No agregues fuentes ni referencias (ni [1], etc).
"""

        try:
            response = await cliente.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=250
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error generando {subtema} - {dimension}: {e}")
            return None

def procesar_respuesta(respuesta_raw, base_id):
    if not respuesta_raw:
        return None

    # Extraer JSON de la respuesta (por si hay texto alrededor o markdown)
    match = re.search(r'\{[^{}]+\}', respuesta_raw)
    if not match:
        return None

    try:
        obj = json.loads(match.group(0))

        # Validaciones y sanitización
        if "intent_id" not in obj or "keywords" not in obj or "base_response" not in obj:
            return None

        # Sanitizar intent_id: asegurar minúsculas, guiones bajos, sin números
        intent_id = re.sub(r'[0-9]', '', obj["intent_id"].lower())
        intent_id = re.sub(r'[^a-z_]', '_', intent_id)
        # Si quedó vacío o genérico, generar uno seguro
        if len(intent_id) < 5 or intent_id == 'intent_id':
             intent_id = base_id

        # Sanitizar keywords: minúsculas, sin tildes, 4 a 6 palabras
        keywords_str = obj["keywords"].lower()
        # Quitar tildes
        replacements = {'á':'a', 'é':'e', 'í':'i', 'ó':'o', 'ú':'u', 'ü':'u', 'ñ':'n'}
        for k, v in replacements.items():
            keywords_str = keywords_str.replace(k, v)

        palabras = re.findall(r'\b[a-z]+\b', keywords_str)
        # Filtrar stop words comunes
        stop_words = {'el', 'la', 'los', 'las', 'un', 'una', 'unos', 'unas', 'de', 'del', 'a', 'al', 'en', 'por', 'con', 'para', 'y', 'o', 'su', 'sus'}
        palabras_filtradas = [p for p in palabras if p not in stop_words]

        if len(palabras_filtradas) < 4:
            return None # Rechazado

        keywords_finales = " ".join(palabras_filtradas[:6])

        # Sanitizar base_response
        base_resp = obj["base_response"]
        base_resp = base_resp.replace('\n', ' ').replace('"', "'")
        base_resp = re.sub(r'\[\[.*?\]\]\(.*?\)', '', base_resp) # Quitar citas raras
        base_resp = re.sub(r'\[\d+\]', '', base_resp) # Quitar citas tipo [1]

        num_palabras_resp = len(re.findall(r'\b\w+\b', base_resp))
        if num_palabras_resp < 35 or num_palabras_resp > 50:
             return None # Rechazado

        # Construir objeto limpio
        return {
            "intent_id": intent_id,
            "keywords": keywords_finales,
            "base_response": base_resp.strip()
        }

    except json.JSONDecodeError:
        return None

async def main():
    cliente = AsyncClient()
    semaforo = asyncio.Semaphore(3) # Límite de concurrencia seguro

    resultados = []
    ids_generados = set()

    # Generar tareas
    print("Iniciando generación de conceptos...")

    for subtema in SUBTEMAS:
        if len(resultados) >= MAX_CONCEPTOS:
            break

        print(f"Procesando subtema: {subtema}")
        tareas = []
        for dimension in DIMENSIONES:
             tareas.append(generar_concepto(cliente, semaforo, subtema, dimension))

        # Ejecutar lote del subtema
        respuestas_brutas = await asyncio.gather(*tareas)

        for i, respuesta in enumerate(respuestas_brutas):
            if len(resultados) >= MAX_CONCEPTOS:
                break

            dimension = DIMENSIONES[i]
            # Generar base_id único sin números
            # Tomar primeras 2 palabras del subtema y 2 de la dimensión
            sub_p = re.findall(r'\b[a-z]+\b', subtema.lower())
            dim_p = re.findall(r'\b[a-z]+\b', dimension.lower())
            base_id = "_".join(sub_p[:2] + dim_p[:2])

            concepto = procesar_respuesta(respuesta, base_id)
            if concepto:
                # Evitar IDs duplicados
                if concepto["intent_id"] in ids_generados:
                    # Alternativa semántica
                    concepto["intent_id"] = f"{base_id}_variacion"
                    if concepto["intent_id"] in ids_generados:
                        concepto["intent_id"] = f"{base_id}_alternativa"

                if concepto["intent_id"] not in ids_generados:
                    ids_generados.add(concepto["intent_id"])
                    resultados.append(concepto)
                    print(f"  + Concepto añadido. Total: {len(resultados)}/{MAX_CONCEPTOS}")

    # Guardar archivo destino final
    with open(ARCHIVO_DESTINO, 'w', encoding='utf-8') as f:
        json.dump(resultados, f, ensure_ascii=False, indent=4)

    print(f"Proceso finalizado. {len(resultados)} conceptos guardados en {ARCHIVO_DESTINO}")

if __name__ == "__main__":
    asyncio.run(main())
