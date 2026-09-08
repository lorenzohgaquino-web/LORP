import requests
from bs4 import BeautifulSoup
import urllib3, re, json

urllib3.disable_warnings()

s = requests.Session()
s.verify = False
s.headers.update({'User-Agent': 'Mozilla/5.0'})

# 1. Fetch FEN profs list
r = s.get('https://www.eng.uerj.br/prof/')
soup = BeautifulSoup(r.text, 'html.parser')

fen_profs = []
for a in soup.find_all('a', href=True):
    href = a['href']
    if '/prof/' in href and href.rstrip('/').split('/')[-1].isdigit():
        pid = href.rstrip('/').split('/')[-1]
        name = a.get_text(strip=True)
        if name and name not in [p['name'] for p in fen_profs]:
            fen_profs.append({'id': pid, 'name': name, 'url': f'https://www.eng.uerj.br/prof/{pid}'})

print(f'Found {len(fen_profs)} FEN professors')

# 2. Fetch PPGMC profs
r_ppgmc = s.get('https://www.ppgmc.uerj.br/docentes')
soup_ppgmc = BeautifulSoup(r_ppgmc.text, 'html.parser')
ppgmc_profs = []
# Parse divs or mailto links
for mailto in soup_ppgmc.find_all('a', href=re.compile('mailto:')):
    email = mailto['href'].replace('mailto:', '').strip()
    # Name is usually in preceding text or parent box
    parent = mailto.find_parent()
    name_el = parent.find_previous_sibling() or parent.parent
    text_block = parent.parent.get_text(separator='|', strip=True)
    ppgmc_profs.append({'email': email, 'block': text_block})

print(f'Found {len(ppgmc_profs)} PPGMC prof mailtos')
