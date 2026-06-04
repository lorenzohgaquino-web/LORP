# UFRJ Institutional Data Gaps & Updates (2025-02-14)

## Structural Gaps
* **Escola Politécnica (POLI):** Many department websites (e.g., Electronic Engineering, Industrial Engineering) do not list individual faculty emails publicly, using contact forms instead.
* **COPPE (Atrio System):** The Atrio graduate management system (used by programs like PEE, PEU, PEM) obfuscates emails or requires login for full details.
* **Instituto de Computação (IC):** Uses tag-injection antispam which prevents simple regex scraping without specialized de-obfuscation.

## Outdated Pages
* **Laboratórios de IA:** Several lab pages under the `liis.ufrj.br` and `lps.ufrj.br` domains have broken SSL certificates or 404 links to "Corpo Docente".
* **NCE:** The faculty list is partially updated; some names link to Lattes pages that are over 2 years old without current institutional emails.

## Technical Blockers
* **SSL Failures:** `if.ufrj.br` and `ccmn.ufrj.br` frequently fail standard certificate validation.
* **Connection Throttling:** `ct.ufrj.br` and `ufrj.br` main portal implemented connection resets for high-frequency automated requests.
