import re
# Cleaner utility functions

def fix_encoding(text: str) -> str:
    if not text:
        return ""
    # Common Mojibake fixes for Latin-1 / UTF-8 misencodings
    try:
        if "Ã" in text or "Â" in text or "â" in text:
            bytes_text = text.encode("iso-8859-1")
            text = bytes_text.decode("utf-8")
    except Exception:
        pass
    text = text.replace("\ufffd", "").replace("", "")
    return text.strip()

def clean_text(text: str) -> str:
    if not text:
        return ""
    text = fix_encoding(text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def strip_honorifics(name: str) -> str:
    if not name:
        return ""
    name = clean_text(name)

    # Strip department suffix tags like DMC, DEMEC, DEMAT, PPGMC, PPGCTM appended at end
    name = re.sub(r'\s+(DMC|DEMEC|DEMAT|PPGMC|PPGCTM)(\s*,\s*(DMC|DEMEC|DEMAT|PPGMC|PPGCTM))*$', '', name, flags=re.IGNORECASE)

    # Strip prefixes repeatedly until clean
    prev_name = ""
    while prev_name != name:
        prev_name = name
        titles = [
            r"^(Profª?|Profa?)\.?\s*",
            r"^Dra?\.?\s*",
            r"^Ph\.?D\.?\s*",
            r"^MSc\.?\s*",
            r"^Engª?\.?\s*",
            r"^Pesquisador\(a\)?\s*",
            r"^Coordenador\(a\)?\s*",
            r"^a\.\s+"
        ]
        for t in titles:
            name = re.sub(t, "", name, flags=re.IGNORECASE).strip()

    return name.strip()

INVALID_NAME_TERMS = [
    "corpo docente", "departamento", "coordenação", "secretaria", "graduação",
    "pós-graduação", "engenharias", "professores", "disciplinas", "home", "contato",
    "laboratório", "grupo", "pesquisa", "universidade", "página", "editais",
    "avenida", "av.", "rua", "resende", "bloco", "campus", "sala", "andar", "bairro", "cep",
    "bacharelado", "licenciatura", "processo seletivo", "edital", "resultado", "professor substituto",
    "essor online", "concurso"
]

def is_valid_person_name(name: str) -> bool:
    if not name:
        return False
    clean_n = strip_honorifics(name)
    if len(clean_n.split()) < 2:
        return False
    lower_n = clean_n.lower()
    for term in INVALID_NAME_TERMS:
        if term in lower_n:
            return False
    if re.search(r'\d', clean_n):
        return False
    return True

DEPARTMENT_FALLBACK_EMAILS = {
    "FEN/MECAN": "mecan@eng.uerj.br",
    "FEN/DEEL": "deel@eng.uerj.br",
    "FEN/DEPRO": "depro@eng.uerj.br",
    "FEN/DEQ": "deq@eng.uerj.br",
    "FEN/Civil": "decivil@eng.uerj.br",
    "IME/PPG-COMPMAT": "ppgcompmat@ime.uerj.br",
    "IME/IF": "diretoria@fis.uerj.br",
    "IME/IQ": "posdir@iq.uerj.br",
    "IPRJ/PPGMC": "ppgmc@iprj.uerj.br",
    "IPRJ/DEMEC": "demec@iprj.uerj.br",
    "IPRJ/DMC": "dmc@iprj.uerj.br",
    "IPRJ/DEMAT": "demat@iprj.uerj.br",
    "FAT/DME": "dme@fat.uerj.br",
    "FAT/DENP": "denp@fat.uerj.br",
    "FAT/DEQA": "deqa@fat.uerj.br",
    "GESAR": "gesar@uerj.br",
    "InovUerj": "inovuerj@uerj.br"
}

def get_fallback_email(unit_key: str) -> str:
    for key, email in DEPARTMENT_FALLBACK_EMAILS.items():
        if key.lower() in unit_key.lower():
            return email
    return "secretaria@uerj.br"

TECHNICAL_KEYWORDS = {
    "CFD / Fluidodinâmica": [r"\bcfd\b", r"\bcomputational fluid dynamics\b", r"\bdinâmica dos fluidos\b", r"\btermofluidodinâmica\b", r"\bescoamento\b", r"\bmeios porosos\b"],
    "Elementos Finitos / FEA": [r"\belementos finitos\b", r"\bfea\b", r"\bfem\b", r"\bmecânica dos sólidos\b", r"\banálise estrutural\b", r"\btensões\b"],
    "CAD / CAM / CAE / Manufatura": [r"\bcad\b(?!\s*a\b)", r"\bcam\b", r"\bcae\b", r"\bmanufatura aditiva\b", r"\businagem\b", r"\bimpressão 3d\b"],
    "Gêmeos Digitais / IoT / IA": [r"\bgêmeos digitais\b", r"\bdigital twin\b", r"\binteligência artificial\b", r"\bmachine learning\b", r"\baprendizado de máquina\b", r"\banalytics\b"],
    "HPC / Computação de Alto Desempenho": [r"\bhpc\b", r"\bcomputação de alto desempenho\b", r"\bparalelismo\b", r"\bsupercomputa", r"\bcluster\b"],
    "Controle, Automação & Robótica": [r"\bsistemas de controle\b", r"\bautomação\b", r"\brobótica\b", r"\beletrônica de potência\b"],
    "Otimização & Processos": [r"\botimização\b", r"\bpesquisa operacional\b", r"\blogística\b", r"\bsimulação de processos\b", r"\breatores\b"],
    "Termodinâmica & Materiais": [r"\btermodinâmica\b", r"\bpolímeros\b", r"\bcompósitos\b", r"\bciência dos materiais\b", r"\bcorrosão\b"]
}

def classify_specialization(research_text: str) -> str:
    if not research_text:
        return "Engenharia & Modelagem Computacional Generalista"
    matched = []
    text_lower = research_text.lower()
    for category, patterns in TECHNICAL_KEYWORDS.items():
        for pat in patterns:
            if re.search(pat, text_lower):
                matched.append(category)
                break
    if matched:
        return "; ".join(matched)
    return "Engenharia & Modelagem Computacional Generalista"
