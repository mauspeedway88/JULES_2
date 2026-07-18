import json
import re

def validar_dataset(ruta_archivo):
    try:
        with open(ruta_archivo, 'r', encoding='utf-8') as f:
            datos = json.load(f)
    except Exception as e:
        print(f"Error cargando JSON: {e}")
        return False

    print(f"Entradas totales cargadas: {len(datos)}")

    intent_ids = set()
    errores = 0

    for i, item in enumerate(datos):
        # Verificar intent_id
        intent_id = item.get("intent_id", "")
        if re.search(r'\d', intent_id):
            print(f"[{i}] ERROR: intent_id contiene números: {intent_id}")
            errores += 1
        if intent_id in intent_ids:
            print(f"[{i}] ERROR: intent_id duplicado: {intent_id}")
            errores += 1
        intent_ids.add(intent_id)

        # Verificar keywords
        keywords = item.get("keywords", [])
        if not (4 <= len(keywords) <= 6):
            print(f"[{i}] ERROR: Longitud de keywords no es 4-6: {keywords}")
            errores += 1
        for kw in keywords:
            if not kw.islower():
                print(f"[{i}] ERROR: Keyword no está en minúsculas: {kw}")
                errores += 1
            if re.search(r'[áéíóúÁÉÍÓÚ]', kw):
                print(f"[{i}] ERROR: Keyword tiene acento: {kw}")
                errores += 1

        # Verificar base_response
        base_response = item.get("base_response", "")
        palabras = base_response.split()
        if not (35 <= len(palabras) <= 50):
            print(f"[{i}] ERROR: Conteo de palabras en base_response {len(palabras)} no está entre 35-50: {base_response}")
            errores += 1

    print(f"\nValidación completa. Errores totales encontrados: {errores}")
    return errores == 0

if __name__ == "__main__":
    exito = validar_dataset("GBX_brain_39B.json")
    if not exito:
        exit(1)
