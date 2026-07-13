import json
import re

with open("MM_brain_45.json", "r", encoding="utf-8") as f:
    concepts = json.load(f)

# Limpiar las respuestas de artefactos y frases dependientes para cumplir el code review
clean_concepts = []

for c in concepts:
    text = c['base_response']

    # Filtrar conceptos que claramente contienen artefactos o referencias
    lower_text = text.lower()

    # Si contiene matemáticas crudas o artefactos evidentes, ignorarlo
    if "displaystyle" in lower_text or "{\\" in lower_text or "frac" in lower_text:
        continue
    if "enlace externo" in lower_text or "youtube" in lower_text or "akesso" in lower_text:
        continue
    if "=" in text or "}" in text or "{" in text or "[" in text or "]" in text:
        continue
    if "figura" in lower_text or "imagen" in lower_text or "véase" in lower_text or "vease" in lower_text:
        continue

    # Verificar que no empiece con conectores dependientes
    first_word = text.split()[0].lower()
    if first_word in ["como", "por", "y", "o", "pero", "además", "sin", "en", "con", "a", "el", "la", "los", "las", "un", "una", "unos", "unas"] and len(text.split()) > 1 and text.split()[1] in ["él", "ella", "ello", "eso", "esto", "aquello", "ellos"]:
        continue

    # Limpiar y asegurar que sea una oración con sentido (empieza con mayúscula y termina en punto)
    text = text.strip()
    if not text.endswith(".") and not text.endswith(":") and not text.endswith(";"):
        text += "."

    text = text[0].upper() + text[1:]

    c['base_response'] = text
    clean_concepts.append(c)

print(f"Conceptos limpios: {len(clean_concepts)}")

with open("MM_brain_45.json", "w", encoding="utf-8") as f:
    json.dump(clean_concepts, f, ensure_ascii=False, indent=2)
