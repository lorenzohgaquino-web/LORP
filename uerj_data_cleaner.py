#!/usr/bin/env python3
"""
uerj_data_cleaner.py - Proper text sanitization and encoding repair utility for UERJ data processing.
"""

import re
import html

def fix_encoding(text: str) -> str:
    """Repair Mojibake and ISO-8859-1 / UTF-8 mis-encodings."""
    if not text:
        return ""
    text = html.unescape(text)

    replacements = {
        'Ã¡': 'á', 'Ã©': 'é', 'Ã­': 'í', 'Ã³': 'ó', 'Ãº': 'ú',
        'Ã£': 'ã', 'Ãµ': 'õ', 'Ã¢': 'â', 'Ãª': 'ê', 'Ã´': 'ô',
        'Ã§': 'ç', 'Ã\x81': 'Á', 'Ã\x89': 'É', 'Ã\x8d': 'Í', 'Ã\x93': 'Ó',
        'Ã\x9a': 'Ú', 'Ã\x83': 'Ã', 'Ã\x95': 'Õ', 'Ã\x82': 'Â', 'Ã\x8a': 'Ê',
        'Ã\x94': 'Ô', 'Ã\x87': 'Ç', 'Ã¼': 'ü', 'Ã\x9c': 'Ü', 'ï¿½': ''
    }
    for bad, good in replacements.items():
        text = text.replace(bad, good)

    return text.strip()

def clean_name(name: str) -> str:
    """Sanitize faculty and researcher names cleanly."""
    if not name:
        return ""
    name = fix_encoding(name)

    # Remove degree titles, honorifics (including Profª, Profº, Prof.), and bios
    prefixes = [
        r'^Prof(a|o|ª|º)?\.?\s*', r'^Professor(a)?\s*', r'^Dr(a|ª)?\.?\s*', r'^Doutor(a)?\s*',
        r'^Ph\.D\.?\s*', r'^MSc\.?\s*', r'^Mestre\s*', r'^Eng(a|ª)?\.?\s*'
    ]
    for p in prefixes:
        name = re.sub(p, '', name, flags=re.IGNORECASE)

    # Remove bios/descriptions attached to name
    name = re.split(r'\(|,|\s-\s|Depto\.|D\.Sc|Msc|Ph\.D|Graduação|Possui|Concluiu|Qualificação|Equipe|Professores', name, flags=re.IGNORECASE)[0].strip()

    # Clean non-name characters
    name = re.sub(r'[^\w\s\.\-áéíóúãõâêôçÁÉÍÓÚÃÕÂÊÔÇ]', '', name)
    name = re.sub(r'\s+', ' ', name)

    # Capitalize cleanly
    words = name.split()
    clean_words = []
    lowercase_particles = {'de', 'da', 'do', 'das', 'dos', 'e'}
    for idx, w in enumerate(words):
        w_low = w.lower()
        if idx > 0 and w_low in lowercase_particles:
            clean_words.append(w_low)
        else:
            clean_words.append(w.capitalize())

    return " ".join(clean_words)

def clean_email(email: str) -> str:
    """Validate and format institutional email address, stripping trailing UI/Lattes text."""
    if not email:
        return ""
    email = email.strip().lower()
    if email.startswith('mailto:'):
        email = email[7:]

    # Match strictly up to standard top-level domain extensions (.br, .com, .org, .edu, .net)
    match = re.search(r'[\w\.-]+@[\w\.-]+\.(?:br|com|org|edu|net)', email)
    if match:
        return match.group(0)
    return ""

if __name__ == "__main__":
    test_email = "sztajnbergalexszt@ime.uerj.brlattes"
    print("Clean email test:", clean_email(test_email))
    test_name = "Profª Marisa Cristina Guimarães Rocha"
    print("Clean name test:", clean_name(test_name))
