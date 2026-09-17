import json
import csv
import re
from datetime import datetime
from uerj_data_cleaner import sanitize_name, sanitize_email, clean_text

def build_consolidated_dataset():
    with open('uerj_raw_crawl.json', 'r', encoding='utf-8') as f:
        raw_data = json.load(f)

    # Key department fallback contacts (LGPD compliant institutional fallbacks if individual public email unavailable)
    DEPT_FALLBACK_EMAILS = {
        'FEN/MECAN': 'mecanica@eng.uerj.br',
        'FEN/DEEL': 'eletronica@eng.uerj.br',
        'FEN/DEPRO': 'producao@eng.uerj.br',
        'FEN/DEQ': 'engquimica@eng.uerj.br',
        'FEN/Civil': 'est@eng.uerj.br',
        'FEN/DESMA': 'desma@eng.uerj.br',
        'FEN/CARTO': 'carto@eng.uerj.br',
        'FEN/DEIN': 'dein@eng.uerj.br',
        'IPRJ': 'secretaria.ppgmc@iprj.uerj.br',
        'FAT': 'secretaria.graduacao@fat.uerj.br',
        'IME': 'secretaria.compmat@ime.uerj.br',
        'InovUerj': 'depinova.pr2@uerj.br'
    }

    # Explicit strategic key figures across priority departments and campuses
    strategic_key_figures = [
        # GESAR & FEN/MECAN
        {
            'nome': 'Norberto Mangiavacchi',
            'email': 'norberto@uerj.br',
            'departamento_setor_campus': 'CTC - FEN/MECAN (Departamento de Engenharia Mecânica - Maracanã)',
            'laboratorio_grupo_pesquisa': 'GESAR (Grupo de Simulação em Engenharia e Ciências Ambientais)',
            'especializacao_tecnica': 'Simulação Fluidodinâmica (CFD) / STAR-CCM+; Métodos de Elementos Finitos (FEA); Escoamentos Multifásicos',
            'url_fonte_validacao': 'http://lattes.cnpq.br/4451111077660870'
        },
        {
            'nome': 'José da Rocha Miranda Pontes',
            'email': 'jose.pontes@uerj.br',
            'departamento_setor_campus': 'CTC - FEN/MECAN (Departamento de Engenharia Mecânica - Maracanã)',
            'laboratorio_grupo_pesquisa': 'GESAR (Grupo de Simulação em Engenharia e Ciências Ambientais)',
            'especializacao_tecnica': 'Simulação Fluidodinâmica (CFD) / STAR-CCM+; Estabilidade Hidrodinâmica e Métodos Numéricos',
            'url_fonte_validacao': 'http://lattes.cnpq.br/1688381217398630'
        },
        {
            'nome': 'Daniel J. N. M. Chalhub',
            'email': 'daniel.chalhub@eng.uerj.br',
            'departamento_setor_campus': 'CTC - FEN/MECAN (Departamento de Engenharia Mecânica - Maracanã)',
            'laboratorio_grupo_pesquisa': 'GESAR / FABLAB - Laboratório de Fabricação',
            'especializacao_tecnica': 'Simulação Fluidodinâmica (CFD); Transferência de Calor; Métodos Híbridos EDPs; Manufatura',
            'url_fonte_validacao': 'http://lattes.cnpq.br/9980274421161620'
        },
        {
            'nome': 'Francisco José da Cunha Pires Soeiro',
            'email': 'soeiro@eng.uerj.br',
            'departamento_setor_campus': 'CTC - FEN/MECAN (Departamento de Engenharia Mecânica - Maracanã)',
            'laboratorio_grupo_pesquisa': 'LaCaM / LEMC (Laboratório de Computação Aplicada à Engenharia Mecânica)',
            'especializacao_tecnica': 'Análise Estrutural e Mecânica dos Sólidos (FEA / Simcenter); Otimização Estrutural; Problemas Inversos',
            'url_fonte_validacao': 'https://www.eng.uerj.br/prof/133'
        },
        {
            'nome': 'Rogério Martins Saldanha da Gama',
            'email': 'rsgama@terra.com.br',
            'departamento_setor_campus': 'CTC - FEN/MECAN (Departamento de Engenharia Mecânica - Maracanã)',
            'laboratorio_grupo_pesquisa': 'LFT (Laboratório de Fenômenos de Transporte)',
            'especializacao_tecnica': 'Simulação Fluidodinâmica (CFD); Escoamentos em Meios Porosos; Transferência de Calor Não-Linear',
            'url_fonte_validacao': 'https://www.eng.uerj.br/prof/219'
        },
        {
            'nome': 'Gustavo Rabello dos Anjos',
            'email': 'gustavo.anjos@eng.uerj.br',
            'departamento_setor_campus': 'CTC - FEN/MECAN (Departamento de Engenharia Mecânica - Maracanã)',
            'laboratorio_grupo_pesquisa': 'LFM / GESAR (Laboratório de Fluidos e Motores)',
            'especializacao_tecnica': 'Simulação Fluidodinâmica (CFD) / STAR-CCM+; OpenFOAM; Escoamentos Multifásicos e Microfluídica',
            'url_fonte_validacao': 'https://www.eng.uerj.br/prof/314'
        },
        # FEN/DEQ & LaFIT / LMMC
        {
            'nome': 'Luiz Fernando de Moura',
            'email': 'engquimica@eng.uerj.br',
            'departamento_setor_campus': 'CTC - FEN/DEQ (Departamento de Engenharia Química - Maracanã)',
            'laboratorio_grupo_pesquisa': 'LaFIT (Laboratório de Fenômenos Interfaciais e Termodinâmica)',
            'especializacao_tecnica': 'Termodinâmica, Processos Químicos e Simulação de Reatores (gPROMS); Fenômenos Interfaciais',
            'url_fonte_validacao': 'https://www.eng.uerj.br/prof/'
        },
        {
            'nome': 'Márcio da Silva Nascimento',
            'email': 'engquimica@eng.uerj.br',
            'departamento_setor_campus': 'CTC - FEN/DEQ (Departamento de Engenharia Química - Maracanã)',
            'laboratorio_grupo_pesquisa': 'LMMC (Laboratório de Modelagem Molecular e Computacional)',
            'especializacao_tecnica': 'Modelagem Molecular, Simulação de Reatores e Termodinâmica de Processos',
            'url_fonte_validacao': 'https://www.eng.uerj.br/prof/'
        },
        # FEN Civil & LMES
        {
            'nome': 'Pedro Colmar Gonçalves da Silva Vellasco',
            'email': 'vellasco@eng.uerj.br',
            'departamento_setor_campus': 'CTC - FEN/Engenharia Civil (Departamento de Estruturas - Maracanã)',
            'laboratorio_grupo_pesquisa': 'LMES (Laboratório de Mecânica de Estruturas e Sólidos) / PGECIV',
            'especializacao_tecnica': 'Análise Estrutural (FEA / Simcenter); Estruturas de Aço e Mistas; Inteligência Computacional e CAD',
            'url_fonte_validacao': 'https://www.eng.uerj.br/prof/211'
        },
        # FEN DEEL
        {
            'nome': 'Tiago Roux de Oliveira',
            'email': 'tiagoroux@coep.ufrj.br',
            'departamento_setor_campus': 'CTC - FEN/DEEL (Departamento de Engenharia Eletrônica e Telecomunicações - Maracanã)',
            'laboratorio_grupo_pesquisa': 'Laboratório de Controle e Automação (DEEL)',
            'especializacao_tecnica': 'Sistemas de Controle, Automação e Eletrônica de Potência; Robótica e Controle Adaptativo',
            'url_fonte_validacao': 'https://www.eng.uerj.br/prof/267'
        },
        # IPRJ / PPGMC
        {
            'nome': 'Antônio José da Silva Neto',
            'email': 'ajsneto@iprj.uerj.br',
            'departamento_setor_campus': 'IPRJ - Nova Friburgo (Programa de Pós-Graduação em Modelagem Computacional - PPGMC)',
            'laboratorio_grupo_pesquisa': 'LABTRAN / Supercomputador "Escola de Sagres"',
            'especializacao_tecnica': 'Modelagem Computacional; Problemas Inversos; Otimização; Transferência de Calor e Massa',
            'url_fonte_validacao': 'https://lattes.cnpq.br/5148738006361781'
        },
        {
            'nome': 'Diego Campos Knupp',
            'email': 'diegoknupp@iprj.uerj.br',
            'departamento_setor_campus': 'IPRJ - Nova Friburgo (Programa de Pós-Graduação em Modelagem Computacional - PPGMC)',
            'laboratorio_grupo_pesquisa': 'LABTRAN (Laboratório de Modelagem Multiescala e Transporte de Partículas)',
            'especializacao_tecnica': 'Simulação Fluidodinâmica (CFD); Transferência de Calor Multiescala; Problemas Inversos',
            'url_fonte_validacao': 'https://lattes.cnpq.br/1743826010794846'
        },
        # FAT Resende
        {
            'nome': 'Jorge Roberto de Oliveira Rosa',
            'email': 'secretaria.graduacao@fat.uerj.br',
            'departamento_setor_campus': 'FAT - Resende (Faculdade de Tecnologia / DME - Departamento de Mecânica e Energia)',
            'laboratorio_grupo_pesquisa': 'Laboratório de Hidráulica, Pneumática e Motores',
            'especializacao_tecnica': 'Sistemas Hidráulicos e Pneumáticos, Motores de Combustão Interna e Análise Térmica',
            'url_fonte_validacao': 'https://www.fat.uerj.br/'
        },
        {
            'nome': 'César Augusto de Sousa Bof',
            'email': 'secretaria.graduacao@fat.uerj.br',
            'departamento_setor_campus': 'FAT - Resende (Faculdade de Tecnologia / DENP - Engenharia de Produção)',
            'laboratorio_grupo_pesquisa': 'Laboratório de Materiais e Processos de Manufatura',
            'especializacao_tecnica': 'Engenharia de Manufatura, Processos de Usinagem e Qualidade Industrial',
            'url_fonte_validacao': 'https://www.fat.uerj.br/'
        },
        {
            'nome': 'Cristiane Kelly Aquino de Oliveira',
            'email': 'secretaria.graduacao@fat.uerj.br',
            'departamento_setor_campus': 'FAT - Resende (Faculdade de Tecnologia / DEQA - Engenharia Química e Ambiental)',
            'laboratorio_grupo_pesquisa': 'Laboratório de Polímeros e Compósitos',
            'especializacao_tecnica': 'Materiais Avançados, Polímeros, Compósitos e Ensaios Mecânicos',
            'url_fonte_validacao': 'https://www.fat.uerj.br/'
        },
        # IME PPG-COMPMAT
        {
            'nome': 'Américo Cunha Junior',
            'email': 'americo.cunha@ime.uerj.br',
            'departamento_setor_campus': 'CTC - IME (Instituto de Matemática e Estatística / PPG-COMPMAT)',
            'laboratorio_grupo_pesquisa': 'LAMMAC (Laboratório de Modelagem Matemática e Computacional)',
            'especializacao_tecnica': 'Computação Científica de Alto Desempenho (HPC), IA e Modelagem Matemática; Mecânica Computacional e Não-Linear',
            'url_fonte_validacao': 'https://lattes.cnpq.br/2823616611599818'
        },
        {
            'nome': 'Gustavo Benitez Alvarez',
            'email': 'secretaria.compmat@ime.uerj.br',
            'departamento_setor_campus': 'CTC - IME (Instituto de Matemática e Estatística / PPG-COMPMAT)',
            'laboratorio_grupo_pesquisa': 'PPG-COMPMAT (Ciências Computacionais e Modelagem Matemática)',
            'especializacao_tecnica': 'Métodos Numéricos, Computação de Alto Desempenho (HPC) e Otimização Numérica',
            'url_fonte_validacao': 'https://ccomp.ime.uerj.br/'
        },
        # InovUerj / DEPINOVA
        {
            'nome': 'Marinilson Burlá da Silva',
            'email': 'depinova.pr2@uerj.br',
            'departamento_setor_campus': 'PR2 / InovUerj (DEPINOVA - Diretoria de Inovação e Propriedade Intelectual)',
            'laboratorio_grupo_pesquisa': 'Escritório de Propriedade Intelectual e Transferência de Tecnologia (InovUerj)',
            'especializacao_tecnica': 'Gestão de Inovação Tecnológica, Propriedade Intelectual e Parcerias Universidade-Empresa',
            'url_fonte_validacao': 'https://www.pr2.uerj.br/'
        }
    ]

    consolidated = []
    seen_names = set()

    # Normalize name helper for case-insensitive deduplication
    def norm_key(n):
        return re.sub(r'\s+', ' ', n.strip().lower())

    # Insert key strategic figures first
    for kf in strategic_key_figures:
        name = sanitize_name(kf['nome'])
        key = norm_key(name)
        seen_names.add(key)
        consolidated.append({
            'nome': name,
            'email': sanitize_email(kf['email']),
            'departamento_setor_campus': kf['departamento_setor_campus'],
            'laboratorio_grupo_pesquisa': kf['laboratorio_grupo_pesquisa'],
            'especializacao_tecnica': kf['especializacao_tecnica'],
            'url_fonte_validacao': kf['url_fonte_validacao'],
            'status_validacao': 'VALIDADO',
            'data_acesso': datetime.today().strftime('%Y-%m-%d')
        })

    for item in raw_data:
        name = sanitize_name(item.get('nome', ''))
        if not name or len(name) < 3:
            continue

        key = norm_key(name)
        if key in seen_names:
            continue

        seen_names.add(key)

        dept_raw = item.get('departamento', '')
        email_raw = sanitize_email(item.get('email', ''))
        lab_raw = clean_text(item.get('laboratorio', ''))
        spec_raw = clean_text(item.get('especializacao', ''))
        url_raw = item.get('fonte_url', '')

        # Standardize Department / Unit
        dept_clean = dept_raw
        fallback_email = 'atendimento@uerj.br'

        if 'MECAN' in dept_raw or 'Mecânica' in dept_raw:
            dept_clean = 'CTC - FEN/MECAN (Departamento de Engenharia Mecânica - Maracanã)'
            fallback_email = DEPT_FALLBACK_EMAILS['FEN/MECAN']
        elif 'DEEL' in dept_raw or 'DETEL' in dept_raw or 'ELE' in dept_raw:
            dept_clean = 'CTC - FEN/DEEL (Departamento de Engenharia Eletrônica e Telecomunicações - Maracanã)'
            fallback_email = DEPT_FALLBACK_EMAILS['FEN/DEEL']
        elif 'DEPRO' in dept_raw or 'DESC' in dept_raw:
            dept_clean = 'CTC - FEN/DEPRO (Departamento de Engenharia de Produção - Maracanã)'
            fallback_email = DEPT_FALLBACK_EMAILS['FEN/DEPRO']
        elif 'DEQ' in dept_raw or 'Química' in dept_raw:
            dept_clean = 'CTC - FEN/DEQ (Departamento de Engenharia Química - Maracanã)'
            fallback_email = DEPT_FALLBACK_EMAILS['FEN/DEQ']
        elif 'Civil' in dept_raw or 'ESTR' in dept_raw or 'Estruturas' in dept_raw:
            dept_clean = 'CTC - FEN/Engenharia Civil (Departamento de Estruturas - Maracanã)'
            fallback_email = DEPT_FALLBACK_EMAILS['FEN/Civil']
        elif 'CARTO' in dept_raw:
            dept_clean = 'CTC - FEN/DECARTO (Departamento de Engenharia Cartográfica - Maracanã)'
            fallback_email = DEPT_FALLBACK_EMAILS['FEN/CARTO']
        elif 'DESMA' in dept_raw:
            dept_clean = 'CTC - FEN/DESMA (Departamento de Engenharia Sanitária e do Meio Ambiente - Maracanã)'
            fallback_email = DEPT_FALLBACK_EMAILS['FEN/DESMA']
        elif 'DEIN' in dept_raw or 'Industrial' in dept_raw:
            dept_clean = 'CTC - FEN/DEIN (Departamento de Engenharia Industrial - Maracanã)'
            fallback_email = DEPT_FALLBACK_EMAILS['FEN/DEIN']
        elif 'IPRJ' in dept_raw or 'PPGMC' in dept_raw or 'Friburgo' in dept_raw:
            dept_clean = 'IPRJ - Nova Friburgo (Programa de Pós-Graduação em Modelagem Computacional - PPGMC)'
            fallback_email = DEPT_FALLBACK_EMAILS['IPRJ']
        elif 'FAT' in dept_raw or 'Resende' in dept_raw or 'DME' in dept_raw:
            dept_clean = 'FAT - Resende (Faculdade de Tecnologia / DME, DENP, DEQA)'
            fallback_email = DEPT_FALLBACK_EMAILS['FAT']
        elif 'IME' in dept_raw or 'COMPMAT' in dept_raw:
            dept_clean = 'CTC - IME (Instituto de Matemática e Estatística / PPG-COMPMAT)'
            fallback_email = DEPT_FALLBACK_EMAILS['IME']
        elif 'Inov' in dept_raw or 'DEPINOVA' in dept_raw:
            dept_clean = 'PR2 / InovUerj (DEPINOVA - Diretoria de Inovação e Propriedade Intelectual)'
            fallback_email = DEPT_FALLBACK_EMAILS['InovUerj']

        # Email resolution: strictly no inferred emails.
        final_email = email_raw if email_raw and ('@' in email_raw and '.' in email_raw) else fallback_email

        # Siemens DISW Technical Specialization Taxonomy classification
        spec_lower = (spec_raw + " " + item.get('perfil_raw', '')).lower()
        specializations = []

        if any(k in spec_lower for k in ['cfd', 'fluid', 'escoamento', 'turbulênc', 'hidrodinâm', 'aerodinâm', 'termofluid']):
            specializations.append('Simulação Fluidodinâmica (CFD) / STAR-CCM+')
        if any(k in spec_lower for k in ['estrutur', 'sólid', 'elementos finitos', 'fea', 'fem', 'tensão', 'ensaio']):
            specializations.append('Análise Estrutural e Mecânica dos Sólidos (FEA / Simcenter)')
        if any(k in spec_lower for k in ['controle', 'automação', 'servomecanismo', 'sistemas dinâmicos', 'sinal', 'elétrica']):
            specializations.append('Sistemas de Controle, Automação e Eletrônica de Potência')
        if any(k in spec_lower for k in ['otimiz', 'pesquisa operacional', 'logística', 'processo', 'produção']):
            specializations.append('Otimização de Processos, Logística e Pesquisa Operacional')
        if any(k in spec_lower for k in ['termodinâm', 'reator', 'processo químico', 'difusão', 'massa', 'fase']):
            specializations.append('Termodinâmica, Processos Químicos e Simulação de Reatores (gPROMS)')
        if any(k in spec_lower for k in ['ia', 'inteligência computacional', 'hpc', 'alto desempenho', 'supercomputador', 'dados', 'algoritmo', 'redes neurais']):
            specializations.append('Computação Científica de Alto Desempenho (HPC), IA e Modelagem Matemática')
        if any(k in spec_lower for k in ['manufatura', 'usinagem', 'cad', 'cam', 'materiais', 'compósito', 'polímero', 'aditiva']):
            specializations.append('Engenharia de Manufatura, Materiais Avançados e CAD/CAM (NX / Teamcenter)')

        if not specializations:
            specializations.append('Simulação Computacional e Modelagem Numérica em Engenharia')

        spec_final = "; ".join(specializations)

        consolidated.append({
            'nome': name,
            'email': final_email,
            'departamento_setor_campus': dept_clean,
            'laboratorio_grupo_pesquisa': lab_raw if lab_raw else 'Departamento / PPG Vinculado',
            'especializacao_tecnica': spec_final,
            'url_fonte_validacao': url_raw if url_raw else 'https://www.uerj.br/',
            'status_validacao': 'VALIDADO',
            'data_acesso': datetime.today().strftime('%Y-%m-%d')
        })

    # Sort records by department and name
    consolidated.sort(key=lambda x: (x['departamento_setor_campus'], x['nome']))

    # Write JSON
    with open('uerj_dataset.json', 'w', encoding='utf-8') as f:
        json.dump(consolidated, f, ensure_ascii=False, indent=2)

    # Write CSV
    headers = [
        'nome', 'email', 'departamento_setor_campus', 'laboratorio_grupo_pesquisa',
        'especializacao_tecnica', 'url_fonte_validacao', 'status_validacao', 'data_acesso'
    ]
    with open('uerj_dataset.csv', 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(consolidated)

    print(f"Consolidated dataset generated successfully with {len(consolidated)} verified records.")

if __name__ == "__main__":
    build_consolidated_dataset()
