"""
Générateurs d'exercices de mathématiques, programme de CM2.

Même principe qu'au CM1 (voir exercices.py) : chaque exercice est tiré au
hasard et résolu ici, en Python ; la correction pas à pas est donc juste.
Les nombres décimaux sont calculés avec Decimal, sans erreur d'arrondi.
"""

from decimal import ROUND_HALF_UP, Decimal

from exercices import (RANGS, RANGS_DECIMAUX, RANGS_SINGULIER, avec_prenom, chiffre_ou_nombre_de,
                       comparer_nombres, ecrire, ecrire_fixe, etapes_division, etapes_division_decimale,
                       etapes_multiplication_2, exercice, nb_decimales, niveau_min, nombre_au_hasard,
                       texte_decimal)


def decimal_au_hasard(rng, places: int, maxi_entier: int = 99) -> Decimal:
    """Un décimal qui a exactement `places` chiffres après la virgule (le dernier n'est pas 0)."""
    entier = rng.randint(0, maxi_entier)
    if places == 0:
        return Decimal(max(entier, 1))
    decimales = [rng.randint(0, 9) for _ in range(places - 1)] + [rng.randint(1, 9)]
    return Decimal(f"{entier}.{''.join(map(str, decimales))}")


# --- 1. Les nombres jusqu'au milliard -----------------------------------------

def decomposer_classes(rng, niveau):
    n = nombre_au_hasard(rng, 6 + niveau)
    m, mi, u = n // 10 ** 6, n // 1000 % 1000, n % 1000
    return exercice("multi", f"Décompose {ecrire(n)} en millions, mille et unités.", [m, mi, u],
                    [f"Je sépare le nombre en classes de 3 chiffres, en partant de la droite : "
                     f"{m} | {mi:03d} | {u:03d}.",
                     f"Classe des millions : {m}.", f"Classe des mille : {mi}.", f"Classe des unités : {u}.",
                     f"{ecrire(n)} = {m} million{'s' if m > 1 else ''} + {mi} mille + {u}"],
                    "Sépare le nombre en tranches de 3 chiffres, en partant de la droite.",
                    champs=[{"label": "millions"}, {"label": "mille"}, {"label": "unités"}])


def ecrire_en_chiffres(rng, niveau):
    m = rng.randint(1, 9) if niveau == 1 else rng.randint(10, 999)
    mi = rng.choice([0, rng.randint(1, 999)]) if niveau == 3 else rng.randint(1, 999)
    u = rng.choice([0, rng.randint(1, 99)]) if niveau > 1 else rng.randint(100, 999)
    n = m * 10 ** 6 + mi * 1000 + u
    morceaux = [f"{m} million{'s' if m > 1 else ''}"] + ([f"{mi} mille"] if mi else []) + ([str(u)] if u else [])
    lignes = [f"Classe des millions : {m}.",
              f"Classe des mille : {mi:03d}" + (" (il n'y a pas de mille)." if not mi else "."),
              f"Classe des unités : {u:03d}" + (" (il n'y a pas d'unités)." if not u else "."),
              f"Chaque classe a 3 chiffres : je les mets bout à bout. Cela fait {ecrire(n)}."]
    return exercice("nombre", f"Écris en chiffres : {' '.join(morceaux)}.", n, lignes,
                    "Chaque classe (millions, mille, unités) s'écrit avec 3 chiffres. "
                    "Une classe vide s'écrit 000.")


def comparer_grands(rng, niveau):
    return comparer_nombres(rng, niveau, taille=6 + niveau)


def chiffre_des_grands(rng, niveau):
    return chiffre_ou_nombre_de(rng, niveau, taille=6 + niveau)


def arrondir_grand(rng, niveau):
    k = 6 + niveau
    rang = rng.choice({1: [3, 6], 2: [4, 5, 6], 3: [3, 4, 5, 6, 7]}[niveau])
    rang = min(rang, k - 1)
    pas = 10 ** rang
    while True:
        n = nombre_au_hasard(rng, k, zeros=False)
        if n % pas:
            break
    bas = n // pas * pas
    haut = bas + pas
    chiffre = n // (pas // 10) % 10
    resultat = haut if chiffre >= 5 else bas
    nom = RANGS_SINGULIER[rang]
    masculin = nom in ("millier", "million", "milliard")
    return exercice("nombre", f"Arrondis {ecrire(n)} {'au' if masculin else 'à la'} {nom} "
                    f"{'le plus proche' if masculin else 'la plus proche'}.", resultat,
                    [f"{ecrire(n)} est entre {ecrire(bas)} et {ecrire(haut)}.",
                     f"Je regarde le chiffre des {RANGS[rang - 1]} : c'est {chiffre}.",
                     "C'est 5 ou plus : j'arrondis au-dessus." if chiffre >= 5
                     else "C'est moins que 5 : j'arrondis en dessous.",
                     f"{ecrire(n)} ≈ {ecrire(resultat)}"],
                    f"Entre quels nombres ronds se trouve {ecrire(n)} ? Regarde ensuite le chiffre "
                    f"juste à droite.")


# --- 2. Fractions ------------------------------------------------------------------

def fraction_vers_decimal(rng, niveau):
    if niveau == 3 and rng.random() < 0.5:
        b = rng.choice([2, 4, 5, 20, 25, 50])
        a = rng.randint(1, b - 1)
        m = 100 // b
        v = Decimal(a) / b
        return exercice("nombre", f"Écris {a}/{b} sous forme de nombre décimal.", texte_decimal(v),
                        [f"Je cherche une fraction égale avec 100 en bas : {b} × {m} = 100.",
                         f"{a}/{b} = {a * m}/100 (je multiplie aussi le haut par {m}).",
                         f"{a * m}/100 = {a * m} centièmes = {ecrire(v)}"],
                        "Trouve une fraction égale qui a 10 ou 100 au dénominateur.", reponse_texte=ecrire(v))
    b = 10 if niveau == 1 else rng.choice([10, 100]) if niveau == 2 else rng.choice([100, 1000])
    a = rng.randint(1, 10 * b - 1)
    while a % 10 == 0:
        a = rng.randint(1, 10 * b - 1)
    v = Decimal(a) / b
    nom = {10: "dixièmes", 100: "centièmes", 1000: "millièmes"}[b]
    rang = {10: "1er", 100: "2e", 1000: "3e"}[b]
    return exercice("nombre", f"Écris {ecrire(a)}/{ecrire(b)} sous forme de nombre décimal.", texte_decimal(v),
                    [f"{ecrire(a)}/{ecrire(b)}, c'est {ecrire(a)} {nom}.",
                     f"Le dernier chiffre de {ecrire(a)} va au rang des {nom} ({rang} chiffre après la virgule).",
                     f"{ecrire(a)}/{ecrire(b)} = {ecrire(v)}"],
                    f"Le dénominateur {ecrire(b)} dit que ce sont des {nom}.", reponse_texte=ecrire(v))


def encadrer_fraction(rng, niveau):
    b = rng.choice([2, 4, 10]) if niveau == 1 else rng.randint(3, 10)
    a = rng.randint(b + 1, (4 if niveau == 1 else 10) * b)
    while a % b == 0:
        a = rng.randint(b + 1, (4 if niveau == 1 else 10) * b)
    e = a // b
    return exercice("multi", f"{a}/{b} est compris entre deux nombres entiers qui se suivent. Lesquels ?",
                    [e, e + 1],
                    [f"{e} = {e * b}/{b} et {e + 1} = {(e + 1) * b}/{b}.",
                     f"{e * b} < {a} < {(e + 1) * b}, donc {e} < {a}/{b} < {e + 1}."],
                    f"Cherche dans la table de {b} les nombres juste avant et juste après {a}.",
                    champs=[{"label": "juste avant"}, {"label": "juste après"}],
                    reponse_texte=f"{e} < {a}/{b} < {e + 1}")


def parts(n: int) -> str:
    return f"{n} part{'s' if n > 1 else ''}"


def ajouter_fractions(rng, niveau):
    b = rng.randint(3, 9) if niveau == 1 else rng.randint(4, 12)
    if niveau == 3 and rng.random() < 0.5:
        a = rng.randint(2, 2 * b)
        c = rng.randint(1, a - 1)
        return exercice("nombre", f"{a}/{b} − {c}/{b} = …/{b}", a - c,
                        [f"Les parts ont la même taille : on coupe l'unité en {b}.",
                         f"{parts(a)} − {parts(c)} = {parts(a - c)}.",
                         f"Donc {a}/{b} − {c}/{b} = {a - c}/{b}. Le dénominateur ne change pas."],
                        "Le dénominateur ne change pas : on soustrait seulement les numérateurs.", grand=True)
    if niveau == 1:
        a = rng.randint(1, b - 2)
        c = rng.randint(1, b - a)
    else:
        a, c = rng.randint(1, b - 1), rng.randint(1, b + 3)
    return exercice("nombre", f"{a}/{b} + {c}/{b} = …/{b}", a + c,
                    [f"Les parts ont la même taille : on coupe l'unité en {b}.",
                     f"{parts(a)} + {parts(c)} = {parts(a + c)}.",
                     f"Donc {a}/{b} + {c}/{b} = {a + c}/{b}. Le dénominateur ne change pas."],
                    "Le dénominateur ne change pas : on additionne seulement les numérateurs.", grand=True)


def fraction_quantite(rng, niveau):
    b = rng.choice([3, 4, 5, 6, 8, 10])
    part = rng.randint(3, 6 + 4 * niveau)
    n = b * part
    a = rng.randint(2, b - 1) if niveau > 1 else 1
    unite = rng.choice(["€", "élèves", "km", "g"])
    quoi = f"les {a}/{b}" if a > 1 else f"1/{b}"
    return exercice("nombre", f"Calcule {quoi} de {n} {unite}.", a * part,
                    [f"Je partage {n} en {b} parts égales : {n} ÷ {b} = {part}.",
                     f"J'en prends {a} : {a} × {part} = {a * part} {unite}." if a > 1
                     else f"1/{b} de {n} {unite}, c'est donc {part} {unite}."],
                    f"Cherche d'abord 1/{b} de {n}, puis prends-en {a}." if a > 1 else f"Partage {n} en {b}.",
                    unite=unite)


# --- 3. Nombres décimaux --------------------------------------------------------------

def chiffre_decimal(rng, niveau):
    places = 2 if niveau == 1 else 3
    v = decimal_au_hasard(rng, places, 999)
    entier, _, decimales = texte_decimal(v).partition(".")
    rangs = [(f"des {RANGS[i]}", entier[-1 - i]) for i in range(min(len(entier), 3))]
    rangs += [(f"des {RANGS_DECIMAUX[i]}", decimales[i]) for i in range(len(decimales))]
    if niveau > 1:
        rangs = rangs[len(rangs) // 2:]
    nom, chiffre = rng.choice(rangs)
    return exercice("nombre", f"Dans {ecrire(v)}, quel est le chiffre {nom} ?", chiffre,
                    ["Avant la virgule : unités, dizaines, centaines (de droite à gauche).",
                     "Après la virgule : dixièmes, centièmes, millièmes (de gauche à droite).",
                     f"Le chiffre {nom} de {ecrire(v)} est {chiffre}."],
                    "Pars de la virgule : juste avant, les unités ; juste après, les dixièmes.")


def explication_comparaison(a: Decimal, b: Decimal) -> list[str]:
    """Compare deux décimaux de même partie entière, en complétant avec des zéros."""
    g, p = max(a, b), min(a, b)
    places = max(nb_decimales(a), nb_decimales(b))
    sg, sp = ecrire_fixe(g, places), ecrire_fixe(p, places)
    dg, dp = sg.split(",")[1], sp.split(",")[1]
    i = next(j for j in range(places) if dg[j] != dp[j])
    lignes = [f"Les parties entières sont pareilles : {ecrire(int(g))}."]
    if nb_decimales(a) != nb_decimales(b):
        lignes.append(f"J'écris autant de chiffres après la virgule : {sg} et {sp}.")
    if i:
        lignes.append(f"Les chiffres sont pareils jusqu'aux {RANGS_DECIMAUX[i - 1]}.")
    lignes.append(f"Aux {RANGS_DECIMAUX[i]} : {dg[i]} > {dp[i]}, donc {ecrire(g)} > {ecrire(p)}.")
    return lignes


def comparer_decimaux_cm2(rng, niveau):
    e = rng.randint(0, 50)
    while True:
        la, lb = rng.sample([1, 2, 3] if niveau == 3 else [1, 2], 2)
        a = e + decimal_au_hasard(rng, la, 0)
        b = e + decimal_au_hasard(rng, lb, 0)
        if a != b:
            break
    lignes = explication_comparaison(a, b)
    if nb_decimales(max(a, b)) < nb_decimales(min(a, b)):
        lignes.insert(-1, "Attention : le nombre qui a le plus de chiffres n'est pas forcément le plus grand.")
    options = [ecrire(a), ecrire(b)]
    rng.shuffle(options)
    return exercice("choix", "Quel est le plus grand nombre ?", ecrire(max(a, b)), lignes,
                    "Ajoute des zéros à droite pour avoir autant de chiffres après la virgule, puis compare.",
                    options=options)


def arrondir_decimal(rng, niveau):
    au_dixieme = niveau > 1 and rng.random() < 0.6
    places = 2 if not au_dixieme else rng.choice([2, 3]) if niveau == 3 else 2
    v = decimal_au_hasard(rng, places, 99 if niveau == 1 else 999)
    pas = Decimal("0.1") if au_dixieme else Decimal(1)
    bas = (v / pas).to_integral_value(rounding="ROUND_FLOOR") * pas
    haut = bas + pas
    resultat = v.quantize(pas, rounding=ROUND_HALF_UP)
    sous = "centièmes" if au_dixieme else "dixièmes"
    chiffre = texte_decimal(v).partition(".")[2][1 if au_dixieme else 0]
    rond = 1 if au_dixieme else 0
    precision = "au dixième" if au_dixieme else "à l'unité"
    return exercice("nombre", f"Arrondis {ecrire(v)} {precision}.",
                    texte_decimal(resultat),
                    [f"{ecrire(v)} est entre {ecrire_fixe(bas, rond)} et {ecrire_fixe(haut, rond)}.",
                     f"Je regarde le chiffre des {sous} : c'est {chiffre}.",
                     "C'est 5 ou plus : j'arrondis au-dessus." if int(chiffre) >= 5
                     else "C'est moins que 5 : j'arrondis en dessous.",
                     f"{ecrire(v)} ≈ {ecrire_fixe(resultat, rond)}"],
                    f"Regarde le chiffre des {sous}.", reponse_texte=ecrire_fixe(resultat, rond))


def operation_decimaux_cm2(rng, niveau):
    la = rng.randint(1, 2 if niveau < 3 else 3)
    lb = rng.randint(0 if niveau > 1 else 1, 2 if niveau < 3 else 3)
    a, b = decimal_au_hasard(rng, la, 99), decimal_au_hasard(rng, lb, 99)
    signe = "+" if niveau == 1 or rng.random() < 0.5 else "−"
    if signe == "−" and b > a:
        a, b = b, a
    if a == b:
        signe = "+"
    r = a + b if signe == "+" else a - b
    places = max(nb_decimales(a), nb_decimales(b))
    lignes = [f"J'aligne les virgules, et j'écris autant de chiffres après : "
              f"{ecrire_fixe(a, places)} {signe} {ecrire_fixe(b, places)}."]
    x, y = int(a.scaleb(places)), int(b.scaleb(places))
    lignes.append(f"Je calcule comme avec des entiers : {ecrire(x)} {signe} {ecrire(y)} = {ecrire(x + y if signe == '+' else x - y)}.")
    lignes.append(f"Je remets la virgule ({places} chiffre{'s' if places > 1 else ''} après) : {ecrire_fixe(r, places)}"
                  + (f" = {ecrire(r)}." if ecrire_fixe(r, places) != ecrire(r) else "."))
    return exercice("nombre", f"{ecrire(a)} {signe} {ecrire(b)}", texte_decimal(r), lignes,
                    "Pose l'opération en alignant les virgules. Ajoute des zéros s'il manque des chiffres.",
                    grand=True, reponse_texte=ecrire(r))


# --- 4. Multiplier ----------------------------------------------------------------------

def fois_10_decimal(rng, niveau):
    k = rng.choice([10, 100, 1000])
    z = len(str(k)) - 1
    v = decimal_au_hasard(rng, rng.randint(1, 3), 99 if niveau < 3 else 999)
    if niveau == 3 and rng.random() < 0.5:
        r = v.scaleb(-z)
        return exercice("nombre", f"{ecrire(v)} ÷ {ecrire(k)}", texte_decimal(r),
                        [f"Diviser par {ecrire(k)}, c'est rendre chaque chiffre {ecrire(k)} fois plus petit : "
                         f"la virgule se déplace de {z} rang{'s' if z > 1 else ''} vers la gauche.",
                         "S'il manque des chiffres, j'ajoute des 0 devant.",
                         f"{ecrire(v)} ÷ {ecrire(k)} = {ecrire(r)}"],
                        f"Déplace la virgule de {z} rang{'s' if z > 1 else ''} vers la gauche.",
                        grand=True, reponse_texte=ecrire(r))
    r = v.scaleb(z)
    return exercice("nombre", f"{ecrire(v)} × {ecrire(k)}", texte_decimal(r),
                    [f"Multiplier par {ecrire(k)}, c'est rendre chaque chiffre {ecrire(k)} fois plus grand : "
                     f"la virgule se déplace de {z} rang{'s' if z > 1 else ''} vers la droite.",
                     "S'il manque des chiffres, j'ajoute des 0.",
                     f"{ecrire(v)} × {ecrire(k)} = {ecrire(r)}"],
                    f"Déplace la virgule de {z} rang{'s' if z > 1 else ''} vers la droite.",
                    grand=True, reponse_texte=ecrire(r))


def decimal_fois_entier(rng, niveau):
    places = 1 if niveau == 1 else rng.choice([1, 2])
    v = decimal_au_hasard(rng, places, 9 if niveau == 1 else 99)
    k = rng.randint(2, 9) if niveau < 3 else rng.randint(11, 25)
    x = int(v.scaleb(places))
    r = v * k
    return exercice("nombre", f"{ecrire(v)} × {k}", texte_decimal(r),
                    [f"Je calcule sans la virgule : {ecrire(x)} × {k} = {ecrire(x * k)}.",
                     f"{ecrire(v)} a {places} chiffre{'s' if places > 1 else ''} après la virgule : "
                     f"le résultat aussi.",
                     f"{ecrire(v)} × {k} = {ecrire_fixe(r, places)}"
                     + (f" = {ecrire(r)}" if ecrire_fixe(r, places) != ecrire(r) else "")],
                    "Multiplie comme si la virgule n'existait pas, puis remets-la.", grand=True,
                    reponse_texte=ecrire(r))


def multiplication_posee(rng, niveau):
    a = rng.randint(21, 98) if niveau == 1 else rng.randint(102, 987)
    b = rng.randint(12, 98)
    if b % 10 == 0:
        b += 1
    return exercice("nombre", f"{a} × {b}", a * b, etapes_multiplication_2(a, b),
                    f"Fais deux lignes : {a} × {b % 10}, puis {a} × {b // 10 * 10} "
                    "(n'oublie pas le 0). Additionne les deux lignes.", grand=True)


# --- 5. Division ------------------------------------------------------------------------

def division_deux_chiffres(rng, niveau):
    d = rng.randint(11, 19) if niveau == 1 else rng.randint(12, 49)
    n = rng.randint(d * 10, 999) if niveau < 3 else rng.randint(1000, 9999)
    q, r = divmod(n, d)
    return exercice("multi", f"Pose la division : {ecrire(n)} ÷ {d}", [q, r], etapes_division(n, d),
                    f"Pour deviner combien de fois {d}, arrondis {d} à la dizaine : {(d + 5) // 10 * 10}. "
                    "Vérifie que le reste est plus petit que le diviseur.",
                    champs=[{"label": "quotient"}, {"label": "reste"}])


def division_decimale(rng, niveau):
    d = rng.choice([2, 5]) if niveau == 1 else rng.choice([2, 4, 5]) if niveau == 2 else rng.choice([4, 8])
    n = rng.randint(11, 99) if niveau == 1 else rng.randint(101, 999)
    while n % d == 0:
        n += 1
    q = Decimal(n) / d
    return exercice("nombre", f"Calcule {n} ÷ {d} (le quotient est un nombre décimal).", texte_decimal(q),
                    etapes_division_decimale(n, d),
                    "Quand il reste quelque chose après les unités, écris une virgule au quotient "
                    "et abaisse un 0.", reponse_texte=ecrire(q))



# --- 6. Proportionnalité ---------------------------------------------------------------------

OBJETS = [("livre", "livres"), ("ballon", "ballons"), ("place de cinéma", "places de cinéma"),
          ("boîte de feutres", "boîtes de feutres"), ("t-shirt", "t-shirts")]


def proportionnalite(rng, niveau):
    un, plusieurs = rng.choice(OBJETS)
    if niveau == 3 and rng.random() < 0.5:
        par_personne = rng.choice([25, 30, 40, 50, 60, 75])
        a, b = rng.sample([2, 3, 4, 5, 6, 8, 10], 2)
        return exercice("nombre", f"Pour {a} personnes, une recette demande {a * par_personne} g de farine. "
                        f"Combien en faut-il pour {b} personnes ?", b * par_personne,
                        [f"Pour 1 personne : {a * par_personne} ÷ {a} = {par_personne} g.",
                         f"Pour {b} personnes : {b} × {par_personne} = {b * par_personne} g."],
                        "Cherche d'abord la quantité pour 1 personne.", unite="g")
    if niveau == 2:
        p = rng.randint(2, 9)
        a = rng.randint(2, 5)
        k = rng.randint(2, 4)
        b = a * k
        return exercice("nombre", f"{a} {plusieurs} coûtent {a * p} €. Combien coûtent {b} {plusieurs} ?", b * p,
                        [f"{b} {plusieurs}, c'est {k} fois plus que {a} {plusieurs}.",
                         f"Le prix est donc {k} fois plus grand : {k} × {a * p} = {b * p} €."],
                        f"Combien de fois {a} dans {b} ?", unite="€")
    p = Decimal(rng.randint(3, 19)) / 2 if niveau == 3 else Decimal(rng.randint(2, 9))
    a, b = rng.sample(range(2, 10), 2)
    total, resultat = a * p, b * p
    return exercice("nombre", f"{a} {plusieurs} coûtent {ecrire(total)} €. Combien coûtent {b} {plusieurs} ?",
                    texte_decimal(resultat),
                    [f"Prix d'1 {un} : {ecrire(total)} ÷ {a} = {ecrire(p)} €.",
                     f"Prix de {b} {plusieurs} : {b} × {ecrire(p)} = {ecrire(resultat)} €."],
                    f"Cherche d'abord le prix d'1 {un}.", unite="€")


def pourcentage(rng, niveau):
    p = rng.choice([50, 10]) if niveau == 1 else rng.choice([25, 75, 20, 50]) if niveau == 2 else \
        rng.choice([5, 15, 30, 35, 40, 60, 70])
    n = 20 * rng.randint(1, 10 if niveau == 1 else 25)
    res = p * n // 100
    if p == 50:
        lignes = [f"50 %, c'est la moitié : {n} ÷ 2 = {res}."]
    elif p in (25, 75):
        quart = n // 4
        lignes = [f"25 %, c'est le quart : {n} ÷ 4 = {quart}."]
        if p == 75:
            lignes.append(f"75 %, c'est 3 quarts : 3 × {quart} = {res}.")
    else:
        dix = n // 10
        lignes = [f"10 %, c'est le dixième : {n} ÷ 10 = {dix}."]
        if p % 10 == 0 and p != 10:
            lignes.append(f"{p} %, c'est {p // 10} fois 10 % : {p // 10} × {dix} = {res}.")
        elif p % 10:
            cinq = n // 20
            lignes.append(f"5 %, c'est la moitié de 10 % : {dix} ÷ 2 = {cinq}.")
            if p != 5:
                lignes.append(f"{p} % = {p // 5} × 5 % : {p // 5} × {cinq} = {res}.")
    return exercice("nombre", f"Calcule {p} % de {n}.", res, lignes,
                    "50 % = la moitié ; 25 % = le quart ; 10 % = le dixième.")


# --- 7. Mesures ----------------------------------------------------------------------------

TABLES_MESURES = {
    "longueur": ["km", "hm", "dam", "m", "dm", "cm", "mm"],
    "masse": ["kg", "hg", "dag", "g", "dg", "cg", "mg"],
    "contenance": ["kL", "hL", "daL", "L", "dL", "cL", "mL"],
}
PAIRES_SIMPLES = [("km", "m"), ("m", "cm"), ("cm", "mm"), ("m", "mm"), ("kg", "g"), ("L", "cL"), ("L", "mL")]


def conversion_decimale(rng, niveau):
    if niveau == 1:
        grande, petite = rng.choice(PAIRES_SIMPLES)
        vers_petite = True
    else:
        table = rng.choice(list(TABLES_MESURES.values())[:2] + [["L", "dL", "cL", "mL"]])
        if niveau == 2:
            grande, petite = rng.choice(PAIRES_SIMPLES)
        else:
            i, j = sorted(rng.sample(range(len(table)), 2))
            grande, petite = table[i], table[j]
        vers_petite = rng.random() < 0.5
    ecart = next(t.index(petite) - t.index(grande) for t in TABLES_MESURES.values() if grande in t and petite in t)
    f = 10 ** ecart
    if vers_petite:
        v = decimal_au_hasard(rng, rng.randint(1, min(2, ecart)), 20)
        r = v.scaleb(ecart)
        lignes = [f"1 {grande} = {ecrire(f)} {petite} : je multiplie par {ecrire(f)}.",
                  f"La virgule se déplace de {ecart} rang{'s' if ecart > 1 else ''} vers la droite.",
                  f"{ecrire(v)} {grande} = {ecrire(r)} {petite}"]
        de, vers = grande, petite
    else:
        v = Decimal(rng.randint(1, 50 * f) if f < 1000 else rng.randint(100, 20000))
        while v % 10 == 0:
            v += 1
        r = v.scaleb(-ecart)
        lignes = [f"1 {grande} = {ecrire(f)} {petite} : pour passer en {grande}, je divise par {ecrire(f)}.",
                  f"La virgule se déplace de {ecart} rang{'s' if ecart > 1 else ''} vers la gauche.",
                  f"{ecrire(v)} {petite} = {ecrire(r)} {grande}"]
        de, vers = petite, grande
    return exercice("nombre", f"{ecrire(v)} {de} =", texte_decimal(r), lignes,
                    f"Combien de {petite} dans 1 {grande} ? Tu peux t'aider d'un tableau de conversion.",
                    unite=vers, reponse_texte=f"{ecrire(r)} {vers}")


def duree(m: int) -> str:
    h, mn = divmod(m, 60)
    if not h:
        return f"{mn} min"
    return f"{h} h {mn:02d} min" if mn else f"{h} h"


def durees(rng, niveau):
    if niveau == 1:
        h, m = rng.randint(1, 4), rng.choice([5, 10, 15, 20, 25, 30, 40, 45, 50])
        return exercice("nombre", f"{h} h {m} min =", 60 * h + m,
                        [f"1 h = 60 min, donc {h} h = {h} × 60 = {60 * h} min.", f"{60 * h} + {m} = {60 * h + m} min"],
                        "Une heure, c'est 60 minutes (pas 100 !).", unite="min")
    if niveau == 2:
        total = rng.randint(70, 290)
        while total % 60 == 0:
            total += 7
        h, m = divmod(total, 60)
        return exercice("multi", f"{total} min =", [h, m],
                        [f"Dans {total}, combien de fois 60 ? {h} fois ({h} × 60 = {60 * h}).",
                         f"Il reste {total} − {60 * h} = {m} min.", f"{total} min = {h} h {m} min"],
                        "Cherche combien de fois 60 min il y a dans ce nombre.",
                        champs=[{"label": "h"}, {"label": "min"}], reponse_texte=f"{h} h {m} min")
    h1, m1 = rng.randint(8, 18), rng.choice([5, 10, 15, 20, 25, 35, 40, 45, 50])
    d = rng.randint(70, 200)
    fin = h1 * 60 + m1 + d
    fh, fm = divmod(fin, 60)
    jusqua = 60 - m1
    reste = d - jusqua
    return exercice("multi", f"Un film commence à {h1} h {m1:02d} et finit à {fh} h {fm:02d}. "
                    "Combien de temps dure-t-il ?", list(divmod(d, 60)),
                    [f"De {h1} h {m1:02d} à {h1 + 1} h : {jusqua} min.",
                     f"De {h1 + 1} h à {fh} h {fm:02d} : {duree(reste)}.",
                     f"En tout : {jusqua} min + {duree(reste)} = {duree(d)}."],
                    "Avance d'abord jusqu'à l'heure pile suivante, puis compte le reste.",
                    champs=[{"label": "h"}, {"label": "min"}], reponse_texte=duree(d))


# --- 8. Périmètres et aires ------------------------------------------------------------------

def aire(rng, niveau):
    u = rng.choice(["cm", "m"])
    forme = rng.choice(["rectangle", "carré"] + (["largeur", "perimetre"] if niveau == 3 else
                                               ["perimetre"] if niveau == 2 else []))
    if forme == "carré":
        c = rng.randint(2, 6 + 3 * niveau)
        return exercice("nombre", f"Un carré a des côtés de {c} {u}. Quelle est son aire ?", c * c,
                        ["Aire du carré = côté × côté.", f"{c} × {c} = {c * c} {u}²"],
                        "Combien de carrés de 1 sur 1 peut-on ranger dedans ?", unite=f"{u}²")
    L, l = rng.randint(4, 8 + 4 * niveau), rng.randint(2, 9)
    if l >= L:
        L, l = l + 2, L
    if forme == "rectangle":
        return exercice("nombre", f"Un rectangle mesure {L} {u} de long et {l} {u} de large. "
                        "Quelle est son aire ?", L * l,
                        ["Aire du rectangle = longueur × largeur.", f"{L} × {l} = {L * l} {u}²"],
                        f"Combien de lignes de {L} carrés de 1 {u} sur 1 {u} ?", unite=f"{u}²")
    if forme == "perimetre":
        quoi = rng.choice(["aire", "périmètre"])
        if quoi == "aire":
            return exercice("nombre", f"Un rectangle mesure {L} {u} sur {l} {u}. Quelle est son aire ?", L * l,
                            ["L'aire, c'est la surface : longueur × largeur.", f"{L} × {l} = {L * l} {u}²"],
                            "Attention : aire (surface) et périmètre (tour) ne se calculent pas pareil.",
                            unite=f"{u}²")
        return exercice("nombre", f"Un rectangle mesure {L} {u} sur {l} {u}. Quel est son périmètre ?",
                        2 * (L + l),
                        ["Le périmètre, c'est le tour : (longueur + largeur) × 2.",
                         f"({L} + {l}) × 2 = {2 * (L + l)} {u}"],
                        "Attention : aire (surface) et périmètre (tour) ne se calculent pas pareil.", unite=u)
    return exercice("nombre", f"Un rectangle a une aire de {L * l} {u}². Sa longueur est {L} {u}. "
                    "Quelle est sa largeur ?", l,
                    ["Aire = longueur × largeur, donc largeur = aire ÷ longueur.", f"{L * l} ÷ {L} = {l} {u}"],
                    f"Quel nombre multiplié par {L} donne {L * l} ?", unite=u)


def aire_triangle_rectangle(rng, niveau):
    u = rng.choice(["cm", "m"])
    a, b = rng.randint(2, 6 + 3 * niveau), rng.randint(2, 6 + 3 * niveau)
    if a * b % 2:
        b += 1
    return exercice("nombre", f"Un triangle rectangle a deux côtés de l'angle droit de {a} {u} et {b} {u}. "
                    "Quelle est son aire ?", a * b // 2,
                    [f"C'est la moitié d'un rectangle de {a} {u} sur {b} {u}.",
                     f"Aire du rectangle : {a} × {b} = {a * b} {u}².",
                     f"Aire du triangle : {a * b} ÷ 2 = {a * b // 2} {u}²."],
                    "Dessine le rectangle dont ce triangle est la moitié.", unite=f"{u}²")


def aire_figure_composee(rng, niveau):
    u = rng.choice(["cm", "m"])
    L, l = rng.randint(8, 16), rng.randint(6, 12)
    a, b = rng.randint(2, L - 3), rng.randint(2, l - 3)
    return exercice("nombre", f"Une figure en forme de L : c'est un rectangle de {L} {u} sur {l} {u} dont on a "
                    f"enlevé un coin rectangulaire de {a} {u} sur {b} {u}. Quelle est son aire ?", L * l - a * b,
                    [f"Aire du grand rectangle : {L} × {l} = {L * l} {u}².",
                     f"Aire du coin enlevé : {a} × {b} = {a * b} {u}².",
                     f"Aire de la figure : {L * l} − {a * b} = {L * l - a * b} {u}²."],
                    "Calcule l'aire du grand rectangle, puis enlève celle du coin.", unite=f"{u}²")


aire_figure_composee = niveau_min(2, aire_figure_composee)


# --- 9. Problèmes ----------------------------------------------------------------------------

@avec_prenom
def probleme_cm2(rng, niveau, prenom="Mouaz"):
    nom = rng.choice([prenom, prenom, "Léa", "Sami", "Inès", "Hugo"])
    il = "elle" if nom in ("Léa", "Inès") else "il"
    if niveau == 1:
        a, b = Decimal(rng.randint(150, 1500)) / 100, Decimal(rng.randint(50, 900)) / 100
        return exercice("nombre", f"{nom} achète un livre à {ecrire_fixe(a, 2)} € et un stylo à "
                        f"{ecrire_fixe(b, 2)} €. Combien dépense-t-{il} en tout ?", texte_decimal(a + b),
                        ["En tout → addition. J'aligne les virgules.",
                         f"{ecrire_fixe(a, 2)} + {ecrire_fixe(b, 2)} = {ecrire_fixe(a + b, 2)} €"],
                        "Pose l'addition en alignant les virgules.", unite="€",
                        reponse_texte=f"{ecrire_fixe(a + b, 2)} €")
    if niveau == 2:
        k = rng.randint(2, 5)
        p = Decimal(rng.randint(150, 480)) / 100
        billet = 10 if k * p < 10 else 20 if k * p < 20 else 50
        total = k * p
        return exercice("nombre", f"Un paquet de céréales coûte {ecrire_fixe(p, 2)} €. {nom} en achète {k} et paie "
                        f"avec un billet de {billet} €. Combien lui rend-on ?", texte_decimal(billet - total),
                        [f"Prix des {k} paquets : {k} × {ecrire_fixe(p, 2)} = {ecrire_fixe(total, 2)} €.",
                         f"Monnaie rendue : {billet} − {ecrire_fixe(total, 2)} = {ecrire_fixe(billet - total, 2)} €."],
                        "Calcule d'abord le prix de tous les paquets.", unite="€",
                        reponse_texte=f"{ecrire_fixe(billet - total, 2)} €")
    cas = rng.randint(1, 2)
    if cas == 1:
        rangees, chaises = rng.randint(12, 25), rng.randint(15, 30)
        total = rangees * chaises
        assis = rng.randint(total // 2, total - 10)
        return exercice("nombre", f"Une salle de spectacle a {rangees} rangées de {chaises} chaises. "
                        f"{ecrire(assis)} spectateurs sont assis. Combien de chaises sont vides ?", total - assis,
                        [f"Nombre de chaises : {rangees} × {chaises} = {ecrire(total)}.",
                         f"Chaises vides : {ecrire(total)} − {ecrire(assis)} = {ecrire(total - assis)}."],
                        "Calcule d'abord le nombre total de chaises.", unite="chaises")
    vitesse = rng.choice([12, 14, 16, 18, 20, 24])
    heures = rng.randint(2, 4)
    distance = vitesse * heures + vitesse // 2
    return exercice("nombre", f"{nom} fait du vélo. {il.capitalize()} roule toujours à la même allure : {vitesse} km "
                    f"en 1 heure. Quelle distance parcourt-{il} en {heures} h 30 min ?", distance,
                    [f"En {heures} h : {heures} × {vitesse} = {heures * vitesse} km.",
                     f"En 30 min (la moitié d'une heure) : {vitesse} ÷ 2 = {vitesse // 2} km.",
                     f"En tout : {heures * vitesse} + {vitesse // 2} = {distance} km."],
                    "30 minutes, c'est la moitié d'une heure.", unite="km")


# --- Catalogue du CM2 ------------------------------------------------------------------------

GENERATEURS = {
    "cm2-nombres": [decomposer_classes, ecrire_en_chiffres, comparer_grands, chiffre_des_grands, arrondir_grand],
    "cm2-fractions": [fraction_vers_decimal, encadrer_fraction, ajouter_fractions, fraction_quantite],
    "cm2-decimaux": [chiffre_decimal, comparer_decimaux_cm2, arrondir_decimal, operation_decimaux_cm2],
    "cm2-multiplication": [fois_10_decimal, decimal_fois_entier, multiplication_posee],
    "cm2-division": [division_deux_chiffres, division_decimale],
    "cm2-proportionnalite": [proportionnalite, proportionnalite, pourcentage],
    "cm2-mesures": [conversion_decimale, conversion_decimale, durees],
    "cm2-aires": [aire, aire, aire_triangle_rectangle, aire_figure_composee],
    "cm2-problemes": [probleme_cm2],
}
