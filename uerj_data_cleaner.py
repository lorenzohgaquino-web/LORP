import re
import html

def sanitize_string(text):
    if not text:
        return ""
    if isinstance(text, bytes):
        text = text.decode('utf-8', errors='ignore')
    text = html.unescape(text)
    # Fix common unicode replacement characters or non-breaking spaces
    text = text.replace('\ufffd', '').replace('\xa0', ' ')
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def strip_academic_titles(name):
    name = sanitize_string(name)
    # Strip common academic title prefixes
    titles = [
        r'^Profª?\.\s*', r'^Drª?\.\s*', r'^Msc\.\s*', r'^Ph\.?D\.?\s*',
        r'^Prof\.?\s+Titular\s*', r'^Prof\.?\s+Associado\s*', r'^Prof\.?\s+Adjunto\s*',
        r'^Prof\.?\s+Assistente\s*', r'^Prof\.?\s+Colaborador\s*', r'^Prof\.?\s+Emerito\s*',
        r'^Coordenador\(a\)\s*', r'^Diretor\(a\)\s*', r'^Chefe\s+de\s+Departamento\s*'
    ]
    for title in titles:
        name = re.sub(title, '', name, flags=re.IGNORECASE)
    return name.strip()

def is_valid_person_name(name):
    clean = strip_academic_titles(name)
    if len(clean) < 4:
        return False
    # Check if name contains non-person keywords or navigation text
    invalid_keywords = [
        'departamento', 'faculdade', 'instituto', 'universidade', 'coordenacao',
        'laboratorio', 'corpo docente', 'pos-graduacao', 'graduacao', 'secretaria',
        'uerj', 'iprj', 'fen', 'fat', 'ime', 'menu', 'home', 'contato', 'portal',
        'mecanica', 'eletronica', 'producao', 'quimica', 'civil', 'computacao',
        'fluxogramas', 'disciplinas', 'horarios', 'manual', 'estudante', 'ver todas'
    ]
    name_lower = clean.lower()
    for kw in invalid_keywords:
        if kw in name_lower:
            return False
    # Must have at least two words
    words = clean.split()
    if len(words) < 2:
        return False
    return True

if __name__ == '__main__':
    test_names = [
        "Prof. Dr. João Marcos Lesqueves",
        "Marco Aurélio",
        "Engenharia Mecânica",
        "Prof. Gustavo Rabello dos Anjos"
    ]
    for n in test_names:
        print(f"Original: '{n}' -> Clean: '{strip_academic_titles(n)}' -> Valid: {is_valid_person_name(n)}")
