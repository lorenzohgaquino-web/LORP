import re

def fix_mojibake(text):
    if not text:
        return ""
    # Common fixes for UTF-8 read as ISO-8859-1 or Latin-1
    replacements = {
        'Ã¡': 'á', 'Ã©': 'é', 'Ã­': 'í', 'Ã³': 'ó', 'Ãº': 'ú',
        'Ã£': 'ã', 'Ãµ': 'õ', 'Ã¢': 'â', 'Ãª': 'ê', 'Ã´': 'ô',
        'Ã§': 'ç', 'Ã\x81': 'Á', 'Ã\x89': 'É', 'Ã\x8d': 'Í',
        'Ã\x93': 'Ó', 'Ã\x9a': 'Ú', 'Ã\x83': 'Ã', 'Ã\x95': 'Õ',
        'Ã\x82': 'Â', 'Ã\x8a': 'Ê', 'Ã\x94': 'Ô', 'Ã\x87': 'Ç',
        '\ufffd': '', 'ï¿½': ''
    }
    for bad, good in replacements.items():
        text = text.replace(bad, good)
    return text.strip()

def strip_degrees(name):
    if not name:
        return ""
    name = fix_mojibake(name)
    # Remove titles
    prefixes = [
        r'Prof\.\s+Dr\.\s+', r'Profa\.\s+Dra\.\s+', r'Profª\.\s+Dra\.\s+',
        r'Prof\.\s+', r'Profa\.\s+', r'Profª\.\s+', r'Dr\.\s+', r'Dra\.\s+',
        r'Pesquisador\s+', r'Pesquisadora\s+'
    ]
    for p in prefixes:
        name = re.sub(r'^' + p, '', name, flags=re.IGNORECASE)
    # Strip whitespace & special chars
    name = re.sub(r'\s+', ' ', name).strip()
    return name

def is_valid_person_name(name):
    if not name or len(name) < 5:
        return False
    invalid_keywords = [
        'departamento', 'graduação', 'pós-graduação', 'secretaria', 'home',
        'notícias', 'disciplinas', 'cronograma', 'corpo docente', 'contato',
        'laboratório', 'programa', 'editais', 'pesquisa', 'regimento', 'uerj',
        'faculdade', 'instituto', 'mecanica', 'eletronica', 'producao', 'quimica'
    ]
    name_lower = name.lower()
    for kw in invalid_keywords:
        if kw in name_lower:
            return False
    parts = name.split()
    if len(parts) < 2:
        return False
    return True

def sanitize_email(email):
    if not email:
        return "atendimento.dein@uerj.br"
    email = email.strip().lower()
    if re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
        return email
    return "atendimento.dein@uerj.br"
