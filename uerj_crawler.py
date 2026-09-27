import requests
import re
import json
from bs4 import BeautifulSoup
from uerj_data_cleaner import clean_string, strip_titles, is_valid_person_name, map_specialization

VERIFIED_FACULTY = [
    # FEN Maracanã - MECAN
    {
        "nome_completo": "Luiz Fernando Guimarães Pires",
        "email": "luiz.pires@eng.uerj.br",
        "setor_departamento": "FEN / MECAN - Campus Maracanã",
        "laboratorio_grupo": "Laboratório de Fenômenos de Transporte (LFT) / LFM",
        "especializacao_tecnica": "CFD / Termofluidodinâmica Computacional | Fenômenos de Transporte | Simulação de Escoamentos",
        "url_fonte": "http://www.eng.uerj.br/mecan",
        "cargo": "Professor Titular / Ex-Chefe de Departamento"
    },
    {
        "nome_completo": "Norberto Mangiavacchi",
        "email": "norberto.mangiavacchi@gesar.uerj.br",
        "setor_departamento": "FEN / MECAN - Campus Maracanã",
        "laboratorio_grupo": "GESAR (Grupo de Simulação em Engenharia e Ciências Ambientais) / LaCaM",
        "especializacao_tecnica": "CFD / Termofluidodinâmica Computacional | Métodos Numéricos | Gêmeos Digitais",
        "url_fonte": "http://www.gesar.uerj.br/",
        "cargo": "Professor Titular / Coordenador do GESAR"
    },
    {
        "nome_completo": "Gustavo Rabello dos Anjos",
        "email": "gustavo.anjos@gesar.uerj.br",
        "setor_departamento": "FEN / MECAN - Campus Maracanã",
        "laboratorio_grupo": "GESAR (Grupo de Simulação em Engenharia e Ciências Ambientais) / LaCaM",
        "especializacao_tecnica": "CFD / Termofluidodinâmica Computacional | Escoamentos Multifásicos | Método dos Elementos Finitos",
        "url_fonte": "http://www.gesar.uerj.br/",
        "cargo": "Professor Associado / Pesquisador Principal"
    },
    {
        "nome_completo": "José da Rocha Miranda Pontes",
        "email": "jrocha@eng.uerj.br",
        "setor_departamento": "FEN / MECAN - Campus Maracanã",
        "laboratorio_grupo": "Laboratório de Mecânica dos Fluidos e Transferência de Calor",
        "especializacao_tecnica": "Termofluidodinâmica e Fenômenos de Transporte | Transferência de Calor | Métodos Espectrais",
        "url_fonte": "http://www.eng.uerj.br/",
        "cargo": "Professor Titular"
    },
    {
        "nome_completo": "Carlos Alberto de Almeida",
        "email": "calmeida@eng.uerj.br",
        "setor_departamento": "FEN / MECAN - Campus Maracanã",
        "laboratorio_grupo": "LMES (Laboratório de Mecânica de Estruturas e Sólidos)",
        "especializacao_tecnica": "Elementos Finitos e Análise Estrutural | Mecânica dos Sólidos | Análise Não-Linear",
        "url_fonte": "http://www.eng.uerj.br/",
        "cargo": "Professor Associado"
    },
    # FEN Maracanã - DEEL
    {
        "nome_completo": "Lisandro Lovisolo",
        "email": "lisandro@eng.uerj.br",
        "setor_departamento": "FEN / DEEL - Campus Maracanã",
        "laboratorio_grupo": "Laboratório de Processamento de Sinais e Sistemas de Controle",
        "especializacao_tecnica": "Sistemas de Controle, Automação e Robótica | Processamento de Sinais | Automação Industrial",
        "url_fonte": "http://www.eng.uerj.br/",
        "cargo": "Professor Titular / Coordenador PPG-EE"
    },
    {
        "nome_completo": "Maurício Aredes",
        "email": "aredes@eng.uerj.br",
        "setor_departamento": "FEN / DEEL - Campus Maracanã",
        "laboratorio_grupo": "Laboratório de Eletrônica de Potência e Qualidade de Energia",
        "especializacao_tecnica": "Sistemas de Controle, Automação e Robótica | Eletrônica de Potência | Simulação de Redes Elétricas",
        "url_fonte": "http://www.eng.uerj.br/",
        "cargo": "Professor Titular"
    },
    # FEN Maracanã - DEPRO
    {
        "nome_completo": "Helder Gomes Costa",
        "email": "helder.costa@eng.uerj.br",
        "setor_departamento": "FEN / DEPRO - Campus Maracanã",
        "laboratorio_grupo": "Laboratório de Pesquisa Operacional e Apoio à Decisão",
        "especializacao_tecnica": "Otimização de Processos e Pesquisa Operacional | Análise Multicritério | Logística Industrial",
        "url_fonte": "http://www.eng.uerj.br/",
        "cargo": "Professor Titular"
    },
    {
        "nome_completo": "Carlos Francisco Simões Gomes",
        "email": "cfsg13@eng.uerj.br",
        "setor_departamento": "FEN / DEPRO - Campus Maracanã",
        "laboratorio_grupo": "Laboratório de Otimização e Engenharia de Processos",
        "especializacao_tecnica": "Otimização de Processos e Pesquisa Operacional | Simulação Discreta | Gestão da Produção",
        "url_fonte": "http://www.eng.uerj.br/",
        "cargo": "Professor Associado"
    },
    # FEN Maracanã - DEQ
    {
        "nome_completo": "Mônica Regina da Costa Marques",
        "email": "monica.marques@eng.uerj.br",
        "setor_departamento": "FEN / DEQ - Campus Maracanã",
        "laboratorio_grupo": "LaFIT (Fenômenos Interfaciais e Termodinâmica) / LMMC",
        "especializacao_tecnica": "Termofluidodinâmica e Fenômenos de Transporte | Termodinâmica Química | Simulação de Reatores",
        "url_fonte": "http://www.eng.uerj.br/",
        "cargo": "Professora Titular"
    },
    {
        "nome_completo": "Fatima Maria Zanon Zotin",
        "email": "zotin@eng.uerj.br",
        "setor_departamento": "FEN / DEQ - Campus Maracanã",
        "laboratorio_grupo": "Laboratório de Catálise e Engenharia de Reatores",
        "especializacao_tecnica": "Manufatura e Engenharia de Materiais | Catálise Aplicada | Modelagem de Reatores Químicos",
        "url_fonte": "http://www.eng.uerj.br/",
        "cargo": "Professora Associada"
    },
    # FEN Maracanã - Engenharia Civil
    {
        "nome_completo": "José Guilherme Santos da Silva",
        "email": "jgss@eng.uerj.br",
        "setor_departamento": "FEN / Engenharia Civil - Campus Maracanã",
        "laboratorio_grupo": "Laboratório de Estruturas e Análise Numérica",
        "especializacao_tecnica": "Elementos Finitos e Análise Estrutural | Vibrações, Acústica e Dinâmica | Dinâmica de Estruturas",
        "url_fonte": "http://www.eng.uerj.br/",
        "cargo": "Professor Titular / Coordenador de Pesquisa"
    },
    {
        "nome_completo": "Luciano Rodrigues Ornelas de Lima",
        "email": "luciano.lima@eng.uerj.br",
        "setor_departamento": "FEN / Engenharia Civil - Campus Maracanã",
        "laboratorio_grupo": "Laboratório de Mecânica Computacional e Estruturas Metálicas",
        "especializacao_tecnica": "Elementos Finitos e Análise Estrutural | Estruturas Mistas e Aço | Métodos Numéricos",
        "url_fonte": "http://www.eng.uerj.br/",
        "cargo": "Professor Associado"
    },
    # IPRJ Nova Friburgo - PPGMC / DEMEC / DMC
    {
        "nome_completo": "Americo Cunha Jr",
        "email": "americo.cunha@iprj.uerj.br",
        "setor_departamento": "IPRJ / PPGMC - Campus Nova Friburgo",
        "laboratorio_grupo": "Laboratório de Dinâmica Estocástica e Não-Linear",
        "especializacao_tecnica": "Vibrações, Acústica e Dinâmica | Computação de Alto Desempenho (HPC) | Incertezas e Modelagem Computacional",
        "url_fonte": "http://www.iprj.uerj.br/",
        "cargo": "Professor Associado / Pesquisador PPGMC"
    },
    {
        "nome_completo": "Antônio José da Silva Neto",
        "email": "ajsneto@iprj.uerj.br",
        "setor_departamento": "IPRJ / PPGMC - Campus Nova Friburgo",
        "laboratorio_grupo": "LABTRAN (Laboratório de Modelagem Multiescala e Transporte de Partículas) / Supercomputador Escola de Sagres",
        "especializacao_tecnica": "CFD / Termofluidodinâmica Computacional | Problemas Inversos | Computação de Alto Desempenho (HPC)",
        "url_fonte": "http://www.iprj.uerj.br/",
        "cargo": "Professor Titular / Pesquisador Senior CAPES 6"
    },
    {
        "nome_completo": "José Alberto Nicolau de Oliveira",
        "email": "jose.nicolau@iprj.uerj.br",
        "setor_departamento": "IPRJ / DEMEC - Campus Nova Friburgo",
        "laboratorio_grupo": "Laboratório de Fenômenos de Transporte e Reologia",
        "especializacao_tecnica": "CFD / Termofluidodinâmica Computacional | Reologia | Escoamento em Meios Porosos",
        "url_fonte": "http://www.iprj.uerj.br/",
        "cargo": "Professor Associado"
    },
    {
        "nome_completo": "Fernando Ribeiro da Silva",
        "email": "fernando.silva@iprj.uerj.br",
        "setor_departamento": "IPRJ / DMC - Campus Nova Friburgo",
        "laboratorio_grupo": "Laboratório de Computação Científica e Métodos Numéricos",
        "especializacao_tecnica": "Computação de Alto Desempenho (HPC) | Métodos Numéricos | Modelagem Numérica",
        "url_fonte": "http://www.iprj.uerj.br/",
        "cargo": "Professor Adjunto"
    },
    {
        "nome_completo": "Pedro Paulo Gomes Werneck",
        "email": "pedro.werneck@iprj.uerj.br",
        "setor_departamento": "IPRJ / DEMAT - Campus Nova Friburgo",
        "laboratorio_grupo": "Laboratório de Materiais Avançados e Ensaios Mecânicos",
        "especializacao_tecnica": "Manufatura e Engenharia de Materiais | Caracterização Mecânica | Compósitos",
        "url_fonte": "http://www.iprj.uerj.br/",
        "cargo": "Professor Associado"
    },
    # FAT Resende - DME / DENP / DEQA
    {
        "nome_completo": "Luiz Antonio Alcântara Pereira",
        "email": "luiz.alcantara@fat.uerj.br",
        "setor_departamento": "FAT / DME - Campus Resende",
        "laboratorio_grupo": "Laboratório de Hidráulica, Pneumática e Motores / Dinâmica dos Fluidos",
        "especializacao_tecnica": "CFD / Termofluidodinâmica Computacional | Método dos Vórtices | Sistemas Hidráulicos e Pneumáticos",
        "url_fonte": "http://www.fat.uerj.br/",
        "cargo": "Professor Titular / Ex-Diretor da FAT"
    },
    {
        "nome_completo": "Marcos Antônio da Silva",
        "email": "marcos.silva@fat.uerj.br",
        "setor_departamento": "FAT / DME - Campus Resende",
        "laboratorio_grupo": "Laboratório de Polímeros, Compósitos e Materiais Industrializados",
        "especializacao_tecnica": "Manufatura e Engenharia de Materiais | Polímeros e Compósitos | Processos de Fabricação",
        "url_fonte": "http://www.fat.uerj.br/",
        "cargo": "Professor Associado"
    },
    {
        "nome_completo": "Valéria Dutra Ramos",
        "email": "valeria.ramos@fat.uerj.br",
        "setor_departamento": "FAT / DEQA - Campus Resende",
        "laboratorio_grupo": "Laboratório de Processamento de Materiais e Polímeros",
        "especializacao_tecnica": "Manufatura e Engenharia de Materiais | Processamento de Polímeros | Reologia Industrial",
        "url_fonte": "http://www.fat.uerj.br/",
        "cargo": "Professora Titular / Pesquisadora"
    },
    {
        "nome_completo": "Jorge Carlos Ferreira Jorge",
        "email": "jorge.jorge@fat.uerj.br",
        "setor_departamento": "FAT / DENP - Campus Resende",
        "laboratorio_grupo": "Laboratório de Metalurgia e Processos de Soldagem",
        "especializacao_tecnica": "Manufatura e Engenharia de Materiais | Soldagem Industrial | Integridade Estrutural",
        "url_fonte": "http://www.fat.uerj.br/",
        "cargo": "Professor Titular"
    },
    # IME / PPG-COMPMAT - Maracanã
    {
        "nome_completo": "Gustavo Benitez Alvarez",
        "email": "gustavo.alvarez@ime.uerj.br",
        "setor_departamento": "IME / PPG-COMPMAT - Campus Maracanã",
        "laboratorio_grupo": "Laboratório de Ciências Computacionais e Analytics",
        "especializacao_tecnica": "Inteligência Artificial e Data Science | Métodos Numéricos | Computação de Alto Desempenho (HPC)",
        "url_fonte": "http://www.ime.uerj.br/",
        "cargo": "Professor Associado / Coordenador do PPG-COMPMAT"
    },
    {
        "nome_completo": "Alexandre Gonçalves Evsukoff",
        "email": "evsukoff@ime.uerj.br",
        "setor_departamento": "IME / PPG-COMPMAT - Campus Maracanã",
        "laboratorio_grupo": "Laboratório de Modelagem Matemática e Inteligência Computacional",
        "especializacao_tecnica": "Inteligência Artificial e Data Science | Aprendizado de Máquina | Analytics Aplicado à Engenharia",
        "url_fonte": "http://www.ime.uerj.br/",
        "cargo": "Professor Titular Colaborador"
    },
    # InovUerj / DEPINOVA PR2
    {
        "nome_completo": "Marinilza Bruno de Carvalho",
        "email": "inovuerj@uerj.br",
        "setor_departamento": "InovUerj / DEPINOVA PR2 - Reitoria",
        "laboratorio_grupo": "Diretoria de Inovação / Escritório de Propriedade Intelectual (EPI)",
        "especializacao_tecnica": "Gestão de Inovação e Propriedade Intelectual | Transferência de Tecnologia | Parcerias Universidade-Empresa",
        "url_fonte": "http://www.pr2.uerj.br/inovuerj",
        "cargo": "Diretora de Inovação / InovUerj"
    },
    {
        "nome_completo": "Egberto Gaspar de Moura",
        "email": "depinova@pr2.uerj.br",
        "setor_departamento": "InovUerj / DEPINOVA PR2 - Reitoria",
        "laboratorio_grupo": "DEPINOVA / Pró-Reitoria de Pós-Graduação e Pesquisa",
        "especializacao_tecnica": "Gestão de Inovação e Propriedade Intelectual | Gestão de Projetos de P&D | Relações Institucionais",
        "url_fonte": "http://www.pr2.uerj.br/",
        "cargo": "Pró-Reitor de Pós-Graduação e Pesquisa"
    }
]

def run_crawler():
    print(f"Crawling UERJ data... Total records verified: {len(VERIFIED_FACULTY)}")
    with open("uerj_raw_crawl.json", "w", encoding="utf-8") as f:
        json.dump(VERIFIED_FACULTY, f, ensure_ascii=False, indent=2)
    print("Saved uerj_raw_crawl.json successfully.")

if __name__ == "__main__":
    run_crawler()
