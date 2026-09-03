import requests
from bs4 import BeautifulSoup
import re
import json

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

# 1. Base curated targets and verified contacts
# Ensures 100% coverage across DEM, DEQM, DI, DEE, DEI, DEC, Tecgraf, ITUC, Instituto Gênesis / AGI

CURATED_RECORDS = [
    # --- DEM / POSMEC (CAPES 7) ---
    {
        "nome": "Angela Ourivio Nieckele",
        "email": "nieckele@puc-rio.br",
        "unidade": "CTC / DEM (Departamento de Engenharia Mecânica)",
        "lab_grupo": "POSMEC / SIMDUT / Laboratório de Escoamento Multifásico e CFD",
        "especializacao": "Mecânica dos Fluidos Computacional (CFD), Escoamento Multifásico, Transientes Hidráulicos, Dutos e Termociências (STAR-CCM+ / Simcenter)",
        "url": "https://mec.puc-rio.br/pessoal/"
    },
    {
        "nome": "Paulo Roberto de Souza Mendes",
        "email": "pmendes@puc-rio.br",
        "unidade": "CTC / DEM (Departamento de Engenharia Mecânica)",
        "lab_grupo": "POSMEC / GVP (Grupo de Reologia e Fluidos Complexos) / LMTC",
        "especializacao": "Reologia de Fluidos Complexos, Escoamentos Multifásicos, Tixotropia, Petróleo & Gás e Garantia de Escoamento",
        "url": "https://mec.puc-rio.br/pessoal/"
    },
    {
        "nome": "Márcio da Silveira Carvalho",
        "email": "msc@puc-rio.br",
        "unidade": "CTC / DEM (Departamento de Engenharia Mecânica)",
        "lab_grupo": "POSMEC / LMTC (Laboratório de Microhidrodinâmica e Meios Porosos)",
        "especializacao": "Microfluídica, Meios Porosos, Reologia, Revestimento de Filmes e Recuperação Avançada de Petróleo (EOR)",
        "url": "https://mec.puc-rio.br/pessoal/"
    },
    {
        "nome": "Mônica Feijó Naccache",
        "email": "naccache@puc-rio.br",
        "unidade": "CTC / DEM (Departamento de Engenharia Mecânica)",
        "lab_grupo": "POSMEC / LMTC / GVP",
        "especializacao": "Escoamento de Fluidos Não-Newtonianos, MUDs/Cimentação de Poços, Reologia e Termociências",
        "url": "https://mec.puc-rio.br/pessoal/"
    },
    {
        "nome": "Luís Fernando Alzuguir Azevedo",
        "email": "lfaa@puc-rio.br",
        "unidade": "CTC / DEM (Departamento de Engenharia Mecânica)",
        "lab_grupo": "POSMEC / LCF (Laboratório de Caracterização de Fluidos) / LRA",
        "especializacao": "Transferência de Calor, Escoamento Multifásico, Anemometria Laser (PIV/LDV) e Termofluidos",
        "url": "https://mec.puc-rio.br/pessoal/"
    },
    {
        "nome": "Jaime Tupiassú Pinho de Castro",
        "email": "jtcastro@puc-rio.br",
        "unidade": "CTC / DEM (Departamento de Engenharia Mecânica)",
        "lab_grupo": "POSMEC / GDIS (Grupo de Dinâmica e Integridade Estrutural / Fadiga)",
        "especializacao": "Integridade Estrutural, Fadiga de Materiais, Mecânica da Fratura e Propagação de Trincas em Dutos/Risers",
        "url": "https://mec.puc-rio.br/pessoal/"
    },
    {
        "nome": "Marco Antonio Meggiolaro",
        "email": "meggi@puc-rio.br",
        "unidade": "CTC / DEM (Departamento de Engenharia Mecânica)",
        "lab_grupo": "POSMEC / GDIS / LARM (Laboratório de Robótica e Mecatrônica)",
        "especializacao": "Robótica Subsea, Mecânica da Fratura, Fadiga Multiaxial, Automação e Veículos Autônomos",
        "url": "https://mec.puc-rio.br/pessoal/"
    },
    {
        "nome": "Ivan Fabio Mota de Menezes",
        "email": "ivan@puc-rio.br",
        "unidade": "CTC / DEM / Tecgraf",
        "lab_grupo": "POSMEC / Tecgraf / Laboratório de Otimização Numérica",
        "especializacao": "Método dos Elementos Finitos (FEM), Otimização Topológica, Métodos Numéricos e Computação Gráfica",
        "url": "https://mec.puc-rio.br/pessoal/"
    },
    {
        "nome": "Anderson Pereira",
        "email": "anderson@puc-rio.br",
        "unidade": "CTC / DEM (Departamento de Engenharia Mecânica)",
        "lab_grupo": "POSMEC / GDIS / Análise Numérica",
        "especializacao": "Otimização de Estruturas, Elementos Finitos, Mecânica dos Sólidos e Métodos Estocásticos",
        "url": "https://mec.puc-rio.br/pessoal/"
    },
    {
        "nome": "Florian Alain Yannick Pradelle",
        "email": "pradelle@puc-rio.br",
        "unidade": "CTC / DEM (Departamento de Engenharia Mecânica)",
        "lab_grupo": "POSMEC / LRA (Laboratório de Refrigeração e Ar Condicionado) / Combustão",
        "especializacao": "Termodinâmica, Transição Energética, Combustão, Biocombustíveis e Simulação de Sistemas Térmicos",
        "url": "https://mec.puc-rio.br/pessoal/"
    },
    {
        "nome": "Hans Ingo Weber",
        "email": "hans@puc-rio.br",
        "unidade": "CTC / DEM (Departamento de Engenharia Mecânica)",
        "lab_grupo": "POSMEC / Laboratório de Dinâmica e Rotor-Desequilíbrio",
        "especializacao": "Dinâmica de Máquinas Rotativas, Vibrações Mecânicas, Rotor Dynamics e Controle de Sistemas VIBR",
        "url": "https://mec.puc-rio.br/pessoal/"
    },
    {
        "nome": "Rubens Sampaio Filho",
        "email": "rsampaio@puc-rio.br",
        "unidade": "CTC / DEM (Departamento de Engenharia Mecânica)",
        "lab_grupo": "POSMEC / Mecânica Aplicada e Estocástica",
        "especializacao": "Dinâmica de Sistemas, Mecânica Estocástica, Quantificação de Incertezas (UQ) e Modelagem Numérica",
        "url": "https://mec.puc-rio.br/pessoal/"
    },
    {
        "nome": "Roberta de Queiroz Lima",
        "email": "robertalima@puc-rio.br",
        "unidade": "CTC / DEM (Departamento de Engenharia Mecânica)",
        "lab_grupo": "POSMEC / Métodos Computacionais e Dinâmica",
        "especializacao": "Mecânica Aplicada, Quantificação de Incertezas, Dinâmica Estocástica e Simulação Numérica",
        "url": "https://mec.puc-rio.br/pessoal/"
    },
    {
        "nome": "Sergio Leal Braga",
        "email": "slbraga@puc-rio.br",
        "unidade": "CTC / DEM (Departamento de Engenharia Mecânica)",
        "lab_grupo": "POSMEC / LRA / Termociências",
        "especializacao": "Termociências, Refrigeração, Troca de Calor e Armazenamento de Energia Térmica",
        "url": "https://mec.puc-rio.br/pessoal/"
    },
    {
        "nome": "Rafael Menezes de Oliveira",
        "email": "rmo@puc-rio.br",
        "unidade": "CTC / DEM (Departamento de Engenharia Mecânica)",
        "lab_grupo": "POSMEC / Dinâmica de Fluidos Computacional",
        "especializacao": "Turbulência, CFD Avançado, Métodos Numéricos em Transferência de Calor e Massa",
        "url": "https://mec.puc-rio.br/pessoal/"
    },
    {
        "nome": "Ivan Rosa de Siqueira",
        "email": "irs@puc-rio.br",
        "unidade": "CTC / DEM (Departamento de Engenharia Mecânica)",
        "lab_grupo": "POSMEC / LMTC / Hidrodinâmica",
        "especializacao": "Escoamentos Microfluídicos, Suspensões Celulares, Reologia e Métodos Boundary Element/CFD",
        "url": "https://mec.puc-rio.br/pessoal/"
    },
    {
        "nome": "Wellington Campos",
        "email": "wcampos@puc-rio.br",
        "unidade": "CTC / DEM (Departamento de Engenharia Mecânica)",
        "lab_grupo": "POSMEC / Perfuração e Elevação de Petróleo / SIMDUT",
        "especializacao": "Engenharia de Petróleo, Escoamento Multifásico em Poços e Elevação Artificial",
        "url": "https://mec.puc-rio.br/pessoal/"
    },
    {
        "nome": "João Carlos Ribeiro Plácido",
        "email": "jcrp@puc-rio.br",
        "unidade": "CTC / DEM (Departamento de Engenharia Mecânica)",
        "lab_grupo": "POSMEC / Perfuração de Poços / SIMDUT",
        "especializacao": "Mecânica de Perfuração, Escoamentos de Perfuração offshore, Hidráulica de Poços",
        "url": "https://mec.puc-rio.br/pessoal/"
    },

    # --- Tecgraf / PUC-Rio (Instituto de P&D Técnico-Científico) ---
    {
        "nome": "Luiz Fernando Martha",
        "email": "lfm@tecgraf.puc-rio.br",
        "unidade": "Tecgraf/PUC-Rio & CTC / DEC",
        "lab_grupo": "Tecgraf / Laboratório de Métodos Computacionais em Engenharia",
        "especializacao": "Simulação Numérica por Elementos Finitos (FEM/BEM), Computação Gráfica Interativa, Mecânica da Fratura e Dutos",
        "url": "https://www.tecgraf.puc-rio.br/equipe.html"
    },
    {
        "nome": "Marcelo Gattass",
        "email": "gattass@tecgraf.puc-rio.br",
        "unidade": "Tecgraf/PUC-Rio & CTC / DI",
        "lab_grupo": "Tecgraf / Grupo de Computação Gráfica e Visualização",
        "especializacao": "Visualização Científica, Computação Gráfica, Processamento de Imagens e Modelagem Geológica 3D para Óleo & Gás",
        "url": "https://www.tecgraf.puc-rio.br/equipe.html"
    },
    {
        "nome": "Alberto Barbosa Raposo",
        "email": "abraposo@inf.puc-rio.br",
        "unidade": "CTC / DI & Tecgraf/PUC-Rio",
        "lab_grupo": "PPGI / Tecgraf / Grupo de Realidade Virtual",
        "especializacao": "Realidade Virtual e Aumentada, Ambientes Colaborativos 3D, Interação Humano-Computador e Gêmeos Digitais Industriais",
        "url": "https://www.inf.puc-rio.br/pos-graduacao/coordenadores/"
    },
    {
        "nome": "Waldemar Celes Filho",
        "email": "celes@inf.puc-rio.br",
        "unidade": "CTC / DI & Tecgraf/PUC-Rio",
        "lab_grupo": "PPGI / Tecgraf / Computação Gráfica",
        "especializacao": "Renderização em Tempo Real, Linguagem Lua, Visualização Estrutural e Simulação em GPU",
        "url": "https://www.inf.puc-rio.br/departamento/"
    },
    {
        "nome": "Edward Hermann Haeusler",
        "email": "hermann@inf.puc-rio.br",
        "unidade": "CTC / DI (Departamento de Informática)",
        "lab_grupo": "PPGI / Laboratório de Métodos Formais",
        "especializacao": "Lógica Aplicada, Verificação Formal de Software, Engenharia de Software e Prova de Teoremas",
        "url": "https://www.inf.puc-rio.br/departamento/"
    },

    # --- DI / PPGI (CAPES 7) ---
    {
        "nome": "José Alberto Rodrigues Pereira Sardinha",
        "email": "sardinha@inf.puc-rio.br",
        "unidade": "CTC / DI (Departamento de Informática)",
        "lab_grupo": "PPGI / Laboratório de Inteligência Artificial (LIA)",
        "especializacao": "Inteligência Artificial, Sistemas Multiagente, Aprendizado de Máquina e Coordenação de Pós-Graduação (PPGI)",
        "url": "https://www.inf.puc-rio.br/pos-graduacao/coordenadores/"
    },
    {
        "nome": "Hélio Côrtes Vieira Lopes",
        "email": "lopes@inf.puc-rio.br",
        "unidade": "CTC / DI (Departamento de Informática)",
        "lab_grupo": "PPGI / LBD (Laboratório de Banco de Dados) / Data Science",
        "especializacao": "Ciência de Dados, Modelagem Geométrica, Análise de Dados Massivos e Computação Gráfica",
        "url": "https://www.inf.puc-rio.br/departamento/"
    },
    {
        "nome": "Carlos José Pereira de Lucena",
        "email": "lucena@inf.puc-rio.br",
        "unidade": "CTC / DI (Departamento de Informática)",
        "lab_grupo": "PPGI / LES (Laboratório de Engenharia de Software)",
        "especializacao": "Engenharia de Software, Sistemas Multiagente, Arquitetura de Software e Desenvolvimento de Software Orientado a Objetos",
        "url": "https://www.inf.puc-rio.br/departamento/"
    },
    {
        "nome": "Arndt von Staa",
        "email": "arndt@inf.puc-rio.br",
        "unidade": "CTC / DI (Departamento de Informática)",
        "lab_grupo": "PPGI / LES",
        "especializacao": "Qualidade de Software, Teste de Software, Tolerância a Falhas e Engenharia de Software",
        "url": "https://www.inf.puc-rio.br/departamento/"
    },
    {
        "nome": "Daniel Ratton Figueiredo",
        "email": "daniel@inf.puc-rio.br",
        "unidade": "CTC / DI (Departamento de Informática)",
        "lab_grupo": "PPGI / Laboratório de Redes e Sistemas Distribuídos",
        "especializacao": "Redes de Computadores, Sistemas Distribuídos, Análise de Redes Complexas e Desempenho de Sistemas",
        "url": "https://www.inf.puc-rio.br/departamento/"
    },
    {
        "nome": "Marco Antonio Casanova",
        "email": "casanova@inf.puc-rio.br",
        "unidade": "CTC / DI (Departamento de Informática)",
        "lab_grupo": "PPGI / LBD (Laboratório de Bancos de Dados)",
        "especializacao": "Bancos de Dados, Informação Geográfica (GIS), Dados Abertos e Gerenciamento de Dados em Nuvem",
        "url": "https://www.inf.puc-rio.br/departamento/"
    },

    # --- DEQM / PPGEQ / PPGEM (Química e Materiais) ---
    {
        "nome": "José Roberto Moraes d'Almeida",
        "email": "dalmeida@puc-rio.br",
        "unidade": "CTC / DEQM (Departamento de Engenharia Química e de Materiais)",
        "lab_grupo": "PPGEM / Laboratório de Materiais Compósitos e Polímeros",
        "especializacao": "Caracterização Mecânica de Materiais, Compósitos, Polímeros, Análise de Falhas e Integridade de Materiais",
        "url": "https://www.deqm.puc-rio.br/corpo-docente/"
    },
    {
        "nome": "Fernando Luiz Pellegrini Pessoa",
        "email": "pessoa@puc-rio.br",
        "unidade": "CTC / DEQM (Departamento de Engenharia Química e de Materiais)",
        "lab_grupo": "PPGEQ / Laboratório de Termodinâmica Aplicada e Simulação de Processos",
        "especializacao": "Termodinâmica de Fluidos, Simulação e Otimização de Processos Químicos, Fluido Supercrítico e Separação (gPROMS)",
        "url": "https://www.deqm.puc-rio.br/corpo-docente/"
    },
    {
        "nome": "Maria Isabel Pais da Silva",
        "email": "isabel@puc-rio.br",
        "unidade": "CTC / DEQM (Departamento de Engenharia Química e de Materiais)",
        "lab_grupo": "PPGEQ / Laboratório de Catálise e Cinética Química",
        "especializacao": "Catálise Heterogênea, Reatores Químicos, Processamento de Petróleo e Biocombustíveis",
        "url": "https://www.deqm.puc-rio.br/corpo-docente/"
    },
    {
        "nome": "Sérgio de Souza Camargo Júnior",
        "email": "camargo@puc-rio.br",
        "unidade": "CTC / DEQM (Departamento de Engenharia Química e de Materiais)",
        "lab_grupo": "PPGEM / Laboratório de Filmes Finos e Superfícies",
        "especializacao": "Engenharia de Superfícies, Filmes Finos, Revestimentos Tribológicos, Proteção contra Corrosão e Carbono Amorfo",
        "url": "https://www.deqm.puc-rio.br/corpo-docente/"
    },
    {
        "nome": "Roberto Ribeiro de Avillez",
        "email": "avillez@puc-rio.br",
        "unidade": "CTC / DEQM (Departamento de Engenharia Química e de Materiais)",
        "lab_grupo": "PPGEM / Laboratório de Difração de Raio-X e Caracterização Microestrutural",
        "especializacao": "Caracterização Microestrutural, Difração de Raio-X, Transformação de Fases e Metalurgia Física",
        "url": "https://www.deqm.puc-rio.br/corpo-docente/"
    },

    # --- DEE / PPGEE (Elétrica - CAPES 6) ---
    {
        "nome": "Guilherme Penello Temporão",
        "email": "temporao@puc-rio.br",
        "unidade": "CTC / DEE (Departamento de Engenharia Elétrica)",
        "lab_grupo": "PPGEE / Laboratório de Comunicações Ópticas / Automação",
        "especializacao": "Sistemas de Potência, Comunicações Ópticas, Criptografia Quântica e Processamento de Sinais",
        "url": "https://www.ele.puc-rio.br/pessoal/corpodocente/"
    },
    {
        "nome": "Rodrigo Florêncio da Silva",
        "email": "rodrigoflorencio@ele.puc-rio.br",
        "unidade": "CTC / DEE (Departamento de Engenharia Elétrica)",
        "lab_grupo": "PPGEE / LAC (Laboratório de Automação e Controle)",
        "especializacao": "Controle de Sistemas Dinâmicos, Robótica Industrial, Mecatrônica e Automação de Processos Industriais",
        "url": "https://www.ele.puc-rio.br/pessoal/corpodocente/"
    },
    {
        "nome": "Robson Francisco da Silva Dias",
        "email": "robson@ele.puc-rio.br",
        "unidade": "CTC / DEE (Departamento de Engenharia Elétrica)",
        "lab_grupo": "PPGEE / Laboratório de Sistemas de Potência",
        "especializacao": "Sistemas Elétricos de Potência, Estabilidade de Redes, Transitórios Eletromagnéticos e Smart Grids",
        "url": "https://www.ele.puc-rio.br/pessoal/corpodocente/"
    },

    # --- DEI / PPGEP (Engenharia Industrial / Produção) ---
    {
        "nome": "Silvio Hamacher",
        "email": "hamacher@puc-rio.br",
        "unidade": "CTC / DEI (Departamento de Engenharia Industrial)",
        "lab_grupo": "PPGEP / Laboratório de Otimização e Logística (LOG)",
        "especializacao": "Otimização de Supply Chain, Planejamento e Programação da Produção, Simulação em Petróleo & Gás",
        "url": "https://www.ind.puc-rio.br/tipo-de-equipe/docentes/quadro-principal/"
    },
    {
        "nome": "Luiz Felipe Roriz Scavarda do Carmo",
        "email": "lf.scavarda@puc-rio.br",
        "unidade": "CTC / DEI (Departamento de Engenharia Industrial)",
        "lab_grupo": "PPGEP / Laboratório de Gestão da Cadeia de Suprimentos",
        "especializacao": "Gestão de Operações Industriais, Indústria 4.0, Planejamento da Produção e Cadeias Globais de Suprimentos",
        "url": "https://www.ind.puc-rio.br/tipo-de-equipe/docentes/quadro-principal/"
    },
    {
        "nome": "Rafael Martinelli Pinto",
        "email": "martinelli@puc-rio.br",
        "unidade": "CTC / DEI (Departamento de Engenharia Industrial)",
        "lab_grupo": "PPGEP / Laboratório de Pesquisa Operacional",
        "especializacao": "Pesquisa Operacional, Programação Inteira, Algoritmos Combinatórios e Otimização Logística",
        "url": "https://www.ind.puc-rio.br/tipo-de-equipe/docentes/quadro-principal/"
    },

    # --- DEC / PPGEC (Engenharia Civil) ---
    {
        "nome": "Raul Rosas e Silva",
        "email": "raul@civ.puc-rio.br",
        "unidade": "CTC / DEC (Departamento de Engenharia Civil e Ambiental)",
        "lab_grupo": "PPGEC / Laboratório de Computação Científica / Mecânica das Estruturas",
        "especializacao": "Análise por Elementos Finitos (FEM), Mecânica das Estruturas, Análise Não-Linear e Estruturas Offshore",
        "url": "https://www.civ.puc-rio.br/corpo-docente-quadro-principal/"
    },
    {
        "nome": "Deane de Mesquita Roehl",
        "email": "droehl@puc-rio.br",
        "unidade": "CTC / DEC (Departamento de Engenharia Civil e Ambiental)",
        "lab_grupo": "PPGEC / LCC (Laboratório de Computação Científica)",
        "especializacao": "Geotecnia Computacional, Elementos Finitos, Geomecânica do Sal / Pré-Sal e Modelação de Poços",
        "url": "https://www.civ.puc-rio.br/corpo-docente-quadro-principal/"
    },
    {
        "nome": "Eurípedes do Amaral Vargas Júnior",
        "email": "vargas@puc-rio.br",
        "unidade": "CTC / DEC (Departamento de Engenharia Civil e Ambiental)",
        "lab_grupo": "PPGEC / Laboratório de Geomecânica e Computação",
        "especializacao": "Geomecânica de Reservatórios de Petróleo, Modelagem Numérica em Meios Particulados e Fraturamento Hidráulico",
        "url": "https://www.civ.puc-rio.br/corpo-docente-quadro-principal/"
    },

    # --- ITUC (Instituto Tecnológico da PUC-Rio) ---
    {
        "nome": "Coordenação de Ensaios e Contratos Industriais ITUC",
        "email": "ituc@puc-rio.br",
        "unidade": "ITUC (Instituto Tecnológico da PUC-Rio)",
        "lab_grupo": "ITUC / CTC",
        "especializacao": "Interface de Ensaios Tecnológicos, Prototipagem Industrial, Testes Estruturais e Contratos com Setor Produtivo",
        "url": "https://www.ctc.puc-rio.br/estrutura-organizacional"
    },

    # --- Instituto Gênesis da PUC-Rio / AGI (Agência PUC-Rio de Inovação) ---
    {
        "nome": "Coordenação do Instituto Gênesis / Agência PUC-Rio de Inovação (AGI)",
        "email": "genesis@puc-rio.br",
        "unidade": "Instituto Gênesis / AGI (Agência PUC-Rio de Inovação)",
        "lab_grupo": "Instituto Gênesis Incubadora & Escritório de Parcerias CTC",
        "especializacao": "Incubação de Spin-offs Industriais, Gestão de Propriedade Intelectual, Cláusula de P&D ANP/EMBRAPII e Transferência Tecnológica",
        "url": "https://genesis.puc-rio.br/equipe/"
    }
]

print(f"Total curated seed records: {len(CURATED_RECORDS)}")
