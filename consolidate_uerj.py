import json
import datetime

from uerj_data_cleaner import (
    clean_person_name,
    is_valid_person_name,
    classify_siemens_specialization,
    DEPT_FALLBACK_EMAILS
)

def consolidate():
    with open('uerj_raw_extraction.json', 'r', encoding='utf-8') as f:
        raw = json.load(f)

    consolidated = []
    seen_names = set()
    access_date = datetime.date.today().strftime('%d/%m/%Y')

    # 1. Process FEN Maracanã
    print("Consolidating FEN records...")
    for item in raw.get('fen', []):
        raw_name = item.get('name', '')
        name = clean_person_name(raw_name)

        if not is_valid_person_name(name):
            continue

        norm_key = name.lower()
        if norm_key in seen_names:
            continue

        depto_raw = item.get('depto', 'FEN').upper()

        # Determine department standard code
        if 'MEC' in depto_raw or 'MECAN' in depto_raw:
            unit = 'FEN/MECAN - Campus Maracanã'
            fallback_email = DEPT_FALLBACK_EMAILS['FEN/MECAN']
            dept_key = 'FEN/MECAN'
        elif 'ELE' in depto_raw or 'DEEL' in depto_raw or 'PEL' in depto_raw:
            unit = 'FEN/DEEL - Campus Maracanã'
            fallback_email = DEPT_FALLBACK_EMAILS['FEN/DEEL']
            dept_key = 'FEN/DEEL'
        elif 'PRO' in depto_raw or 'IND' in depto_raw or 'DEIN' in depto_raw:
            unit = 'FEN/DEPRO - Campus Maracanã'
            fallback_email = DEPT_FALLBACK_EMAILS['FEN/DEPRO']
            dept_key = 'FEN/DEPRO'
        elif 'QUI' in depto_raw or 'DEQ' in depto_raw:
            unit = 'FEN/DEQ - Campus Maracanã'
            fallback_email = DEPT_FALLBACK_EMAILS['FEN/DEQ']
            dept_key = 'FEN/DEQ'
        elif 'CIV' in depto_raw or 'DESC' in depto_raw:
            unit = 'FEN/CIVIL - Campus Maracanã'
            fallback_email = DEPT_FALLBACK_EMAILS['FEN/CIVIL']
            dept_key = 'FEN/CIVIL'
        else:
            unit = 'FEN - Campus Maracanã'
            fallback_email = DEPT_FALLBACK_EMAILS['FEN']
            dept_key = 'FEN'

        # Email: if prof public email exists, use it; otherwise use department fallback email (NO INFERRED)
        raw_emails = item.get('emails', [])
        valid_emails = [e for e in raw_emails if 'eng.uerj.br' in e or 'uerj.br' in e or 'gmail' in e or 'yahoo' in e]
        primary_email = valid_emails[0] if valid_emails else fallback_email

        # Lab
        html_summary = item.get('html_summary', '')
        lab = "Laboratório / Grupo de Pesquisa FEN"
        if "GESAR" in html_summary:
            lab = "GESAR (Grupo de Simulação em Eng. e Ciências Ambientais)"
        elif "LAMMAC" in html_summary:
            lab = "LAMMAC (Laboratório de Modelagem Matemática e Computacional)"
        elif "LaCaM" in html_summary:
            lab = "LaCaM (Laboratório de Computação Aplicada à Eng. Mecânica)"
        elif "LFT" in html_summary:
            lab = "LFT (Laboratório de Fenômenos de Transporte)"
        elif "LFM" in html_summary:
            lab = "LFM (Laboratório de Fluidos e Motores)"
        elif "LMES" in html_summary:
            lab = "LMES (Laboratório de Mecânica de Estruturas e Sólidos)"
        elif "LaFIT" in html_summary:
            lab = "LaFIT (Fenômenos Interfaciais e Termodinâmica)"
        elif "LMMC" in html_summary:
            lab = "LMMC (Modelagem Molecular e Computacional)"

        # Lattes
        lattes_list = item.get('lattes', [])
        lattes_url = lattes_list[0] if lattes_list else item.get('url', '')

        spec = classify_siemens_specialization(html_summary, unit, lab)

        consolidated.append({
            'nome': name,
            'email': primary_email,
            'unidade_departamento': unit,
            'laboratorio_grupo': lab,
            'especializacao_tecnica': spec,
            'url_fonte': lattes_url or item.get('url', ''),
            'status_validacao': 'Validado via Portal FEN / UERJ',
            'data_acesso': access_date
        })
        seen_names.add(norm_key)

    # 2. Process IPRJ & PPGMC (Nova Friburgo)
    print("Consolidating IPRJ records...")
    for item in raw.get('iprj', []):
        raw_name = item.get('name', '')
        name = clean_person_name(raw_name)

        if not is_valid_person_name(name):
            continue

        norm_key = name.lower()
        if norm_key in seen_names:
            continue

        unit = 'IPRJ - Campus Nova Friburgo'
        fallback_email = DEPT_FALLBACK_EMAILS['IPRJ']

        raw_emails = item.get('emails', [])
        primary_email = raw_emails[0] if raw_emails else fallback_email

        context = item.get('context', '')
        lab = "PPGMC / LABTRAN (Laboratório de Modelagem Multiescala e Transporte de Partículas)" if "LABTRAN" in context else "PPGMC / IPRJ (Modelagem Computacional)"

        lattes_list = item.get('lattes', [])
        lattes_url = lattes_list[0] if lattes_list else item.get('url', '')

        spec = classify_siemens_specialization(context, unit, lab)

        consolidated.append({
            'nome': name,
            'email': primary_email,
            'unidade_departamento': unit,
            'laboratorio_grupo': lab,
            'especializacao_tecnica': spec,
            'url_fonte': lattes_url or item.get('url', ''),
            'status_validacao': 'Validado via Portal IPRJ / UERJ',
            'data_acesso': access_date
        })
        seen_names.add(norm_key)

    # 3. Process FAT (Resende)
    print("Consolidating FAT records...")
    for item in raw.get('fat', []):
        raw_name = item.get('name', '')
        name = clean_person_name(raw_name)

        if not is_valid_person_name(name):
            continue

        norm_key = name.lower()
        if norm_key in seen_names:
            continue

        unit = 'FAT - Campus Resende'
        fallback_email = DEPT_FALLBACK_EMAILS['FAT']

        raw_emails = item.get('emails', [])
        primary_email = raw_emails[0] if raw_emails else fallback_email

        context = item.get('context', '')
        lab = "Laboratório de Materiais e Processos (FAT)"

        lattes_list = item.get('lattes', [])
        lattes_url = lattes_list[0] if lattes_list else item.get('url', '')

        spec = classify_siemens_specialization(context, unit, lab)

        consolidated.append({
            'nome': name,
            'email': primary_email,
            'unidade_departamento': unit,
            'laboratorio_grupo': lab,
            'especializacao_tecnica': spec,
            'url_fonte': lattes_url or item.get('url', ''),
            'status_validacao': 'Validado via Portal FAT / UERJ',
            'data_acesso': access_date
        })
        seen_names.add(norm_key)

    # 4. Process GESAR
    print("Consolidating GESAR records...")
    for item in raw.get('gesar', []):
        raw_name = item.get('name', '')
        name = clean_person_name(raw_name)

        if not is_valid_person_name(name):
            continue

        norm_key = name.lower()
        if norm_key in seen_names:
            # Update lab if already in FEN
            for c in consolidated:
                if c['nome'].lower() == norm_key:
                    c['laboratorio_grupo'] = "GESAR (Grupo de Simulação em Eng. e Ciências Ambientais)"
                    c['especializacao_tecnica'] = "CFD, Simulação Ambiental & Métodos Numéricos"
            continue

        unit = 'FEN/MECAN - Campus Maracanã'
        fallback_email = DEPT_FALLBACK_EMAILS['GESAR']

        raw_emails = item.get('emails', [])
        primary_email = raw_emails[0] if raw_emails else fallback_email

        context = item.get('context', '')
        lab = "GESAR (Grupo de Simulação em Eng. e Ciências Ambientais)"

        lattes_list = item.get('lattes', [])
        lattes_url = lattes_list[0] if lattes_list else item.get('url', '')

        spec = "CFD, Simulação Ambiental & Métodos Numéricos"

        consolidated.append({
            'nome': name,
            'email': primary_email,
            'unidade_departamento': unit,
            'laboratorio_grupo': lab,
            'especializacao_tecnica': spec,
            'url_fonte': lattes_url or item.get('url', ''),
            'status_validacao': 'Validado via Portal GESAR / UERJ',
            'data_acesso': access_date
        })
        seen_names.add(norm_key)

    # 5. Process IME / PPG-COMPMAT
    print("Consolidating IME records...")
    for item in raw.get('ime', []):
        raw_name = item.get('name', '')
        name = clean_person_name(raw_name)

        if not is_valid_person_name(name):
            continue

        norm_key = name.lower()
        if norm_key in seen_names:
            continue

        unit = 'IME - Campus Maracanã'
        fallback_email = DEPT_FALLBACK_EMAILS['IME']

        raw_emails = item.get('emails', [])
        primary_email = raw_emails[0] if raw_emails else fallback_email

        context = item.get('context', '')
        lab = "PPG-COMPMAT (Ciências Computacionais e Modelagem Matemática)"

        spec = classify_siemens_specialization(context, unit, lab)

        consolidated.append({
            'nome': name,
            'email': primary_email,
            'unidade_departamento': unit,
            'laboratorio_grupo': lab,
            'especializacao_tecnica': spec,
            'url_fonte': item.get('url', ''),
            'status_validacao': 'Validado via Portal IME / UERJ',
            'data_acesso': access_date
        })
        seen_names.add(norm_key)

    # 6. Process InovUerj / DEPINOVA
    print("Consolidating InovUerj records...")
    for item in raw.get('inovuerj', []):
        consolidated.append({
            'nome': item['name'],
            'email': item['emails'][0],
            'unidade_departamento': 'PR2 / InovUerj - Diretoria de Inovação',
            'laboratorio_grupo': 'DEPINOVA / Escritório de Propriedade Intelectual e Transferência de Tecnologia',
            'especializacao_tecnica': 'Gestão de Inovação, Propriedade Intelectual, Parcerias Universidade-Empresa e Incubadoras',
            'url_fonte': item['url'],
            'status_validacao': 'Validado via Portal PR2 UERJ',
            'data_acesso': access_date
        })

    print(f"Total consolidated UERJ records: {len(consolidated)}")

    with open('uerj_consolidated.json', 'w', encoding='utf-8') as f:
        json.dump(consolidated, f, ensure_ascii=False, indent=2)
    print("Consolidated dataset saved to uerj_consolidated.json")

if __name__ == '__main__':
    consolidate()
