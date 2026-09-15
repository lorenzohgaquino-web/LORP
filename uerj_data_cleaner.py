import json
import re

def clean_name(name):
    if not name:
        return ""
    # Strip degrees and titles
    name = re.sub(r'^(Prof\.|Profa\.|Dr\.|Dra\.|Professor|Professora)\s+', '', name, flags=re.IGNORECASE)
    # Strip double spaces and trailing punctuation
    name = re.sub(r'\s+', ' ', name).strip()
    return name

def sanitize_dataset(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    cleaned = []
    seen = set()
    for row in data:
        row['nome'] = clean_name(row['nome'])
        key = (row['nome'], row['email'])
        if key not in seen:
            seen.add(key)
            cleaned.append(row)

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(cleaned, f, ensure_ascii=False, indent=2)
    return len(cleaned)

if __name__ == '__main__':
    count = sanitize_dataset('uerj_dataset.json', 'uerj_dataset.json')
    print(f"Sanitized dataset saved with {count} unique entries.")
