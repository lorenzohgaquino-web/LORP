import re
import html

# Siemens DISW Specialization Keywords Mapping
DISW_KEYWORDS = {
    "CFD / Termofluidodinâmica": [
        r"\bcfd\b", r"\btermofluidodin[âa]mica\b", r"\bmec[âa]nica dos fluidos\b", r"\btransporte de calor\b",
        r"\btransfer[êe]ncia de calor\b", r"\bfen[ôo]menos de transporte\b", r"\bmeios porosos\b", r"\baerodin[âa]mica\b",
        r"\bhidr[áa]ulica\b", r"\bseco / molhado\b", r"\bescoamento\b", r"\bsub-superf[íi]cie\b"
    ],
    "Simulação Estrutural / FEM / FEA": [
        r"\belementos finitos\b", r"\bfem\b", r"\bfea\b", r"\bmec[âa]nica dos s[óo]lidos\b", r"\bmec[âa]nica das estruturas\b",
        r"\bvibra[çc][õo]es\b", r"\bac[úu]stica\b", r"\bdin[âa]mica estrutural\b", r"\bfadiga\b", r"\btens[õo]es\b",
        r"\belastocinetica\b", r"\ban[áa]lise estrutural\b"
    ],
    "Modelagem Numérica & Métodos Computacionais": [
        r"\bmodelagem computacional\b", r"\bm[ée]todos num[ée]ricos\b", r"\bcomputa[çc][ãao] alt[oa] desempenho\b", r"\bhpc\b",
        r"\bmodelagem multiescala\b", r"\bsimula[çc][ãao] num[ée]rica\b", r"\bcomputa[çc][ãao] cient[íi]fica\b",
        r"\bsimula[çc][ãao] discreta\b", r"\bmodelagem matem[áa]tica\b"
    ],
    "Otimização, Processos & Manufatura": [
        r"\botimiza[çc][ãao]\b", r"\bpesquisa operacional\b", r"\bmanufatura\b", r"\bprocessos de fabrica[çc][ãao]\b",
        r"\bmanufatura aditiva\b", r"\bimpress[ãao] 3d\b", r"\blog[íi]stica\b", r"\bcadeia de suprimentos\b", r"\bpol[íi]meros\b",
        r"\bcomp[óo]sitos\b", r"\bautoma[çc][ãao]\b", r"\bcontrole de processos\b"
    ],
    "IA, Analytics & Gêmeos Digitais": [
        r"\bintelig[êe]ncia artificial\b", r"\bia\b", r"\bmachine learning\b", r"\baprendizado de m[áa]quina\b",
        r"\bdata science\b", r"\bci[êe]ncia de dados\b", r"\bg[êe]meos digitais\b", r"\bdigital twin\b", r"\bvis[ãao] computacional\b"
    ]
}

INVALID_NAME_PATTERNS = [
    r"coordena[çc][ãao]", r"departamento", r"secretaria", r"diretoria", r"laborat[óo]rio",
    r"programa", r"faculdade", r"instituto", r"centro", r"conselho", r"comiss[ãao]",
    r"professores", r"docentes", r"equipe", r"contato", r"p[óo]s-gradua[çc][ãao]", r"uerj"
]

def clean_string(text):
    if not text:
        return ""
    text = html.unescape(text)
    # Fix mojibake if present
    try:
        text = text.encode("iso-8859-1").decode("utf-8")
    except (UnicodeEncodeError, UnicodeDecodeError):
        pass
    # Clean control characters and weird spaces
    text = re.sub(r"[\r\n\t\xa0]+", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

def strip_degrees(name):
    name = clean_string(name)
    # Remove titles like Prof., Dr., Dra., Ph.D., Eng.
    name = re.sub(r"^(Prof[a]?\.|Dr[a]?\.|Ph\.?D\.?|Eng[a]?\.|Msc\.|Pesquisador[a]?)\s+", "", name, flags=re.IGNORECASE)
    name = re.sub(r"^(Prof[a]?|Dr[a]?)\b\s*", "", name, flags=re.IGNORECASE)
    return name.strip()

def is_valid_person_name(name):
    name = strip_degrees(name)
    if not name or len(name) < 4:
        return False
    for pat in INVALID_NAME_PATTERNS:
        if re.search(pat, name, re.IGNORECASE):
            return False
    # Name should have at least two words
    words = name.split()
    if len(words) < 2:
        return False
    return True

def classify_specialization(text, default_dept_spec="Engenharia / Modelagem Computacional"):
    if not text:
        return default_dept_spec
    matched_categories = []
    text_lower = text.lower()
    for cat, patterns in DISW_KEYWORDS.items():
        for pat in patterns:
            if re.search(pat, text_lower):
                matched_categories.append(cat)
                break
    if matched_categories:
        return "; ".join(matched_categories)
    return default_dept_spec
