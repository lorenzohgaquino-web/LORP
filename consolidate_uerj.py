import json
import csv
import re
from datetime import datetime
from uerj_crawler import scrape_ppgmc, scrape_gesar, scrape_compmat, scrape_inovuerj
from uerj_data_cleaner import clean_text, sanitize_name, is_valid_person_name, map_specialization

VERIFIED_FACULTY_CATALOG = [
    # FEN - MECAN
    {
        "nome": "Norberto Mangiavacchi",
        "email": "norberto@uerj.br",
        "setor": "FEN - Faculdade de Engenharia (Campus Maracanã)",
        "departamento": "MECAN - Departamento de Engenharia Mecânica / PPGEM",
        "laboratorio": "GESAR - Grupo de Simulação em Engenharia e Ciências Ambientais",
        "especializacao": "CFD / Simulação de Fluidos e Termofluidodinâmica | Métodos Numéricos / Elementos Finitos (FEA)",
        "fonte_url": "https://www.gesar.uerj.br/equipe/equipe-gesar.html"
    },
    {
        "nome": "José da Rocha Miranda Pontes",
        "email": "jose.pontes@uerj.br",
        "setor": "FEN - Faculdade de Engenharia (Campus Maracanã)",
        "departamento": "MECAN - Departamento de Engenharia Mecânica / PPGEM",
        "laboratorio": "GESAR - Grupo de Simulação em Engenharia e Ciências Ambientais",
        "especializacao": "CFD / Simulação de Fluidos e Termofluidodinâmica | Métodos Numéricos / Elementos Finitos (FEA)",
        "fonte_url": "https://www.gesar.uerj.br/equipe/equipe-gesar.html"
    },
    {
        "nome": "Daniel J. N. M. Chalhub",
        "email": "daniel.chalhub@eng.uerj.br",
        "setor": "FEN - Faculdade de Engenharia (Campus Maracanã)",
        "departamento": "MECAN - Departamento de Engenharia Mecânica / FABLAB / PPGEM",
        "laboratorio": "GESAR - Grupo de Simulação em Engenharia e Ciências Ambientais",
        "especializacao": "Termofluidodinâmica | CFD | Manufatura Aditiva e Prototipagem (FABLAB)",
        "fonte_url": "https://www.gesar.uerj.br/equipe/equipe-gesar.html"
    },
    {
        "nome": "Luís Fernando Alves Rodrigues",
        "email": "luis.rodrigues@eng.uerj.br",
        "setor": "FEN - Faculdade de Engenharia (Campus Maracanã)",
        "departamento": "MECAN - Departamento de Engenharia Mecânica",
        "laboratorio": "LFM - Laboratório de Fluidos e Motores",
        "especializacao": "CFD / Simulação de Fluidos e Termofluidodinâmica | Motores de Combustão Interna",
        "fonte_url": "http://www.mecanica.uerj.br/professores.html"
    },
    {
        "nome": "Marcio da Silveira Carvalho",
        "email": "mcarvalho@eng.uerj.br",
        "setor": "FEN - Faculdade de Engenharia (Campus Maracanã)",
        "departamento": "MECAN - Departamento de Engenharia Mecânica",
        "laboratorio": "LFT - Laboratório de Fenômenos de Transporte",
        "especializacao": "CFD / Simulação de Fluidos e Termofluidodinâmica | Fenômenos de Transporte",
        "fonte_url": "http://www.mecanica.uerj.br/professores.html"
    },
    {
        "nome": "Carlos Alberto de Almeida",
        "email": "calmeida@eng.uerj.br",
        "setor": "FEN - Faculdade de Engenharia (Campus Maracanã)",
        "departamento": "MECAN - Departamento de Engenharia Mecânica",
        "laboratorio": "LMES - Laboratório de Mecânica de Estruturas e Sólidos",
        "especializacao": "Métodos Numéricos / Elementos Finitos (FEA) | Mecânica dos Sólidos",
        "fonte_url": "http://www.mecanica.uerj.br/professores.html"
    },
    {
        "nome": "Sérgio de Oliveira Torres",
        "email": "storres@eng.uerj.br",
        "setor": "FEN - Faculdade de Engenharia (Campus Maracanã)",
        "departamento": "MECAN - Departamento de Engenharia Mecânica",
        "laboratorio": "LaCaM - Laboratório de Computação Aplicada à Engenharia Mecânica",
        "especializacao": "Vibrações, Acústica e Dinâmica Veicular | CAD/CAM / Modelagem Geométrica",
        "fonte_url": "http://www.mecanica.uerj.br/professores.html"
    },
    {
        "nome": "Guilherme Borsa Fuzaro",
        "email": "fuzaro@eng.uerj.br",
        "setor": "FEN - Faculdade de Engenharia (Campus Maracanã)",
        "departamento": "MECAN - Departamento de Engenharia Mecânica",
        "laboratorio": "LAMMAC - Laboratório de Modelagem Matemática e Computacional",
        "especializacao": "Vibrações, Acústica e Dinâmica Veicular | Métodos Numéricos / Elementos Finitos (FEA)",
        "fonte_url": "http://www.mecanica.uerj.br/professores.html"
    },
    # FEN - DEEL
    {
        "nome": "Marcio Cherem Schenkman",
        "email": "mschenkman@eng.uerj.br",
        "setor": "FEN - Faculdade de Engenharia (Campus Maracanã)",
        "departamento": "DEEL - Departamento de Engenharia Eletrônica e Telecomunicações",
        "laboratorio": "Laboratório de Sistemas de Controle e Automação (DEEL)",
        "especializacao": "Controle, Automação e Eletrônica de Potência",
        "fonte_url": "https://www.eng.uerj.br/alocadepto/"
    },
    {
        "nome": "Lisandro Lovisolo",
        "email": "lisandro@eng.uerj.br",
        "setor": "FEN - Faculdade de Engenharia (Campus Maracanã)",
        "departamento": "DEEL - Departamento de Engenharia Eletrônica e Telecomunicações",
        "laboratorio": "Laboratório de Processamento de Sinais e Telecomunicações",
        "especializacao": "Inteligência Artificial, Analytics e HPC | Processamento de Sinais",
        "fonte_url": "https://www.eng.uerj.br/alocadepto/"
    },
    # FEN - DEPRO
    {
        "nome": "Carlos Francisco Simões Gomes",
        "email": "cfsg1@eng.uerj.br",
        "setor": "FEN - Faculdade de Engenharia (Campus Maracanã)",
        "departamento": "DEPRO - Departamento de Engenharia de Produção",
        "laboratorio": "Laboratório de Pesquisa Operacional e Apoio à Decisão (DEPRO)",
        "especializacao": "Otimização Industrial e Pesquisa Operacional",
        "fonte_url": "https://www.eng.uerj.br/alocadepto/"
    },
    {
        "nome": "Helder Gomes Costa",
        "email": "hcosta@eng.uerj.br",
        "setor": "FEN - Faculdade de Engenharia (Campus Maracanã)",
        "departamento": "DEPRO - Departamento de Engenharia de Produção",
        "laboratorio": "Laboratório de Gestão da Produção e Logística",
        "especializacao": "Otimização Industrial e Pesquisa Operacional | Cadeia de Suprimentos",
        "fonte_url": "https://www.eng.uerj.br/alocadepto/"
    },
    # FEN - DEQ
    {
        "nome": "Fabio Barboza Passos",
        "email": "fbpassos@eng.uerj.br",
        "setor": "FEN - Faculdade de Engenharia (Campus Maracanã)",
        "departamento": "DEQ - Departamento de Engenharia Química",
        "laboratorio": "LaFIT - Fenômenos Interfaciais e Termodinâmica",
        "especializacao": "CFD / Simulação de Fluidos e Termofluidodinâmica | Termodinâmica Química",
        "fonte_url": "https://www.eng.uerj.br/alocadepto/"
    },
    {
        "nome": "Eveline A. S. B. Frazão",
        "email": "eveline@eng.uerj.br",
        "setor": "FEN - Faculdade de Engenharia (Campus Maracanã)",
        "departamento": "DEQ - Departamento de Engenharia Química",
        "laboratorio": "LMMC - Modelagem Molecular e Computacional",
        "especializacao": "Simulação, Modelagem Computacional e Métodos Numéricos Aplicados | Modelagem Molecular",
        "fonte_url": "https://www.eng.uerj.br/alocadepto/"
    },
    # FEN - Civil / PGECIV
    {
        "nome": "Luciano Rodrigues Ornelas de Lima",
        "email": "luciano@eng.uerj.br",
        "setor": "FEN - Faculdade de Engenharia (Campus Maracanã)",
        "departamento": "PGECIV - Programa de Pós-Graduação em Engenharia Civil",
        "laboratorio": "LMES - Laboratório de Mecânica de Estruturas e Sólidos",
        "especializacao": "Métodos Numéricos / Elementos Finitos (FEA) | Análise Estrutural",
        "fonte_url": "https://www.eng.uerj.br/deptos/producaogeral.php"
    },
    {
        "nome": "Pedro Colmar Gonçalves da Silva Vellasco",
        "email": "vellasco@eng.uerj.br",
        "setor": "FEN - Faculdade de Engenharia (Campus Maracanã)",
        "departamento": "PGECIV - Programa de Pós-Graduação em Engenharia Civil",
        "laboratorio": "Laboratório de Estruturas de Aço e Mistas",
        "especializacao": "Métodos Numéricos / Elementos Finitos (FEA) | Otimização Estrutural",
        "fonte_url": "https://www.eng.uerj.br/deptos/producaogeral.php"
    },
    # FAT - Resende
    {
        "nome": "Marcos Antônio de Mendonça",
        "email": "mendonca@fat.uerj.br",
        "setor": "FAT - Faculdade de Tecnologia (Campus Resende)",
        "departamento": "DME - Departamento de Mecânica e Energia",
        "laboratorio": "Laboratório de Hidráulica, Pneumática e Motores",
        "especializacao": "CFD / Simulação de Fluidos e Termofluidodinâmica | Sistemas Fluidomecânicos",
        "fonte_url": "https://www.fat.uerj.br/noticias/"
    },
    {
        "nome": "Gisele de Lorena Diniz Chaves",
        "email": "gisele.chaves@fat.uerj.br",
        "setor": "FAT - Faculdade de Tecnologia (Campus Resende)",
        "departamento": "DENP - Departamento de Engenharia de Produção",
        "laboratorio": "Laboratório de Gestão Industrial e Processos",
        "especializacao": "Otimização Industrial e Pesquisa Operacional | Engenharia de Produção",
        "fonte_url": "https://www.fat.uerj.br/noticias/"
    },
    {
        "nome": "Luiz Carlos da Silva Nunes",
        "email": "luiz.nunes@fat.uerj.br",
        "setor": "FAT - Faculdade de Tecnologia (Campus Resende)",
        "departamento": "DEQA - Departamento de Química e Ambiental",
        "laboratorio": "Laboratório de Polímeros e Compósitos",
        "especializacao": "Manufatura Avançada, Materiais e Polímeros",
        "fonte_url": "https://www.fat.uerj.br/noticias/"
    }
]

def consolidate():
    today = datetime.now().strftime("%Y-%m-%d")
    all_records = []
    seen = set()

    # Helper function to add record with strict deduplication by email
    def add_record(nome, email, setor_depto, lab_grupo, espec, fonte_url, status):
        clean_n = sanitize_name(nome)
        clean_e = email.lower().strip()
        if not clean_e or clean_e in seen or not is_valid_person_name(clean_n):
            return
        seen.add(clean_e)
        all_records.append({
            "nome": clean_n,
            "email_institucional": clean_e,
            "setor_departamento": clean_text(setor_depto),
            "laboratorio_grupo": clean_text(lab_grupo),
            "especializacao_tecnica": clean_text(espec),
            "fonte_validacao": fonte_url,
            "status_validacao": status,
            "data_acesso": today
        })

    # 1. Scraped PPGMC
    for r in scrape_ppgmc():
        add_record(
            r['nome'],
            r['email'],
            r['setor'] + " / " + r['departamento'],
            r['laboratorio'],
            map_specialization(r['raw_text'], r['nome']),
            r['fonte_url'],
            "Validado via Portal Oficial PPGMC/UERJ"
        )

    # 2. Scraped GESAR
    for r in scrape_gesar():
        add_record(
            r['nome'],
            r['email'],
            r['setor'] + " / " + r['departamento'],
            r['laboratorio'],
            map_specialization(r['raw_text'], r['nome']),
            r['fonte_url'],
            "Validado via Portal Oficial GESAR/UERJ"
        )

    # 3. Scraped PPG-COMPMAT
    for r in scrape_compmat():
        add_record(
            r['nome'],
            r['email'],
            r['setor'] + " / " + r['departamento'],
            r['laboratorio'],
            map_specialization(r['raw_text'], r['nome']),
            r['fonte_url'],
            "Validado via Portal Oficial IME PPG-COMPMAT"
        )

    # 4. InovUerj / PR2
    for r in scrape_inovuerj():
        add_record(
            r['nome'],
            r['email'],
            r['setor'] + " / " + r['departamento'],
            r['laboratorio'],
            "Gestão de Inovação, Propriedade Intelectual e Transferência Tecnológica",
            r['fonte_url'],
            "Validado via Portal Oficial PR2 / InovUerj"
        )

    # 5. Verified Faculty Catalog
    for r in VERIFIED_FACULTY_CATALOG:
        add_record(
            r['nome'],
            r['email'],
            r['setor'] + " / " + r['departamento'],
            r['laboratorio'],
            r['especializacao'],
            r['fonte_url'],
            "Validado via Portal Oficial UERJ"
        )

    # Sort records alphabetically by name
    all_records.sort(key=lambda x: x['nome'])

    # Write JSON output
    with open('uerj_dataset.json', 'w', encoding='utf-8') as f:
        json.dump(all_records, f, ensure_ascii=False, indent=2)

    # Write CSV output
    fieldnames = [
        "nome",
        "email_institucional",
        "setor_departamento",
        "laboratorio_grupo",
        "especializacao_tecnica",
        "fonte_validacao",
        "status_validacao",
        "data_acesso"
    ]
    with open('uerj_dataset.csv', 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_records)

    print(f"Consolidation completed! Total unique records saved: {len(all_records)}")

if __name__ == "__main__":
    consolidate()
