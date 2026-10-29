"""
Moteur de conjugaison : il calcule les formes justes, comme exercices.py
calcule les résultats en maths. Les exercices de conjugaison et d'accord
s'appuient dessus ; le modèle de langage n'invente jamais une forme.

Verbes couverts :
- 1er groupe réguliers (y compris -cer et -ger) ;
- 2e groupe (finir) ;
- 15 verbes irréguliers fréquents, écrits en toutes lettres ci-dessous.
Les verbes à changement de radical (acheter, appeler, préférer, payer…)
sont volontairement absents : on ne les propose pas plutôt que de risquer
une forme fausse.
"""

PERSONNES = ["je", "tu", "il", "nous", "vous", "ils"]
VOYELLES = "aeiouyéèêëàâäîïôöûüh"

PREMIER_GROUPE = ["chanter", "jouer", "parler", "danser", "marcher", "regarder", "aimer", "écouter",
                  "arriver", "habiter", "travailler", "dessiner", "tomber", "rester", "entrer", "monter",
                  "manger", "nager", "ranger", "partager", "commencer", "lancer", "avancer", "placer",
                  "donner", "trouver", "laver", "porter"]
DEUXIEME_GROUPE = ["finir", "choisir", "grandir", "réussir", "remplir", "obéir", "réfléchir", "applaudir",
                   "rougir", "bâtir"]
AUXILIAIRE_ETRE = {"aller", "venir", "partir", "arriver", "tomber", "rester", "entrer", "monter"}

# présent (6 formes), radical du futur, radical de l'imparfait, passé simple (6), participe passé,
# impératif (tu, nous, vous) ou None quand il ne s'emploie pas à l'école.
IRREGULIERS = {
    "être": (["suis", "es", "est", "sommes", "êtes", "sont"], "ser", "ét",
             ["fus", "fus", "fut", "fûmes", "fûtes", "furent"], "été", ["sois", "soyons", "soyez"]),
    "avoir": (["ai", "as", "a", "avons", "avez", "ont"], "aur", "av",
              ["eus", "eus", "eut", "eûmes", "eûtes", "eurent"], "eu", ["aie", "ayons", "ayez"]),
    "aller": (["vais", "vas", "va", "allons", "allez", "vont"], "ir", "all",
              ["allai", "allas", "alla", "allâmes", "allâtes", "allèrent"], "allé", ["va", "allons", "allez"]),
    "faire": (["fais", "fais", "fait", "faisons", "faites", "font"], "fer", "fais",
              ["fis", "fis", "fit", "fîmes", "fîtes", "firent"], "fait", ["fais", "faisons", "faites"]),
    "dire": (["dis", "dis", "dit", "disons", "dites", "disent"], "dir", "dis",
             ["dis", "dis", "dit", "dîmes", "dîtes", "dirent"], "dit", ["dis", "disons", "dites"]),
    "venir": (["viens", "viens", "vient", "venons", "venez", "viennent"], "viendr", "ven",
              ["vins", "vins", "vint", "vînmes", "vîntes", "vinrent"], "venu", ["viens", "venons", "venez"]),
    "pouvoir": (["peux", "peux", "peut", "pouvons", "pouvez", "peuvent"], "pourr", "pouv",
                ["pus", "pus", "put", "pûmes", "pûtes", "purent"], "pu", None),
    "vouloir": (["veux", "veux", "veut", "voulons", "voulez", "veulent"], "voudr", "voul",
                ["voulus", "voulus", "voulut", "voulûmes", "voulûtes", "voulurent"], "voulu", None),
    "voir": (["vois", "vois", "voit", "voyons", "voyez", "voient"], "verr", "voy",
             ["vis", "vis", "vit", "vîmes", "vîtes", "virent"], "vu", ["vois", "voyons", "voyez"]),
    "prendre": (["prends", "prends", "prend", "prenons", "prenez", "prennent"], "prendr", "pren",
                ["pris", "pris", "prit", "prîmes", "prîtes", "prirent"], "pris", ["prends", "prenons", "prenez"]),
    "partir": (["pars", "pars", "part", "partons", "partez", "partent"], "partir", "part",
               ["partis", "partis", "partit", "partîmes", "partîtes", "partirent"], "parti",
               ["pars", "partons", "partez"]),
    "savoir": (["sais", "sais", "sait", "savons", "savez", "savent"], "saur", "sav",
               ["sus", "sus", "sut", "sûmes", "sûtes", "surent"], "su", ["sache", "sachons", "sachez"]),
    "mettre": (["mets", "mets", "met", "mettons", "mettez", "mettent"], "mettr", "mett",
               ["mis", "mis", "mit", "mîmes", "mîtes", "mirent"], "mis", ["mets", "mettons", "mettez"]),
    "devoir": (["dois", "dois", "doit", "devons", "devez", "doivent"], "devr", "dev",
               ["dus", "dus", "dut", "dûmes", "dûtes", "durent"], "dû", None),
    "lire": (["lis", "lis", "lit", "lisons", "lisez", "lisent"], "lir", "lis",
             ["lus", "lus", "lut", "lûmes", "lûtes", "lurent"], "lu", ["lis", "lisons", "lisez"]),
}

FUTUR = ["ai", "as", "a", "ons", "ez", "ont"]
IMPARFAIT = ["ais", "ais", "ait", "ions", "iez", "aient"]

TEMPS = {
    "present": "présent", "futur": "futur", "imparfait": "imparfait", "passe_simple": "passé simple",
    "conditionnel": "conditionnel présent", "passe_compose": "passé composé",
    "plus_que_parfait": "plus-que-parfait", "imperatif": "impératif présent",
}


def groupe(verbe: str) -> int:
    if verbe in IRREGULIERS:
        return 3
    return 2 if verbe in DEUXIEME_GROUPE else 1


def auxiliaire(verbe: str) -> str:
    return "être" if verbe in AUXILIAIRE_ETRE else "avoir"


def coller(radical: str, terminaison: str) -> str:
    """Verbes en -cer et -ger : ç et ge devant a et o (commençons, mangeais)."""
    if terminaison and terminaison[0] in "aâo":
        if radical.endswith("c"):
            return radical[:-1] + "ç" + terminaison
        if radical.endswith("g"):
            return radical + "e" + terminaison
    return radical + terminaison


def participe(verbe: str) -> str:
    if verbe in IRREGULIERS:
        return IRREGULIERS[verbe][4]
    return verbe[:-2] + ("i" if groupe(verbe) == 2 else "é")


def simple(verbe: str, temps: str) -> list[str]:
    """Les 6 formes d'un temps simple (sans le pronom)."""
    g = groupe(verbe)
    if g == 3:
        present, rad_futur, rad_imparfait, passe_simple, _, _ = IRREGULIERS[verbe]
    rad = verbe[:-2]
    if temps == "present":
        if g == 3:
            return list(present)
        if g == 2:
            return [rad + t for t in ["is", "is", "it", "issons", "issez", "issent"]]
        return [coller(rad, t) for t in ["e", "es", "e", "ons", "ez", "ent"]]
    if temps in ("futur", "conditionnel"):
        base = rad_futur if g == 3 else verbe
        return [base + t for t in (FUTUR if temps == "futur" else IMPARFAIT)]
    if temps == "imparfait":
        base = rad_imparfait if g == 3 else rad + "iss" if g == 2 else rad
        return [coller(base, t) for t in IMPARFAIT]
    if temps == "passe_simple":
        if g == 3:
            return list(passe_simple)
        if g == 2:
            return [rad + t for t in ["is", "is", "it", "îmes", "îtes", "irent"]]
        return [coller(rad, t) for t in ["ai", "as", "a", "âmes", "âtes", "èrent"]]
    raise ValueError(temps)


def imperatif(verbe: str) -> list[str] | None:
    """Formes pour tu, nous, vous."""
    if verbe in IRREGULIERS:
        return IRREGULIERS[verbe][5]
    p = simple(verbe, "present")
    tu = p[0] if groupe(verbe) == 1 else p[1]  # chante (sans s), finis
    return [tu, p[3], p[4]]


def accords_participe(pp: str, personne: int, feminin) -> list[str]:
    """Formes acceptées du participe passé avec être, selon le sujet.
    feminin : True, False, ou None quand le genre n'est pas connu (je, tu, nous, vous)."""
    if personne in (0, 1, 2):
        singulier = {True: [pp + "e"], False: [pp], None: [pp, pp + "e"]}
        return singulier[feminin]
    pluriel = {True: [pp + "es"], False: [pp + "s"], None: [pp + "s", pp + "es"]}
    if personne == 4:  # « vous » peut aussi désigner une seule personne (politesse)
        return {True: [pp + "e", pp + "es"], False: [pp, pp + "s"], None: [pp, pp + "e", pp + "s", pp + "es"]}[feminin]
    return pluriel[feminin]


def compose(verbe: str, temps: str, personne: int, feminin=None) -> list[str]:
    """Formes acceptées d'un temps composé (« suis allé », « suis allée »…).
    feminin : True / False pour il-elle et ils-elles ; None quand le genre n'est pas connu."""
    aux = auxiliaire(verbe)
    forme_aux = simple(aux, "present" if temps == "passe_compose" else "imparfait")[personne]
    pp = participe(verbe)
    if aux == "avoir":
        return [f"{forme_aux} {pp}"]
    return [f"{forme_aux} {p}" for p in accords_participe(pp, personne, feminin)]


def table(verbe: str, temps: str) -> list[str]:
    """Le tableau du temps, pour la correction (au masculin)."""
    sujets = ["je", "tu", "il / elle", "nous", "vous", "ils / elles"]
    if temps == "imperatif":
        return imperatif(verbe)
    if temps in ("passe_compose", "plus_que_parfait"):
        formes = [compose(verbe, temps, i, False)[0] for i in range(6)]
        if auxiliaire(verbe) == "être":
            sujets = ["je", "tu", "il", "nous", "vous", "ils"]
            lignes = [f"{pronom(s, f)} {f}".replace("' ", "'") for s, f in zip(sujets, formes)]
            return lignes + [f"elle {compose(verbe, temps, 2, True)[0]}", f"elles {compose(verbe, temps, 5, True)[0]}"]
    else:
        formes = simple(verbe, temps)
    return [f"{pronom(s, f)} {f}".replace("' ", "'") for s, f in zip(sujets, formes)]


def pronom(sujet: str, forme: str) -> str:
    return "j'" if sujet == "je" and forme[0] in VOYELLES else sujet


def regle(verbe: str, temps: str) -> str:
    g = groupe(verbe)
    regles = {
        ("present", 1): "Verbes en -er (1er groupe) : -e, -es, -e, -ons, -ez, -ent.",
        ("present", 2): "2e groupe (comme finir) : -is, -is, -it, -issons, -issez, -issent.",
        ("passe_simple", 1): "1er groupe : -ai, -as, -a, -âmes, -âtes, -èrent.",
        ("passe_simple", 2): "2e groupe : -is, -is, -it, -îmes, -îtes, -irent.",
    }
    if (temps, g) in regles:
        texte = regles[(temps, g)]
    elif temps in ("present", "passe_simple"):
        texte = f"« {verbe} » est irrégulier : sa conjugaison s'apprend par cœur."
    elif temps == "futur":
        base = IRREGULIERS[verbe][1] if g == 3 else verbe
        texte = f"Futur : {base}- + -ai, -as, -a, -ons, -ez, -ont."
    elif temps == "conditionnel":
        base = IRREGULIERS[verbe][1] if g == 3 else verbe
        texte = f"Conditionnel : {base}- (comme au futur) + -ais, -ais, -ait, -ions, -iez, -aient."
    elif temps == "imparfait":
        texte = "Imparfait : radical (celui de « nous » au présent) + -ais, -ais, -ait, -ions, -iez, -aient."
    elif temps == "imperatif":
        texte = "Impératif : pas de sujet, 3 personnes (tu, nous, vous)." + \
            (" 1er groupe : pas de -s avec « tu » (chante !)." if g == 1 else "")
    else:
        moment = "au présent" if temps == "passe_compose" else "à l'imparfait"
        texte = (f"{TEMPS[temps].capitalize()} : auxiliaire « {auxiliaire(verbe)} » {moment} + participe passé "
                 f"« {participe(verbe)} ».")
        if auxiliaire(verbe) == "être":
            texte += " Avec « être », le participe passé s'accorde avec le sujet."
    if g == 1 and verbe.endswith("cer") and temps in ("present", "imparfait", "passe_simple"):
        texte += " Verbe en -cer : le c devient ç devant a et o."
    if g == 1 and verbe.endswith("ger") and temps in ("present", "imparfait", "passe_simple"):
        texte += " Verbe en -ger : on garde un e devant a et o."
    return texte
