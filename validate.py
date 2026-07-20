import json
import re
from unidecode import unidecode

def clean_dataset():
    try:
        with open("GBX_brain_60A.json", "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        print("No se encontro GBX_brain_60A.json")
        return

    cleaned_data = []
    seen_ids = set()

    for item in data:
        if not isinstance(item, dict):
            continue

        intent_id = item.get("intent_id", "")
        keywords = item.get("keywords", [])
        base_response = item.get("base_response", "")

        # 1. intent_id sin numeros secuenciales, sin acentos
        intent_id = re.sub(r'\d+', '', intent_id)
        intent_id = unidecode(intent_id).lower().strip('_')
        # Ensure semantic uniqueness without arbitrary numbers
        if intent_id in seen_ids:
            continue
        seen_ids.add(intent_id)

        # 2. keywords: sin acentos, solo minúsculas, limpiar palabras funcionales (en la medida de lo básico)
        clean_keywords = []
        for kw in keywords:
            kw = unidecode(kw).lower().strip()
            # Omitir palabras funcionales obvias si se colaron
            if kw not in ['el', 'la', 'los', 'las', 'un', 'una', 'unos', 'unas', 'a', 'ante', 'bajo', 'cabe', 'con', 'contra', 'de', 'desde', 'en', 'entre', 'hacia', 'hasta', 'para', 'por', 'segun', 'sin', 'so', 'sobre', 'tras']:
                clean_keywords.append(kw)

        # 3. base_response: texto plano sin saltos de linea, ni comillas dobles sin escapar, ni muletillas/saludos
        base_response = base_response.replace('\n', ' ').replace('"', "'")
        base_response = re.sub(r'\[\[.*?\]\]\(.*?\)', '', base_response) # Quitar citaciones tipo markdown
        base_response = re.sub(r'\(\d+\s*palabras\)', '', base_response, flags=re.IGNORECASE) # Quitar metatexto de conteo
        base_response = base_response.strip()

        # Remover 'esta' al inicio
        if base_response.lower().startswith('esta '):
            base_response = base_response[5:].strip()
            base_response = base_response.capitalize()

        cleaned_item = {
            "intent_id": intent_id,
            "keywords": clean_keywords[:6], # Max 6
            "base_response": base_response
        }
        cleaned_data.append(cleaned_item)

    # Limitar a máximo 225
    cleaned_data = cleaned_data[:225]

    with open("GBX_brain_60A.json", "w", encoding="utf-8") as f:
        json.dump(cleaned_data, f, ensure_ascii=False, indent=2)

    print(f"Limpieza completada. Total conceptos válidos: {len(cleaned_data)}")

if __name__ == "__main__":
    clean_dataset()
