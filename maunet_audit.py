import json
import os
import re
from collections import defaultdict
import zipfile
import shutil
import urllib.request

def get_last_sentence(text):
    text = text.strip()
    sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
    if not sentences:
        return ""
    return sentences[-1].lower()

def has_stopwords(keywords):
    stopwords = {"el", "la", "los", "las", "un", "una", "unos", "unas", "de", "del", "a", "al", "en", "con", "por", "para", "sin", "sobre", "y", "o", "u", "e", "que", "como"}
    for kw in keywords:
        words = kw.lower().split()
        if any(w in stopwords for w in words):
            return True
    return False

def count_words(text):
    return len(re.findall(r'\b\w+\b', text))

def is_sequential_ids(intent_ids):
    nums = []
    for iid in intent_ids:
        m = re.search(r'\d+$', iid)
        if m:
            nums.append(int(m.group()))

    # Check if there are sequential numbers
    seq_count = 0
    for i in range(len(nums) - 1):
        if nums[i+1] == nums[i] + 1:
            seq_count += 1
            if seq_count >= 1: # even two consecutive numbers is sequential
                return True
        else:
            seq_count = 0
    return False

def parse_keywords(kws):
    if isinstance(kws, list):
        return [str(k) for k in kws]
    elif isinstance(kws, str):
        return kws.split()
    return []

def audit_file(filepath):
    filename = os.path.basename(filepath)
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception:
        return f"❌ RECHAZADO: {filename}"

    if not isinstance(data, list) or len(data) == 0:
        return f"❌ RECHAZADO: {filename}"

    total_concepts = len(data)
    keyword_arrays = []
    last_sentences = defaultdict(int)
    intent_ids = []

    minor_errors = 0

    for item in data:
        if not isinstance(item, dict):
            return f"❌ RECHAZADO: {filename}"

        if "intent_id" not in item or "keywords" not in item or "base_response" not in item:
            return f"❌ RECHAZADO: {filename}"

        intent_id = item["intent_id"]
        keywords_raw = item["keywords"]
        base_response = item["base_response"]

        if not isinstance(intent_id, str) or not isinstance(base_response, str):
            return f"❌ RECHAZADO: {filename}"

        keywords = parse_keywords(keywords_raw)
        if not keywords and keywords_raw: # Failed to parse properly but not empty
             return f"❌ RECHAZADO: {filename}"

        intent_ids.append(intent_id)

        kw_tuple = tuple(sorted([k.lower() for k in keywords]))
        keyword_arrays.append(kw_tuple)

        last_sentence = get_last_sentence(base_response)
        if last_sentence:
            last_sentences[last_sentence] += 1

        has_minor_error = False

        if not (4 <= len(keywords) <= 6):
            has_minor_error = True
        elif has_stopwords(keywords):
            has_minor_error = True
        else:
            has_tildes = False
            for kw in keywords:
                if re.search(r'[áéíóúÁÉÍÓÚ]', kw):
                    has_tildes = True
                    break
            if has_tildes:
                has_minor_error = True

        word_count = count_words(base_response)
        if not (35 <= word_count <= 60):
            has_minor_error = True

        if has_minor_error:
            minor_errors += 1

    kw_counts = defaultdict(int)
    for kw in keyword_arrays:
        kw_counts[kw] += 1
        if kw_counts[kw] >= 2:
            return f"❌ RECHAZADO: {filename}"

    for sent, count in last_sentences.items():
        if count >= 3:
            return f"❌ RECHAZADO: {filename}"

    if is_sequential_ids(intent_ids):
        return f"❌ RECHAZADO: {filename}"

    error_rate = minor_errors / total_concepts
    if error_rate > 0.03:
        return f"❌ RECHAZADO: {filename}"

    return f"✅ APROBADO: {filename}"

if __name__ == "__main__":
    url = "https://github.com/mauspeedway88/JULES_2/raw/main/REVISION_JULES_GRUPO_A002.zip"
    zip_path = "/tmp/REVISION_JULES_GRUPO_A002.zip"
    extract_dir = "/tmp/rev_a002_final"

    urllib.request.urlretrieve(url, zip_path)

    if os.path.exists(extract_dir):
        shutil.rmtree(extract_dir)
    os.makedirs(extract_dir, exist_ok=True)

    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_dir)

    results = []
    for root, _, files in os.walk(extract_dir):
        if "__MACOSX" in root:
            continue
        for file in files:
            if file.endswith(".json") and not file.startswith("._"):
                filepath = os.path.join(root, file)
                results.append(audit_file(filepath))

    results.sort(key=lambda x: x.split(": ")[1])

    for r in results:
        print(r)

    shutil.rmtree(extract_dir)
