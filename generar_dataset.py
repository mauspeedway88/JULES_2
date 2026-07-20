import asyncio
import json
import os
import random
from g4f.client import AsyncClient

# Configuración de los subtemas
SUBTEMAS = [
    "Ideas principales de lectura", "Inferencias de comprensión lectora", "Resumen de textos leídos",
    "Análisis de comprensión lectora", "Lectura crítica de textos", "Contexto de comprensión lectora",
    "Ideas secundarias de lectura", "Detalles específicos del texto", "Propósito del autor leído",
    "Intención comunicativa de lectura", "Público objetivo del texto", "Mensaje implícito de lectura",
    "Información explícita de textos", "Tema central de lectura", "Argumento principal del texto",
    "Estructura textual de lectura", "Hipótesis de comprensión lectora", "Anticipación de contenidos leídos",
    "Predicciones durante la lectura", "Lectura exploratoria de textos", "Lectura analítica de documentos",
    "Subrayado de textos leídos", "Esquemas de comprensión lectora"
]

DIMENSIONES = [
    "Definición anatómica o estructural", "Dinámica y funcionamiento físico", "Propiedades químicas o materiales",
    "Errores, fallas y patologías comunes", "Historia, origen y evolución", "Contexto y entorno ecológico",
    "Aplicaciones prácticas en la vida real", "Importancia e impacto social", "Ventajas y desventajas comparativas",
    "Riesgos y medidas de seguridad", "Clasificación taxonómica", "Cálculos y fórmulas asociadas",
    "Mitos y concepciones erróneas", "Relación simbiótica con otros sistemas", "Transformación y ciclos energéticos",
    "Experimentos y demostraciones escolares", "Consecuencias a largo plazo", "Impacto ambiental",
    "Mantenimiento y prevención", "Proyecciones futuras y tecnología"
]

MAX_CONCEPTOS = 200
ARCHIVO_DESTINO = "GBX_brain_63A.json"

dataset = []
conceptos_generados = 0

async def generar_concepto(cliente, semaforo, subtema, dimension, index_dim):
    global conceptos_generados, dataset
    if conceptos_generados >= MAX_CONCEPTOS:
        return

    prompt = f"""Genera un concepto educativo sobre '{subtema}' enfocado en su '{dimension}'.
    NIVEL ACADÉMICO: Estudiantes de Tercer Ciclo (9 a 15 años). Simplifica pero mantén la veracidad científica.
    RESTRICCIONES:
    - NO uses Markdown ni viñetas.
    - NO repitas conceptos.
    - NO escribas en inglés. SOLO ESPAÑOL.
    - NO añadas referencias ni enlaces bibliográficos.

    Genera EXACTAMENTE la respuesta en formato JSON con las siguientes claves:
    {{
        "intent_id": "{subtema.lower().replace(' ', '_').replace('á','a').replace('é','e').replace('í','i').replace('ó','o').replace('ú','u')}_{index_dim}",
        "keywords": "4 a 6 palabras clave, TODO MINÚSCULAS, SIN TILDES, SIN ARTÍCULOS NI PREPOSICIONES, separados por espacio",
        "base_response": "Texto de 35 a 50 palabras exactas. Oraciones completas, tono instruccional directo, ortografía inmaculada CON tildes. TODO EN UNA SOLA LÍNEA SIN SALTOS NI COMILLAS DOBLES INTERNAS."
    }}
    Responde ÚNICAMENTE con el objeto JSON válido. NO AGREGUES texto antes ni después.
    """

    async with semaforo:
        if conceptos_generados >= MAX_CONCEPTOS:
            return

        try:
            # Inicializando un cliente async por cada request
            response = await cliente.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}]
            )
            content = response.choices[0].message.content

            # Limpiar contenido extra si G4F retorna markdown
            content = content.replace("```json", "").replace("```", "").strip()

            # Validar JSON
            data = json.loads(content)

            if "intent_id" in data and "keywords" in data and "base_response" in data:
                dataset.append(data)
                conceptos_generados += 1
                print(f"Generado concepto {conceptos_generados}: {subtema} - {dimension}")

        except Exception as e:
            pass

async def main():
    cliente = AsyncClient()
    semaforo = asyncio.Semaphore(2)
    tareas = []

    for subtema in SUBTEMAS:
        for i, dimension in enumerate(DIMENSIONES):
            if conceptos_generados >= MAX_CONCEPTOS:
                break
            tareas.append(generar_concepto(cliente, semaforo, subtema, dimension, i))

    await asyncio.gather(*tareas)

    with open(ARCHIVO_DESTINO, 'w', encoding='utf-8') as f:
        json.dump(dataset[:MAX_CONCEPTOS], f, ensure_ascii=False, indent=2)

    print(f"Completado. Generados: {len(dataset[:MAX_CONCEPTOS])}")

if __name__ == "__main__":
    asyncio.run(main())
