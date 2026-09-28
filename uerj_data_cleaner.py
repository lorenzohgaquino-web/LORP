import re
import html

def clean_text(text: str) -> str:
    if not text:
        return ""
    # Unescape HTML
    text = html.unescape(text)
    # Fix common mojibake / latin-1 issues
    try:
        if 'Ã' in text or 'Â' in text:
            text = text.encode('latin1').decode('utf-8')
    except Exception:
        pass
    # Replace unicode replacement char
    text = text.replace('\ufffd', '')
    # Strip honorifics
    text = re.sub(r'^(Prof\.|Profa\.|Dr\.|Dra\.|Ph\.D\.|PhD|Profª|Profº)\s*', '', text, flags=re.IGNORECASE)
    # Strip navigation text / UI noise
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def is_valid_person_name(name: str) -> bool:
    if not name or len(name) < 3:
        return False
    invalid_keywords = [
        'departamento', 'coordenacao', 'laboratorio', 'secretaria', 'diretoria',
        'faculdade', 'instituto', 'engenharias', 'uerj', 'iprj', 'fat', 'fen', 'ime'
    ]
    name_lower = name.lower()
    for kw in invalid_keywords:
        if kw in name_lower:
            return False
    return True

def map_specialization(text: str) -> str:
    text_lower = text.lower()
    specs = []

    # Use word boundary or specific regex to prevent false positives like 'acadêmica' matching 'cad'
    if re.search(r'\bcfd\b|fluidos|termofluido|aerodinâmica|escoamento', text_lower):
        specs.append("CFD & Termofluidodinâmica (STAR-CCM+)")
    if re.search(r'\belementos finitos\b|\bfea\b|\bfem\b|estruturas|sólidos|tensões', text_lower):
        specs.append("Elementos Finitos & Análise Estrutural (Simcenter)")
    if re.search(r'\bcad\b|\bcam\b|modelagem 3d|geometria computacional', text_lower):
        specs.append("CAD/CAM & Modelagem Geométrica (NX)")
    if re.search(r'otimização|pesquisa operacional|logística|simulação discreta', text_lower):
        specs.append("Otimização de Processos & Pesquisa Operacional (Plant Simulation)")
    if re.search(r'inteligência artificial|\bia\b|machine learning|aprendizado de máquina|hpc|supercomputação', text_lower):
        specs.append("IA & Computação de Alto Desempenho (HPC)")
    if re.search(r'polímeros|compósitos|materiais|metalurgia', text_lower):
        specs.append("Engenharia de Materiais & Manufatura Avançada")
    if re.search(r'inovação|propriedade intelectual|patentes|transferência de tecnologia', text_lower):
        specs.append("Gestão de Inovação & Propriedade Intelectual")

    if not specs:
        specs.append("Modelagem Computacional & Simulação Numérica")

    return "; ".join(specs)
