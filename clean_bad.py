import json
import re

def main():
    with open("GBX_brain_19B.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    filtered_data = [d for d in data if "silbido_rapido_de_altos" not in d["intent_id"]]

    with open("GBX_brain_19B.json", "w", encoding="utf-8") as f:
        json.dump(filtered_data, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()