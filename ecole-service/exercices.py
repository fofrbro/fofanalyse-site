"""
Outils communs des générateurs d'exercices, et les générateurs du CM1.
Ceux du CM2 et de la 6e sont dans exercices_cm2.py et exercices_6e.py ;
catalogue.py les réunit par classe.

Le principe : le code calcule, l'IA explique. Chaque exercice est tiré au
hasard puis résolu ici, en Python : la bonne réponse et l'explication pas à
pas sont donc toujours justes. Le modèle de langage n'intervient qu'ensuite,
pour réexpliquer autrement, en recevant la bonne réponse calculée ici.

Un exercice est un dictionnaire :
  type         "nombre" (une réponse), "multi" (plusieurs cases), "choix" ou "texte" (un mot ou
               un groupe de mots, en français : « reponse » est alors la liste des formes acceptées)
  enonce       le texte de la question
  grand        True pour un calcul court affiché en gros (« 47 × 23 »)
  unite        unité affichée après la case (« cm »), ou None
  champs       pour "multi" : [{"label": "centaines"}, ...]
  options      pour "choix" : ["3/4", "1/2"]
  indice       un coup de pouce, sans donner la réponse
  reponse      la ou les bonnes réponses (jamais envoyées au navigateur)
  reponse_texte  la bonne réponse écrite pour l'enfant
  explication  les étapes, une par ligne
"""

import math
from decimal import Decimal, InvalidOperation

ESPACE = " "  # espace fine insécable entre les milliers : 36 408

RANGS = ["unités", "dizaines", "centaines", "milliers", "dizaines de mille",
         "centaines de mille", "millions", "dizaines de millions", "centaines de millions",
         "milliards"]
RANGS_SINGULIER = ["unité", "dizaine", "centaine", "millier", "dizaine de mille",
                   "centaine de mille", "million", "dizaine de millions", "centaine de millions",
                   "milliard"]
RANGS_DECIMAUX = ["dixièmes", "centièmes", "millièmes"]


# --- Écriture des nombres ------------------------------------------------

def ecrire(n) -> str:
    """36408 → « 36 408 » ; Decimal("2.5") → « 2,5 »."""
    if isinstance(n, Decimal):
        signe = "-" if n < 0 else ""
        texte = format(abs(n), "f")
        entier, _, decimales = texte.partition(".")
        decimales = decimales.rstrip("0")
        entier = ecrire(int(entier))
        return signe + entier + ("," + decimales if decimales else "")
    return f"{n:,}".replace(",", ESPACE)


def ecrire_fixe(d, places: int) -> str:
    """Decimal("2.5"), 2 → « 2,50 » : garde les zéros, pour aligner les virgules."""
    if places == 0:
        return ecrire(int(d))
    texte = format(Decimal(d).quantize(Decimal(1).scaleb(-places)), "f")
    entier, _, decimales = texte.partition(".")
    return f"{ecrire(int(entier))},{decimales}"


def nb_decimales(d) -> int:
    """Nombre de chiffres utiles après la virgule : 2,50 → 1."""
    texte = format(Decimal(d).normalize(), "f")
    return len(texte.partition(".")[2])


def texte_decimal(d) -> str:
    """Decimal → la réponse attendue, sans zéro inutile (« 2.5 », « 10 »)."""
    return format(Decimal(d).normalize(), "f")


def lire(texte):
    """Ce que l'enfant a tapé → Decimal, ou None si ce n'est pas un nombre.
    Accepte les espaces entre les milliers et la virgule (ou le point)."""
    if texte is None:
        return None
    propre = str(texte).strip().replace(" ", "").replace(ESPACE, "").replace(" ", "")
    propre = propre.replace(",", ".")
    if not propre or len(propre) > 15:
        return None
    try:
        valeur = Decimal(propre)
    except InvalidOperation:
        return None
    return valeur if valeur.is_finite() else None


def chiffres(n: int) -> list[int]:
    """Chiffres de n, des unités vers la gauche : 352 → [2, 5, 3]."""
    return [int(c) for c in reversed(str(n))]


def normaliser(texte) -> str:
    """Réponse écrite : minuscules, apostrophe droite, espaces simples, sans point final.
    Les accents comptent : c'est de l'orthographe."""
    t = str(texte or "").replace("’", "'").replace(" ", " ").strip().lower()
    t = " ".join(t.split()).replace(" '", "'").replace("' ", "'")
    return t.rstrip(" .!?")


def exercice(type_, enonce, reponse, explication, indice, *, grand=False, unite=None,
             champs=None, options=None, reponse_texte=None):
    if type_ == "texte":
        reponse = [reponse] if isinstance(reponse, str) else list(reponse)
        reponse_texte = reponse_texte or reponse[0]
        reponse = sorted({normaliser(r) for r in reponse})
    if type_ == "multi":
        reponse = [str(r) for r in reponse]
    elif type_ == "nombre":
        reponse = str(reponse)
    if reponse_texte is None:
        if type_ == "nombre":
            reponse_texte = ecrire(Decimal(reponse) if "." in reponse else int(reponse))
            if unite:
                reponse_texte += f" {unite}"
        elif type_ == "multi":
            reponse_texte = " ; ".join(f"{r} {c['label']}" for r, c in zip(reponse, champs))
        else:
            reponse_texte = reponse
    return {
        "type": type_, "enonce": enonce, "grand": grand, "unite": unite,
        "champs": champs, "options": options, "indice": indice,
        "reponse": reponse, "reponse_texte": reponse_texte,
        "explication": "\n".join(explication) if isinstance(explication, list) else explication,
    }


def verifier(ex: dict, reponse_eleve) -> bool:
    """Compare la réponse de l'enfant à la bonne réponse."""
    if ex["type"] == "choix":
        return str(reponse_eleve).strip() == ex["reponse"]
    if ex["type"] == "texte":
        return normaliser(reponse_eleve) in ex["reponse"]
    if ex["type"] == "multi":
        if not isinstance(reponse_eleve, list) or len(reponse_eleve) != len(ex["reponse"]):
            return False
        return all(lire(r) is not None and lire(r) == Decimal(b)
                   for r, b in zip(reponse_eleve, ex["reponse"]))
    valeur = lire(reponse_eleve)
    return valeur is not None and valeur == Decimal(ex["reponse"])


# --- Étapes des opérations posées ----------------------------------------

def etapes_addition(a: int, b: int) -> list[str]:
    da, db = chiffres(a), chiffres(b)
    n = max(len(da), len(db))
    lignes, retenue = [], 0
    for i in range(n):
        x = da[i] if i < len(da) else 0
        y = db[i] if i < len(db) else 0
        s = x + y + retenue
        calcul = f"{x} + {y}" + (f" + {retenue}" if retenue else "")
        rang = RANGS[i].capitalize()
        if s >= 10 and i < n - 1:
            lignes.append(f"{rang} : {calcul} = {s} → j'écris {s % 10}, je retiens 1.")
        else:
            lignes.append(f"{rang} : {calcul} = {s} → j'écris {s}.")
        retenue = s // 10
    lignes.append(f"Résultat : {ecrire(a + b)}")
    return lignes


def etapes_soustraction(a: int, b: int) -> list[str]:
    """Méthode enseignée en France : quand on emprunte une dizaine en haut,
    on rend la retenue en bas, au rang suivant."""
    da, db = chiffres(a), chiffres(b)
    lignes, retenue = [], 0
    for i, x in enumerate(da):
        rang = RANGS[i].capitalize()
        if i >= len(db) and retenue == 0:
            if i < len(da) - 1 or x:
                lignes.append(f"{rang} : rien à enlever, j'abaisse le {x}.")
            continue
        y = db[i] if i < len(db) else 0
        bas = y + retenue
        bas_texte = f"({y} + 1)" if retenue else f"{y}"
        if x >= bas:
            lignes.append(f"{rang} : {x} − {bas_texte} = {x - bas}.")
            retenue = 0
        else:
            lignes.append(f"{rang} : {x} − {bas_texte}, impossible → {x + 10} − {bas} = "
                          f"{x + 10 - bas}, je retiens 1.")
            retenue = 1
    lignes.append(f"Résultat : {ecrire(a - b)}. Vérification : {ecrire(a - b)} + {ecrire(b)} = {ecrire(a)} ✓")
    return lignes


def etapes_multiplication_1(a: int, k: int) -> list[str]:
    da = chiffres(a)
    lignes, retenue = [], 0
    for i, x in enumerate(da):
        p = x * k
        t = p + retenue
        calcul = f"{x} × {k} = {p}" + (f", + {retenue} = {t}" if retenue else "")
        if i < len(da) - 1:
            lignes.append(f"{calcul} → j'écris {t % 10}" + (f", je retiens {t // 10}." if t >= 10 else "."))
        else:
            lignes.append(f"{calcul} → j'écris {t}.")
        retenue = t // 10
    lignes.append(f"Résultat : {ecrire(a * k)}")
    return lignes


def etapes_multiplication_2(a: int, b: int) -> list[str]:
    u, d = b % 10, b // 10
    return [
        f"Ligne 1 : {a} × {u} = {ecrire(a * u)}",
        f"Ligne 2 : {a} × {d * 10} → j'écris un 0, puis {a} × {d} = {ecrire(a * d)} → {ecrire(a * d * 10)}",
        f"J'additionne : {ecrire(a * u)} + {ecrire(a * d * 10)} = {ecrire(a * b)}",
    ]


PREMIERS = {2: "deux", 3: "trois", 4: "quatre", 5: "cinq"}


def etapes_division(n: int, d: int) -> list[str]:
    s = str(n)
    lignes = []
    courant, i = int(s[0]), 1
    while courant < d and i < len(s):
        courant, i = int(s[:i + 1]), i + 1
    if i > 1:
        lignes.append(f"{s[:i - 1]} est plus petit que {d} : je prends les {PREMIERS.get(i, i)} "
                      f"premiers chiffres, {courant}.")
    while True:
        q = courant // d
        reste = courant - q * d
        ligne = f"En {courant}, combien de fois {d} ? {q} fois ({q} × {d} = {q * d}), il reste {reste}."
        if i >= len(s):
            lignes.append(ligne)
            break
        courant = reste * 10 + int(s[i])
        lignes.append(ligne + f" J'abaisse le {s[i]} : cela fait {courant}.")
        i += 1
    q, r = divmod(n, d)
    if r:
        lignes.append(f"Quotient : {ecrire(q)}, reste : {r}. Vérification : {ecrire(q)} × {d} + {r} = {ecrire(n)} ✓")
    else:
        lignes.append(f"Résultat : {ecrire(q)}. Vérification : {ecrire(q)} × {d} = {ecrire(n)} ✓")
    return lignes


def etapes_division_decimale(dividende, d: int) -> list[str]:
    """Division posée qui continue après la virgule, jusqu'à un reste nul.
    Le quotient doit tomber juste avec peu de décimales (le générateur le choisit ainsi)."""
    dividende = Decimal(dividende)
    entier, _, decimales = texte_decimal(dividende).partition(".")
    n = int(entier)
    if n >= d:
        lignes = etapes_division(n, d)[:-1]
    else:
        lignes = [f"En {n}, combien de fois {d} ? 0 fois : le quotient commence par 0."]
    reste, a_abaisser = n % d, list(decimales)
    if reste or a_abaisser:
        lignes.append("J'écris la virgule au quotient, puis je continue.")
    for _ in range(8):
        if not (reste or a_abaisser):
            break
        if a_abaisser:
            chiffre = a_abaisser.pop(0)
            quoi = f"le {chiffre}"
        else:
            chiffre, quoi = "0", "un 0"
        courant = reste * 10 + int(chiffre)
        q = courant // d
        reste = courant - q * d
        lignes.append(f"J'abaisse {quoi} : {courant}. En {courant}, combien de fois {d} ? "
                      f"{q} fois ({q} × {d} = {q * d}), il reste {reste}.")
    resultat = dividende / d
    lignes.append(f"Résultat : {ecrire(dividende)} ÷ {d} = {ecrire(resultat)}. "
                  f"Vérification : {ecrire(resultat)} × {d} = {ecrire(dividende)} ✓")
    return lignes


# --- 1. Les grands nombres -------------------------------------------------

def nombre_au_hasard(rng, nb_chiffres, zeros=True):
    c = [rng.randint(1, 9)] + [rng.randint(0, 9) for _ in range(nb_chiffres - 1)]
    if zeros and nb_chiffres > 3 and rng.random() < 0.6:
        c[rng.randint(1, nb_chiffres - 1)] = 0
    return int("".join(map(str, c)))


def decomposer(rng, niveau):
    n = nombre_au_hasard(rng, 3 + niveau)
    d = list(reversed(chiffres(n)))
    k = len(d)
    champs = [{"label": RANGS[k - 1 - j]} for j in range(k)]
    lignes = []
    for j, c in enumerate(d):
        rang = k - 1 - j
        if c:
            lignes.append(f"{c} {RANGS[rang] if c > 1 else RANGS_SINGULIER[rang]} = {ecrire(c * 10 ** rang)}")
        else:
            lignes.append(f"0 {RANGS_SINGULIER[rang]}")
    morceaux = [ecrire(c * 10 ** (k - 1 - j)) for j, c in enumerate(d) if c]
    lignes.append(" + ".join(morceaux) + f" = {ecrire(n)}")
    return exercice("multi", f"Décompose {ecrire(n)}", d, lignes,
                    "Écris le nombre dans un tableau de numération, un chiffre par case. "
                    "Quand il y a un 0, écris 0.", champs=champs)


def comparer_nombres(rng, niveau, taille=None):
    k = taille or 3 + niveau
    a = nombre_au_hasard(rng, k, zeros=False)
    da = list(str(a))
    pos = rng.randint(1, k - 1)
    autre = rng.choice([c for c in "0123456789" if c != da[pos]])
    db = da[:pos] + [autre] + [str(rng.randint(0, 9)) for _ in range(k - pos - 1)]
    b = int("".join(db))
    grand, petit = max(a, b), min(a, b)
    rang = RANGS[k - 1 - pos]
    sa, sb = str(grand), str(petit)
    lignes = [
        f"Les deux nombres ont {k} chiffres : je compare de gauche à droite.",
        f"Ils sont pareils jusqu'aux {rang}." if pos else "",
        f"Aux {rang} : {sa[pos]} > {sb[pos]}, donc {ecrire(grand)} > {ecrire(petit)}.",
    ]
    options = [ecrire(a), ecrire(b)]
    return exercice("choix", "Quel est le plus grand nombre ?", ecrire(grand), [l for l in lignes if l],
                    "Compare chiffre par chiffre, en partant de la gauche.", options=options)


def arrondir(rng, niveau):
    rang = {1: rng.choice([1, 2]), 2: rng.choice([2, 3]), 3: rng.choice([3, 4])}[niveau]
    pas = 10 ** rang
    while True:
        n = nombre_au_hasard(rng, 3 + niveau, zeros=False)
        if n % pas and n > pas:
            break
    bas = n // pas * pas
    haut = bas + pas
    chiffre = (n // (pas // 10)) % 10
    resultat = haut if chiffre >= 5 else bas
    nom = RANGS_SINGULIER[rang]
    article = "au" if nom in ("millier",) else "à la"
    sous = RANGS[rang - 1]
    lignes = [
        f"{ecrire(n)} est entre {ecrire(bas)} et {ecrire(haut)}.",
        f"Je regarde le chiffre des {sous} : c'est {chiffre}.",
        ("C'est 5 ou plus : j'arrondis au-dessus." if chiffre >= 5 else "C'est moins que 5 : j'arrondis en dessous."),
        f"{ecrire(n)} ≈ {ecrire(resultat)}",
    ]
    return exercice("nombre", f"Arrondis {ecrire(n)} {article} {nom} la plus proche." if article == "à la"
                    else f"Arrondis {ecrire(n)} {article} {nom} le plus proche.",
                    resultat, lignes, f"Entre quelles {RANGS[rang] if rang < 3 else 'valeurs'} se trouve "
                    f"{ecrire(n)} ? Regarde ensuite le chiffre des {sous}.".replace("valeurs", "nombres ronds"))


def chiffre_ou_nombre_de(rng, niveau, taille=None):
    n = nombre_au_hasard(rng, taille or 3 + niveau, zeros=False)
    k = len(str(n))
    rang = rng.randint(1, k - 1)
    if niveau == 3 and rng.random() < 0.6:
        rang = rng.randint(1, 3)
        total = n // 10 ** rang
        return exercice("nombre", f"Combien y a-t-il de {RANGS[rang]} en tout dans {ecrire(n)} ?", total,
                        [f"Je cache les chiffres à droite des {RANGS[rang]}.",
                         f"Il reste {ecrire(total)} : il y a {ecrire(total)} {RANGS[rang]} en tout dans {ecrire(n)}."],
                        "Attention : « le chiffre des… » et « le nombre de… » ne sont pas la même question.")
    c = (n // 10 ** rang) % 10
    return exercice("nombre", f"Dans {ecrire(n)}, quel est le chiffre des {RANGS[rang]} ?", c,
                    [f"De droite à gauche : unités, dizaines, centaines, milliers…",
                     f"Le chiffre des {RANGS[rang]} de {ecrire(n)} est {c}."],
                    "Pars de la droite : le premier chiffre est celui des unités.")


# --- 2. Addition et soustraction posées ------------------------------------

def addition(rng, niveau):
    tailles = {1: (3, 3), 2: (4, 4), 3: (5, 4)}[niveau]
    a = nombre_au_hasard(rng, tailles[0], zeros=False)
    b = nombre_au_hasard(rng, tailles[1], zeros=False)
    return exercice("nombre", f"{ecrire(a)} + {ecrire(b)}", a + b, etapes_addition(a, b),
                    "Pose l'opération en alignant les unités, et n'oublie pas les retenues.", grand=True)


def soustraction(rng, niveau):
    k = {1: 3, 2: 4, 3: 5}[niveau]
    a = nombre_au_hasard(rng, k, zeros=niveau > 1)
    b = rng.randint(10 ** (k - 2), a - 1)
    return exercice("nombre", f"{ecrire(a)} − {ecrire(b)}", a - b, etapes_soustraction(a, b),
                    "Commence par les unités. Si le chiffre du haut est trop petit, ajoute-lui 10 "
                    "et rends la retenue en bas, au rang suivant.", grand=True)


# --- 3. Tables et calcul mental ------------------------------------------

def produit_table(rng, niveau):
    a = rng.randint(2, 5) if niveau == 1 else rng.randint(6, 9) if niveau == 2 else rng.randint(3, 9)
    b = rng.randint(2, 10)
    if rng.random() < 0.5:
        a, b = b, a
    p = a * b
    if b == 10:
        lignes = [f"Multiplier par 10, c'est écrire un 0 à la fin : {a} → {p}."]
    elif a == 10:
        lignes = [f"10 × {b}, c'est {b} dizaines : {p}."]
    elif b <= 5:
        lignes = [" + ".join([str(a)] * b) + f" = {p}", f"Donc {a} × {b} = {p}."]
    else:
        lignes = [f"{a} × 5 = {a * 5}",
                  f"{a} × {b - 5} = {a * (b - 5)}",
                  f"{a * 5} + {a * (b - 5)} = {p}, donc {a} × {b} = {p}."]
    return exercice("nombre", f"{a} × {b}", p, lignes,
                    f"Récite la table de {a}, ou pars de {a} × 5 que tu connais.", grand=True)


def division_table(rng, niveau):
    d = rng.randint(2, 5) if niveau == 1 else rng.randint(3, 9)
    q = rng.randint(2, 10)
    n = d * q
    return exercice("nombre", f"{n} ÷ {d}", q,
                    [f"Combien de fois {d} dans {n} ?", f"{d} × {q} = {n}, donc {n} ÷ {d} = {q}."],
                    f"Cherche dans la table de {d} le nombre {n}.", grand=True)


def fois_10_100(rng, niveau):
    k = rng.choice([10, 100, 1000] if niveau == 3 else [10, 100])
    a = rng.randint(2, 99) if niveau < 3 else rng.randint(12, 250)
    zeros = {10: "un 0", 100: "deux 0", 1000: "trois 0"}[k]
    return exercice("nombre", f"{ecrire(a)} × {ecrire(k)}", a * k,
                    [f"Multiplier par {ecrire(k)}, c'est écrire {zeros} à la fin : {ecrire(a)} → {ecrire(a * k)}."],
                    "Chaque chiffre avance d'un rang vers la gauche pour chaque 0.", grand=True)


def complement(rng, niveau):
    cible = 100 if niveau < 3 else 1000
    if cible == 100:
        n = rng.randint(11, 89)
        lignes = []
        dizaine = (n + 9) // 10 * 10
        if dizaine != n:
            lignes.append(f"De {n} à {dizaine}, il faut {dizaine - n}.")
        lignes.append(f"De {dizaine} à 100, il faut {100 - dizaine}.")
        if dizaine != n:
            lignes.append(f"{dizaine - n} + {100 - dizaine} = {100 - n}")
    else:
        n = rng.randint(11, 98) * 10
        centaine = (n + 99) // 100 * 100
        lignes = []
        if centaine != n:
            lignes.append(f"De {n} à {centaine}, il faut {centaine - n}.")
        lignes.append(f"De {ecrire(centaine)} à 1{ESPACE}000, il faut {ecrire(1000 - centaine)}.")
        if centaine != n:
            lignes.append(f"{centaine - n} + {ecrire(1000 - centaine)} = {ecrire(1000 - n)}")
    return exercice("nombre", f"Combien faut-il ajouter à {ecrire(n)} pour faire {ecrire(cible)} ?",
                    cible - n, lignes, "Avance par bonds : d'abord jusqu'à la dizaine (ou la centaine) suivante.")


# --- 4. Multiplication posée -------------------------------------------------

def multiplication(rng, niveau):
    if niveau == 3:
        a = rng.randint(21, 98)
        b = rng.randint(12, 49)
        if b % 10 == 0:
            b += 1
        return exercice("nombre", f"{a} × {b}", a * b, etapes_multiplication_2(a, b),
                        f"Fais deux lignes : {a} × {b % 10}, puis {a} × {b // 10 * 10} "
                        "(n'oublie pas le 0). Additionne les deux lignes.", grand=True)
    a = rng.randint(12, 98) if niveau == 1 else nombre_au_hasard(rng, 3)
    k = rng.randint(3, 9)
    return exercice("nombre", f"{ecrire(a)} × {k}", a * k, etapes_multiplication_1(a, k),
                    f"Multiplie chaque chiffre par {k} en commençant par les unités. Ajoute les retenues.",
                    grand=True)


# --- 5. Division ----------------------------------------------------------

def division(rng, niveau):
    if niveau == 1:
        d = rng.randint(2, 5)
        q = rng.randint(11, 99 // d)
        n = q * d
    elif niveau == 2:
        d = rng.randint(3, 9)
        q = rng.randint(100 // d + 1, 999 // d)
        n = q * d
    else:
        d = rng.randint(3, 9)
        while True:
            n = rng.randint(100, 999)
            if n % d:
                break
        q, r = divmod(n, d)
        return exercice("multi", f"Pose la division : {n} ÷ {d}", [q, r], etapes_division(n, d),
                        f"Commence par les centaines. À chaque étape : combien de fois {d} ? "
                        "Puis abaisse le chiffre suivant.",
                        champs=[{"label": "quotient"}, {"label": "reste"}])
    return exercice("nombre", f"{ecrire(n)} ÷ {d}", q, etapes_division(n, d),
                    f"Partage d'abord le premier chiffre (ou les deux premiers) par {d}, puis abaisse le suivant.",
                    grand=True)


# --- 6. Fractions -----------------------------------------------------------

NOMS_PART = {2: "demi", 3: "tiers", 4: "quart", 5: "cinquième", 10: "dixième"}
NOMS_PARTS = {2: "demis", 3: "tiers", 4: "quarts", 5: "cinquièmes", 10: "dixièmes"}
LE_NOM = {2: "La moitié", 3: "Le tiers", 4: "Le quart", 5: "Le cinquième", 10: "Le dixième"}


def fraction_de(rng, niveau):
    b = rng.choice([2, 3, 4, 5, 10])
    unite = rng.randint(2, 10)
    n = b * unite
    if niveau == 1:
        return exercice("nombre", f"{LE_NOM[b]} de {n}", unite,
                        [f"{LE_NOM[b]}, c'est partager en {b} parts égales.",
                         f"{n} ÷ {b} = {unite}, car {b} × {unite} = {n}."],
                        f"Partage {n} en {b} parts égales.")
    b = rng.choice([3, 4, 5, 10])
    n = b * unite
    a = rng.randint(2, b - 1)
    return exercice("nombre", f"Les {a}/{b} de {n}", a * unite,
                    [f"{LE_NOM[b]} de {n} : {n} ÷ {b} = {unite}.",
                     f"Les {a}/{b}, c'est {a} fois plus : {a} × {unite} = {a * unite}."],
                    f"Cherche d'abord {LE_NOM[b].lower()} de {n}, puis prends-en {a}.")


def comparer_fractions(rng, niveau):
    if niveau == 1:
        b = rng.choice([3, 4, 5, 6, 8, 10])
        x, y = rng.sample(range(1, b), 2)
        g, p = max(x, y), min(x, y)
        return exercice("choix", "Quelle fraction est la plus grande ?", f"{g}/{b}",
                        [f"Les deux fractions sont coupées en {b} parts égales.",
                         f"{g} parts, c'est plus que {p} parts, donc {g}/{b} > {p}/{b}."],
                        f"Les parts ont la même taille. Qui en prend le plus ?",
                        options=[f"{x}/{b}", f"{y}/{b}"])
    if niveau == 2:
        x, y = rng.sample([2, 3, 4, 5, 8, 10], 2)
        g, p = min(x, y), max(x, y)
        return exercice("choix", "Quelle fraction est la plus grande ?", f"1/{g}",
                        [f"Plus on partage en beaucoup de parts, plus chaque part est petite.",
                         f"En {g} parts, chaque part est plus grosse qu'en {p} parts.",
                         f"Donc 1/{g} > 1/{p}."],
                        "Une pizza pour 3 personnes ou pour 8 personnes : où la part est-elle la plus grosse ?",
                        options=[f"1/{x}", f"1/{y}"])
    if rng.random() < 0.5:
        b = rng.choice([2, 3, 4, 5, 10])
        k = rng.randint(2, 4)
        return exercice("nombre", f"Combien de {NOMS_PARTS[b]} y a-t-il dans {k} unités ?", b * k,
                        [f"Dans 1 unité, il y a {b} {NOMS_PARTS[b]}.",
                         f"Dans {k} unités : {k} × {b} = {b * k} {NOMS_PARTS[b]}."],
                        f"Commence par : combien de {NOMS_PARTS[b]} dans 1 unité ?")
    b = rng.choice([2, 3, 4, 5, 10])
    a = rng.choice([x for x in range(1, 2 * b + 1)])
    bonne = "plus petite que 1" if a < b else "égale à 1" if a == b else "plus grande que 1"
    return exercice("choix", f"La fraction {a}/{b} est…", bonne,
                    [f"1 unité, c'est {b}/{b} : {b} parts sur {b}.",
                     f"{a}/{b}, c'est {a} parts. {a} " + ("<" if a < b else "=" if a == b else ">") + f" {b}.",
                     f"Donc {a}/{b} est {bonne}."],
                    f"Combien de parts faut-il pour faire une unité entière ?",
                    options=["plus petite que 1", "égale à 1", "plus grande que 1"])


# --- 7. Nombres décimaux ------------------------------------------------------

def ecrire_decimal(rng, niveau):
    if niveau == 1:
        u, d = rng.randint(0, 9), rng.randint(1, 9)
        if u:
            enonce = f"Écris en chiffres : {u} unité{'s' if u > 1 else ''} et {d} dixième{'s' if d > 1 else ''}."
        else:
            enonce = f"Écris en chiffres : {d} dixième{'s' if d > 1 else ''}."
        v = Decimal(u) + Decimal(d) / 10
        lignes = [f"Les dixièmes s'écrivent juste après la virgule.", f"Cela fait {ecrire(v)}."]
    else:
        c = rng.randint(11, 99) if rng.random() < 0.6 else rng.randint(1, 9)
        u = rng.randint(0, 9) if niveau == 3 else 0
        v = Decimal(u) + Decimal(c) / 100
        enonce = (f"Écris en chiffres : {u} unité{'s' if u > 1 else ''} et {c} centième{'s' if c > 1 else ''}."
                  if u else f"Écris en chiffres : {c} centième{'s' if c > 1 else ''}.")
        lignes = ["1 centième = 0,01 : les centièmes occupent le 2e rang après la virgule.",
                  f"{c} centième{'s' if c > 1 else ''} = {ecrire(Decimal(c) / 100)}.",
                  f"Cela fait {ecrire(v)}."]
    return exercice("nombre", enonce, format(v, "f"), lignes,
                    "Après la virgule : d'abord les dixièmes, puis les centièmes.",
                    reponse_texte=ecrire(v))


def comparer_decimaux(rng, niveau):
    e = rng.randint(1, 20)
    if niveau == 1:
        x, y = rng.sample(range(1, 10), 2)
        a, b = Decimal(e) + Decimal(x) / 10, Decimal(e) + Decimal(y) / 10
    else:
        # Le piège classique : 2,5 et 2,45 (le plus long n'est pas le plus grand)
        d1 = rng.randint(2, 9)
        d2 = rng.randint(0, d1 - 1)
        c2 = rng.randint(1, 9)
        a, b = Decimal(e) + Decimal(d1) / 10, Decimal(e) + Decimal(d2 * 10 + c2) / 100
    g, p = max(a, b), min(a, b)
    sg, sp = format(g, "f").split(".")[1], format(p, "f").split(".")[1]
    lignes = [f"Les parties entières sont pareilles : {e}.",
              f"Je compare les dixièmes : {sg[0]} et {sp[0]}." if sg[0] != sp[0]
              else f"Les dixièmes sont pareils, je compare les centièmes.",
              f"Donc {ecrire(g)} > {ecrire(p)}."]
    if niveau > 1:
        lignes.insert(2, "Attention : le nombre qui a le plus de chiffres n'est pas forcément le plus grand.")
    options = [ecrire(a), ecrire(b)]
    rng.shuffle(options)
    return exercice("choix", "Quel est le plus grand nombre ?", ecrire(g), lignes,
                    "Compare d'abord la partie entière, puis les dixièmes, puis les centièmes.",
                    options=options)


def operation_decimaux(rng, niveau):
    places = 1 if niveau == 2 else rng.choice([1, 2])
    echelle = 10 ** places
    x = rng.randint(11, 99 * (10 if places == 2 else 1))
    y = rng.randint(11, 99 * (10 if places == 2 else 1))
    signe = "+" if niveau < 3 or rng.random() < 0.5 else "−"
    if signe == "−" and y > x:
        x, y = y, x
    a, b = Decimal(x) / echelle, Decimal(y) / echelle
    r = a + b if signe == "+" else a - b
    entiers = x + y if signe == "+" else x - y
    lignes = [f"J'aligne les virgules : {ecrire(a)} {signe} {ecrire(b)}.",
              f"Je calcule comme avec des nombres entiers : {x} {signe} {y} = {entiers}.",
              f"Je remets la virgule au même endroit ({places} chiffre{'s' if places > 1 else ''} après) : {ecrire(r)}."]
    return exercice("nombre", f"{ecrire(a)} {signe} {ecrire(b)}", format(r, "f"), lignes,
                    "Pose l'opération en alignant les virgules les unes sous les autres.", grand=True,
                    reponse_texte=ecrire(r))


def niveau_min(niveau_requis, generateur):
    """N'utilise ce générateur qu'à partir d'un certain niveau."""
    generateur.niveau_min = niveau_requis
    return generateur


def avec_prenom(generateur):
    """Le générateur reçoit le prénom de l'élève, pour l'écrire dans ses énoncés."""
    generateur.avec_prenom = True
    return generateur


operation_decimaux = niveau_min(2, operation_decimaux)


# --- 8. Mesures ---------------------------------------------------------------

def conversion(rng, niveau):
    if niveau == 1:
        cas = rng.choice([("m", "cm", 100), ("km", "m", 1000), ("kg", "g", 1000),
                          ("L", "cL", 100), ("h", "min", 60), ("cm", "mm", 10), ("€", "centimes", 100)])
        n = rng.randint(2, 9)
        de, vers, f = cas
        return exercice("nombre", f"{n} {de} =", n * f,
                        [f"1 {de} = {ecrire(f)} {vers}", f"{n} {de} = {n} × {ecrire(f)} = {ecrire(n * f)} {vers}"],
                        f"Combien de {vers} dans 1 {de} ?", unite=vers)
    if niveau == 2:
        cas = rng.choice([("m", "cm", 100), ("kg", "g", 1000), ("h", "min", 60),
                          ("km", "m", 1000), ("€", "c", 100)])
        de, vers, f = cas
        n = rng.randint(1, 5)
        reste = rng.choice({60: [10, 15, 20, 30, 40, 45], 100: [5, 10, 25, 50, 75],
                            1000: [50, 100, 250, 500, 750]}[f])
        total = n * f + reste
        return exercice("nombre", f"{n} {de} {reste} {vers} =", total,
                        [f"1 {de} = {ecrire(f)} {vers}, donc {n} {de} = {ecrire(n * f)} {vers}.",
                         f"{ecrire(n * f)} + {reste} = {ecrire(total)} {vers}"],
                        f"Convertis d'abord les {de} en {vers}, puis ajoute.", unite=vers)
    cas = rng.choice([("cm", "m", 100), ("g", "kg", 1000), ("min", "h", 60), ("m", "km", 1000)])
    de, vers, f = cas
    if rng.random() < 0.5:
        n = rng.randint(2, 9)
        return exercice("nombre", f"{ecrire(n * f)} {de} =", n,
                        [f"{ecrire(f)} {de} = 1 {vers}",
                         f"Combien de fois {ecrire(f)} dans {ecrire(n * f)} ? {n} fois.",
                         f"Donc {ecrire(n * f)} {de} = {n} {vers}."],
                        f"Combien de {de} font 1 {vers} ?", unite=vers)
    n = rng.randint(1, 5)
    reste = rng.choice({60: [10, 15, 20, 30, 45], 100: [5, 25, 40, 50, 75], 1000: [50, 250, 500, 750]}[f])
    total = n * f + reste
    return exercice("multi", f"{ecrire(total)} {de} =", [n, reste],
                    [f"{ecrire(f)} {de} = 1 {vers}.",
                     f"Dans {ecrire(total)}, il y a {n} fois {ecrire(f)} ({ecrire(n * f)}), et il reste {reste}.",
                     f"Donc {ecrire(total)} {de} = {n} {vers} {reste} {de}."],
                    f"Combien de fois {ecrire(f)} {de} dans {ecrire(total)} {de} ? Ce qui reste, ce sont les {de}.",
                    champs=[{"label": vers}, {"label": de}])


# --- 9. Périmètres --------------------------------------------------------------

def perimetre(rng, niveau):
    u = rng.choice(["cm", "m"])
    forme = rng.choice(["rectangle", "carré", "triangle"]) if niveau < 3 else rng.choice(
        ["rectangle", "carré", "largeur", "côté"])
    if forme == "rectangle":
        L, l = rng.randint(4, 15 * niveau), rng.randint(2, 9)
        if l >= L:
            L, l = l + 3, L
        return exercice("nombre", f"Un rectangle mesure {L} {u} de long et {l} {u} de large. "
                        "Quel est son périmètre ?", 2 * (L + l),
                        ["Le périmètre, c'est la longueur du tour : 2 longueurs et 2 largeurs.",
                         f"{L} + {l} + {L} + {l} = {2 * (L + l)} {u}",
                         f"Ou plus vite : ({L} + {l}) × 2 = {2 * (L + l)} {u}"],
                        "Fais le tour du rectangle avec ton doigt : combien de côtés ?", unite=u)
    if forme == "carré":
        c = rng.randint(3, 12 * niveau)
        return exercice("nombre", f"Un carré a des côtés de {c} {u}. Quel est son périmètre ?", 4 * c,
                        ["Un carré a 4 côtés de même longueur.", f"{c} × 4 = {4 * c} {u}"],
                        "Combien de côtés a un carré ? Sont-ils pareils ?", unite=u)
    if forme == "triangle":
        a, b, c = rng.randint(3, 12), rng.randint(3, 12), rng.randint(3, 12)
        while not (a + b > c and a + c > b and b + c > a):
            a, b, c = rng.randint(3, 12), rng.randint(3, 12), rng.randint(3, 12)
        return exercice("nombre", f"Un triangle a des côtés de {a} {u}, {b} {u} et {c} {u}. "
                        "Quel est son périmètre ?", a + b + c,
                        ["Le périmètre, c'est la somme des côtés.", f"{a} + {b} + {c} = {a + b + c} {u}"],
                        "Additionne la longueur de tous les côtés.", unite=u)
    if forme == "côté":
        c = rng.randint(4, 25)
        return exercice("nombre", f"Un carré a un périmètre de {4 * c} {u}. Combien mesure un côté ?", c,
                        ["Le carré a 4 côtés égaux.", f"{4 * c} ÷ 4 = {c} {u}"],
                        "Le périmètre est partagé en 4 côtés égaux.", unite=u)
    L, l = rng.randint(8, 30), rng.randint(2, 7)
    P = 2 * (L + l)
    return exercice("nombre", f"Un rectangle a un périmètre de {P} {u}. Sa longueur est {L} {u}. "
                    "Quelle est sa largeur ?", l,
                    [f"Une longueur et une largeur font la moitié du tour : {P} ÷ 2 = {L + l} {u}.",
                     f"{L + l} − {L} = {l} {u}"],
                    "Commence par la moitié du périmètre : c'est une longueur plus une largeur.", unite=u)


# --- 10. Problèmes -----------------------------------------------------------------

@avec_prenom
def probleme(rng, niveau, prenom="Mouaz"):
    nom = rng.choice([prenom, prenom, "Léa", "Sami", "Inès", "Hugo"])
    il = "elle" if nom in ("Léa", "Inès") else "il"
    Il = il.capitalize()
    if niveau == 1:
        cas = rng.randint(1, 4)
        if cas == 1:
            a, b = rng.randint(25, 80), rng.randint(12, 45)
            return exercice("nombre", f"{nom} a {a} billes. À la récré, {il} en gagne {b}. "
                            f"Combien de billes a-t-{il} maintenant ?", a + b,
                            [f"{Il} gagne des billes : on ajoute.", f"{a} + {b} = {a + b} billes"],
                            "Gagner, c'est en avoir plus : addition ou soustraction ?", unite="billes")
        if cas == 2:
            a = rng.randint(80, 250)
            b = rng.randint(20, a - 10)
            return exercice("nombre", f"Un livre a {a} pages. {nom} en a déjà lu {b}. "
                            "Combien de pages reste-t-il à lire ?", a - b,
                            ["On enlève les pages déjà lues.", f"{a} − {b} = {a - b} pages"],
                            "Ce qui reste, c'est le total moins ce qui est fait.", unite="pages")
        if cas == 3:
            a, b = rng.randint(6, 25), rng.randint(3, 9)
            return exercice("nombre", f"Une boîte contient {a} crayons. Combien de crayons y a-t-il "
                            f"dans {b} boîtes ?", a * b,
                            [f"{b} boîtes de {a} crayons : {a} × {b}.", f"{a} × {b} = {a * b} crayons"],
                            f"Ajouter {b} fois la même quantité, c'est une multiplication.", unite="crayons")
        k = rng.randint(2, 6)
        q = rng.randint(4, 15)
        return exercice("nombre", f"On partage {k * q} bonbons entre {k} enfants, de façon égale. "
                        "Combien de bonbons reçoit chaque enfant ?", q,
                        [f"Partager en {k}, c'est diviser par {k}.",
                         f"{k * q} ÷ {k} = {q}, car {k} × {q} = {k * q}."],
                        "Partager en parts égales : quelle opération ?", unite="bonbons")
    if niveau == 2:
        cas = rng.randint(1, 3)
        if cas == 1:
            a, b, c = rng.randint(30, 60), rng.randint(8, 25), rng.randint(3, 15)
            return exercice("nombre", f"Un bus transporte {a} passagers. À un arrêt, {b} personnes descendent "
                            f"et {c} montent. Combien de passagers y a-t-il maintenant ?", a - b + c,
                            [f"Ceux qui descendent : {a} − {b} = {a - b}.",
                             f"Ceux qui montent : {a - b} + {c} = {a - b + c} passagers."],
                            "Fais-le en deux étapes : d'abord ceux qui descendent.", unite="passagers")
        if cas == 2:
            k, p, s = rng.randint(3, 6), rng.randint(2, 5), rng.randint(2, 9)
            return exercice("nombre", f"Maman achète {k} cahiers à {p} € chacun et un stylo à {s} €. "
                            "Combien paie-t-elle en tout ?", k * p + s,
                            [f"Les cahiers : {k} × {p} = {k * p} €.", f"Avec le stylo : {k * p} + {s} = {k * p + s} €."],
                            "Calcule d'abord le prix de tous les cahiers.", unite="€")
        k, p = rng.randint(3, 6), rng.randint(2, 4)
        billet = 20 if k * p < 20 else 50
        return exercice("nombre", f"Un paquet de gâteaux coûte {p} €. Papa en achète {k} et paie avec un billet "
                        f"de {billet} €. Combien la caissière lui rend-elle ?", billet - k * p,
                        [f"Prix des gâteaux : {k} × {p} = {k * p} €.",
                         f"La monnaie : {billet} − {k * p} = {billet - k * p} €."],
                        "Combien coûtent tous les paquets ? Ensuite, que reste-t-il du billet ?", unite="€")
    cas = rng.randint(1, 3)
    if cas == 1:
        k = rng.choice([4, 6, 8])
        n = rng.randint(3, 9) * k + rng.randint(1, k - 1)
        q, r = divmod(n, k)
        return exercice("nombre", f"{n} élèves partent en sortie. Chaque minibus a {k} places. "
                        "Combien de minibus faut-il au minimum ?", q + 1,
                        [f"{n} ÷ {k} : {q} minibus pleins ({q} × {k} = {q * k}), il reste {r} élève{'s' if r > 1 else ''}.",
                         f"Ces {r} élève{'s' if r > 1 else ''} ont aussi besoin d'un minibus : {q} + 1 = {q + 1}."],
                        "Fais la division, puis réfléchis : que fait-on des élèves qui restent ?", unite="minibus")
    if cas == 2:
        h, m = rng.randint(8, 16), rng.choice([10, 15, 20, 30, 40, 45, 50])
        dh, dm = rng.randint(1, 2), rng.choice([15, 20, 30, 40, 45])
        total = h * 60 + m + dh * 60 + dm
        fh, fm = divmod(total, 60)
        etape = h + dh
        lignes = [f"{h} h {m} + {dh} h = {etape} h {m}"]
        if m + dm >= 60:
            lignes.append(f"{etape} h {m} + {60 - m} min = {etape + 1} h")
            if dm - (60 - m):
                lignes.append(f"Il reste {dm - (60 - m)} min à ajouter : {fh} h {fm:02d}.")
        else:
            lignes += [f"{etape} h {m} + {dm} min = {fh} h {fm:02d}"]
        lignes.append(f"Le film finit à {fh} h {fm:02d}.")
        return exercice("multi", f"Un film commence à {h} h {m} et dure {dh} h {dm} min. "
                        "À quelle heure finit-il ?", [fh, fm], lignes,
                        "Ajoute d'abord les heures, puis les minutes. Attention : 60 min font 1 h.",
                        champs=[{"label": "h"}, {"label": "min"}], reponse_texte=f"{fh} h {fm:02d}")
    k = rng.randint(2, 4)
    part = rng.randint(5, 20)
    total = part * (k + 1)
    return exercice("nombre", f"{nom} a {k} fois plus de cartes que Tom. Ensemble, ils ont {total} cartes. "
                    "Combien de cartes a Tom ?", part,
                    [f"Tom a 1 part, {nom} a {k} parts : {k + 1} parts en tout.",
                     f"{total} ÷ {k + 1} = {part}, donc 1 part = {part} cartes.",
                     f"Tom a {part} cartes, {nom} en a {k * part}. Vérification : {part} + {k * part} = {total} ✓"],
                    f"Fais un dessin : Tom a 1 part, {nom} a {k} parts. Combien de parts en tout ?", unite="cartes")


# --- Catalogue du CM1 (catalogue.py réunit toutes les classes) ---------------------

GENERATEURS = {
    "nombres": [decomposer, comparer_nombres, arrondir, chiffre_ou_nombre_de],
    "addsous": [addition, soustraction],
    "tables": [produit_table, produit_table, division_table, fois_10_100, complement],
    "multiplication": [multiplication],
    "division": [division],
    "fractions": [fraction_de, comparer_fractions],
    "decimaux": [ecrire_decimal, comparer_decimaux, operation_decimaux],
    "mesures": [conversion],
    "perimetre": [perimetre],
    "problemes": [probleme],
}
