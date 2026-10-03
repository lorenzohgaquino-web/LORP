import re
import unicodedata

def clean_text(text):
    if not text:
        return ""
    text = unicodedata.normalize('NFKC', text)
    text = re.sub(r'[\r\n\t]+', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def is_valid_person_name(name):
    name_clean = clean_text(name)
    if not name_clean or len(name_clean.split()) < 2:
        return False

    forbidden = [
        'ppg', 'programa', 'página', 'linha', 'doutorado', 'mestrado',
        'processo', 'secretaria', 'lattes', 'docentes', 'serviços',
        'contato', 'universidade', 'faculdade', 'instituto', 'departamento',
        'disciplina', 'regulamento', 'laboratório', 'resultado', 'edital',
        'membros', 'professores', 'pesquisadores', 'alunos', 'notícias',
        'conheça', 'corpo', 'filtre', 'eng', 'iprj', 'uerj', 'fat'
    ]
    name_lower = name_clean.lower()
    if any(f in name_lower for f in forbidden):
        return False
    if re.search(r'\d', name_clean):
        return False
    return True

def clean_name(name):
    name = clean_text(name)

    # Strip titles, roles, honorifics from anywhere in the string
    roles = [
        r'Prof(?:essor|a)?\.?\s*Colaborador(?:a)?',
        r'Prof(?:essor|a)?\.?\s*Visitante',
        r'Prof(?:essor|a)?\.?\s*Titular',
        r'Prof(?:essor|a)?\.?\s*Adjunto(?:a)?',
        r'Prof(?:essor|a)?\.?\s*Associado(?:a)?',
        r'Prof(?:essor|a)?\.?\s*Emérito(?:a)?',
        r'Prof(?:essor|a)?\.?\s*Substituto(?:a)?',
        r'Prof(?:essor|a)?\.?',
        r'Dr(?:a)?\.?',
        r'Ph\.?D\.?',
        r'MSc\.?',
        r'DSc\.?',
        r'Eng\.?',
        r'\(Coordenador(?:a)?\)',
        r'\(Vice-Coordenador(?:a)?\)',
        r'\(Chefe\)',
        r'\(Diretor(?:a)?\)',
        r'\(Líder\)'
    ]
    for r in roles:
        name = re.sub(r, '', name, flags=re.IGNORECASE)

    name = re.sub(r'^\d+\.?\s*', '', name)
    name = re.sub(r'[\(\)\[\]]', '', name)
    return clean_text(name)

def clean_email(email):
    if not email:
        return ""
    email = email.lower().strip()
    email = re.sub(r'^(mailto:|email:\s*|e-mail:\s*)', '', email)
    if re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
        return email
    return ""

def clean_lattes(url):
    if not url:
        return ""
    url = url.strip()
    match = re.search(r'lattes\.cnpq\.br/(\d{16})', url)
    if match:
        return f"https://lattes.cnpq.br/{match.group(1)}"
    if "lattes.cnpq.br/search" in url or "buscatextual.cnpq.br" in url:
        return url
    return url

def infer_specialization(text, name=""):
    text_lower = text.lower()
    specs = []

    if re.search(r'\bcfd\b|fluidodinâmica|dinâmica dos fluidos|mecânica dos fluidos|escoamento|aerodinâmica|hidrodinâmica|turbomáquinas', text_lower):
        specs.append("CFD / Termofluidodinâmica")
    if re.search(r'elementos finitos|\bfem\b|\bfea\b|sólidos|mecânica dos sólidos|estruturas|elasticidade|plasticidade', text_lower):
        specs.append("Métodos Numéricos / Elementos Finitos (FEA)")
    if re.search(r'térmica|termodinâmica|transferência de calor|combustão|refrigeração|energia|trocadores de calor', text_lower):
        specs.append("Termodinâmica e Transferência de Calor")
    if re.search(r'vibrações|acústica|ruído|dinâmica das estruturas|vibroacústica', text_lower):
        specs.append("Vibrações e Acústica")
    if re.search(r'controle|automação|eletrônica de potência|sistemas dinâmicos|robótica|mecatrônica', text_lower):
        specs.append("Sistemas de Controle e Automação")
    if re.search(r'otimização|pesquisa operacional|logística|gestão da produção|manufatura', text_lower):
        specs.append("Otimização de Processos e Manufatura")
    if re.search(r'polímeros|compósitos|materiais|metalurgia|caracterização de materiais|nanomateriais', text_lower):
        specs.append("Ciência e Engenharia de Materiais")
    if re.search(r'inteligência artificial|aprendizado de máquina|machine learning|analytics|computação de alto desempenho|\bhpc\b|modelagem matemática|modelagem computacional', text_lower):
        specs.append("Modelagem Computacional / IA / HPC")
    if re.search(r'inovação|propriedade intelectual|patentes|parcerias|transferência de tecnologia', text_lower):
        specs.append("Gestão de Inovação e Transferência Tecnológica")

    if not specs:
        specs.append("Engenharia e Modelagem Aplicada")

    return " | ".join(sorted(list(set(specs))))

if __name__ == "__main__":
    print("Testing uerj_data_cleaner.py...")
    print("Clean name 1:", clean_name("FERNANDO CARVALHO DA SILVAProf. Colaborador"))
    print("Clean name 2:", clean_name("HELIO MIGONProf. Visitante"))
