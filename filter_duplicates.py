import json
import sys
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def filtrar_dataset(ruta_archivo, umbral=0.85):
    with open(ruta_archivo, 'r', encoding='utf-8') as f:
        datos = json.load(f)

    if not datos:
        return datos

    textos = [item['base_response'] for item in datos]
    vectorizador = TfidfVectorizer()
    matriz_tfidf = vectorizador.fit_transform(textos)

    matriz_similitud = cosine_similarity(matriz_tfidf)

    a_mantener = set(range(len(datos)))

    for i in range(len(datos)):
        if i not in a_mantener:
            continue
        for j in range(i + 1, len(datos)):
            if matriz_similitud[i, j] > umbral:
                if j in a_mantener:
                    a_mantener.remove(j)

    datos_filtrados = [datos[i] for i in sorted(list(a_mantener))]

    with open(ruta_archivo, 'w', encoding='utf-8') as f:
        json.dump(datos_filtrados, f, ensure_ascii=False, indent=2)

    return len(datos) - len(datos_filtrados)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        ruta_archivo = sys.argv[1]
        removidos = filtrar_dataset(ruta_archivo)
        print(f"Removidos {removidos} duplicados.")
