"""
Générateurs d'exercices de mathématiques, programme de 6e.

Même principe qu'au CM1 et au CM2 : le code tire et résout chaque exercice,
avec Decimal pour les nombres à virgule ; l'IA n'explique qu'ensuite.
"""

import math
from decimal import Decimal

from exercices import (avec_prenom, ecrire, ecrire_fixe, etapes_division, etapes_division_decimale, exercice,
                       nb_decimales, niveau_min, texte_decimal)
from exercices_cm2 import decimal_au_hasard, fois_10_decimal

PI = Decimal("3.14")


# --- 1. Nombres décimaux ------------------------------------------------------------

def decimal_en_fraction(rng, niveau):
    places = 1 if niveau == 1 else rng.choice([2, 3]) if niveau == 3 else 2
    v = decimal_au_hasard(rng, places, 9 if niveau == 1 else 99)
    b = 10 ** places
    a = int(v.scaleb(places))
    nom = {1: "dixièmes", 2: "centièmes", 3: "millièmes"}[places]
    return exercice("nombre", f"Complète : {ecrire(v)} = …/{ecrire(b)}", a,
                    [f"Le dernier chiffre de {ecrire(v)} est au rang des {nom}.",
                     f"{ecrire(v)}, c'est {ecrire(a)} {nom}.",
                     f"{ecrire(v)} = {ecrire(a)}/{ecrire(b)}"],
                    f"Combien de {nom} y a-t-il en tout dans {ecrire(v)} ?", grand=True)


def encadrer_decimal(rng, niveau):
    precision = niveau - 1  # 0 : à l'unité ; 1 : au dixième ; 2 : au centième
    v = decimal_au_hasard(rng, precision + rng.randint(1, 2), 99)
    pas = Decimal(1).scaleb(-precision)
    bas = (v / pas).to_integral_value(rounding="ROUND_FLOOR") * pas
    haut = bas + pas
    consigne = ["à l'unité", "au dixième", "au centième"][precision]
    rang = ["des unités", "des dixièmes", "des centièmes"][precision]
    return exercice("multi", f"Encadre {ecrire(v)} {consigne} : … < {ecrire(v)} < …",
                    [texte_decimal(bas), texte_decimal(haut)],
                    [f"Je garde les chiffres de {ecrire(v)} jusqu'au rang {rang} : {ecrire_fixe(bas, precision)}.",
                     f"Le nombre suivant à ce rang est {ecrire_fixe(haut, precision)}.",
                     f"{ecrire_fixe(bas, precision)} < {ecrire(v)} < {ecrire_fixe(haut, precision)}"],
                    "Le premier nombre, c'est le début de " + ecrire(v) + " ; le second, le suivant.",
                    champs=[{"label": "juste avant"}, {"label": "juste après"}],
                    reponse_texte=f"{ecrire_fixe(bas, precision)} < {ecrire(v)} < {ecrire_fixe(haut, precision)}")


def plus_petit_de_trois(rng, niveau):
    e = rng.randint(0, 30)
    while True:
        nombres = [e + decimal_au_hasard(rng, rng.randint(1, 1 + niveau), 0) for _ in range(3)]
        if len(set(nombres)) == 3 and len({ecrire(x) for x in nombres}) == 3:
            break
    ordre = sorted(nombres)
    places = max(nb_decimales(x) for x in nombres)
    return exercice("choix", "Quel est le plus petit nombre ?", ecrire(ordre[0]),
                    [f"La partie entière est la même : {e}.",
                     "J'écris autant de chiffres après la virgule : "
                     + " ; ".join(ecrire_fixe(x, places) for x in nombres) + ".",
                     "Je compare de gauche à droite, rang par rang.",
                     "Dans l'ordre croissant : " + " < ".join(ecrire(x) for x in ordre) + "."],
                    "Ajoute des zéros pour avoir autant de chiffres après la virgule.",
                    options=[ecrire(x) for x in nombres])


def fois_0_1(rng, niveau):
    if niveau < 3:
        return fois_10_decimal(rng, 3)
    k, z = rng.choice([(Decimal("0.1"), 1), (Decimal("0.01"), 2)])
    v = decimal_au_hasard(rng, rng.randint(0, 2), 999)
    r = v.scaleb(-z)
    diviser = {1: "10", 2: "100"}[z]
    return exercice("nombre", f"{ecrire(v)} × {ecrire(k)}", texte_decimal(r),
                    [f"Multiplier par {ecrire(k)}, c'est diviser par {diviser}.",
                     f"La virgule se déplace de {z} rang{'s' if z > 1 else ''} vers la gauche.",
                     f"{ecrire(v)} × {ecrire(k)} = {ecrire(r)}"],
                    f"Multiplier par {ecrire(k)}, est-ce que ça agrandit ou ça rapetisse ?", grand=True,
                    reponse_texte=ecrire(r))


# --- 2. Opérations sur les décimaux ---------------------------------------------------

def produit_decimaux(rng, niveau):
    pa = 1 if niveau == 1 else rng.choice([1, 2])
    pb = 0 if niveau == 1 else 1
    a = decimal_au_hasard(rng, pa, 9 if niveau < 3 else 30)
    b = decimal_au_hasard(rng, pb, 9) if pb else Decimal(rng.randint(3, 9))
    x, y = int(a.scaleb(pa)), int(b.scaleb(pb))
    r = a * b
    total = pa + pb
    return exercice("nombre", f"{ecrire(a)} × {ecrire(b)}", texte_decimal(r),
                    [f"Je calcule sans les virgules : {ecrire(x)} × {ecrire(y)} = {ecrire(x * y)}.",
                     f"Chiffres après la virgule : {pa} + {pb} = {total}. Le résultat en a {total}." if pb
                     else f"{ecrire(a)} a {pa} chiffre{'s' if pa > 1 else ''} après la virgule : le résultat aussi.",
                     f"{ecrire(a)} × {ecrire(b)} = {ecrire_fixe(r, total)}"
                     + (f" = {ecrire(r)}" if ecrire_fixe(r, total) != ecrire(r) else "")],
                    "Multiplie sans les virgules, puis compte les chiffres après la virgule des deux nombres.",
                    grand=True, reponse_texte=ecrire(r))


def division_decimale_6e(rng, niveau):
    d = rng.randint(2, 5) if niveau == 1 else rng.randint(3, 9)
    q = decimal_au_hasard(rng, 1 if niveau < 3 else 2, 9 if niveau == 1 else 60)
    dividende = q * d
    return exercice("nombre", f"Calcule {ecrire(dividende)} ÷ {d}", texte_decimal(q),
                    etapes_division_decimale(dividende, d),
                    "Pose la division. Quand tu abaisses le premier chiffre après la virgule, "
                    "écris la virgule au quotient.", grand=True, reponse_texte=ecrire(q))


def calcul_ordre(rng, niveau):
    a, b, c = rng.randint(2, 12), rng.randint(2, 9), rng.randint(2, 9)
    if niveau == 1 or rng.random() < 0.5:
        r = a + b * c
        return exercice("nombre", f"{a} + {b} × {c}", r,
                        ["La multiplication se fait avant l'addition.", f"{b} × {c} = {b * c}",
                         f"{a} + {b * c} = {r}"],
                        "Qui passe en premier : + ou × ?", grand=True)
    r = (a + b) * c
    return exercice("nombre", f"({a} + {b}) × {c}", r,
                    ["On calcule d'abord ce qui est entre parenthèses.", f"{a} + {b} = {a + b}",
                     f"{a + b} × {c} = {r}"],
                    "Les parenthèses passent en premier.", grand=True)


# --- 3. Multiples et diviseurs ---------------------------------------------------------

def somme_chiffres(n: int) -> tuple[str, int]:
    c = [int(x) for x in str(n)]
    return " + ".join(map(str, c)), sum(c)


def critere(n: int, k: int) -> list[str]:
    """Explique le critère de divisibilité de n par k."""
    u = n % 10
    if k == 2:
        return [f"Le chiffre des unités de {ecrire(n)} est {u}.",
                f"{u} est pair : {ecrire(n)} est divisible par 2." if u % 2 == 0
                else f"{u} est impair : {ecrire(n)} n'est pas divisible par 2."]
    if k == 5:
        return [f"Le chiffre des unités de {ecrire(n)} est {u}.",
                f"C'est 0 ou 5 : {ecrire(n)} est divisible par 5." if u in (0, 5)
                else f"Ce n'est ni 0 ni 5 : {ecrire(n)} n'est pas divisible par 5."]
    if k == 10:
        return [f"Le chiffre des unités de {ecrire(n)} est {u}.",
                f"C'est 0 : {ecrire(n)} est divisible par 10." if u == 0
                else f"Ce n'est pas 0 : {ecrire(n)} n'est pas divisible par 10."]
    if k == 4:
        fin = n % 100
        return [f"Les deux derniers chiffres de {ecrire(n)} forment {fin}.",
                f"{fin} est dans la table de 4 ({fin} = 4 × {fin // 4}) : {ecrire(n)} est divisible par 4."
                if fin % 4 == 0 else f"{fin} n'est pas dans la table de 4 : {ecrire(n)} n'est pas divisible par 4."]
    calcul, s = somme_chiffres(n)
    oui = s % k == 0
    return [f"Je fais la somme des chiffres : {calcul} = {s}.",
            f"{s} est dans la table de {k} : {ecrire(n)} est divisible par {k}." if oui
            else f"{s} n'est pas dans la table de {k} : {ecrire(n)} n'est pas divisible par {k}."]


def est_divisible(rng, niveau):
    k = rng.choice([2, 5, 10]) if niveau == 1 else rng.choice([3, 9, 5, 2]) if niveau == 2 else rng.choice([3, 4, 9])
    voulu = rng.random() < 0.5
    while True:
        n = rng.randint(100, 9999 if niveau > 1 else 999)
        if (n % k == 0) == voulu:
            break
    return exercice("choix", f"{ecrire(n)} est-il divisible par {k} ?", "oui" if voulu else "non",
                    critere(n, k), {2: "Regarde le chiffre des unités.", 5: "Regarde le chiffre des unités.",
                                    10: "Regarde le chiffre des unités.", 3: "Additionne ses chiffres.",
                                    9: "Additionne ses chiffres.", 4: "Regarde ses deux derniers chiffres."}[k],
                    options=["oui", "non"])


def trouver_multiple(rng, niveau):
    k = rng.choice([3, 9]) if niveau < 3 else rng.choice([3, 4, 9])
    bon = k * rng.randint(12, 999 // k)
    autres = set()
    while len(autres) < 2:
        x = bon + rng.choice([1, 2, -1, -2, 10, 11, -10, 20])
        if x % k and x > 0:
            autres.add(x)
    options = [bon, *autres]
    rng.shuffle(options)
    lignes = []
    for x in options:
        lignes.append(critere(x, k)[-1] if k == 4 else f"{ecrire(x)} : {somme_chiffres(x)[0]} = "
                      f"{somme_chiffres(x)[1]}" + (" → oui." if x % k == 0 else " → non."))
    lignes.append(f"Le multiple de {k} est {ecrire(bon)}.")
    return exercice("choix", f"Lequel de ces nombres est un multiple de {k} ?", ecrire(bon), lignes,
                    "Un multiple de 3 ou de 9 : la somme de ses chiffres est dans la table." if k != 4
                    else "Un multiple de 4 : ses deux derniers chiffres forment un nombre de la table de 4.",
                    options=[ecrire(x) for x in options])


def division_euclidienne(rng, niveau):
    d = rng.randint(3, 9) if niveau == 1 else rng.randint(11, 25) if niveau == 2 else rng.randint(12, 60)
    n = rng.randint(d * 5, 999 if niveau < 3 else 9999)
    while n % d == 0:
        n += 1
    q, r = divmod(n, d)
    return exercice("multi", f"Division euclidienne : {ecrire(n)} = {d} × … + …", [q, r],
                    etapes_division(n, d) + [f"Donc {ecrire(n)} = {d} × {ecrire(q)} + {r}, avec {r} < {d}."],
                    "Pose la division : le premier nombre est le quotient, le second le reste "
                    "(plus petit que le diviseur).",
                    champs=[{"label": "quotient"}, {"label": "reste"}],
                    reponse_texte=f"{ecrire(n)} = {d} × {ecrire(q)} + {r}")


# --- 4. Fractions -------------------------------------------------------------------------

def fraction_irreductible(rng, maxi=9):
    while True:
        b = rng.randint(2, maxi)
        a = rng.randint(1, b - 1)
        if math.gcd(a, b) == 1:
            return a, b


def fraction_egale(rng, niveau):
    a, b = fraction_irreductible(rng, 9 if niveau < 3 else 12)
    k = rng.randint(2, 6 if niveau == 1 else 10)
    if niveau == 1 or rng.random() < 0.5:
        return exercice("nombre", f"Complète : {a}/{b} = …/{b * k}", a * k,
                        [f"Pour passer de {b} à {b * k}, on multiplie par {k}.",
                         f"On multiplie aussi le numérateur par {k} : {a} × {k} = {a * k}.",
                         f"{a}/{b} = {a * k}/{b * k}"],
                        "On multiplie le numérateur et le dénominateur par le même nombre.")
    return exercice("nombre", f"Complète : {a * k}/{b * k} = {a}/…", b,
                    [f"Pour passer de {a * k} à {a}, on divise par {k}.",
                     f"On divise aussi le dénominateur par {k} : {b * k} ÷ {k} = {b}.",
                     f"{a * k}/{b * k} = {a}/{b}"],
                    "On divise le numérateur et le dénominateur par le même nombre.")



def simplifier(rng, niveau):
    a, b = fraction_irreductible(rng, 9 if niveau < 3 else 15)
    k = rng.choice([2, 3, 5, 10]) if niveau == 1 else rng.randint(2, 9 if niveau == 2 else 12)
    return exercice("multi", f"Simplifie au maximum la fraction {a * k}/{b * k}.", [a, b],
                    [f"{a * k} et {b * k} sont tous les deux dans la table de {k} : "
                     f"{a * k} = {k} × {a} et {b * k} = {k} × {b}.",
                     f"Je divise le haut et le bas par {k} : {a * k}/{b * k} = {a}/{b}.",
                     f"{a} et {b} n'ont plus de diviseur commun (à part 1) : c'est fini."],
                    "Cherche un nombre qui divise à la fois le numérateur et le dénominateur. "
                    "Tu peux simplifier en plusieurs fois.",
                    champs=[{"label": "numérateur"}, {"label": "dénominateur"}], reponse_texte=f"{a}/{b}")


def ajouter_fractions_6e(rng, niveau):
    b = rng.randint(3, 8)
    if niveau == 1:
        a, c = rng.randint(1, b), rng.randint(1, b)
        return exercice("nombre", f"{a}/{b} + {c}/{b} = …/{b}", a + c,
                        [f"Même dénominateur : j'additionne les numérateurs. {a} + {c} = {a + c}.",
                         f"{a}/{b} + {c}/{b} = {a + c}/{b}"],
                        "Le dénominateur ne change pas.", grand=True)
    k = rng.randint(2, 4)
    B = b * k
    a, c = rng.randint(1, b - 1), rng.randint(1, B - 1)
    if niveau == 3 and rng.random() < 0.5 and a * k > c:
        return exercice("nombre", f"{a}/{b} − {c}/{B} = …/{B}", a * k - c,
                        [f"{B} = {b} × {k} : j'écris {a}/{b} avec {B} au dénominateur.",
                         f"{a}/{b} = {a * k}/{B} (× {k} en haut et en bas).",
                         f"{a * k}/{B} − {c}/{B} = {a * k - c}/{B}"],
                        f"Transforme d'abord {a}/{b} en une fraction de dénominateur {B}.", grand=True)
    return exercice("nombre", f"{a}/{b} + {c}/{B} = …/{B}", a * k + c,
                    [f"{B} = {b} × {k} : j'écris {a}/{b} avec {B} au dénominateur.",
                     f"{a}/{b} = {a * k}/{B} (× {k} en haut et en bas).",
                     f"{a * k}/{B} + {c}/{B} = {a * k + c}/{B}"],
                    f"Transforme d'abord {a}/{b} en une fraction de dénominateur {B}.", grand=True)


def fraction_quotient(rng, niveau):
    while True:
        a, b = rng.sample(range(2, 10), 2)
        if math.gcd(a, b) == 1:
            break
    options = [f"{a}/{b}", f"{b}/{a}", str(a * b)]
    rng.shuffle(options)
    return exercice("choix", f"Quel nombre, multiplié par {b}, donne {a} ?", f"{a}/{b}",
                    [f"La fraction {a}/{b} est le nombre qui, multiplié par {b}, donne {a}.",
                     f"{b} × {a}/{b} = {a}. C'est la fraction-quotient : {a}/{b} = {a} ÷ {b}."],
                    f"{a}/{b}, c'est {a} divisé par {b}.", options=options)


fraction_quotient = niveau_min(2, fraction_quotient)


# --- 5. Proportionnalité ----------------------------------------------------------------------

def quatrieme_proportionnelle(rng, niveau):
    prix_kg = Decimal(rng.randint(2, 6)) if niveau == 1 else Decimal(rng.randint(3, 13)) / 2
    a, b = rng.sample([2, 3, 4, 5, 6, 8, 10], 2)
    fruit = rng.choice(["pommes", "cerises", "tomates", "oranges"])
    return exercice("nombre", f"Le prix des {fruit} est proportionnel à leur masse. {a} kg coûtent "
                    f"{ecrire_fixe(a * prix_kg, 2)} €. Combien coûtent {b} kg ?", texte_decimal(b * prix_kg),
                    [f"Prix d'1 kg : {ecrire_fixe(a * prix_kg, 2)} ÷ {a} = {ecrire_fixe(prix_kg, 2)} €.",
                     f"Prix de {b} kg : {b} × {ecrire_fixe(prix_kg, 2)} = {ecrire_fixe(b * prix_kg, 2)} €."],
                    "Passe par le prix d'1 kg.", unite="€", reponse_texte=f"{ecrire_fixe(b * prix_kg, 2)} €")


def appliquer_pourcentage(rng, niveau):
    p = rng.choice([10, 20, 50]) if niveau == 1 else rng.choice([15, 25, 30, 40])
    prix = 20 * rng.randint(2, 10)
    reduction = prix * p // 100
    objet = rng.choice(["Un pull", "Un jeu vidéo", "Une paire de baskets", "Un sac à dos"])
    if niveau < 3:
        return exercice("nombre", f"{objet} coûte {prix} €. Il est soldé à {p} %. "
                        "Quel est le montant de la réduction ?", reduction,
                        [f"{p} % de {prix}, c'est {p}/100 de {prix}.",
                         f"{prix} ÷ 100 = {ecrire(Decimal(prix) / 100)}, puis × {p} = {reduction} €."],
                        f"Calcule {p} % de {prix}. Tu peux passer par 10 %.", unite="€")
    return exercice("nombre", f"{objet} coûte {prix} €. Il est soldé à {p} %. Quel est son nouveau prix ?",
                    prix - reduction,
                    [f"Réduction : {p} % de {prix} = {prix} × {p} ÷ 100 = {reduction} €.",
                     f"Nouveau prix : {prix} − {reduction} = {prix - reduction} €."],
                    "Calcule d'abord la réduction, puis enlève-la du prix.", unite="€")


def echelle(rng, niveau):
    k, phrase = rng.choice([(100, "1 cm représente 1 m"), (200, "1 cm représente 2 m"),
                            (1000, "1 cm représente 10 m")] if niveau > 1 else [(100, "1 cm représente 1 m")])
    plan = Decimal(rng.randint(15, 120)) / 10
    reel = plan * k / 100
    return exercice("nombre", f"Sur un plan à l'échelle 1/{ecrire(k)}, une pièce mesure {ecrire(plan)} cm de long. "
                    "Quelle est sa longueur réelle, en mètres ?", texte_decimal(reel),
                    [f"Échelle 1/{ecrire(k)} : {phrase} ({ecrire(k)} cm).",
                     f"{ecrire(plan)} × {ecrire(k)} = {ecrire(plan * k)} cm en vrai.",
                     f"{ecrire(plan * k)} cm = {ecrire(reel)} m"],
                    f"1 cm sur le plan = {ecrire(k)} cm en vrai.", unite="m", reponse_texte=f"{ecrire(reel)} m")


echelle = niveau_min(2, echelle)


# --- 6. Aires, volumes et cercle ---------------------------------------------------------------

def perimetre_cercle(rng, niveau):
    r = rng.randint(2, 15)
    u = rng.choice(["cm", "m"])
    if niveau == 1:
        d = 2 * r
        res = d * PI
        return exercice("nombre", f"Un cercle a un diamètre de {d} {u}. Calcule son périmètre (prends π ≈ 3,14).",
                        texte_decimal(res),
                        ["Périmètre du cercle = diamètre × π.", f"{d} × 3,14 = {ecrire(res)} {u}"],
                        "Multiplie le diamètre par 3,14.", unite=u, reponse_texte=f"{ecrire(res)} {u}")
    if niveau == 3 and rng.random() < 0.5:
        res = r * r * PI
        return exercice("nombre", f"Un disque a un rayon de {r} {u}. Calcule son aire (prends π ≈ 3,14).",
                        texte_decimal(res),
                        ["Aire du disque = rayon × rayon × π.", f"{r} × {r} = {r * r}",
                         f"{r * r} × 3,14 = {ecrire(res)} {u}²"],
                        "Aire : rayon × rayon × 3,14.", unite=f"{u}²", reponse_texte=f"{ecrire(res)} {u}²")
    res = 2 * r * PI
    return exercice("nombre", f"Un cercle a un rayon de {r} {u}. Calcule son périmètre (prends π ≈ 3,14).",
                    texte_decimal(res),
                    ["Le diamètre est le double du rayon : " + f"{r} × 2 = {2 * r} {u}.",
                     "Périmètre du cercle = diamètre × π.", f"{2 * r} × 3,14 = {ecrire(res)} {u}"],
                    "Attention : rayon ou diamètre ? Le diamètre, c'est 2 rayons.", unite=u,
                    reponse_texte=f"{ecrire(res)} {u}")


def aire_triangle(rng, niveau):
    u = rng.choice(["cm", "m"])
    base, h = rng.randint(3, 8 + 4 * niveau), rng.randint(2, 6 + 3 * niveau)
    if base * h % 2:
        h += 1
    return exercice("nombre", f"Un triangle a une base de {base} {u} et une hauteur de {h} {u}. "
                    "Quelle est son aire ?", base * h // 2,
                    ["Aire du triangle = base × hauteur ÷ 2.", f"{base} × {h} = {base * h}",
                     f"{base * h} ÷ 2 = {base * h // 2} {u}²"],
                    "Un triangle, c'est la moitié d'un rectangle de même base et même hauteur.", unite=f"{u}²")


def volume_pave(rng, niveau):
    L, l, h = rng.randint(3, 12), rng.randint(2, 9), rng.randint(2, 8)
    if niveau < 3:
        return exercice("nombre", f"Un pavé droit mesure {L} cm de long, {l} cm de large et {h} cm de haut. "
                        "Quel est son volume ?", L * l * h,
                        ["Volume du pavé = longueur × largeur × hauteur.", f"{L} × {l} = {L * l}",
                         f"{L * l} × {h} = {L * l * h} cm³"],
                        "Combien de petits cubes de 1 cm de côté peut-on ranger dedans ?", unite="cm³")
    L, l, h = L * 10, l * 10, h * 10
    v = L * l * h
    litres = Decimal(v) / 1000
    return exercice("nombre", f"Un aquarium a la forme d'un pavé de {L} cm sur {l} cm sur {h} cm. "
                    "Combien de litres d'eau peut-il contenir ?", texte_decimal(litres),
                    [f"Volume : {L} × {l} × {h} = {ecrire(v)} cm³.",
                     "1 L = 1 dm³ = 1 000 cm³.", f"{ecrire(v)} ÷ 1 000 = {ecrire(litres)} L"],
                    "Calcule le volume en cm³, puis souviens-toi : 1 L = 1 000 cm³.", unite="L",
                    reponse_texte=f"{ecrire(litres)} L")


def conversion_aires(rng, niveau):
    unites = ["km²", "hm²", "dam²", "m²", "dm²", "cm²", "mm²"]
    i = rng.randint(2, 5) if niveau < 3 else rng.randint(0, 5)
    ecart = 1 if niveau == 1 else rng.randint(1, 2)
    j = min(i + ecart, 6)
    ecart = j - i
    v = Decimal(rng.randint(2, 50)) if niveau < 3 else decimal_au_hasard(rng, 1, 20)
    r = v.scaleb(2 * ecart)
    return exercice("nombre", f"{ecrire(v)} {unites[i]} =", texte_decimal(r),
                    [f"Pour les aires, chaque unité vaut 100 fois la suivante : 1 {unites[i]} = "
                     f"{ecrire(10 ** (2 * ecart))} {unites[j]}.",
                     f"{ecrire(v)} × {ecrire(10 ** (2 * ecart))} = {ecrire(r)} {unites[j]}"],
                    "En aire, on change d'unité de 100 en 100 (pas de 10 en 10) : 2 colonnes par unité.",
                    unite=unites[j], reponse_texte=f"{ecrire(r)} {unites[j]}")


conversion_aires = niveau_min(2, conversion_aires)


# --- 7. Angles -----------------------------------------------------------------------------------

def nature_angle(rng, niveau):
    mesure = rng.choice([rng.randint(10, 85), 90, rng.randint(95, 175), 180])
    nature = "aigu" if mesure < 90 else "droit" if mesure == 90 else "obtus" if mesure < 180 else "plat"
    return exercice("choix", f"Un angle mesure {mesure}°. Comment s'appelle-t-il ?", nature,
                    ["Aigu : moins de 90°. Droit : 90°. Obtus : entre 90° et 180°. Plat : 180°.",
                     f"{mesure}° → angle {nature}."],
                    "Compare la mesure à 90° (l'angle droit) et à 180° (l'angle plat).",
                    options=["aigu", "droit", "obtus", "plat"])


def angle_manquant(rng, niveau):
    total, nom = rng.choice([(90, "droit"), (180, "plat")] if niveau > 1 else [(90, "droit")])
    a = rng.randint(15, total - 15)
    if niveau == 3 and total == 180:
        a = rng.randint(15, 120)
        b = rng.randint(10, 180 - a - 10)
        return exercice("nombre", f"Un angle plat est partagé en trois angles. Deux d'entre eux mesurent {a}° "
                        f"et {b}°. Combien mesure le troisième ?", 180 - a - b,
                        ["Un angle plat mesure 180°.", f"{a} + {b} = {a + b}",
                         f"180 − {a + b} = {180 - a - b}°"],
                        "Les trois angles ensemble font un angle plat : 180°.", unite="°",
                        reponse_texte=f"{180 - a - b}°")
    return exercice("nombre", f"Un angle {nom} est partagé en deux angles. L'un mesure {a}°. "
                    "Combien mesure l'autre ?", total - a,
                    [f"Un angle {nom} mesure {total}°.", f"{total} − {a} = {total - a}°"],
                    f"Combien mesure un angle {nom} ?", unite="°", reponse_texte=f"{total - a}°")


# --- 8. Problèmes ----------------------------------------------------------------------------------

@avec_prenom
def probleme_6e(rng, niveau, prenom="Mouaz"):
    nom = rng.choice([prenom, prenom, "Léa", "Sami", "Inès", "Hugo"])
    il = "elle" if nom in ("Léa", "Inès") else "il"
    cas = rng.randint(1, 2)
    if niveau == 1 and cas == 1:
        k, prix = rng.randint(3, 6), Decimal(rng.randint(45, 180)) / 100
        total = k * prix
        return exercice("nombre", f"{nom} achète {k} cahiers à {ecrire_fixe(prix, 2)} € pièce. "
                        f"Combien paie-t-{il} ?", texte_decimal(total),
                        [f"{k} × {ecrire_fixe(prix, 2)} = {ecrire_fixe(total, 2)} €"],
                        "Plusieurs fois le même prix → multiplication.", unite="€",
                        reponse_texte=f"{ecrire_fixe(total, 2)} €")
    if niveau == 1:
        amis = rng.randint(3, 6)
        part = Decimal(rng.randint(150, 900)) / 100
        total = amis * part
        return exercice("nombre", f"{amis} amis partagent équitablement une addition de {ecrire_fixe(total, 2)} €. "
                        "Combien paie chacun ?", texte_decimal(part),
                        [f"Partager en {amis} parts égales → division.",
                         f"{ecrire_fixe(total, 2)} ÷ {amis} = {ecrire_fixe(part, 2)} €"],
                        "Partager équitablement → division.", unite="€", reponse_texte=f"{ecrire_fixe(part, 2)} €")
    if niveau == 2:
        argent = rng.randint(30, 60)
        a = Decimal(rng.randint(500, 1500)) / 100
        b = Decimal(rng.randint(300, 1200)) / 100
        reste = argent - a - b
        return exercice("nombre", f"{nom} a {argent} €. {il.capitalize()} achète une BD à {ecrire_fixe(a, 2)} € "
                        f"et un jeu à {ecrire_fixe(b, 2)} €. Combien lui reste-t-il ?", texte_decimal(reste),
                        [f"Dépenses : {ecrire_fixe(a, 2)} + {ecrire_fixe(b, 2)} = {ecrire_fixe(a + b, 2)} €.",
                         f"Il reste : {argent} − {ecrire_fixe(a + b, 2)} = {ecrire_fixe(reste, 2)} €."],
                        "Calcule d'abord tout ce qui est dépensé.", unite="€",
                        reponse_texte=f"{ecrire_fixe(reste, 2)} €")
    if cas == 1:
        conso = Decimal(rng.randint(45, 80)) / 10
        km = 100 * rng.randint(2, 6)
        litres = conso * km / 100
        return exercice("nombre", f"Une voiture consomme {ecrire(conso)} L d'essence pour 100 km. "
                        f"Combien consomme-t-elle pour {km} km ?", texte_decimal(litres),
                        [f"{km} km, c'est {km // 100} fois 100 km.",
                         f"{km // 100} × {ecrire(conso)} = {ecrire(litres)} L"],
                        "Combien de fois 100 km ?", unite="L", reponse_texte=f"{ecrire(litres)} L")
    eleves = rng.randint(22, 30)
    filles = rng.randint(8, eleves - 8)
    sortie = rng.randint(4, 9)
    total = eleves * sortie
    return exercice("nombre", f"Une classe de {eleves} élèves ({filles} filles) part en sortie. "
                    f"Chaque élève paie {sortie} €, et la mairie ajoute 50 €. Combien d'argent y a-t-il pour la sortie ?",
                    total + 50,
                    [f"Ce que paient les élèves : {eleves} × {sortie} = {total} €.",
                     f"Avec la mairie : {total} + 50 = {total + 50} €.",
                     f"Le nombre de filles ({filles}) ne sert pas : il faut bien choisir les informations utiles."],
                    "Toutes les informations ne servent pas ! Lesquelles sont utiles ?", unite="€")


# --- Catalogue de la 6e ----------------------------------------------------------------------------

GENERATEURS = {
    "6e-decimaux": [decimal_en_fraction, encadrer_decimal, plus_petit_de_trois, fois_0_1],
    "6e-operations": [produit_decimaux, division_decimale_6e, calcul_ordre],
    "6e-divisibilite": [est_divisible, trouver_multiple, division_euclidienne],
    "6e-fractions": [fraction_egale, simplifier, ajouter_fractions_6e, fraction_quotient],
    "6e-proportionnalite": [quatrieme_proportionnelle, appliquer_pourcentage, echelle],
    "6e-aires-volumes": [perimetre_cercle, aire_triangle, volume_pave, conversion_aires],
    "6e-angles": [nature_angle, angle_manquant],
    "6e-problemes": [probleme_6e],
}
