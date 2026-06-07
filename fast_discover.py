import requests
import urllib3
import concurrent.futures

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

base_url = "https://w1.solucaoatrio.net.br/"
units = [
    "pesc", "pee", "pem", "pep", "pen", "pec", "peq", "peb", "peno", "ppe", "pemm", "pent", "pet",
    "ppgi", "ppgcc", "ppgm", "ppgmat", "ppgf", "ppgq", "ppgqu", "pgqu", "ppgg", "ppggeo", "ppgbio",
    "ppgbme", "ppge", "ppgee", "ppgmec", "ppgep", "ppgen", "ppgeq", "ppgbc", "ppgb", "ppgz", "ppga",
    "ppget", "ppgo", "ppgpe", "ppgmm", "ppgn", "ppgt", "ppgmc", "ppgma", "ppgst", "ppgmfa", "ppggeoq",
    "facc", "fnd", "ie", "ippur", "coppead", "irid", "eefd", "eean", "impg", "ices", "idt", "ig",
    "indc", "ipub", "ippmg", "cenabio", "hucff", "hesfa", "nupem", "ibccf", "ibqm", "nutes", "ippn",
    "me", "nubea", "needier", "ima", "nides", "ian", "icf", "icm", "ienf", "imq", "ipoli"
]

def check_slug(s):
    found = []
    for prefix in ["ufrj-", "ppg", "ppg-", "pg-", "pg"]:
        slug = f"{prefix}{s}"
        url = f"{base_url}{slug}/pub/Professor.do?method=professorPermanentActive&lng=pt"
        try:
            r = requests.get(url, verify=False, timeout=2)
            if r.status_code == 200 and "Atrio" in r.text:
                return slug
        except:
            pass
    return None

with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
    results = list(executor.map(check_slug, units))

found_slugs = [r for r in results if r]
print("Found Slugs:", found_slugs)
