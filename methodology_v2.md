# Methodological Documentation (V2)

## 1. Objective
Systematic mapping of STEM faculty (Engineering, CS, AI, IT) at USP, UFRJ, UFMG, and UFU.

## 2. Extraction & Cleaning
- **Strategy**: Targeted extraction from specific department rosters.
- **Cleaning**: Automated regex passes to strip academic titles (Prof., Dr.) and unit labels (Obstetrícia, etc.) to ensure "True Name" delivery.
- **Validation**: Strict domain check (@usp.br, @ufrj.br, etc.) and subdomain allowance (@dcc.ufmg.br, @cos.ufrj.br).

## 3. Ethical Adherence
- Only explicitly published contact info was collected.
- No email guessing or pattern completion.
- Documented limits where institutional protection (anti-bot) was encountered.
