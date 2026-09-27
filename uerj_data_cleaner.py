import re
import html

TITLE_PREFIXES = [
    r'^prof(?:essor|a|\.a?|\.dra?|\.dr)?\b',
    r'^dra?\.\b',
    r'^ph\.?d\.?\b',
    r'^msc\.\b',
    r'^eng\.\b',
    r'^pesquisador(?:a)?\b',
    r'^coordenador(?:a)?\b',
    r'^diretor(?:a)?\b'
]

SPECIALIZATION_MAP = {
    r'\b(?:cfd|din[âa]mica dos fluidos computacional|computational fluid dynamics)\b': 'CFD / Termofluidodinâmica Computacional',
    r'\b(?:termofluidodin[âa]mica|termic[ao]|fluidos?|transfer[êe]ncia de calor)\b': 'Termofluidodinâmica e Fenômenos de Transporte',
    r'\b(?:elementos finitos|fem|fea|m[ée]todos num[ée]ricos|mec[âa]nica dos s[óo]lidos|estruturas)\b': 'Elementos Finitos e Análise Estrutural',
    r'\b(?:vibra[çc][õo]es|ac[úu]stica|nvh|din[âa]mica)\b': 'Vibrações, Acústica e Dinâmica',
    r'\b(?:otimiza[çc][ãa]o|pesquisa operacional|gest[ãa]o da produ[çc][ãa]o|log[íi]stica)\b': 'Otimização de Processos e Pesquisa Operacional',
    r'\b(?:manufatura|processos de fabrica[çc][ãa]o|usinagem|soldagem|pol[íi]meros|comp[óo]sitos|materiais)\b': 'Manufatura e Engenharia de Materiais',
    r'\b(?:controle|automa[çc][ãa]o|rob[óo]tica|eletr[ôo]nica de pot[êe]ncia|sistemas embarcados)\b': 'Sistemas de Controle, Automação e Robótica',
    r'\b(?:intelig[êe]ncia artificial|ia|aprendizado de m[áa]quina|machine learning|analytics|data science)\b': 'Inteligência Artificial e Data Science',
    r'\b(?:hpc|computa[çc][ãa]o de alto desempenho|supercomputa[çc][ãa]o|paralela)\b': 'Computação de Alto Desempenho (HPC)',
    r'\b(?:g[êe]meos digitais|digital twin|cad|cam|cae|simula[çc][ãa]o)\b': 'Gêmeos Digitais e Modelação 3D / CAD/CAE',
    r'\b(?:inova[çc][ãa]o|propriedade intelectual|transfer[êe]ncia de tecnologia|patentes)\b': 'Gestão de Inovação e Propriedade Intelectual'
}

INVALID_NAMES = {
    'docentes', 'corpo docente', 'professores', 'contato', 'equipe', 'diretoria',
    'secretaria', 'home', 'início', 'sobre', 'ensino', 'pesquisa', 'extensão',
    'laboratórios', 'departamento', 'coordenação', 'mecan', 'deel', 'depro', 'deq',
    'dme', 'denp', 'deqa', 'ppgmc', 'ppg-compmat', 'gesar', 'inovuerj', 'depinova'
}

def fix_encoding(text: str) -> str:
    if not text:
        return ""
    text = html.unescape(text)
    try:
        if 'Ã' in text or 'Â' in text or 'ï¿½' in text:
            decoded = text.encode('iso-8859-1').decode('utf-8')
            return decoded
    except Exception:
        pass
    return text

def clean_string(text: str) -> str:
    if not text:
        return ""
    text = fix_encoding(text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def strip_titles(name: str) -> str:
    name = clean_string(name)
    original = name
    for pattern in TITLE_PREFIXES:
        name = re.sub(pattern, '', name, flags=re.IGNORECASE).strip()
    # Remove degree suffixes or leading symbols
    name = re.sub(r'^[,\-\.\s]+', '', name)
    name = re.sub(r'\s*\((?:PhD|D\.Sc\.|Dr\.|M\.Sc\.)\)', '', name, flags=re.IGNORECASE)
    return name.strip() or original

def is_valid_person_name(name: str) -> bool:
    cleaned = strip_titles(name).lower()
    if not cleaned or len(cleaned) < 5:
        return False
    if cleaned in INVALID_NAMES:
        return False
    if any(inv in cleaned for inv in ['departamento', 'faculdade', 'instituto', 'universidade', 'laboratório', 'programa de pós']):
        return False
    # Check if contains at least first and last name or valid single word name
    parts = cleaned.split()
    if len(parts) < 2:
        return False
    return True

def map_specialization(text: str) -> str:
    if not text:
        return "Modelagem Computacional e Engenharia"
    matched = []
    for pattern, label in SPECIALIZATION_MAP.items():
        if re.search(pattern, text, re.IGNORECASE):
            matched.append(label)
    if matched:
        return " | ".join(dict.fromkeys(matched))
    return "Simulação e Engenharia Aplicada"
