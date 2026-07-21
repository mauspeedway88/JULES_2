import asyncio
import json
import logging
import re
from g4f.client import AsyncClient

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Constantes del dataset
SUBTEMAS = [
    "Verbos copulativos tiempos ingleses", "Verbos frasales inseparables inglés",
    "Verbos frasales separables inglés", "Conjugación afirmativa tiempos ingleses",
    "Conjugación negativa tiempos ingleses", "Conjugación interrogativa tiempos ingleses",
    "Raíz verbal léxico inglés", "Terminación verbal tiempos ingleses",
    "Tercera persona singular inglés", "Verbo poder habilidad inglés",
    "Verbo deber obligación inglés", "Verbo querer desear inglés",
    "Verbo ir movimiento inglés", "Verbo venir acercamiento inglés",
    "Verbo decir comunicar inglés", "Verbo hablar articular inglés",
    "Verbo mirar observar inglés", "Verbo escuchar atención inglés",
    "Verbo pensar razonar inglés", "Verbo saber conocer inglés",
    "Verbo encontrar descubrir inglés", "Verbo dar entregar inglés",
    "Verbo tomar agarrar inglés", "Verbos de estado inglés",
    "Verbos de acción inglés", "Verbos perceptivos léxico inglés",
    "Concordancia temporal verbal inglesa"
]

DIMENSIONES = [
    "Definición anatómica o estructural", "Dinámica y funcionamiento físico",
    "Propiedades químicas o materiales", "Errores, fallas y patologías comunes",
    "Historia, origen y evolución", "Contexto y entorno ecológico",
    "Aplicaciones prácticas en la vida real", "Importancia e impacto social",
    "Ventajas y desventajas comparativas", "Riesgos y medidas de seguridad",
    "Clasificación taxonómica", "Cálculos y fórmulas asociadas",
    "Mitos y concepciones erróneas", "Relación simbiótica con otros sistemas",
    "Transformación y ciclos energéticos", "Experimentos y demostraciones escolares",
    "Consecuencias a largo plazo", "Impacto ambiental",
    "Mantenimiento y prevención", "Proyecciones futuras y tecnología"
]

MAX_CONCEPTOS = 175
ARCHIVO_DESTINO = "GBX_brain_68A.json"

# Inicializar cliente
client = AsyncClient()
# Limitar concurrencia
sem = asyncio.Semaphore(5)

def clean_text_for_json(text):
    text = text.replace('\n', ' ').replace('"', "'")
    text = re.sub(r'\[\[.*?\]\]\(.*?\)', '', text)
    text = re.sub(r'\[\d+\]', '', text)
    text = re.sub(r'\[cita requerida\]', '', text)
    return text.strip()

async def generar_concepto(subtema, dimension):
    async with sem:
        prompt = f"""
        Actúa como un experto en minería de información educativa para estudiantes de Tercer Ciclo (9 a 15 años).
        Genera un concepto educativo sobre el subtema '{subtema}' respondiendo específicamente a la dimensión '{dimension}'.
        Si esta dimensión no aplica científicamente a este tema de inglés, responde exactamente con la palabra 'OMITIR'.

        Reglas estrictas de calidad:
        - NUNCA uses inglés, solo español.
        - Simplifica conceptos universitarios sin perder veracidad científica.
        - No alucinar ni inventar historias. Aporta valor real.

        Devuelve tu respuesta en el siguiente formato JSON estricto:
        {{
            "intent_id": "generar_un_id_unico_semantico_en_minusculas_con_guiones_bajos_sin_numeros",
            "keywords": "entre 4 y 6 palabras, sustantivos y verbos nucleares unicos, todo minusculas, sin tildes, sin articulos, sin preposiciones",
            "base_response": "Explicacion de entre 35 y 50 palabras, ortografia inmaculada con tildes, texto plano, sin saltos de linea, sin comillas dobles sin escapar, tono instruccional, iniciando con carga de conocimiento real."
        }}
        Devuelve SOLO un JSON válido, sin bloques de código markdown, sin texto adicional alrededor.
        """
        try:
            response = await client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}]
            )
            content = response.choices[0].message.content

            if "OMITIR" in content:
                return None

            # Extraer JSON
            match = re.search(r'\{[^{}]+\}', content)
            if match:
                data = json.loads(match.group(0))
                # Limpiar texto para prevenir corrupcion JSON
                data['base_response'] = clean_text_for_json(data['base_response'])

                # Simple validacion de extension de base_response
                words = data['base_response'].split()
                if not (30 <= len(words) <= 55): # Un poco de margen que corregiremos luego si es necesario, o filtramos despues
                    # Mejor no retornarlo si es muy corto o largo
                    pass

                return data
            return None
        except Exception as e:
            logging.error(f"Error generando para {subtema} - {dimension}: {e}")
            return None

async def main():
    dataset = []
    conceptos_generados = 0

    logging.info("Iniciando generación de dataset...")

    for subtema in SUBTEMAS:
        if conceptos_generados >= MAX_CONCEPTOS:
            break

        logging.info(f"Procesando subtema: {subtema}")
        tasks = []
        for dimension in DIMENSIONES:
            tasks.append(generar_concepto(subtema, dimension))

        resultados = await asyncio.gather(*tasks)

        for res in resultados:
            if res and conceptos_generados < MAX_CONCEPTOS:
                dataset.append(res)
                conceptos_generados += 1
                logging.info(f"Concepto {conceptos_generados}/{MAX_CONCEPTOS} generado: {res['intent_id']}")

        # Guardado incremental por cada subtema
        with open(ARCHIVO_DESTINO, 'w', encoding='utf-8') as f:
            json.dump(dataset, f, ensure_ascii=False, indent=4)

    logging.info(f"Generación completa. Total conceptos: {len(dataset)}")

if __name__ == "__main__":
    asyncio.run(main())
