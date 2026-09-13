import re

def clean_text(text):
    if not text:
        return ""

    replacements = {
        'Ã¡': 'á', 'Ã©': 'é', 'Ã­': 'í', 'Ã³': 'ó', 'Ãº': 'ú',
        'Ã£': 'ã', 'Ãµ': 'õ', 'Ã¢': 'â', 'Ãª': 'ê', 'Ã´': 'ô',
        'Ã§': 'ç', 'Ã': 'Á', 'Ã‰': 'É', 'ÃI': 'Í', 'ÃÓ': 'Ó', 'ÃÚ': 'Ú',
        'ÃÃo': 'ção', 'Ã§Ã£o': 'ção', 'Ã§Ãµes': 'ções',
        'â€“': '-', 'â€”': '-', 'â€œ': '"', 'â€': '"', 'â€™': "'",
        '\ufffd': '', '': ''
    }
    for old, new in replacements.items():
        text = text.replace(old, new)

    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def sanitize_name(name):
    name = clean_text(name)

    if ',' in name:
        name = name.split(',')[0].strip()
    if ' - ' in name:
        name = name.split(' - ')[0].strip()

    honorifics = [
        r'^Prof\.\s*', r'^Profa\.\s*', r'^Professor\s*', r'^Professora\s*',
        r'^Dr\.\s*', r'^Dra\.\s*', r'^Doutor\s*', r'^Doutora\s*',
        r'^Me\.\s*', r'^Msc\.\s*', r'^Eng\.\s*'
    ]
    for h in honorifics:
        name = re.sub(h, '', name, flags=re.IGNORECASE)

    name = re.sub(r'\s*\(.*?\)', '', name)
    name = re.sub(r'\b(LATTES|S)\b', '', name, flags=re.IGNORECASE)

    name = re.sub(r'\s+', ' ', name).strip()
    return name

def extract_specialization(bio, dept):
    bio_upper = bio.upper() if bio else ""
    dept_upper = dept.upper() if dept else ""

    specs = []

    # CFD & Fluid Mechanics
    if any(k in bio_upper for k in ['CFD', 'DINÂMICA DOS FLUIDOS COMPUTACIONAL', 'FLUIDODINÂMICA', 'TURBULÊNCIA', 'ESCOAMENTO', 'FENÔMENOS DE TRANSPORTE', 'MECÂNICA DOS FLUIDOS']):
        specs.append("CFD / Dinâmica dos Fluidos Computacional / Fenômenos de Transporte")

    # FEA & Structural Simulation
    if any(k in bio_upper for k in ['ELEMENTOS FINITOS', 'FEA', 'MECÂNICA DOS SÓLIDOS', 'ESTRUTURAS', 'VIBRAÇÕES', 'ACÚSTICA', 'SÓLIDOS', 'TENSÕES']):
        specs.append("Elementos Finitos (FEA) / Mecânica das Estruturas e Sólidos")

    # Thermal & Heat Transfer
    if any(k in bio_upper for k in ['TERMODINÂMICA', 'TRANSFERÊNCIA DE CALOR', 'MUDANÇA DE FASE', 'PROBLEMAS INVERSOS', 'TÉRMICA', 'REATOR']):
        specs.append("Termofluidodinâmica / Transferência de Calor / Termodinâmica")

    # Polymers & Materials
    if any(k in bio_upper for k in ['POLÍMEROS', 'COMPÓSITOS', 'MATERIAIS', 'ENGENHARIA DE MATERIAIS', 'CORROSÃO', 'REOLOGIA']):
        specs.append("Polímeros & Compósitos / Ciência dos Materiais / Corrosão")

    # Optimization, Process & CAD/CAM/Digital Twin
    if any(k in bio_upper for k in ['OTIMIZAÇÃO', 'PESQUISA OPERACIONAL', 'LOGÍSTICA', 'CAD/CAM', 'CAD', 'CAM', 'GÊMEOS DIGITAIS', 'DIGITAL TWIN', 'SIMULAÇÃO DE PROCESSOS']):
        specs.append("Otimização de Processos / Pesquisa Operacional / CAD-CAM")

    # AI & Scientific Computing / HPC
    if any(k in bio_upper for k in ['INTELIGÊNCIA ARTIFICIAL', 'APRENDIZADO DE MÁQUINA', 'MODELAGEM COMPUTACIONAL', 'MÉTODOS NUMÉRICOS', 'HPC', 'COMPUTAÇÃO DE ALTO DESEMPENHO', 'ALGORITMOS']):
        specs.append("Modelagem Computacional / Métodos Numéricos / IA & Analytics / HPC")

    # Control Systems & Automation
    if any(k in bio_upper for k in ['SISTEMAS DE CONTROLE', 'AUTOMAÇÃO', 'ELETRÔNICA DE POTÊNCIA', 'SISTEMAS EMBARCADOS', 'ROBÓTICA', 'PROCESSAMENTO DE SINAIS']):
        specs.append("Sistemas de Controle / Automação / Eletrônica de Potência")

    if not specs:
        if "MECAN" in dept_upper or "MECÂNICA" in dept_upper or "DME" in dept_upper:
            specs.append("Engenharia Mecânica / Térmica e Fluidos / Sólidos")
        elif "DEEL" in dept_upper or "ELETRÔNICA" in dept_upper or "DETEL" in dept_upper or "ELE" in dept_upper:
            specs.append("Sistemas de Controle e Automação / Eletrônica")
        elif "DEPRO" in dept_upper or "DENP" in dept_upper or "PRODUÇÃO" in dept_upper or "DEIN" in dept_upper:
            specs.append("Engenharia de Produção / Otimização e Processos")
        elif "DEQ" in dept_upper or "DEQA" in dept_upper or "QUÍMICA" in dept_upper:
            specs.append("Engenharia Química / Termodinâmica e Processos")
        elif "CIVIL" in dept_upper or "ESTR" in dept_upper or "DESC" in dept_upper:
            specs.append("Engenharia Civil / Estruturas e Métodos Numéricos")
        elif "DMC" in dept_upper or "COMPMAT" in dept_upper:
            specs.append("Modelagem Computacional / Métodos Numéricos e Computação Científica")
        else:
            specs.append("Engenharia Aplicada / Modelagem Numérica")

    return " ; ".join(specs)

if __name__ == "__main__":
    print("uerj_data_cleaner loaded successfully.")
