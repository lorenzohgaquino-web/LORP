import re
import ftfy

def sanitize_string(text):
    if not text:
        return ""
    text = ftfy.fix_text(text)
    text = text.replace('\ufffd', '')
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def clean_record(record):
    raw_name = record.get('name', '')
    name = sanitize_string(raw_name)

    # Strip prefix boilerplate
    name = re.sub(r'^(CORPO DOCENTE:?\s*|CHEFE\s*|SUBCHEFE\s*)', '', name, flags=re.IGNORECASE)
    name = re.sub(r'^(Prof\.?|Profa\.?|Dr\.?|Dra\.?|Ph\.?D\.?|Eng\.?)\s+', '', name, flags=re.IGNORECASE)

    # Cut off Depto or biography sentences
    name = re.split(r'\b(Depto\.?|Departamento|Possui|Gradua|Doutor|Doutora|Mestre|Profess|Engenhar|Obteve|Mais informações)\b', name, flags=re.IGNORECASE)[0]
    name = name.split('(')[0].split(' - ')[0].split(',')[0].strip()

    email = record.get('email', '').strip().lower()
    # Fix email artifacts like ldmm@eng.uerj.brcv -> ldmm@eng.uerj.br
    if email.endswith('brcv'):
        email = email[:-2]
    elif email.endswith('brlattes'):
        email = email[:-6]
    elif email.endswith('brsite'):
        email = email[:-4]

    department = sanitize_string(record.get('department', ''))
    laboratory = sanitize_string(record.get('laboratory', ''))
    specialization = sanitize_string(record.get('specialization', ''))

    source_url = record.get('source_url', '').strip()
    if 'lattes.cnpq.br' in source_url:
        lattes_id_match = re.search(r'\d{10,16}', source_url)
        if lattes_id_match:
            source_url = f"http://lattes.cnpq.br/{lattes_id_match.group(0)}"

    validation_date = record.get('validation_date', '2026-03-09')

    return {
        "name": name,
        "email": email,
        "department": department,
        "laboratory": laboratory,
        "specialization": specialization,
        "source_url": source_url,
        "validation_date": validation_date
    }
