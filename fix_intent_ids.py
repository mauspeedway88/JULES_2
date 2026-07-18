import json

def corregir_intent_ids(ruta_archivo):
    with open(ruta_archivo, 'r', encoding='utf-8') as f:
        datos = json.load(f)

    vistos = {}

    for item in datos:
        id_original = item['intent_id']
        if id_original not in vistos:
            vistos[id_original] = 1
        else:
            # Generar un nuevo ID semántico usando keywords
            keywords = item['keywords']
            nuevo_id = f"{id_original}_{'_'.join(keywords[:2])}"

            # Asegurarse de que sea único
            while nuevo_id in vistos:
                import random
                nuevo_id = f"{id_original}_{random.choice(keywords)}_{random.choice(keywords)}"

            item['intent_id'] = nuevo_id
            vistos[nuevo_id] = 1

    with open(ruta_archivo, 'w', encoding='utf-8') as f:
        json.dump(datos, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    corregir_intent_ids("GBX_brain_39B.json")
