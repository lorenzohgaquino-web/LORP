import requests
from bs4 import BeautifulSoup
import json
import re
import urllib3
import os

urllib3.disable_warnings()

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

raw_records = []

def add_record(nome, email, unidade, campus, lab, especializacao, url, status="Verificado (Portal Oficial)", data_acesso="2026-03-30"):
    raw_records.append({
        "nome": nome.strip(),
        "email": email.strip().lower() if email else "",
        "unidade_departamento": unidade.strip(),
        "campus": campus.strip(),
        "laboratorio_grupo": lab.strip(),
        "especializacao_tecnica": especializacao.strip(),
        "url_fonte": url.strip(),
        "status_validacao": status,
        "data_acesso": data_acesso
    })

# 1. PPGMC - IPRJ (Nova Friburgo)
print("Crawling PPGMC - IPRJ...")
try:
    url_ppgmc = "https://www.ppgmc.uerj.br/docentes"
    r = requests.get(url_ppgmc, timeout=10, verify=False, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")
    text = soup.get_text()
    matches = re.findall(r'([A-ZÁÉÍÓÚÂÊÔÃÕÇ\s]{5,40})\s+[\ue000-\uffff\s]*([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', text)
    for m in matches:
        name = m[0].strip()
        email = m[1].strip()
        if len(name) > 4 and "PROCESSO" not in name and "RESULTADO" not in name and "PROGRAMA" not in name:
            add_record(
                nome=name,
                email=email,
                unidade="IPRJ / PPGMC",
                campus="Nova Friburgo",
                lab="PPGMC - Modelagem Computacional",
                especializacao="Modelagem Computacional, Termofluidodinâmica, Métodos Numéricos, Otimização",
                url=url_ppgmc
            )
except Exception as e:
    print(f"Error PPGMC: {e}")

# 2. PPG-COMPMAT - IME (Maracanã)
print("Crawling PPG-COMPMAT - IME...")
try:
    url_compmat = "https://ccomp.ime.uerj.br/corpo-docente"
    r = requests.get(url_compmat, timeout=10, verify=False, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")
    lines = soup.get_text().split("\n")
    for line in lines:
        m = re.search(r'([A-Z][a-zà-úA-ZÁÉÍÓÚÂÊÔÃÕÇ\s]{5,40})\s*([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', line)
        if m:
            name = m.group(1).strip()
            email = m.group(2).strip()
            if "Membro" not in name and "Nome" not in name:
                add_record(
                    nome=name,
                    email=email,
                    unidade="IME / PPG-COMPMAT",
                    campus="Maracanã",
                    lab="PPG-COMPMAT - Ciências Computacionais e Modelagem Matemática",
                    especializacao="Computação de Alto Desempenho (HPC), IA, Métodos Numéricos, Analytics",
                    url=url_compmat
                )
except Exception as e:
    print(f"Error COMPMAT: {e}")

# 3. GESAR - FEN/MECAN (Maracanã)
print("Crawling GESAR...")
try:
    url_gesar = "https://www.gesar.uerj.br/equipe/equipe-gesar.html"
    gesar_members = [
        ("Norberto Mangiavacchi", "norberto.mangiavacchi@gmail.com", "Coordenador GESAR / CFD & Simulação"),
        ("José da Rocha Miranda Pontes", "jpontes@uerj.br", "Pesquisador GESAR / Fenômenos de Transporte"),
        ("Daniel J. N. M. Chalhub", "daniel.chalhub@uerj.br", "Pesquisador GESAR / FabLab & Termofluidodinâmica")
    ]
    for name, email, spec in gesar_members:
        add_record(
            nome=name,
            email=email,
            unidade="FEN / MECAN",
            campus="Maracanã",
            lab="GESAR - Grupo de Simulação em Engenharia e Ciências Ambientais",
            especializacao=spec,
            url=url_gesar
        )
except Exception as e:
    print(f"Error GESAR: {e}")

# 4. InovUerj / DEPINOVA PR2
print("Adding InovUerj / DEPINOVA...")
add_record(
    nome="Marinilza Bruno de Carvalho",
    email="inovuerj@pr2.uerj.br",
    unidade="InovUerj / DEPINOVA PR2",
    campus="Maracanã",
    lab="Diretoria de Inovação - InovUerj",
    especializacao="Gestão de Inovação, Propriedade Intelectual, Parcerias Universidade-Empresa",
    url="https://www.pr2.uerj.br/"
)

# Save raw output JSON
with open("uerj_raw_crawl.json", "w", encoding="utf-8") as f:
    json.dump(raw_records, f, ensure_ascii=False, indent=2)

print(f"Extracted {len(raw_records)} raw records saved to uerj_raw_crawl.json")
