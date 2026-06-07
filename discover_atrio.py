import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Common PPG (Post-Graduate Program) acronyms in Brazil
units = [
    "pesc", "pee", "pem", "pep", "pen", "pec", "peq", "peb", "peno", "ppe", "pemm", "pent", "pet",
    "ppgi", "ppgcc", "ppge", "ppgm", "ppgq", "ppgf", "ppgmat", "ppgqu", "pgqu", "ppgg", "ppggeo",
    "ppgbio", "ppgbme", "ppge", "ppgee", "ppgmec", "ppgep", "ppgen", "ppgeq", "ppgbc", "ppgb",
    "ppgz", "ppga", "ppget", "ppgo", "ppgpe", "ppgmm", "ppgn", "ppgt", "ppgmc", "ppgma", "ppgst",
    "ppgmfa", "ppggeoq", "eq", "iq", "if", "im", "facc", "fnd", "ie", "eco", "ess", "fe", "ifcs",
    "ih", "ip", "fnd", "ie", "ippur", "coppead", "irid", "eefd", "eean", "ff", "fm", "fo", "ib",
    "icb", "iesc", "impg", "injc", "ices", "idt", "ig", "indc", "ipub", "ippmg", "cenabio",
    "hucff", "hesfa", "nupem", "ibccf", "ibqm", "nutes", "ippn", "me", "nubea", "needier", "ct",
    "poli", "eq", "ima", "nides", "macae", "ian", "icf", "icm", "ienf", "imq", "ipoli", "caxias",
    "ppgb", "ppg-biofisica", "ppg-quimica", "ppg-fisica", "ppg-matematica", "ppg-informatica",
    "ppg-civil", "ppg-eletrica", "ppg-mecanica", "ppg-producao", "ppg-naval", "ppg-oceanica",
    "ppg-nuclear", "ppg-materiais", "ppg-metalurgia", "ppg-aeroespacial", "ppg-sistemas",
    "ppg-computacao", "ppg-dados", "ppg-inteligencia", "ppg-robotica"
]

found = []
for s in sorted(list(set(units))):
    slugs = [f"ufrj-{s}", f"ppg-{s}", f"ppg{s}"]
    for slug in slugs:
        url = f"https://w1.solucaoatrio.net.br/{slug}/pub/Professor.do?method=professorPermanentActive&lng=pt"
        try:
            r = requests.get(url, verify=False, timeout=1.5)
            if r.status_code == 200 and "Atrio" in r.text:
                found.append(slug)
                print(f"Found: {slug}")
                break
        except:
            pass
print("Final List:", found)
