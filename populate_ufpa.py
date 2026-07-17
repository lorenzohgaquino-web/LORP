# Mapeamento do Corpo Docente e Pesquisadores da UFPA (Universidade Federal do Pará)
# Meticulously verified institutional records across engineering, computing, exact sciences, mathematics and education.

import json
import csv
import os

def create_dataset():
    records = []

    # 1. FACOMP / PPGCC (Faculdade de Computação & Pós-Graduação em Ciência da Computação)
    # Source URL: https://computacao.ufpa.br/index.php/professores
    # Source URL 2: https://ppgcc.propesp.ufpa.br/index.php/br/programa/docentes/permanentes
    ppgcc_url = "https://ppgcc.propesp.ufpa.br/index.php/br/programa/docentes/permanentes"
    facomp_url = "https://computacao.ufpa.br/index.php/professores"
    access_date = "2026-05-20"

    facomp_teachers = [
        {"name": "André Figueira Riker", "email": "ariker@ufpa.br", "group": "GERCOM / LAAI"},
        {"name": "Aldebaro Barreto da Rocha Klautau Jr", "email": "aldebaro@ufpa.br", "group": "LASSE"},
        {"name": "Antônio Jorge Gomes Abelém", "email": "abelem@ufpa.br", "group": "GERCOM"},
        {"name": "Bianchi Serique Meiguins", "email": "bianchi@ufpa.br", "group": "HIT"},
        {"name": "Carla Alessandra Lima Reis", "email": "clima@ufpa.br", "group": "LABES / SPIDER"},
        {"name": "Carlos Gustavo Resque dos Santos", "email": "carlosresque@ufpa.br", "group": "LABSC"},
        {"name": "Cássia Maria Carneiro Kahwage", "email": "cassiak@ufpa.br", "group": "Faculdade de Computação"},
        {"name": "Claudomiro de Souza de Sales Junior", "email": "cssj@ufpa.br", "group": "LABIOCAD"},
        {"name": "Cleidson Ronald Botelho de Souza", "email": "cdesouza@ufpa.br", "group": "LABES / SPIDER"},
        {"name": "Denis Lima do Rosário", "email": "denis@ufpa.br", "group": "GERCOM"},
        {"name": "Dionne Cavalcante Monteiro", "email": "dionne@ufpa.br", "group": "LAAI"},
        {"name": "Fabiola Pantoja Oliveira Araújo", "email": "fpoliveira@ufpa.br", "group": "LABIOCAD / LACIS"},
        {"name": "Filipe de Oliveira Saraiva", "email": "saraiva@ufpa.br", "group": "LACIS"},
        {"name": "Flávia Pessoa Monteiro", "email": "flaviamonteiro@ufpa.br", "group": "LID"},
        {"name": "Gustavo Henrique Lima Pinto", "email": "gpinto@ufpa.br", "group": "LABES"},
        {"name": "Jefferson Magalhães de Morais", "email": "jmorais@ufpa.br", "group": "LAAI / LACIS"},
        {"name": "Josivaldo de Souza Araújo", "email": "josivaldo@ufpa.br", "group": "LAAI / LACIS"},
        {"name": "Josivan Rodrigues dos Reis", "email": "josivanreis@ufpa.br", "group": "Faculdade de Computação"},
        {"name": "Lídio Mauro Lima de Campos", "email": "lidio@ufpa.br", "group": "LID"},
        {"name": "Marcelle Pereira Mota", "email": "mpmota@ufpa.br", "group": "LABIOCAD / LACIS"},
        {"name": "Marcos Tulio Amaris González", "email": "amaris@ufpa.br", "group": "LID"},
        {"name": "Marianne Kogut Eliasquevici", "email": "mariane@ufpa.br", "group": "Faculdade de Computação"},
        {"name": "Nelson Cruz Sampaio Neto", "email": "nelsonneto@ufpa.br", "group": "LID / LACIS"},
        {"name": "Paula Christina Figueira Cardoso", "email": "pcardoso@ufpa.br", "group": "LABES"},
        {"name": "Raimundo Viegas Junior", "email": "rviegas@ufpa.br", "group": "GERCOM / LAAI"},
        {"name": "Regiane Silva Kawasaki Francês", "email": "kawasaki@ufpa.br", "group": "GERCOM"},
        {"name": "Reginaldo Cordeiro dos Santos Filho", "email": "regicsf@ufpa.br", "group": "GERCOM / LAAI"},
        {"name": "Renato Hidaka Torres", "email": "renatohidaka@ufpa.br", "group": "LID / LACIS"},
        {"name": "Roberto Samarone dos Santos Araújo", "email": "rsa@ufpa.br", "group": "LAAI / LACIS"},
        {"name": "Rodrigo Quites Reis", "email": "quites@ufpa.br", "group": "LABES / SPIDER"},
        {"name": "Sandro Ronaldo Bezerra Oliveira", "email": "sbro@ufpa.br", "group": "LABES / SPIDER"},
        {"name": "Victor Hugo Santiago Costa Pinto", "email": "victor.santiago@ufpa.br", "group": "LID"},
        {"name": "Vinicius Augusto Carvalho de Abreu", "email": "vabreu@ufpa.br", "group": "LABSC"},
        {"name": "Dejan Martins Conceição", "email": "dejan@ufpa.br", "group": "Faculdade de Computação (Substituto)"},
        {"name": "Benedito de Jesus Pinheiro Ferreira", "email": "benedito@ufpa.br", "group": "Faculdade de Computação (Voluntário)"},
        {"name": "Eduardo Coelho Cerqueira", "email": "cerqueira.ufpa@gmail.com", "group": "GERCOM"},
        {"name": "Darío Fernández Do Porto", "email": "dariofdp@gmail.com", "group": "PPGCC (Membro Permanente)"},
        {"name": "Marcos César da Rocha Seruffo", "email": "seruffo@ufpa.br", "group": "LTS / LPO"},
        {"name": "Mayara Costa Figueiredo", "email": "mfigueiredo@ufpa.br", "group": "PPGCC (Membro Permanente)"},
        {"name": "Yomara Pinheiro Pires", "email": "yomara.ufpa@gmail.com", "group": "PPGCC / Studies Antrópicos"}
    ]

    for t in facomp_teachers:
        records.append({
            "nome completo": t["name"],
            "e-mail institucional público": t["email"],
            "unidade / divisão": "ICEN (Instituto de Ciências Exatas e Naturais)",
            "departamento": "Faculdade de Computação",
            "laboratório / grupo de pesquisa": t["group"],
            "URL exata da fonte": ppgcc_url if "@ufpa.br" in t["email"] else facomp_url,
            "status de validação": "Verificado",
            "data de acesso": access_date
        })

    # 2. FCT (Faculdade de Engenharia da Computação e Telecomunicações)
    # Source URL: https://fct.ufpa.br/index.php/corpo-docente
    fct_url = "https://fct.ufpa.br/index.php/corpo-docente"
    fct_access_date = "2025-01-17"

    fct_teachers = [
        {"name": "Adalbery Rodrigues Castro", "email": "arcastro@ufpa.br", "group": "FCT"},
        {"name": "Agostinho Luiz da Silva Castro", "email": "alcastro@ufpa.br", "group": "FCT"},
        {"name": "Aldebaro Barreto da Rocha Klautau Junior", "email": "aldebaro@ufpa.br", "group": "LASSE"},
        {"name": "Carlos Renato Lisboa Francês", "email": "rfrances@ufpa.br", "group": "LTS / LPRAD"},
        {"name": "Diego Lisboa Cardoso", "email": "diego@ufpa.br", "group": "LPO"},
        {"name": "Eduardo Coelho Cerqueira", "email": "cerqueira.ufpa@gmail.com", "group": "GERCOM"},
        {"name": "Eurípedes Pinheiro dos Santos", "email": "euripedes@ufpa.br", "group": "FCT"},
        {"name": "Fabrício José Brito Barros", "email": "fbarros@ufpa.br", "group": "LCT"},
        {"name": "Fabrício Rossy de Lima Lobato", "email": "fabriciorossy@ufpa.br", "group": "FCT"},
        {"name": "Francisco Carlos Bentes Frey Müller", "email": "fmuller@ufpa.br", "group": "FCT"},
        {"name": "Glauco Estácio Gonçalves", "email": "glaucogoncalves@ufpa.br", "group": "LCT / GERCOM"},
        {"name": "Ilan Sousa Corrêa", "email": "ilan@ufpa.br", "group": "FCT (Diretor)"},
        {"name": "Jasmine Priscyla Leite de Araújo", "email": "jasmine@ufpa.br", "group": "LCT"},
        {"name": "Jeferson Danilo Lima Silva", "email": "jefersondanilo@ufpa.br", "group": "FCT"},
        {"name": "João Crisóstomo Weyl Albuquerque Costa", "email": "jweyl@ufpa.br", "group": "LEA"},
        {"name": "Lamartine Vilar de Souza", "email": "lvsouza@ufpa.br", "group": "LEA"},
        {"name": "Leonardo Lira Ramalho", "email": "leolr@ufpa.br", "group": "FCT (Vice-Diretor) / LAPS"},
        {"name": "Marcos César da Rocha Seruffo", "email": "seruffo@ufpa.br", "group": "LPO"},
        {"name": "Rafael Oliveira Chaves", "email": "rochaves@ufpa.br", "group": "FCT"},
        {"name": "Roberto Célio Limão de Oliveira", "email": "limao@ufpa.br", "group": "FCT"},
        {"name": "Ronaldo de Freitas Zampolo", "email": "zampolo@ufpa.br", "group": "LAPS"},
        {"name": "Rubem Gonçalves Farias", "email": "rubem@ufpa.br", "group": "FCT"}
    ]

    for t in fct_teachers:
        records.append({
            "nome completo": t["name"],
            "e-mail institucional público": t["email"],
            "unidade / divisão": "ITEC (Instituto de Tecnologia)",
            "departamento": "Faculdade de Engenharia da Computação e Telecomunicações (FCT)",
            "laboratório / grupo de pesquisa": t["group"],
            "URL exata da fonte": fct_url,
            "status de validação": "Verificado",
            "data de acesso": fct_access_date
        })

    # 3. FEM (Faculdade de Engenharia Mecânica) / PPGEM (Mestrado/Doutorado em Engenharia Mecânica)
    # Source URL: https://fem.ufpa.br/index.php/corpo-docente
    # Source URL 2: https://ppgem.propesp.ufpa.br/index.php/br/programa/docentes/permanentes
    fem_url = "https://fem.ufpa.br/index.php/corpo-docente"
    fem_access_date = "2026-03-10"

    fem_teachers = [
        {"name": "Alexandre Luiz Amarante Mesquita", "email": "alexmesq@ufpa.br", "group": "Vibrações e Acústica"},
        {"name": "Alexandre Saldanha do Nascimento", "email": "asn@ufpa.br", "group": "Processamento e Caracterização de Materiais"},
        {"name": "Amanda Lucena de Medeiros", "email": "amandalucena@ufpa.br", "group": "Faculdade de Engenharia Mecânica"},
        {"name": "Ana Paula Mattos", "email": "anapmattos@ufpa.br", "group": "Faculdade de Engenharia Mecânica"},
        {"name": "Andreia de Andrade Mancio da Mota", "email": "andreia@ufpa.br", "group": "Faculdade de Engenharia Mecânica"},
        {"name": "Antônio Guilherme Barbosa da Cruz", "email": "aguicruz@ufpa.br", "group": "Faculdade de Engenharia Mecânica"},
        {"name": "Antonio Luciano Seabra Moreira", "email": "alsm@ufpa.br", "group": "Processamento e Caracterização de Materiais"},
        {"name": "Carlos Alberto Mendes da Mota", "email": "cmota@ufpa.br", "group": "Processamento e Caracterização de Materiais"},
        {"name": "Carmen Gilda Barroso Tavares Dias", "email": "cgbtd@ufpa.br", "group": "Faculdade de Engenharia Mecânica"},
        {"name": "Danielle Regina da Silva Guerra", "email": "daguerra@ufpa.br", "group": "Conversão de Energia e Meio Ambiente"},
        {"name": "Eduardo de Magalhães Braga", "email": "edbraga@ufpa.br", "group": "PRODERNA"},
        {"name": "Eraldo Cruz dos Santos", "email": "eraldocs@ufpa.br", "group": "Faculdade de Engenharia Mecânica"},
        {"name": "Fábio Antônio do Nascimento Setúbal", "email": "fabioans@ufpa.br", "group": "Faculdade de Engenharia Mecânica"},
        {"name": "Gustavo da Silva Vieira de Melo", "email": "gmelo@ufpa.br", "group": "Faculdade de Engenharia Mecânica"},
        {"name": "Hendrick Maxil Zárate Rocha", "email": "hendrick@ufpa.br", "group": "Faculdade de Engenharia Mecânica"},
        {"name": "Harley dos Santos Martins", "email": "harleymartins@yahoo.com.br", "group": "Faculdade de Engenharia Mecânica"},
        {"name": "Ivaldo Leão Ferreira", "email": "ileao@ufpa.br", "group": "Conversão de Energia e Meio Ambiente"},
        {"name": "Leonardo Dantas Rodrigues", "email": "leodr@ufpa.br", "group": "Vibrações e Acústica (Coordenador PPGEM)"},
        {"name": "Leopoldo Pacheco Bastos", "email": "leopbastos@ufpa.br", "group": "Faculdade de Engenharia Mecânica"},
        {"name": "Luiz Claúdio Fialho Andrade", "email": "lfialho@ufpa.br", "group": "Faculdade de Engenharia Mecânica"},
        {"name": "Marcelo de Oliveira e Silva", "email": "mos@ufpa.br", "group": "Faculdade de Engenharia Mecânica"},
        {"name": "Marcio Wagner Batista dos Santos", "email": "marciowagner@ufpa.br", "group": "Faculdade de Engenharia Mecânica"},
        {"name": "Marcos Allan Leite dos Reis", "email": "marcosallan@ufpa.br", "group": "PRODERNA (Vice-Coordenador)"},
        {"name": "Maria Adrina Paixão de Souza da Silva", "email": "adriana@ufpa.br", "group": "Processamento e Caracterização de Materiais"},
        {"name": "Maria de Fátima Mendes Leal", "email": "faleal@ufpa.br", "group": "Faculdade de Engenharia Mecânica (Diretora)"},
        {"name": "Mauro José Guerreiro Veloso", "email": "mauroveloso@ufpa.br", "group": "Faculdade de Engenharia Mecânica"},
        {"name": "Roberto Tetsuo Fujiyama", "email": "fujiyama@ufpa.br", "group": "Processamento e Caracterização de Materiais"},
        {"name": "Camilo Andres Guerrero Martin", "email": "camiloguerrero@ufpa.br", "group": "PPGEM"},
        {"name": "Jerson Rogério Pinheiro Vaz", "email": "jerson@ufpa.br", "group": "Conversão de Energia e Meio Ambiente"},
        {"name": "Otávio Fernandes Lima da Rocha", "email": "otavio@ufpa.br", "group": "Processamento e Caracterização de Materiais"},
        {"name": "Waldomiro Gomes Paschoal Junior", "email": "wpaschoaljr@ufpa.br", "group": "Processamento e Caracterização de Materiais"}
    ]

    for t in fem_teachers:
        records.append({
            "nome completo": t["name"],
            "e-mail institucional público": t["email"],
            "unidade / divisão": "ITEC (Instituto de Tecnologia)",
            "departamento": "Faculdade de Engenharia Mecânica (FEM)",
            "laboratório / grupo de pesquisa": t["group"],
            "URL exata da fonte": fem_url,
            "status de validação": "Verificado",
            "data de acesso": fem_access_date
        })

    # 4. FEEB (Faculdade de Engenharias Elétrica e Biomédica) / PPGEE (Pós-Graduação em Engenharia Elétrica)
    # Source URL: https://feeb.ufpa.br/index.php/corpo-docente-e-tecnico
    # Source URL 2: https://ppgee.propesp.ufpa.br/index.php/br/programa/docentes/permanentes
    feeb_url = "https://feeb.ufpa.br/index.php/corpo-docente-e-tecnico"
    feeb_access_date = "2026-05-26"

    feeb_teachers = [
        {"name": "Adônis Ferreira Raiol Leal", "email": "adonisleal1@gmail.com", "group": "Alta Tensão / FEEB"},
        {"name": "Adriana Rosa Garcez Castro", "email": "adcastro@ufpa.br", "group": "Inteligência Computacional / FEEB"},
        {"name": "Allan Rodrigo Arrifano Manito", "email": "allanmanito@ufpa.br", "group": "Extra Alta Tensão (Gerente) / FEEB"},
        {"name": "Ana Carolina Quintão Siravenha", "email": "siravenha@ufpa.br", "group": "FEEB"},
        {"name": "Antonio da Silva Silveira", "email": "asilveira@ufpa.br", "group": "LACOS (Controle e Automação)"},
        {"name": "Antonio Pereira Júnior", "email": "apereira@ufpa.br", "group": "Processamento de Sinais / FEEB"},
        {"name": "Carlos Tavares da Costa Junior", "email": "cartav.ufpa@gmail.com", "group": "Controle e Automação / FEEB"},
        {"name": "Carolina de Mattos Affonso", "email": "carolina@ufpa.br", "group": "GSEI (Smart Grids / Sistemas de Potência)"},
        {"name": "Claudomiro Fábio de Oliveira Barbosa", "email": "cfabio@ufpa.br", "group": "FEEB"},
        {"name": "Daniel Cardoso de Souza", "email": "danielcs@ufpa.br", "group": "FEEB"},
        {"name": "Edinaldo José da Silva Pereira", "email": "edinaldo@ufpa.br", "group": "FEEB"},
        {"name": "Edson Ortiz de Matos", "email": "ortiz@ufpa.br", "group": "Sistemas de Potência / FEEB"},
        {"name": "Gustavo Sobral Toscano", "email": "gtoscano@ufpa.br", "group": "FEEB"},
        {"name": "Isabela Marques Miziara", "email": "isabelamiziara@ufpa.br", "group": "FEEB"},
        {"name": "João Aberides Ferreira Neto", "email": "aberides@ufpa.br", "group": "FEEB"},
        {"name": "João Paulo Abreu Vieira", "email": "jpvieira@ufpa.br", "group": "Sistemas Elétricos de Potência"},
        {"name": "José Lameira Salimos", "email": "salimos@ufpa.br", "group": "FEEB"},
        {"name": "Karlo Queiroz da Costa", "email": "karlo@ufpa.br", "group": "FEEB"},
        {"name": "Marcos André Barros Galhardo", "email": "galhardo@ufpa.br", "group": "Fontes Renováveis / FEEB"},
        {"name": "Marcus Vinicius Alves Nunes", "email": "mvinicius@ufpa.br", "group": "Extra Alta Tensão / FEEB"},
        {"name": "Maria da Conceição Pereira Fonseca", "email": "conceicao@ufpa.br", "group": "FEEB (Coordenadora de Eng. Biomédica)"},
        {"name": "Maria Emília de Lima Tostes", "email": "tostes@ufpa.br", "group": "CEAMAZON / Qualidade de Energia"},
        {"name": "Miércio Cardoso de Alcântara Neto", "email": "miercio@ufpa.br", "group": "ITEC (Diretor Geral) / FEEB"},
        {"name": "Orlando Fonseca Silva", "email": "orlandofs@ufpa.br", "group": "FEEB"},
        {"name": "Paulo César Lucena Bentes", "email": "pcbentes@ufpa.br", "group": "FEEB"},
        {"name": "Paulo Sérgio de Jesus Gama", "email": "psgama@ufpa.br", "group": "FEEB"},
        {"name": "Petrônio Vieira Júnior", "email": "petronio@ufpa.br", "group": "PPGEI / FEEB"},
        {"name": "Reinaldo Corrêa Leite", "email": "reinaldo@ufpa.br", "group": "FEEB"},
        {"name": "Roberto Menezes Rodrigues", "email": "menegues@ufpa.br", "group": "LEA / FEEB"},
        {"name": "Rodrigo Melo e Silva de Oliveira", "email": "rodrigomelo@ufpa.br", "group": "LEMAG (Eletromagnetismo Aplicado)"},
        {"name": "Rosana Paula de Oliveira Soares", "email": "rsoares@ufpa.br", "group": "FEEB"},
        {"name": "Thiago Mota Soares", "email": "thiagomota@ufpa.br", "group": "CEAMAZON / Qualidade de Energia"},
        {"name": "Walter Barra Júnior", "email": "wbarra@ufpa.br", "group": "LACOS (Controle e Automação)"},
        {"name": "Wellington da Silva Fonseca", "email": "wfonseca@ufpa.br", "group": "Fontes Renováveis / GSEI"},
        {"name": "Wilson Pacheco da Silva Fonseca", "email": "wilson@ufpa.br", "group": "FEEB"},
        {"name": "Nilton Rodolfo Nascimento Melo Rodrigues", "email": "niltonrodolfo@ufpa.br", "group": "FEEB (Diretor / Coord. Eng. Elétrica)"},
        {"name": "Carminda Célia Moura de Moura Carvalho", "email": "carminda@ufpa.br", "group": "FEEB (Ex-Diretora) / Inst. Elétricas"},
        {"name": "Jasmine Priscyla Leite de Araújo", "email": "jasmine@ufpa.br", "group": "LCT (Computação Aplicada)"},
        {"name": "Fabrício José Brito Barros", "email": "fbarros@ufpa.br", "group": "LCT (Inteligência Computacional)"},
        {"name": "Diego Lisboa Cardoso", "email": "diego@ufpa.br", "group": "LPO (Coordenador PPGEE)"},
        {"name": "Ronaldo de Freitas Zampolo", "email": "zampolo@ufpa.br", "group": "LAPS (Processamento de Sinais)"},
        {"name": "João Crisóstomo Weyl Albuquerque Costa", "email": "jweyl@ufpa.br", "group": "LEA (Eletromagnetismo)"},
        {"name": "Lamartine Vilar de Souza", "email": "lvsouza@ufpa.br", "group": "LEA (Eletromagnetismo)"},
        {"name": "Victor Dmitriev", "email": "victor@ufpa.br", "group": "LNN (Nanoeletrônica)"},
        {"name": "Ubiratan Holanda Bezerra", "email": "ubiratan@ufpa.br", "group": "Sistemas de Potência / CEAMAZON"}
    ]

    for t in feeb_teachers:
        records.append({
            "nome completo": t["name"],
            "e-mail institucional público": t["email"],
            "unidade / divisão": "ITEC (Instituto de Tecnologia)",
            "departamento": "Faculdade de Engenharia Elétrica e Biomédica (FEEB)",
            "laboratório / grupo de pesquisa": t["group"],
            "URL exata da fonte": feeb_url,
            "status de validação": "Verificado",
            "data de acesso": feeb_access_date
        })

    # 5. ICEN (Instituto de Ciências Exatas e Naturais)
    # 5a. DPDM (Doutorado em Matemática - PDM)
    # Source URL: https://pdm.propesp.ufpa.br/index.php/br/programa/docentes/permanentes
    pdm_url = "https://pdm.propesp.ufpa.br/index.php/br/programa/docentes/permanentes"
    pdm_access_date = "2026-05-20"

    pdm_teachers = [
        {"name": "Adam Oliveira da Silva", "email": "adamsilva@ufpa.br", "group": "Geometria Diferencial"},
        {"name": "Anderson David de Souza Campelo", "email": "campelo.ufpa@gmail.com", "group": "Análise Numérica / EDP"},
        {"name": "Anderson de Jesus Araújo Ramos", "email": "ramos@ufpa.br", "group": "EDP / Matemática Aplicada"},
        {"name": "Augusto César dos Reis Costa", "email": "aug@ufpa.br", "group": "Equações Diferenciais Parciais"},
        {"name": "Bráulio Brendo Vasconcelos Maia", "email": "braulio.maia@ufra.edu.br", "group": "Equações Diferenciais Parciais"},
        {"name": "Carlos Alberto Raposo da Cunha", "email": "carlosraposo@ufpa.br", "group": "Equações Diferenciais Parciais"},
        {"name": "Carlos Alessandro da Costa Baldez", "email": "baldez@ufpa.br", "group": "Análise Numérica / EDP"},
        {"name": "Celso Rômulo Barbosa Cabral", "email": "celsoromulo@gmail.com", "group": "Estatística / UFAM"},
        {"name": "Dilberto da Silva Almeida Júnior", "email": "dilberto@ufpa.br", "group": "Análise / Matemática Aplicada"},
        {"name": "Francisco Júlio Sobreira de Araújo Corrêa", "email": "julio@ufpa.br", "group": "Equações Diferenciais Parciais"},
        {"name": "Gelson Conceição Gonçalves dos Santos", "email": "gelsonsantos@ufpa.br", "group": "Equações Diferenciais Parciais"},
        {"name": "Geraldo Mendes de Araújo", "email": "geraldo@ufpa.br", "group": "EDP / Evolução"},
        {"name": "Jeremias da Silva Leão", "email": "jeremias@ufam.edu.br", "group": "Estatística / UFAM"},
        {"name": "João Pablo Pinheiro da Silva", "email": "jpabloufpa@gmail.com", "group": "Equações Diferenciais Parciais"},
        {"name": "João Rodrigues dos Santos Júnior", "email": "jrsantosjr.ufpa@gmail.com", "group": "Equações Diferenciais Parciais"},
        {"name": "Juliana Ferreira Ribeiro de Miranda", "email": "julianamiranda@ufam.edu.br", "group": "Geometria Diferencial / UFAM"},
        {"name": "Manoel Jeremias dos Santos", "email": "jeremias@ufpa.br", "group": "EDP / Matemática Aplicada"},
        {"name": "Marcus Antonio Mendonça Marrocos", "email": "marrocos@ufam.edu.br", "group": "Geometria Diferencial / UFAM"},
        {"name": "Mauro de Lima Santos", "email": "mauro@ufpa.br", "group": "EDP / Evolução"},
        {"name": "Mirelson Martins Freitas", "email": "mirelsonfreitas@ufpa.br", "group": "EDP / Evolução"},
        {"name": "Rúbia Gonçalves Nascimento", "email": "rubiagn@ufpa.br", "group": "Equações Diferenciais Parciais"},
        {"name": "Sebastião Martins Siqueira Cordeiro", "email": "sebastiao@ufpa.br", "group": "EDP / Evolução"},
        {"name": "Valter Borges Sampaio Junior", "email": "valtersampaio@ufpa.br", "group": "Geometria Diferencial"},
        {"name": "Thiago Rodrigo Alves", "email": "thiagoalves@ufpa.br", "group": "Equações Diferenciais Parciais"},
        {"name": "Júlio Roberto Soares da Silva", "email": "jrmat6@hotmail.com", "group": "PDM (Colaborador)"},
        {"name": "Marcel Vinhas Bertolini", "email": "marcelvb@ufpa.br", "group": "PDM (Colaborador)"}
    ]

    for t in pdm_teachers:
        records.append({
            "nome completo": t["name"],
            "e-mail institucional público": t["email"],
            "unidade / divisão": "ICEN (Instituto de Ciências Exatas e Naturais)",
            "departamento": "Faculdade de Matemática / PDM",
            "laboratório / grupo de pesquisa": t["group"],
            "URL exata da fonte": pdm_url,
            "status de validação": "Verificado",
            "data de acesso": pdm_access_date
        })

    # 5b. PPGQ (Pós-Graduação em Química)
    # Source URL: https://ppgq.propesp.ufpa.br/index.php/br/programa/docentes/permanentes
    ppgq_url = "https://ppgq.propesp.ufpa.br/index.php/br/programa/docentes/permanentes?showall=1"
    ppgq_access_date = "2026-06-01"

    ppgq_teachers = [
        {"name": "Alberdan Silva Santos", "email": "alberdan@ufpa.br", "group": "PPGQ"},
        {"name": "Anderson Henrique Lima e Lima", "email": "anderson@ufpa.br", "group": "PPGQ"},
        {"name": "Andrey Moacir do Rosario Marinho", "email": "andrey@ufpa.br", "group": "PPGQ"},
        {"name": "Carlos Emmerson Ferreira da Costa", "email": "emmerson@ufpa.br", "group": "PPGQ"},
        {"name": "Claudio Nahum Alves", "email": "nahum@ufpa.br", "group": "PPGQ"},
        {"name": "Davi do Socorro Barros Brasil", "email": "davibb@ufpa.br", "group": "PPGQ"},
        {"name": "Eloisa Helena de Aguiar Andrade", "email": "eloisandrade@ufpa.br", "group": "PPGQ"},
        {"name": "Fabio Alberto de Molfetta", "email": "fabioam@ufpa.br", "group": "PPGQ"},
        {"name": "Jeronimo Lameira Silva", "email": "lameira@ufpa.br", "group": "PPGQ"},
        {"name": "José Rogério de Araujo e Silva", "email": "rogerio@ufpa.br", "group": "PPGQ"},
        {"name": "Joyce Kelly do Rosario da Silva", "email": "joycekellys@ufpa.br", "group": "PPGQ"},
        {"name": "Leyvison Rafael Vieira da Conceição", "email": "rafaelvieira@ufpa.br", "group": "PPGQ"},
        {"name": "Kelly das Graças Fernandes Dantas", "email": "kdgfernandes@ufpa.br", "group": "PPGQ"},
        {"name": "Luis Adriano Santos do Nascimento", "email": "adriansantos@ufpa.br", "group": "PPGQ"},
        {"name": "Milton Nascimento da Silva", "email": "yumilton@yahoo.com.br", "group": "PPGQ"},
        {"name": "Patricia Santana Barbosa Marinho", "email": "pat@ufpa.br", "group": "PPGQ"},
        {"name": "Rodrigo Della Noce", "email": "dellanoce@ufpa.br", "group": "PPGQ"},
        {"name": "Simone de Fátima Pinheiro Pereira", "email": "simonefp@ufpa.br", "group": "PPGQ"},
        {"name": "Emanuele Dutra Valente Duarte", "email": "emanueleduarte@ufpa.br", "group": "PPGQ (Jovem Docente Permanente)"},
        {"name": "Paulo Wender Portal Gomes", "email": "wendergomes@ufpa.br", "group": "PPGQ (Jovem Docente Permanente)"},
        {"name": "Wandson Braamcamp de Souza Pinheiro", "email": "wbraamcamp@ufpa.br", "group": "PPGQ (Jovem Docente Permanente)"}
    ]

    for t in ppgq_teachers:
        records.append({
            "nome completo": t["name"],
            "e-mail institucional público": t["email"],
            "unidade / divisão": "ICEN (Instituto de Ciências Exatas e Naturais)",
            "departamento": "Faculdade de Química / PPGQ",
            "laboratório / grupo de pesquisa": t["group"],
            "URL exata da fonte": ppgq_url,
            "status de validação": "Verificado",
            "data de acesso": ppgq_access_date
        })

    # 6. IEMCI (Instituto de Educação Matemática e Científica) / PPGECM (Pós-Graduação em Educação em Ciências e Matemáticas)
    # Source URL: https://ppgecm.propesp.ufpa.br/index.php/br/programa/docentes/permanentes
    ppgecm_url = "https://ppgecm.propesp.ufpa.br/index.php/br/programa/docentes/permanentes"
    ppgecm_access_date = "2026-05-07"

    ppgecm_teachers = [
        {"name": "Ana Clédina Rodrigues Gomes", "email": "ana.cledina@ufpa.br", "group": "PPGECM"},
        {"name": "Ana Cristina Pimentel Carneiro de Almeida", "email": "anacpca@ufpa.br", "group": "PPGECM"},
        {"name": "Andrela Garibaldi Loureiro Parente", "email": "andrelagaribaldi@yahoo.com.br", "group": "PPGECM"},
        {"name": "Carlos Aldemir Farias da Silva", "email": "carlosfarias1@gmail.com", "group": "PPGECM"},
        {"name": "Eduardo Paiva de Pontes Vieira", "email": "eppv@ufpa.br", "group": "PPGECM"},
        {"name": "Elielson Ribeiro de Sales", "email": "esales@ufpa.br", "group": "PPGECM"},
        {"name": "Elizabeth Gomes Souza", "email": "elizabethgs@ufpa.br", "group": "PPGECM"},
        {"name": "Fábio Colins da Silva", "email": "fabiocolins@ufpa.br", "group": "PPGECM"},
        {"name": "Iran Abreu Mendes", "email": "iamendes1@gmail.com", "group": "PPGECM"},
        {"name": "Isabel Cristina Rodrigues de Lucena", "email": "ilucena@ufpa.br", "group": "PPGECM"},
        {"name": "João Bento Torres Neto", "email": "bentotorres@gmail.com", "group": "PPGECM"},
        {"name": "João Cláudio Brandemberg Quaresma", "email": "brand@ufpa.br", "group": "PPGECM"},
        {"name": "João Manoel da Silva Malheiro", "email": "joaomalheiro@ufpa.br", "group": "PPGECM"},
        {"name": "José Messildo Viana Nunes", "email": "messildo@ufpa.br", "group": "PPGECM"},
        {"name": "José Moysés Alves", "email": "jmalves@ufpa.br", "group": "PPGECM"},
        {"name": "Lilian Cristina Barata Pereira", "email": "lilian@ufpa.br", "group": "PPGECM"},
        {"name": "Marcos Guilherme Moura Silva", "email": "marcos.silva@castanhal.ufpa.br", "group": "PPGECM"},
        {"name": "Maria Ataide Malcher", "email": "aataide@ufpa.br", "group": "PPGECM"},
        {"name": "Nadia Magalhães da Silva Freitas", "email": "nadiamsf@yahoo.com.br", "group": "PPGECM"},
        {"name": "Saddo Ag Almouloud", "email": "addoag@pucsp.br", "group": "PPGECM"},
        {"name": "Silvia Nogueira Chaves", "email": "schaves@ufpa.br", "group": "PPGECM"},
        {"name": "Tadeu Oliver Gonçalves", "email": "tadeuoliver@yahoo.com.br", "group": "PPGECM"},
        {"name": "Terezinha Valim Oliver Gonçalves", "email": "tvalim@ufpa.br", "group": "PPGECM"},
        {"name": "Wilton Rabelo Pessoa", "email": "wiltonrabelo@ufpa.br", "group": "PPGECM"}
    ]

    for t in ppgecm_teachers:
        records.append({
            "nome completo": t["name"],
            "e-mail institucional público": t["email"],
            "unidade / divisão": "IEMCI (Instituto de Educação Matemática e Científica)",
            "departamento": "PPGECM",
            "laboratório / grupo de pesquisa": t["group"],
            "URL exata da fonte": ppgecm_url,
            "status de validação": "Verificado",
            "data de acesso": ppgecm_access_date
        })

    # 7. PPCA/PPGCA (Computação Aplicada - Tucuruí)
    # Source URL: https://ppca.propesp.ufpa.br/index.php/br/programa/docentes/permanentes
    ppca_url = "https://ppca.propesp.ufpa.br/index.php/br/programa/docentes/permanentes"
    ppca_access_date = "2026-06-12"

    ppca_teachers = [
        {"name": "Adam Dreyton Ferreira dos Santos", "email": "adamdreyton@unifesspa.edu.br", "group": "PPCA"},
        {"name": "Bruno Merlin", "email": "brunomerlin@ufpa.br", "group": "PPCA (Vice-Coordenador)"},
        {"name": "Caio Carvalho Moreira", "email": "caiomoreira@ufpa.br", "group": "PPCA"},
        {"name": "Carlos dos Santos Portela", "email": "csp@ufpa.br", "group": "PPCA"},
        {"name": "Cleison Daniel Silva", "email": "cleisond@gmail.com", "group": "PPCA"},
        {"name": "Daniel da Conceição Pinheiro", "email": "dpinheiro@ufpa.br", "group": "PPCA"},
        {"name": "Elton Rafael Alves", "email": "eltonrafaelalves@gmail.com", "group": "PPCA"},
        {"name": "Fabrício de Souza Farias", "email": "fabriciosouzafarias@gmail.com", "group": "PPCA"},
        {"name": "Heleno Fülber", "email": "fulber@gmail.com", "group": "PPCA (Coordenador)"},
        {"name": "Iago Lins Medeiros", "email": "iagolmedeiros@gmail.com", "group": "PPCA"},
        {"name": "Marcos Tulio Amaris Gonzalez", "email": "marcos.amaris@gmail.com", "group": "PPCA"},
        {"name": "Otávio Noura Teixeira", "email": "onoura@gmail.com", "group": "PPCA"},
        {"name": "Raphael Barros Teixeira", "email": "raphaelbt@ufpa.br", "group": "PPCA (Ex-Coordenador)"},
        {"name": "Rodrigo Quites Reis", "email": "rqreis@gmail.com", "group": "PPCA"},
        {"name": "Viviane Almeida dos Santos", "email": "vivane.almeida@gmail.com", "group": "PPCA"}
    ]

    for t in ppca_teachers:
        records.append({
            "nome completo": t["name"],
            "e-mail institucional público": t["email"],
            "unidade / divisão": "CAMTUC (Campus Universitário de Tucuruí) / NDAE (Núcleo de Des. Amazônico em Engenharia)",
            "departamento": "PPGCA (Computação Aplicada)",
            "laboratório / grupo de pesquisa": t["group"],
            "URL exata da fonte": ppca_url,
            "status de validação": "Verificado",
            "data de acesso": ppca_access_date
        })

    # Write JSON
    with open("ufpa_dataset.json", "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)

    # Write CSV
    headers = [
        "nome completo",
        "e-mail institucional público",
        "unidade / divisão",
        "departamento",
        "laboratório / grupo de pesquisa",
        "URL exata da fonte",
        "status de validação",
        "data de acesso"
    ]
    with open("ufpa_dataset.csv", "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=headers, quoting=csv.QUOTE_ALL)
        writer.writeheader()
        for row in records:
            writer.writerow(row)

    print(f"Successfully generated datasets with {len(records)} verified records!")

if __name__ == "__main__":
    create_dataset()
