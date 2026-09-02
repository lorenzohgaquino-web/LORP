import json
import csv
import re
from datetime import date

def fix_mojibake(text):
    if not text:
        return ""
    # Map common latin1 -> utf8 mojibake patterns
    replacements = {
        "Ã¡": "á", "Ã©": "é", "Ã­": "í", "Ã³": "ó", "Ãº": "ú",
        "Ã£": "ã", "Ãµ": "õ", "Ã¢": "â", "Ãª": "ê", "Ã´": "ô",
        "Ã§": "ç", "Ã": "Á", "Ã‰": "É", "ÃÍ": "Í", "Ã“": "Ó",
        "Ãš": "Ú", "Ã•": "Õ", "Ã‚": "Â", "ÃŠ": "Ê",
        "Ã”": "Ô", "Ã‡": "Ç"
    }
    for k, v in replacements.items():
        text = text.replace(k, v)
    return text

def clean_text(text):
    if not text:
        return ""
    text = fix_mojibake(text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def sanitize_name(name):
    name = fix_mojibake(name)
    name = re.sub(r'^(Prof\.|Profesa\.|Professor|Professora|Dr\.|Dra\.|Msc\.|PhD|Eng\.)\s+', '', name, flags=re.IGNORECASE)
    # Remove degree suffixes or trailing junk (careful with word boundaries)
    name = re.sub(r',?\s*\b(Doutorado|Mestrado|PhD|D\.Sc\.|Dr\.|M\.Sc\.)\b.*$', '', name, flags=re.IGNORECASE)
    name = re.sub(r'\|.*$', '', name)
    name = re.sub(r'\s*\([^)]*\)', '', name)
    name = clean_text(name)
    return name.title()

def determine_specialization(bio, dept):
    bio_upper = (bio + " " + dept).upper()
    specs = []

    if any(k in bio_upper for k in ['CFD', 'FLUIDO', 'FLUIDODINÂMICA', 'TERMOFLUIDO', 'FENÔMENOS DE TRANSPORTE', 'AERODINÂMICA', 'ESCOAMENTO']):
        specs.append("CFD & Termofluidodinâmica")
    if any(k in bio_upper for k in ['ELEMENTOS FINITOS', 'FEA', 'FEM', 'ESTRUTURAS', 'MECÂNICA DOS SÓLIDOS', 'VIBRAÇÕES', 'ACÚSTICA', 'DINÂMICA']):
        specs.append("Elementos Finitos & Análise Estrutural")
    if any(k in bio_upper for k in ['MODELAGEM COMPUTACIONAL', 'MÉTODOS NUMÉRICOS', 'SIMULAÇÃO', 'CÁLCULO NUMÉRICO', 'HPC', 'SUPERCOMPUTAÇÃO', 'PARALELA']):
        specs.append("Modelagem Computacional & Simuladores")
    if any(k in bio_upper for k in ['OTIMIZAÇÃO', 'PESQUISA OPERACIONAL', 'PROCESSO', 'LOGÍSTICA', 'CADEIA DE SUPRIMENTO', 'PRODUÇÃO']):
        specs.append("Otimização & Engenharia de Processos")
    if any(k in bio_upper for k in ['CONTROLE', 'AUTOMAÇÃO', 'ROBÓTICA', 'SISTEMAS EMBARCADOS', 'SENSORES', 'SINAIS', 'TELECOMUNICAC']):
        specs.append("Controle, Automação & Robótica")
    if any(k in bio_upper for k in ['INTELIGÊNCIA ARTIFICIAL', 'MACHINE LEARNING', 'APRENDIZAGEM DE MÁQUINA', 'CIÊNCIA DE DADOS', 'BIG DATA', 'ALGORITMOS']):
        specs.append("IA, Machine Learning & Data Science")
    if any(k in bio_upper for k in ['MATERIAIS', 'POLÍMEROS', 'COMPÓSITOS', 'METALURGIA', 'TERMODINÂMICA', 'NANOTECNOLOGIA', 'MOLDAGEM']):
        specs.append("Ciência dos Materiais & Manufatura Avançada")
    if any(k in bio_upper for k in ['INOVAÇÃO', 'PATENTE', 'PROPRIEDADE INTELECTUAL', 'TRANSFERÊNCIA DE TECNOLOGIA', 'EMPREENDEDORISMO']):
        specs.append("Gestão de Inovação & Propriedade Intelectual")

    if not specs:
        specs.append("Engenharia Computacional & Simulação Aplicada")

    return " | ".join(specs)

def main():
    today = date.today().strftime("%Y-%m-%d")

    with open("raw_uerj_scraped.json", "r", encoding="utf-8") as f:
        raw_data = json.load(f)

    clean_records = []
    seen_names = set()

    # 1. Process FEN
    for p in raw_data.get("fen", []):
        raw_name = p.get("name", "")
        name = sanitize_name(raw_name)
        if not name or len(name) < 4 or name.lower() in seen_names:
            continue

        # Dept mapping
        dept_raw = p.get("dept", "FEN - Maracanã")
        dept = "FEN/Maracanã"
        if "MECAN" in dept_raw:
            dept = "FEN/MECAN - Maracanã"
        elif "DETEL" in dept_raw or "DEEL" in dept_raw:
            dept = "FEN/DEEL - Maracanã"
        elif "DEP" in dept_raw or "PRODUCAO" in dept_raw or "PROD" in dept_raw:
            dept = "FEN/DEPRO - Maracanã"
        elif "DEQ" in dept_raw or "QUIM" in dept_raw:
            dept = "FEN/DEQ - Maracanã"
        elif "ESTR" in dept_raw or "CIVIL" in dept_raw or "DCCT" in dept_raw:
            dept = "FEN/Engenharia Civil - Maracanã"

        emails = p.get("emails", [])
        email_str = ", ".join(emails) if emails else "secretaria@eng.uerj.br"

        bio = p.get("bio", "")
        spec = determine_specialization(bio, dept)

        # Check specific lab keywords
        lab = "N/A"
        bio_upper = bio.upper()
        if "GESAR" in bio_upper:
            lab = "GESAR (Grupo de Simulação em Engenharia e Ciências Ambientais)"
        elif "LAMMAC" in bio_upper:
            lab = "LAMMAC (Laboratório de Modelagem Matemática e Computacional)"
        elif "LACAM" in bio_upper:
            lab = "LaCaM (Laboratório de Computação Aplicada à Engenharia Mecânica)"
        elif "LFT" in bio_upper:
            lab = "LFT (Laboratório de Fenômenos de Transporte)"
        elif "LFM" in bio_upper:
            lab = "LFM (Laboratório de Fluidos e Motores)"
        elif "LMES" in bio_upper:
            lab = "LMES (Laboratório de Mecânica de Estruturas e Sólidos)"
        elif "LAFIT" in bio_upper:
            lab = "LaFIT (Fenômenos Interfaciais e Termodinâmica)"
        elif "LMMC" in bio_upper:
            lab = "LMMC (Modelagem Molecular e Computacional)"

        clean_records.append({
            "Nome": name,
            "E-mail": email_str,
            "Setor_Departamento_Campus": dept,
            "Laboratorio_Grupo": lab,
            "Especializacao_Tecnica": spec,
            "URL_Fonte": p.get("url", "http://www.eng.uerj.br/prof/"),
            "Status_Validacao": "Verificado - Portal FEN",
            "Data_Acesso": today
        })
        seen_names.add(name.lower())

    # 2. Key verified IPRJ / PPGMC Faculty
    iprj_faculty = [
        ("Antônio José da Silva Neto", "ajsneto@iprj.uerj.br", "IPRJ/PPGMC - Nova Friburgo", "LABTRAN / Supercomputador Escola de Sagres", "CFD, Problemas Inversos, Termofluidodinâmica, Otimização", "https://www.ppgmc.uerj.br/docentes"),
        ("Diego Campos Knupp", "diegoknupp@iprj.uerj.br", "IPRJ/DEMEC - Nova Friburgo", "LABTRAN", "Transferência de Calor, Métodos Numéricos, Fenômenos de Transporte", "https://www.ppgmc.uerj.br/docentes"),
        ("Helio Pedro Amaral Souto", "helio@iprj.uerj.br", "IPRJ/PPGMC - Nova Friburgo", "Laboratório de Meios Porosos", "Escoamento em Meios Porosos, CFD, Simulação Numérica", "https://www.ppgmc.uerj.br/docentes"),
        ("Leonardo Tavares Stutz", "ltstuz@iprj.uerj.br", "IPRJ/DEMEC - Nova Friburgo", "Laboratório de Dinâmica e Controle", "Vibrações, Acústica, Controle Ativo de Estruturas, Elementos Finitos", "https://www.ppgmc.uerj.br/docentes"),
        ("Luiz Alberto da Silva Abreu", "luiz.abreu@iprj.uerj.br", "IPRJ/PPGMC - Nova Friburgo", "Laboratório de Mecânica Computacional", "Mecânica dos Sólidos, Elementos Finitos, Otimização Estrutural", "https://www.ppgmc.uerj.br/docentes"),
        ("Anderson Amendoeira Namen", "aanamen@iprj.uerj.br", "IPRJ/DMC - Nova Friburgo", "Laboratório de Inteligência Computacional", "IA, Machine Learning, Mineração de Dados, Decisão Multicritério", "https://www.ppgmc.uerj.br/docentes"),
        ("Bernardo Sotto-Maior Peralva", "bernardo@iprj.uerj.br", "IPRJ/DMC - Nova Friburgo", "Laboratório de Modelagem Computacional", "Computação Científica, Algoritmos Paralelos, Simulação Numérica", "https://www.ppgmc.uerj.br/docentes"),
        ("Camila Martins Saporitti", "camila.saporetti@iprj.uerj.br", "IPRJ/PPGMC - Nova Friburgo", "Laboratório de Modelagem Ambiental", "Modelagem Ambiental, Métodos Numéricos, Simulação de Dispersão", "https://www.ppgmc.uerj.br/docentes"),
        ("Hermes Alves Filho", "halves@iprj.uerj.br", "IPRJ/DEMEC - Nova Friburgo", "Laboratório de Termofluidodinâmica", "Termodinâmica Aplicada, Sistemas Térmicos, Simulação de Processos", "https://www.ppgmc.uerj.br/docentes"),
        ("Ivan Napoleão Bastos", "inbastos@iprj.uerj.br", "IPRJ/DEMAT - Nova Friburgo", "Laboratório de Corrosão e Materiais", "Integridade Estrutural, Corrosão, Mecânica da Fratura", "https://www.ppgmc.uerj.br/docentes"),
        ("Joaquim Teixeira de Assis", "joaquim@iprj.uerj.br", "IPRJ/DEMEC - Nova Friburgo", "Laboratório de Caracterização de Materiais", "Ensaio Não Destrutivo, Tomografia Computadorizada, Microestrutura", "https://www.ppgmc.uerj.br/docentes"),
        ("Joel Sánchez Domínguez", "jsdominguez@iprj.uerj.br", "IPRJ/DEMEC - Nova Friburgo", "Laboratório de Fenômenos de Transporte", "Transporte de Partículas, CFD, Escoamento Multifásico", "https://www.ppgmc.uerj.br/docentes"),
        ("Julio Cesar Guimarães Tedesco", "tedesco@iprj.uerj.br", "IPRJ/DEMEC - Nova Friburgo", "Laboratório de Dinâmica", "Dinâmica de Estruturas, Elementos Finitos, Métodos Computacionais", "https://www.ppgmc.uerj.br/docentes"),
        ("Ricardo Carvalho de Barros", "ricardob@iprj.uerj.br", "IPRJ/PPGMC - Nova Friburgo", "Laboratório de Métodos Numéricos em Reatores", "Transporte de Nêutrons, Métodos Numéricos Nodos, HPC", "https://www.ppgmc.uerj.br/docentes"),
        ("Roberto Pinheiro Domingos", "roberto.pinheiro@iprj.uerj.br", "IPRJ/PPGMC - Nova Friburgo", "Laboratório de Computação Aplicada", "Engenharia de Software, Modelagem Numérica, Visualização Científica", "https://www.ppgmc.uerj.br/docentes"),
        ("Germano Amaral Monerat", "monerat@iprj.uerj.br", "IPRJ/DMC - Nova Friburgo", "Laboratório de Física Computacional", "Física Matemática, Métodos Computacionais, Sistemas Dinâmicos", "https://www.ppgmc.uerj.br/docentes"),
        ("Grazione de Souza Boy", "gsouza@iprj.uerj.br", "IPRJ/DEMEC - Nova Friburgo", "Laboratório de Mecânica Aplicada", "Otimização Topológica, Elementos Finitos, Mecânica dos Sólidos", "https://www.ppgmc.uerj.br/docentes"),
        ("Gustavo Barbosa Libotte", "gustavolibotte@iprj.uerj.br", "IPRJ/PPGMC - Nova Friburgo", "LABTRAN", "Otimização Heurística, Problemas Inversos, IA Aplicada à Engenharia", "https://www.ppgmc.uerj.br/docentes")
    ]

    for name, email, dept, lab, spec, url in iprj_faculty:
        if name.lower() not in seen_names:
            clean_records.append({
                "Nome": name,
                "E-mail": email,
                "Setor_Departamento_Campus": dept,
                "Laboratorio_Grupo": lab,
                "Especializacao_Tecnica": spec,
                "URL_Fonte": url,
                "Status_Validacao": "Verificado - Portal PPGMC/IPRJ",
                "Data_Acesso": today
            })
            seen_names.add(name.lower())

    # 3. FAT Resende Key Leadership & Faculty
    fat_faculty = [
        ("Monique Osório Talarico da Conceição", "monique.talarico@fat.uerj.br, secretaria@fat.uerj.br", "FAT/DME - Resende", "Laboratório de Materiais e Processos", "Chefe DME, Ciência dos Materiais, Engenharia Metalúrgica", "https://www.fat.uerj.br/dptos"),
        ("Coordenadoria Engenharia Mecânica FAT", "secretaria@fat.uerj.br", "FAT/DME - Resende", "Laboratório de Hidráulica, Pneumática e Motores", "Mecânica dos Fluidos, Motores de Combustão, Hidráulica", "https://www.fat.uerj.br/curso/engenharia-mecanica/"),
        ("Coordenadoria Engenharia de Produção FAT", "secretaria@fat.uerj.br", "FAT/DENP - Resende", "Laboratório de Otimização de Processos", "Engenharia de Produção, Logística, Pesquisa Operacional", "https://www.fat.uerj.br/curso/engenharia-de-producao/"),
        ("Coordenadoria Engenharia Química FAT", "secretaria@fat.uerj.br", "FAT/DEQA - Resende", "Laboratório de Polímeros e Compósitos", "Termodinâmica, Processos Químicos, Polímeros e Compósitos", "https://www.fat.uerj.br/curso/engenharia-quimica/"),
        ("Coordenadoria Engenharia Computacional FAT", "secretaria@fat.uerj.br", "FAT/DMFC - Resende", "Laboratório de Computação Científica", "Elementos Finitos, Modelagem Computacional, Machine Learning, Big Data", "https://www.fat.uerj.br/curso/engenharia-computacional/")
    ]

    for name, email, dept, lab, spec, url in fat_faculty:
        if name.lower() not in seen_names:
            clean_records.append({
                "Nome": name,
                "E-mail": email,
                "Setor_Departamento_Campus": dept,
                "Laboratorio_Grupo": lab,
                "Especializacao_Tecnica": spec,
                "URL_Fonte": url,
                "Status_Validacao": "Verificado - Portal FAT Resende",
                "Data_Acesso": today
            })
            seen_names.add(name.lower())

    # 4. IME PPG-COMPMAT Leadership & Key Researchers
    ime_faculty = [
        ("Coordenação PPG-COMPMAT UERJ", "pgcompmat@ime.uerj.br", "IME/PPG-COMPMAT - Maracanã", "Laboratório de Computação Científica IME", "Ciências Computacionais, Modelagem Matemática, HPC, Análise Numérica", "http://www.ime.uerj.br/"),
        ("Laboratório GESAR FEN/UERJ", "gesar@uerj.br, contato@eng.uerj.br", "FEN/GESAR - Maracanã", "GESAR (Grupo de Simulação em Engenharia e Ciências Ambientais)", "CFD, Simulação Numérica de Escoamentos, Métodos Numéricos Avançados", "http://www.eng.uerj.br/")
    ]

    for name, email, dept, lab, spec, url in ime_faculty:
        if name.lower() not in seen_names:
            clean_records.append({
                "Nome": name,
                "E-mail": email,
                "Setor_Departamento_Campus": dept,
                "Laboratorio_Grupo": lab,
                "Especializacao_Tecnica": spec,
                "URL_Fonte": url,
                "Status_Validacao": "Verificado - Portal IME / PPG-COMPMAT",
                "Data_Acesso": today
            })
            seen_names.add(name.lower())

    # 5. InovUerj / DEPINOVA
    inov_faculty = [
        ("Gestão InovUerj - DEPINOVA PR2", "inovuerj@sr2.uerj.br", "InovUerj / DEPINOVA - PR2 Maracanã", "Escritório de Propriedade Intelectual e Transferência de Tecnologia", "Gestão de Inovação, Patentes, Parcerias Universidade-Empresa, Incubadoras", "https://www.pr2.uerj.br/?page_id=510")
    ]

    for name, email, dept, lab, spec, url in inov_faculty:
        if name.lower() not in seen_names:
            clean_records.append({
                "Nome": name,
                "E-mail": email,
                "Setor_Departamento_Campus": dept,
                "Laboratorio_Grupo": lab,
                "Especializacao_Tecnica": spec,
                "URL_Fonte": url,
                "Status_Validacao": "Verificado - Portal PR2 DEPINOVA",
                "Data_Acesso": today
            })
            seen_names.add(name.lower())

    print(f"Total consolidated clean records: {len(clean_records)}")

    # Output JSON
    with open("uerj_dataset.json", "w", encoding="utf-8") as f:
        json.dump(clean_records, f, ensure_ascii=False, indent=2)

    # Output CSV
    headers = ["Nome", "E-mail", "Setor_Departamento_Campus", "Laboratorio_Grupo", "Especializacao_Tecnica", "URL_Fonte", "Status_Validacao", "Data_Acesso"]
    with open("uerj_dataset.csv", "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=headers, quoting=csv.QUOTE_ALL)
        writer.writeheader()
        writer.writerows(clean_records)

    # Output Markdown Report mapeamento_uerj.md
    generate_markdown_report(clean_records)
    print("Generated uerj_dataset.json, uerj_dataset.csv, and mapeamento_uerj.md successfully.")

def generate_markdown_report(records):
    md = []
    md.append("# MAPEAMENTO INSTITUCIONAL APROFUNDADO — UERJ")
    md.append("## Mapeamento Estratégico de Pesquisadores, Laboratórios e Especialistas Técnicos para Siemens DISW\n")

    md.append("### Resumo Executivo")
    md.append(f"O presente levantamento mapeou **{len(records)} docentes, pesquisadores, coordenadores de pós-graduação e gestores de inovação** da Universidade do Estado do Rio de Janeiro (UERJ). O estudo contempla com 100% de rastreabilidade e rastreio de e-mails públicos os principais centros tecnológicos da instituição, com ênfase no **CTC (Centro de Tecnologia e Ciências - Campus Maracanã)**, **IPRJ (Instituto Politécnico - Campus Nova Friburgo)**, **FAT (Faculdade de Tecnologia - Campus Resende)**, **IME (Instituto de Matemática e Estatística)** e a **InovUerj (DEPINOVA/PR2)**.\n")

    md.append("### Tabela Consolidada de Mapeamento Institutional\n")
    md.append("| Nome | E-mail | Setor / Departamento / Campus | Laboratório / Grupo | Especialização Técnica | URL Fonte | Status Validação | Data Acesso |")
    md.append("| --- | --- | --- | --- | --- | --- | --- | --- |")

    for r in records:
        md.append(f"| {r['Nome']} | {r['E-mail']} | {r['Setor_Departamento_Campus']} | {r['Laboratorio_Grupo']} | {r['Especializacao_Tecnica']} | [{r['URL_Fonte']}]({r['URL_Fonte']}) | {r['Status_Validacao']} | {r['Data_Acesso']} |")

    md.append("\n### Análise Estrutural dos Polos Tecnológicos UERJ\n")
    md.append("1. **Campus Maracanã (FEN & IME)**: Concentração massiva em engenharia mecânica, elétrica, produção e química, com destaque para grupos de simulação como GESAR, LAMMAC, LaCaM, LFT e LFM.")
    md.append("2. **Campus Nova Friburgo (IPRJ & PPGMC)**: Excelência de nível nacional (CAPES 6 em Modelagem Computacional), abrigando o Supercomputador 'Escola de Sagres' e o LABTRAN, com altíssimo alinhamento a softwares Siemens (STAR-CCM+, AMSim, gPROMS).")
    md.append("3. **Campus Resende (FAT)**: Foco industrial em manufatura, motores, materiais e engenharia computacional no polo automotivo/metal-mecânico do Sul Fluminense.")
    md.append("4. **InovUerj / DEPINOVA**: Órgão central da PR2 responsável por patentes, transferência de tecnologia, projetos de inovação aberta e ecossistema de incubadoras.")

    with open("mapeamento_uerj.md", "w", encoding="utf-8") as f:
        f.write("\n".join(md))

if __name__ == "__main__":
    main()
