import re

def clean_name(name):
    if not name:
        return ""
    # Strip explicit keywords LATTES, S (standalone), and whitespace without stripping 'S' from actual names
    name = re.sub(r'^\s*(LATTES|S)\b\s*', '', name, flags=re.IGNORECASE)
    name = re.sub(r'\s*\b(LATTES)\b\s*$', '', name, flags=re.IGNORECASE)
    name = re.sub(r'\s+', ' ', name).strip()
    return name

def fix_mojibake(text):
    if not text:
        return ""
    rep = {
        'Ã¡': 'á', 'Ã©': 'é', 'Ã­': 'í', 'Ã³': 'ó', 'Ãº': 'ú',
        'Ã£': 'ã', 'Ãµ': 'õ', 'Ã¢': 'â', 'Ãª': 'ê', 'Ã´': 'ô',
        'Ã§': 'ç', 'Ã\xa0': 'à', 'Ã\x81': 'Á', 'Ã\x89': 'É',
        'Ã\x8d': 'Í', 'Ã\x93': 'Ó', 'Ã\x9a': 'Ú', 'Ã\x83': 'Ã',
        'Ã\x95': 'Õ', 'Ã\x82': 'Â', 'Ã\x8a': 'Ê', 'Ã\x94': 'Ô',
        'Ã\x87': 'Ç', 'Â': ''
    }
    for k, v in rep.items():
        text = text.replace(k, v)
    return text.strip()
