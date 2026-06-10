import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Try variations
prefixes = ["ufrj-", "coppe-", "poli-"]
terms = ["ppgi", "ppgcc", "ppge", "ppgm", "ppgq", "ppgf", "ppgmat", "ppgqu", "pgqu", "ppgg", "ppggeo", "ppgbio", "ppgbme", "ppge", "ppgee", "ppgmec", "ppgep", "ppgen", "ppgeq", "ppgbc", "ppgb", "ppgz", "ppga", "ppget", "ppgo", "ppgpe", "ppgmm", "ppgn", "ppgt", "ppgmc", "ppgma", "ppgst", "ppgmfa", "ppggeoq", "eq", "iq", "if", "im", "facc", "fnd", "ie", "eco", "ess", "fe", "ifcs", "ih", "ip", "fnd", "ie", "ippur", "coppead", "irid", "eefd", "eean", "ff", "fm", "fo", "ib", "icb", "iesc", "impg", "injc", "ices", "idt", "ig", "indc", "ipub", "ippmg", "cenabio", "hucff", "hesfa", "nupem", "ibccf", "ibqm", "nutes", "ippn", "me", "nubea", "needier", "ct", "poli", "eq", "ima", "nides", "macae", "ian", "icf", "icm", "ienf", "imq", "ipoli", "caxias"]

found = []
for p in prefixes:
    for s in terms:
        slug = f"{p}{s}"
        url = f"https://w1.solucaoatrio.net.br/{slug}/pub/Professor.do?method=professorPermanentActive&lng=pt"
        try:
            r = requests.get(url, verify=False, timeout=2)
            if r.status_code == 200:
                found.append(slug)
                print(f"Found: {slug}")
        except:
            pass
print("Final List:", found)
