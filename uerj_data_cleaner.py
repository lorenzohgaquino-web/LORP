import re

# Department default emails for LGPD compliant fallbacks (NO INFERRED EMAILS)
DEPT_FALLBACK_EMAILS = {
    'FEN/MECAN': 'ppgem@eng.uerj.br',
    'FEN/DEEL': 'pel@eng.uerj.br',
    'FEN/DEPRO': 'dein@eng.uerj.br',
    'FEN/DEQ': 'deq@eng.uerj.br',
    'FEN/CIVIL': 'pgeciv@eng.uerj.br',
    'FEN': 'diretoria@eng.uerj.br',
    'IPRJ': 'ppgmc@iprj.uerj.br',
    'FAT': 'dirfat@fat.uerj.br',
    'GESAR': 'gesar@uerj.br',
    'IME': 'ppgcompmat@ime.uerj.br',
    'INOVUERJ': 'inovuerj@uerj.br'
}

INVALID_NAME_PATTERNS = [
    r'conheça', r'corpo docente', r'filtre', r'departamento', r'pos-gradua', r'pós-gradua',
    r'historico', r'histórico', r'horario', r'horário', r'disciplina', r'regimento', r'noticia', r'notícia',
    r'atendimento', r'graduacao', r'graduação', r'extensao', r'extensão', r'pesquisa', r'mencao', r'menção',
    r'docentes', r'ver todas', r'retorna', r'chefia', r'coordenacao', r'coordenação',
    r'matrícula', r'curriculum', r'lattes', r'email', r'e-mail', r'contato', r'equipe',
    r'subir', r'topo', r'menu', r'voltar', r'aluno', r'professor', r'professora',
    r'analista', r'engenheiro', r'engenheira', r'membro', r'pesquisador',
    r'proteção de dados', r'protecao de dados', r'lgpd', r'ouvidoria', r'moodle', r'calendário', r'calendario',
    r'manual do estudante', r'processo seletivo', r'professor substituto', r'professor adjunto',
    r'ead-iprj', r'reserva de', r'saiba mais', r'diretoria', r'secretaria', r'conselho'
]

def clean_person_name(raw_name):
    if not raw_name:
        return ""

    # Strip UI button text like "saiba mais"
    name = re.sub(r'saiba\s*mais', '', raw_name, flags=re.IGNORECASE)

    # Remove honorifics and titles
    name = re.sub(r'^(Prof|Profa|Profª|Dr|Dra|MSc|DSc|PhD|Eng|Engª|Docente)\.?\s*', '', name, flags=re.IGNORECASE)
    name = re.sub(r'^(Prof|Profa|Profª|Dr|Dra|MSc|DSc|PhD|Eng|Engª|Docente)\.?\s*', '', name, flags=re.IGNORECASE)

    # Remove trailing qualifications or IDs like ", DSc - k(143)", "(303)"
    name = re.sub(r',?\s*(DSc|MSc|PhD|k\(\d+\)|\(\d+\)).*', '', name, flags=re.IGNORECASE)
    name = re.sub(r'\d+', '', name)

    # Clean whitespace and capitalization
    name = re.sub(r'\s+', ' ', name).strip()

    # Titlecase while keeping lowercase prepositions
    words = name.split()
    cleaned_words = []
    prepositions = {'de', 'da', 'do', 'dos', 'das', 'e'}
    for idx, w in enumerate(words):
        w_lower = w.lower()
        if idx > 0 and w_lower in prepositions:
            cleaned_words.append(w_lower)
        else:
            cleaned_words.append(w.capitalize())

    return " ".join(cleaned_words)

def is_valid_person_name(name):
    if not name or len(name) < 5:
        return False

    name_lower = name.lower()
    for pat in INVALID_NAME_PATTERNS:
        if re.search(pat, name_lower):
            return False

    words = name.split()
    if len(words) < 2:
        return False

    # Must be alphabetic characters / spaces / accents
    if not re.match(r'^[A-Za-zÀ-ÖØ-öø-ÿ\s\.\'-]+$', name):
        return False

    return True

def classify_siemens_specialization(text, depto, lab=""):
    text_lower = (text + " " + depto + " " + lab).lower()

    specializations = []

    # CFD & Fluidodynamics
    if any(k in text_lower for k in ['cfd', 'fluidos', 'escoamento', 'meio poroso', 'meios porosos', 'aerodinâmica', 'hidrodinâmica', 'turbomáquinas', 'termofluidodinâmica', 'fenômenos de transporte', 'star-ccm']):
        specializations.append("CFD & Termofluidodinâmica")

    # FEA & Structural Mechanics
    if any(k in text_lower for k in ['elementos finitos', 'fea', 'mecânica dos sólidos', 'estruturas', 'vibrações', 'acústica', 'fadiga', 'fratura', 'simcenter', 'nx', 'mecanica computacional']):
        specializations.append("Análise Estrutural & FEA")

    # Thermal & Thermodynamics
    if any(k in text_lower for k in ['termodinâmica', 'transferência de calor', 'reatores', 'troca térmica', 'motores', 'trocadores', 'energia']):
        specializations.append("Térmica & Reatores")

    # Control, Automation & Power Electronics
    if any(k in text_lower for k in ['controle', 'automação', 'robótica', 'eletrônica de potência', 'sistemas embarcados', 'mecatrônica', 'automação industrial']):
        specializations.append("Controle & Automação Industrial")

    # Optimization, Logistics & Operations Research
    if any(k in text_lower for k in ['otimização', 'pesquisa operacional', 'simulação discreta', 'logística', 'gestão de processos', 'cadeia de suprimentos']):
        specializations.append("Otimização & Pesquisa Operacional")

    # Materials Science & Polymers
    if any(k in text_lower for k in ['materiais', 'polímeros', 'compósitos', 'corrosão', 'metalurgia', 'nanotecnologia']):
        specializations.append("Engenharia de Materiais & Compósitos")

    # Scientific Computing, AI & HPC
    if any(k in text_lower for k in ['inteligência artificial', 'aprendizado de máquina', 'ia', 'hpc', 'computação de alto desempenho', 'gêmeos digitais', 'modelagem matemática', 'métodos numéricos', 'gproms', 'amsim', 'modelagem computacional']):
        specializations.append("Computação Científica & IA")

    if not specializations:
        # Department fallbacks
        if 'mecan' in depto.lower():
            specializations.append("Engenharia Mecânica & Simulação")
        elif 'deel' in depto.lower():
            specializations.append("Sistemas de Controle & Eletrônica")
        elif 'depro' in depto.lower() or 'dein' in depto.lower():
            specializations.append("Otimização de Processos & Logística")
        elif 'deq' in depto.lower():
            specializations.append("Simulação de Processos Químicos")
        elif 'civil' in depto.lower():
            specializations.append("Mecânica dos Sólidos & Estruturas")
        elif 'iprj' in depto.lower() or 'ppgmc' in depto.lower():
            specializations.append("Modelagem Computacional & Métodos Numéricos")
        elif 'fat' in depto.lower():
            specializations.append("Engenharia Industrial & Materiais")
        elif 'ime' in depto.lower():
            specializations.append("Modelagem Matemática & Computação de Alto Desempenho")
        else:
            specializations.append("Engenharia & Modelagem Numérica")

    return ", ".join(specializations)
