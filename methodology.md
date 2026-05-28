# Methodological Documentation

## 1. Strategy
The data collection followed a systematic search of official institutional directories for UFMG, USP, UFRJ, and UFU. The focus was on "Corpo Docente" (Faculty Body) pages where names and emails are explicitly disclosed for public contact.

## 2. Collection Process
- **Mapping**: Identification of university organizational trees.
- **Access**: Accessing public URLs of faculties and departments.
- **Extraction**: Using Python scripts with regular expressions to extract names and emails matching specific institutional domains (@usp.br, @ufrj.br, etc.).
- **Validation**: Verification of domain suffix and removal of duplicates or incomplete records.

## 3. Data Integrity and Ethics
- **No Inference**: Emails were not guessed or generated; only explicitly published data was captured.
- **Privacy**: Respect for `robots.txt` and anti-scraping measures. Where data was protected (e.g., UFMG FACE), the limitation was documented rather than bypassed.
- **LGPD**: Ensuring all data is of public interest and collected from official transparency portals or department catalogs.

## 4. Technical Constraints
- Some departments use contact forms instead of disclosing emails.
- Frequent network issues or access restrictions on specific university domains (e.g., UFU, UFRJ subdomains) limited the depth of extraction in this iteration.
- All-caps names and varied listing formats required multiple regex passes for normalization.
