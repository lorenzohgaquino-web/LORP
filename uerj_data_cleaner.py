import re
import html

def sanitize_string(text):
    if not text:
        return ""
    text = html.unescape(text)
    replacements = {
        'Ã¡': 'á', 'Ã©': 'é', 'Ã­': 'í', 'Ã³': 'ó', 'Ãº': 'ú',
        'Ã£': 'ã', 'Ãµ': 'õ', 'Ã¢': 'â', 'Ãª': 'ê', 'Ã´': 'ô',
        'Ã§': 'ç', 'Ã': 'Á', 'Ã‰': 'É', 'Ã ': 'À', 'Ã': 'Í',
        'Ã“': 'Ó', 'Ãš': 'Ú', 'Ãƒ': 'Ã', 'Ã•': 'Õ', 'Ã‡': 'Ç',
        'Â': '', 'ï¿½': '', '\ufffd': ''
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    text = text.strip(" '\"`\t\r\n")
    text = re.sub(r'\s+', ' ', text)
    return text

def is_valid_person_name(name):
    if not name:
        return False
    name = sanitize_string(name)
    name_lower = name.lower()

    # Reject junk navigation, non-person titles, test accounts, and placeholders
    invalid_keywords = [
        'histórico', 'sobre', 'laboratório', 'laboratorios', 'extensão', 'notícias', 'noticias',
        'fluxogramas', 'manual do estudante', 'graduação', 'graduacao', 'departamento', 'conselho',
        'biblioteca', 'atendimento', 'voltar', 'mais informações', 'mais informacoes',
        'teste', 'subst1', 'subst2', 'subst3', 'subst4', 'substitut', 'professor(a)', 'lattes',
        'ementário', 'calendário', 'comissão', 'coordenação', 'coordenacao', 'uerj', 'diretoria',
        'pesquisa', 'ensino', 'home', 'crr', 'projeto', 'curso'
    ]

    if any(k in name_lower for k in invalid_keywords):
        return False

    # Name length and word count sanity checks
    words = [w for w in re.split(r'\s+', name) if len(w) > 1]
    if len(words) < 2 or len(words) > 6:
        return False

    if len(name) < 5 or len(name) > 60:
        return False

    # Must contain only letters, spaces, hyphens, or apostrophes
    if not re.match(r'^[A-Za-zÀ-ÖØ-öø-ÿ\s\-\'\.]+$', name):
        return False

    return True

def clean_academic_title(name):
    if not name:
        return ""
    name = sanitize_string(name)

    # Remove parenthetical details like (No momento não leciona...)
    name = re.sub(r'\(.*?\)', '', name)

    # Remove titles & honorifics
    prefixes = [
        r'^Profª?\.?\s*', r'^Professora?\s*', r'^Drª?\.?\s*', r'^Doutor\(a\)\s*', r'^Doutora?\s*',
        r'^MSc\.?\s*', r'^Mestre\s*', r'^Engº?\.?\s*', r'^Engenheiro\(a\)\s*'
    ]
    for p in prefixes:
        name = re.sub(p, '', name, flags=re.IGNORECASE)

    # Cut at first dot or comma if accidental text attached
    if '.' in name:
        name = name.split('.')[0]
    if ',' in name:
        name = name.split(',')[0]

    return name.strip(" ,.-")

if __name__ == "__main__":
    test_names = [
        "Prof. Dr. Francisco José Da Cunha Pires Soeiro",
        "Manual do Estudante Engenharia Mecânica",
        "Vilma Teste",
        "Subst1",
        "Gustavo Rabello Dos Anjos"
    ]
    for tn in test_names:
        cleaned = clean_academic_title(tn)
        valid = is_valid_person_name(cleaned)
        print(f"'{tn}' -> cleaned: '{cleaned}' | valid: {valid}")
