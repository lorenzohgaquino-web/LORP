import re
import unicodedata

def sanitize_text(text):
    if not text:
        return ""
    # Fix encoding issues if any
    text = text.strip()
    # Replace multiple spaces/newlines
    text = re.sub(r'\s+', ' ', text)
    return text

def clean_person_name(name):
    if not name:
        return ""
    # Remove honorifics and titles
    name = re.sub(r'^(Prof\.|Profa\.|Profª\.|Dr\.|Dra\.|Eng\.|MSc\.|Ph\.D\.|PhD|Chefe)\s*', '', name, flags=re.IGNORECASE)
    # Remove titles at the end or degrees
    name = re.sub(r',?\s*(D\.Sc\.|M\.Sc\.|Ph\.D\.|PhD|DSc|MSc|Dr\.|Dra\.).*$', '', name, flags=re.IGNORECASE)
    # Remove trailing numbers or parens
    name = re.sub(r'\s*\(\d+\).*$', '', name)
    name = name.strip()
    return name

def is_valid_person_name(name):
    if not name or len(name) < 4 or len(name) > 70:
        return False
    # Filter out common UI texts
    invalid_keywords = [
        'disciplinas', 'cronograma', 'ementa', 'regimento', 'grade', 'horario',
        'processo', 'seleção', 'edital', 'noticias', 'notícia', 'corpo docente',
        'coordenacao', 'coordenação', 'secretaria', 'atendimento', 'departamento'
    ]
    name_lower = name.lower()
    if any(k in name_lower for k in invalid_keywords):
        return False
    # Must have at least two words
    words = name.split()
    if len(words) < 2:
        return False
    return True

def classify_siemens_specialization(dept, lab, text):
    content = (f"{dept} {lab} {text}").lower()
    specs = []

    # CFD & Fluid Mechanics
    if any(k in content for k in ['cfd', 'fluidos', 'fluido', 'termofluidodinâmica', 'fenômenos de transporte', 'hidráulica', 'aerodinâmica', 'escoamento', 'meios porosos', 'turbomáquinas']):
        specs.append("Termofluidodinâmica, CFD & Fenômenos de Transporte (STAR-CCM+ / Simcenter Flomaster)")

    # Finite Element Analysis & Structural Mechanics
    if any(k in content for k in ['elementos finitos', 'mecânica dos sólidos', 'estruturas', 'vibrações', 'acústica', 'dinâmica', 'materiais compósitos', 'ensaio mecânico', 'fadiga', 'elasticidade']):
        specs.append("Análise Estrutural, Vibrações, Acústica & Elementos Finitos (Simcenter 3D / Nastran / Femap)")

    # Process Simulation & Thermodynamics / Chemistry
    if any(k in content for k in ['termodinâmica', 'reatores', 'processos químicos', 'simulação de processos', 'destilação', 'polímeros', 'cinética']):
        specs.append("Engenharia de Processos, Termodinâmica & Simulação de Reatores (gPROMS / Simcenter Amesim)")

    # Control, Automation & Mechatronics
    if any(k in content for k in ['controle', 'automação', 'robótica', 'eletrônica de potência', 'sistemas dinâmicos', 'mechatronics', 'sensores', 'embarcados']):
        specs.append("Sistemas de Controle, Automação & Mecatrônica (Simcenter Amesim / HEEDS)")

    # Computational Modeling, HPC & AI / Analytics
    if any(k in content for k in ['computação de alto desempenho', 'hpc', 'inteligência artificial', 'aprendizado de máquina', 'analytics', 'métodos numéricos', 'otimização', 'modelagem computacional', 'supercomputação']):
        specs.append("Modelagem Computacional, HPC & Inteligência Artificial Aplicada (Simcenter HEEDS / MindSphere)")

    # CAD / CAM & Advanced Manufacturing
    if any(k in content for k in ['cad', 'cam', 'manufatura', 'usinagem', 'conformação', 'impressão 3d', 'manufatura aditiva', 'projeto mecânico']):
        specs.append("Projeto Mecânico CAD/CAM & Manufatura Avançada (NX CAD/CAM / Tecnomatix)")

    # Industrial Engineering & Operations Research
    if any(k in content for k in ['pesquisa operacional', 'logística', 'otimização de processos', 'cadeia de suprimentos', 'gestão da produção', 'ergonomia']):
        specs.append("Otimização Industrial, Logística & Pesquisa Operacional (Plant Simulation / Opcenter)")

    if not specs:
        specs.append("Modelagem Numérica, Simulação & Engenharia Aplicada (Siemens DISW Suite)")

    return " | ".join(specs)

def get_lgpd_department_email(dept_str):
    dept_lower = dept_str.lower()
    if 'mecan' in dept_lower or 'mecanica' in dept_lower:
        return 'mecanica@eng.uerj.br'
    elif 'deel' in dept_lower or 'eletronica' in dept_lower or 'eletrica' in dept_lower:
        return 'deel@eng.uerj.br'
    elif 'depro' in dept_lower or 'producao' in dept_lower:
        return 'depro@eng.uerj.br'
    elif 'deq' in dept_lower or 'quimica' in dept_lower:
        return 'deq@eng.uerj.br'
    elif 'civil' in dept_lower:
        return 'decivil@eng.uerj.br'
    elif 'iprj' in dept_lower or 'friburgo' in dept_lower or 'ppgmc' in dept_lower:
        return 'ppgmc@iprj.uerj.br'
    elif 'fat' in dept_lower or 'resende' in dept_lower:
        return 'fat@fat.uerj.br'
    elif 'ime' in dept_lower or 'ccomp' in dept_lower or 'compmat' in dept_lower:
        return 'ccomp@ime.uerj.br'
    elif 'inovuerj' in dept_lower or 'depinova' in dept_lower:
        return 'inovuerj@sr2.uerj.br'
    else:
        return 'secretaria@eng.uerj.br'
