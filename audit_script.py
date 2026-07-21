import os
import glob
import json
import re
import zipfile
import shutil
from collections import Counter

def parse_keywords(kws):
    if isinstance(kws, list):
        return tuple(kws)
    elif isinstance(kws, str):
        # split by comma or spaces
        words = [w.strip() for w in re.split(r'[\s,]+', kws) if w.strip()]
        return tuple(words)
    return ()

def get_last_sentence(text):
    text = text.strip()
    # split by punctuation (. ! ?) followed by space or end of string
    sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', text) if s.strip()]
    if sentences:
        return sentences[-1]
    return ""

def check_sequential_ids(intent_ids):
    # Extract trailing number or any number from each id
    numbers = []
    for iid in intent_ids:
        match = re.search(r'\d+', iid)
        if match:
            numbers.append(int(match.group()))
        else:
            numbers.append(None)

    # Check if there is a sequence of consecutive non-None integers of length >= 3
    # where each is exactly previous + 1
    for i in range(len(numbers) - 2):
        if numbers[i] is not None and numbers[i+1] is not None and numbers[i+2] is not None:
            if numbers[i+1] == numbers[i] + 1 and numbers[i+2] == numbers[i+1] + 1:
                return True
    return False

def analyze_file(filepath):
    results = {
        "filepath": filepath,
        "filename": os.path.basename(filepath),
        "is_valid_json": True,
        "missing_keys": False,
        "cloned_keywords": False,
        "robotic_templates": False,
        "sequential_ids": False,
        "fatal_error": False,
        "minor_errors_pct": 0.0,
        "details": []
    }

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        results["is_valid_json"] = False
        results["fatal_error"] = True
        results["details"].append(f"Invalid JSON syntax: {str(e)}")
        return results

    if not isinstance(data, list):
        results["fatal_error"] = True
        results["details"].append("JSON root is not a list")
        return results

    total_concepts = len(data)
    if total_concepts == 0:
        results["fatal_error"] = True
        results["details"].append("JSON list is empty")
        return results

    # 1. Missing keys
    for idx, item in enumerate(data):
        if not isinstance(item, dict):
            results["fatal_error"] = True
            results["details"].append(f"Item at index {idx} is not an object")
            return results
        if not all(k in item for k in ('intent_id', 'keywords', 'base_response')):
            results["missing_keys"] = True
            results["fatal_error"] = True
            results["details"].append(f"Missing required keys at index {idx}: {list(item.keys())}")
            break

    if results["fatal_error"]:
        return results

    # 2. Cloned keywords (more than 3 repetitions of exact array)
    kws_list = []
    for item in data:
        kws_list.append(parse_keywords(item['keywords']))

    kws_counter = Counter(kws_list)
    cloned_kws = {kw: count for kw, count in kws_counter.items() if count > 3}
    if cloned_kws:
        results["cloned_keywords"] = True
        results["fatal_error"] = True
        results["details"].append(f"Cloned keywords repeated > 3 times: {cloned_kws}")

    # 3. Robotic templates (last sentence repeated 5 or more times)
    last_sentences = []
    for item in data:
        last_s = get_last_sentence(item['base_response'])
        if last_s:
            last_sentences.append(last_s)

    sentence_counter = Counter(last_sentences)
    robotic = {s: count for s, count in sentence_counter.items() if count >= 5}
    if robotic:
        results["robotic_templates"] = True
        results["fatal_error"] = True
        results["details"].append(f"Robotic templates repeated >= 5 times: {robotic}")

    # 4. Sequential numeric IDs (simulating variety)
    intent_ids = [str(item['intent_id']) for item in data]
    if check_sequential_ids(intent_ids):
        results["sequential_ids"] = True
        results["fatal_error"] = True
        results["details"].append("Sequential numeric IDs found simulating variety")

    # 5. Minor errors (ignored if < 10% of the file)
    minor_count = 0
    for idx, item in enumerate(data):
        has_minor = False
        kws = item['keywords']
        words = parse_keywords(kws)

        # keywords range 4 to 6
        if len(words) < 4 or len(words) > 6:
            has_minor = True

        # check tildes in keywords
        for w in words:
            if re.search(r'[áéíóúÁÉÍÓÚ]', w):
                has_minor = True
                break

        # base_response length: "menos de 35 o más de 60 palabras"
        resp_words = item['base_response'].split()
        if len(resp_words) < 35 or len(resp_words) > 60:
            has_minor = True

        if has_minor:
            minor_count += 1

    results["minor_errors_pct"] = (minor_count / total_concepts) * 100.0

    if results["minor_errors_pct"] >= 10.0:
        results["fatal_error"] = True
        results["details"].append(f"Minor errors exceed 10% tolerance threshold: {results['minor_errors_pct']:.2f}%")

    return results

def main():
    zip_path = 'REVISION_JULES_GRUPO_A002.zip'
    extract_dir = '/tmp/extracted_revision_a002'

    # clean old extraction
    if os.path.exists(extract_dir):
        shutil.rmtree(extract_dir)

    os.makedirs(extract_dir, exist_ok=True)

    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_dir)

    json_files = glob.glob(os.path.join(extract_dir, '**/*.json'), recursive=True)
    json_files = sorted([f for f in json_files if '__MACOSX' not in f])

    for f in json_files:
        res = analyze_file(f)
        status = "❌ RECHAZADO" if res["fatal_error"] else "✅ APROBADO"
        print(f"{status}: {os.path.basename(f)}")

    # Clean up extraction
    if os.path.exists(extract_dir):
        shutil.rmtree(extract_dir)

if __name__ == '__main__':
    main()
