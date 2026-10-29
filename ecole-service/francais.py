"""
Générateurs d'exercices de français, du CM1 à la 6e.

Même principe qu'en maths : la bonne réponse vient du code. La conjugaison
et les accords sont calculés par conjugaison.py et par les règles écrites
ici ; la grammaire, les homophones et le vocabulaire viennent des banques
vérifiées de francais_banques.py.
"""

import re

import conjugaison as C
import francais_banques as B
from exercices import exercice

SUJETS = ["je", "tu", "il", "nous", "vous", "ils"]
VERBES_SIMPLES = [v for v in C.PREMIER_GROUPE if not v.endswith(("cer", "ger"))]
VERBES_CER_GER = [v for v in C.PREMIER_GROUPE if v.endswith(("cer", "ger"))]
IRREGULIERS_FACILES = ["être", "avoir", "aller", "faire"]
IRREGULIERS_AUTRES = [v for v in C.IRREGULIERS if v not in IRREGULIERS_FACILES]
VERBES_AVOIR_SIMPLES = [v for v in VERBES_SIMPLES if C.auxiliaire(v) == "avoir"]


def article_temps(temps: str) -> str:
    nom = C.TEMPS[temps]
    return f"à l'{nom}" if nom[0] in "aeiou" else f"au {nom}"


def verbes_du_niveau(niveau: int) -> list[str]:
    if niveau == 1:
        return VERBES_SIMPLES + ["être", "avoir"]
    if niveau == 2:
        return VERBES_SIMPLES + VERBES_CER_GER + C.DEUXIEME_GROUPE + IRREGULIERS_FACILES
    return VERBES_CER_GER + C.DEUXIEME_GROUPE + IRREGULIERS_FACILES + IRREGULIERS_AUTRES


def exercice_conjugaison(rng, verbe: str, temps: str, personne: int):
    g = C.groupe(verbe)
    groupe_texte = "du 1er groupe" if g == 1 else "du 2e groupe" if g == 2 else "irrégulier"
    tableau = C.table(verbe, temps)
    if temps == "imperatif":
        formes = C.imperatif(verbe)
        qui = ["tu", "nous", "vous"][personne]
        forme = formes[personne]
        return exercice("texte", f"Conjugue « {verbe} » à l'impératif présent, avec « {qui} ».", [forme],
                        [C.regle(verbe, temps), "Tableau : " + " ; ".join(formes) + "."],
                        f"« {verbe} » est un verbe {groupe_texte}. À l'impératif, on n'écrit pas le sujet.",
                        reponse_texte=f"{forme} !")
    feminin = None
    sujet = SUJETS[personne]
    if personne in (2, 5):
        feminin = rng.random() < 0.4
        sujet = ("elle" if personne == 2 else "elles") if feminin else sujet
    if temps in ("passe_compose", "plus_que_parfait"):
        formes = C.compose(verbe, temps, personne, feminin)
    else:
        formes = [C.simple(verbe, temps)[personne]]
    affiche = C.pronom(sujet, formes[0])
    acceptees = formes + [f"{affiche} {f}".replace("' ", "'") for f in formes]
    return exercice("texte", f"Conjugue « {verbe} » {article_temps(temps)} : {affiche} …", acceptees,
                    [C.regle(verbe, temps), "Tableau :"] + tableau
                    + [f"Réponse : {affiche} {formes[0]}".replace("' ", "'")
                       + (f" (ou : {', '.join(formes[1:])})" if len(formes) > 1 else "")],
                    f"« {verbe} » est un verbe {groupe_texte}. Quelle terminaison avec « {sujet} » ?",
                    reponse_texte=f"{affiche} {formes[0]}".replace("' ", "'"))


def conjuguer(rng, niveau, temps_possibles, personnes=range(6), verbes=None):
    temps = rng.choice(temps_possibles)
    verbe = rng.choice(verbes or verbes_du_niveau(niveau))
    if temps == "imperatif":
        while C.imperatif(verbe) is None:
            verbe = rng.choice(verbes_du_niveau(niveau))
        return exercice_conjugaison(rng, verbe, temps, rng.randint(0, 2))
    return exercice_conjugaison(rng, verbe, temps, rng.choice(list(personnes)))


def passe_compose(rng, niveau):
    """Niveau 1 : verbes avec « avoir » ; niveau 2 : participes irréguliers ; niveau 3 : avec « être »."""
    if niveau == 1:
        verbes = VERBES_AVOIR_SIMPLES + C.DEUXIEME_GROUPE
    elif niveau == 2:
        verbes = VERBES_AVOIR_SIMPLES + ["faire", "dire", "prendre", "voir", "mettre", "lire", "avoir", "être"]
    else:
        verbes = sorted(C.AUXILIAIRE_ETRE) + ["faire", "prendre", "voir", "pouvoir", "vouloir", "savoir"]
    return conjuguer(rng, niveau, ["passe_compose"], verbes=verbes)


# --- Accord sujet-verbe ----------------------------------------------------------------------

SUJETS_NOMS = [("Les enfants", 5, False), ("Mon frère", 2, False), ("Ma sœur", 2, True), ("Léa et moi", 3, None),
               ("Toi et ton ami", 4, None), ("Le chat", 2, False), ("Mes cousines", 5, True),
               ("Les oiseaux", 5, False), ("La maîtresse", 2, True), ("Papa et toi", 4, None),
               ("Mes amis et moi", 3, None), ("Les filles", 5, True)]
PRONOMS_REMPLACEMENT = {(2, False): "il", (2, True): "elle", (5, False): "ils", (5, True): "elles",
                        (3, None): "nous", (4, None): "vous"}


def accord_sujet_verbe(rng, niveau):
    sujet, personne, feminin = rng.choice(SUJETS_NOMS)
    verbe = rng.choice(verbes_du_niveau(niveau))
    forme = C.simple(verbe, "present")[personne]
    remplacant = PRONOMS_REMPLACEMENT[(personne, feminin)]
    return exercice("texte", f"Écris le verbe « {verbe} » au présent : {sujet} …", [forme, f"{sujet} {forme}"],
                    [f"Le sujet « {sujet} » peut être remplacé par « {remplacant} ».",
                     f"Avec « {remplacant} », « {verbe} » au présent s'écrit « {forme} ».",
                     "Le verbe s'accorde toujours avec son sujet."],
                    f"Par quel pronom peux-tu remplacer « {sujet} » ?", reponse_texte=f"{sujet} {forme}")


# --- Pluriel des noms et accord des adjectifs --------------------------------------------------

NOMS_PLURIEL = {
    1: [("ami", "amis", "un", "On ajoute un s."), ("fleur", "fleurs", "une", "On ajoute un s."),
        ("bateau", "bateaux", "un", "Les noms en -eau prennent un x."),
        ("oiseau", "oiseaux", "un", "Les noms en -eau prennent un x."),
        ("table", "tables", "une", "On ajoute un s."), ("gâteau", "gâteaux", "un", "Les noms en -eau prennent un x.")],
    2: [("cheval", "chevaux", "un", "Les noms en -al font -aux."), ("journal", "journaux", "un", "Les noms en -al font -aux."),
        ("jeu", "jeux", "un", "Les noms en -eu prennent un x."), ("feu", "feux", "un", "Les noms en -eu prennent un x."),
        ("souris", "souris", "une", "Un nom qui finit par s, x ou z ne change pas."),
        ("nez", "nez", "un", "Un nom qui finit par s, x ou z ne change pas."),
        ("prix", "prix", "un", "Un nom qui finit par s, x ou z ne change pas."),
        ("animal", "animaux", "un", "Les noms en -al font -aux.")],
    3: [("bijou", "bijoux", "un", "7 noms en -ou prennent un x : bijou, caillou, chou, genou, hibou, joujou, pou."),
        ("caillou", "cailloux", "un", "7 noms en -ou prennent un x : bijou, caillou, chou, genou, hibou, joujou, pou."),
        ("genou", "genoux", "un", "7 noms en -ou prennent un x : bijou, caillou, chou, genou, hibou, joujou, pou."),
        ("clou", "clous", "un", "Les autres noms en -ou prennent un s (sauf les 7 en -oux)."),
        ("trou", "trous", "un", "Les autres noms en -ou prennent un s (sauf les 7 en -oux)."),
        ("pneu", "pneus", "un", "Exception : pneu et bleu prennent un s."),
        ("bal", "bals", "un", "Exceptions en -al : bal, carnaval, festival, récital prennent un s."),
        ("festival", "festivals", "un", "Exceptions en -al : bal, carnaval, festival, récital prennent un s."),
        ("travail", "travaux", "un", "Quelques noms en -ail font -aux : travail, vitrail, corail, émail…"),
        ("détail", "détails", "un", "La plupart des noms en -ail prennent un s.")],
}

# masculin singulier, féminin singulier, masculin pluriel, féminin pluriel
ADJECTIFS_COULEUR = {"noir": ("noir", "noire", "noirs", "noires"), "vert": ("vert", "verte", "verts", "vertes"),
                     "bleu": ("bleu", "bleue", "bleus", "bleues"), "blanc": ("blanc", "blanche", "blancs", "blanches"),
                     "gris": ("gris", "grise", "gris", "grises"), "rouge": ("rouge", "rouge", "rouges", "rouges")}
ADJECTIFS_CARACTERE = {"heureux": ("heureux", "heureuse", "heureux", "heureuses"),
                       "sportif": ("sportif", "sportive", "sportifs", "sportives"),
                       "sérieux": ("sérieux", "sérieuse", "sérieux", "sérieuses"),
                       "joyeux": ("joyeux", "joyeuse", "joyeux", "joyeuses"),
                       "content": ("content", "contente", "contents", "contentes"),
                       "gentil": ("gentil", "gentille", "gentils", "gentilles"),
                       "français": ("français", "française", "français", "françaises")}
NOMS_OBJETS = [("voiture", "voitures", True), ("ballon", "ballons", False), ("robe", "robes", True),
               ("pull", "pulls", False), ("chemise", "chemises", True), ("vélo", "vélos", False),
               ("fleur", "fleurs", True), ("chat", "chats", False)]
NOMS_PERSONNES = [("fille", "filles", True), ("garçon", "garçons", False), ("voisine", "voisines", True),
                  ("voisin", "voisins", False), ("chanteuse", "chanteuses", True), ("joueur", "joueurs", False)]


def pluriel_nom(rng, niveau):
    choix = NOMS_PLURIEL[1] + (NOMS_PLURIEL[2] if niveau > 1 else []) + (NOMS_PLURIEL[3] if niveau > 2 else [])
    if niveau > 1:
        choix = [n for n in choix if n not in NOMS_PLURIEL[1]] + NOMS_PLURIEL[1][:2]
    sing, plur, det, regle = rng.choice(choix)
    return exercice("texte", f"Écris au pluriel : {det} {sing} → des …", [plur, f"des {plur}"],
                    [regle, f"{det} {sing} → des {plur}"],
                    "Regarde comment le nom se termine.", reponse_texte=f"des {plur}")


def accord_adjectif(rng, niveau):
    if rng.random() < 0.5:
        adjectifs, noms = ADJECTIFS_COULEUR, NOMS_OBJETS
    else:
        adjectifs, noms = ADJECTIFS_CARACTERE, NOMS_PERSONNES
    if niveau == 1:
        adjectifs = {k: v for k, v in adjectifs.items() if v[1] == k + "e" or v[1] == k}
    base = rng.choice(list(adjectifs))
    sing, plur, feminin = rng.choice(noms)
    pluriel = rng.random() < 0.5
    forme = adjectifs[base][(1 if feminin else 0) + (2 if pluriel else 0)]
    det = "des" if pluriel else ("une" if feminin else "un")
    nom = plur if pluriel else sing
    genre = "féminin" if feminin else "masculin"
    nombre = "pluriel" if pluriel else "singulier"
    return exercice("texte", f"Accorde l'adjectif « {base} » : {det} {nom} …", [forme, f"{det} {nom} {forme}"],
                    [f"« {nom} » est au {genre} {nombre}.",
                     f"L'adjectif s'accorde avec le nom : {base} → {forme}."],
                    "Le nom est-il masculin ou féminin ? Singulier ou pluriel ?",
                    reponse_texte=f"{det} {nom} {forme}")


# --- Participe passé ---------------------------------------------------------------------------

VERBES_OBJET = [("manger", "une pomme"), ("chanter", "une chanson"), ("regarder", "un film"),
                ("dessiner", "un chat"), ("ranger", "la chambre"), ("laver", "la voiture"),
                ("écouter", "la radio"), ("donner", "un cadeau"), ("trouver", "une solution"), ("porter", "un sac")]
AVANT_INFINITIF = ["Il va", "Elle veut", "Nous allons", "Tu dois", "J'aime"]
AVANT_PARTICIPE = ["Il a", "Elle avait", "Nous avons", "Tu as", "J'ai"]


def e_ou_er(rng, niveau):
    verbe, objet = rng.choice(VERBES_OBJET)
    pp = C.participe(verbe)
    if rng.random() < 0.5:
        debut, bonne, test, nature = rng.choice(AVANT_INFINITIF), verbe, "vendre", "un infinitif"
    else:
        debut, bonne, test, nature = rng.choice(AVANT_PARTICIPE), pp, "vendu", "un participe passé"
    options = [pp, verbe]
    rng.shuffle(options)
    return exercice("choix", f"Complète : {debut} ___ {objet}.", bonne, options=options,
                    explication=[f"Je remplace par « vendre » ou « vendu » : on dit « {debut} {test} ».",
                                 f"C'est {nature} : j'écris « {bonne} »."],
                    indice="Remplace le verbe par « vendre » ou « vendu » : lequel sonne juste ?")


SUJETS_GENRE = [("Léa", 2, True), ("Paul", 2, False), ("Les filles", 5, True), ("Mes frères", 5, False),
                ("Ma cousine et sa sœur", 5, True), ("Le train", 2, False), ("Les voitures", 5, True),
                ("Mon père et ma mère", 5, False)]


def accord_participe(rng, niveau, avec_avoir=False):
    sujet, personne, feminin = rng.choice(SUJETS_GENRE)
    if avec_avoir and rng.random() < 0.5:
        verbe, objet = rng.choice(VERBES_OBJET)
        aux = C.simple("avoir", "present")[personne]
        pp = C.participe(verbe)
        return exercice("texte", f"Écris le participe passé de « {verbe} » : {sujet} {aux} … {objet}.",
                        [pp, f"{aux} {pp}"],
                        ["Avec l'auxiliaire « avoir », le participe passé ne s'accorde pas avec le sujet.",
                         f"{sujet} {aux} {pp} {objet}."],
                        "Quel est l'auxiliaire : être ou avoir ?", reponse_texte=pp)
    verbe = rng.choice(sorted(C.AUXILIAIRE_ETRE))
    aux = C.simple("être", "present")[personne]
    pp = C.accords_participe(C.participe(verbe), personne, feminin)[0]
    genre = ("féminin" if feminin else "masculin") + (" pluriel" if personne == 5 else " singulier")
    return exercice("texte", f"Écris le participe passé de « {verbe} » : {sujet} {aux} …", [pp, f"{aux} {pp}"],
                    ["Avec l'auxiliaire « être », le participe passé s'accorde avec le sujet.",
                     f"« {sujet} » est {genre} : {C.participe(verbe)} → {pp}."],
                    "Avec « être », regarde le sujet : masculin ou féminin ? Singulier ou pluriel ?",
                    reponse_texte=pp)


# --- Questions des banques ----------------------------------------------------------------------

ARTICLES = {"nom": "un ", "verbe": "un ", "adjectif": "un ", "déterminant": "un ", "pronom": "un ",
            "adverbe": "un ", "préposition": "une ", "conjonction de coordination": "une ",
            "sujet": "le ", "COD": "le ", "COI": "le ", "complément circonstanciel": "un ",
            "attribut du sujet": "l'", "épithète": "", "complément du nom": "le "}


def nature_mot(rng, niveau, natures=B.NATURES_CM1):
    phrase, mot, nature = rng.choice([q for q in B.NATURE if q[2] in natures])
    return exercice("choix", f"Dans « {phrase} », quelle est la classe (nature) du mot « {mot} » ?", nature,
                    [B.ASTUCES_NATURE[nature], f"« {mot} » est {ARTICLES[nature]}{nature}."],
                    "Remplace le mot, déplace-le ou change le temps : comment se comporte-t-il ?",
                    options=list(natures))


def fonction_groupe(rng, niveau, fonctions=B.FONCTIONS_CM2):
    phrase, groupe_mots, fonction = rng.choice([q for q in B.FONCTION if q[2] in fonctions])
    return exercice("choix", f"Dans « {phrase} », quelle est la fonction de « {groupe_mots} » ?", fonction,
                    [B.ASTUCES_FONCTION[fonction], f"« {groupe_mots} » est {ARTICLES[fonction]}{fonction}."],
                    "Pose les questions : qui fait l'action ? quoi ? à qui ? où ? quand ?",
                    options=list(fonctions))


def homophone(rng, niveau, banque=B.HOMOPHONES_CM1):
    options, (astuce, phrases) = rng.choice(list(banque.items()))
    phrase, bonne = rng.choice(phrases)
    return exercice("choix", f"Complète : {phrase}", bonne,
                    [astuce, "La phrase : " + phrase.replace("___", bonne)],
                    astuce.split(".")[0] + ".", options=list(options))


def synonyme_antonyme(rng, niveau):
    sorte = rng.choice(["synonyme", "contraire"])
    mot, bonne, autres = rng.choice(B.SYNONYMES if sorte == "synonyme" else B.ANTONYMES)
    options = [bonne, *autres]
    rng.shuffle(options)
    definition = "un mot de sens proche" if sorte == "synonyme" else "un mot de sens opposé"
    return exercice("choix", f"Quel est le {sorte} de « {mot} » ?", bonne, options=options,
                    explication=[f"Un {sorte}, c'est {definition}.", f"Le {sorte} de « {mot} » est « {bonne} »."],
                    indice=f"Cherche {definition}.")


def prefixe(rng, niveau):
    mot, contraire = rng.choice(B.PREFIXES)
    debut = contraire[:len(contraire) - len(mot)]
    return exercice("texte", f"Forme le contraire de « {mot} » en ajoutant un préfixe.", [contraire],
                    [f"On ajoute le préfixe « {debut}- » : {mot} → {contraire}.",
                     "im- devant m, b, p ; il- devant l ; ir- devant r ; in- ailleurs ; dé- (ou dés-) pour beaucoup de verbes."],
                    "Pense à in-, im-, il-, ir-, dé-, mé-.")


def famille(rng, niveau):
    mot, membres, intrus = rng.choice(B.FAMILLES)
    options = rng.sample(membres, 2) + [intrus]
    rng.shuffle(options)
    return exercice("choix", f"Quel mot n'est pas de la famille de « {mot} » ?", intrus, options=options,
                    explication=[f"Les mots de la famille de « {mot} » partagent le même radical et un sens commun : "
                                 + ", ".join(membres) + ".",
                                 f"« {intrus} » se ressemble à l'oreille, mais n'a pas le même sens."],
                    indice="Cherche le mot qui n'a rien à voir avec le sens.")


def sens_propre_figure(rng, niveau):
    phrase, expression, sens = rng.choice(B.SENS)
    return exercice("choix", f"Dans « {phrase} », « {expression} » est employé au…", sens,
                    options=["sens propre", "sens figuré"],
                    explication=["Sens propre : le sens premier, concret. Sens figuré : une image.",
                                 f"Ici, « {expression} » est au {sens}."],
                    indice="Est-ce à prendre au pied de la lettre ?")


def niveau_langue(rng, niveau):
    phrase, registre = rng.choice(B.NIVEAUX_LANGUE)
    return exercice("choix", f"« {phrase} » : quel est le niveau de langue ?", registre,
                    options=["familier", "courant", "soutenu"],
                    explication=["Familier : entre copains. Courant : tous les jours, à l'école. Soutenu : très soigné, à l'écrit.",
                                 f"« {phrase} » est {registre}."],
                    indice="Le dirais-tu à un copain, à la maîtresse, ou dans un livre ancien ?")


def type_phrase(rng, niveau):
    phrase, sorte = rng.choice(B.TYPES_PHRASE)
    return exercice("choix", f"« {phrase} » : quel est le type de cette phrase ?", sorte,
                    options=["déclarative", "interrogative", "exclamative", "injonctive"],
                    explication=["Déclarative : donne une information. Interrogative : pose une question (?). "
                                 "Exclamative : exprime une émotion (!). Injonctive : donne un ordre ou un conseil.",
                                 f"« {phrase} » est {sorte}."],
                    indice="Regarde la ponctuation et ce que veut dire la phrase.")


def simple_complexe(rng, niveau):
    phrase, verbes = rng.choice(B.PHRASES_VERBES)
    sorte = "simple" if len(verbes) == 1 else "complexe"
    return exercice("choix", f"« {phrase} » : phrase simple ou complexe ?", sorte,
                    options=["simple", "complexe"],
                    explication=["Une phrase simple a un seul verbe conjugué ; une phrase complexe en a plusieurs.",
                                 f"Verbe{'s' if len(verbes) > 1 else ''} conjugué{'s' if len(verbes) > 1 else ''} : "
                                 + ", ".join(f"« {v} »" for v in verbes) + f" → phrase {sorte}."],
                    indice="Compte les verbes conjugués (un infinitif ne compte pas).")


def mot_present_une_fois(phrase: str, mot: str) -> bool:
    return len(re.findall(rf"(?<![\w']){re.escape(mot)}(?![\w'])", phrase)) == 1


# --- Catalogue ---------------------------------------------------------------------------------------

def _g(fonction, **options):
    def generateur(rng, niveau):
        return fonction(rng, niveau, **options)
    generateur.__name__ = fonction.__name__
    return generateur


GENERATEURS = {
    "fr-cm1-present": [_g(conjuguer, temps_possibles=["present"])] * 2 + [accord_sujet_verbe],
    "fr-cm1-temps": [_g(conjuguer, temps_possibles=["futur", "imparfait"])],
    "fr-cm1-passe-compose": [passe_compose],
    "fr-cm1-nature": [nature_mot],
    "fr-cm1-homophones": [homophone],
    "fr-cm1-accords": [pluriel_nom, accord_adjectif],
    "fr-cm2-temps-simples": [_g(conjuguer, temps_possibles=["present", "futur", "imparfait", "conditionnel",
                                                            "imperatif"]),
                             _g(conjuguer, temps_possibles=["passe_simple"], personnes=[2, 5])],
    "fr-cm2-temps-composes": [_g(conjuguer, temps_possibles=["passe_compose", "plus_que_parfait"])],
    "fr-cm2-fonctions": [fonction_groupe],
    "fr-cm2-homophones": [_g(homophone, banque=B.HOMOPHONES_CM2)],
    "fr-cm2-participe": [e_ou_er, accord_participe],
    "fr-cm2-vocabulaire": [synonyme_antonyme, prefixe, famille],
    "fr-6e-conjugaison": [_g(conjuguer, temps_possibles=["present", "futur", "imparfait", "passe_simple",
                                                         "conditionnel", "passe_compose", "plus_que_parfait",
                                                         "imperatif"])],
    "fr-6e-classes": [_g(nature_mot, natures=B.NATURES_6E)],
    "fr-6e-fonctions": [_g(fonction_groupe, fonctions=B.FONCTIONS_6E)],
    "fr-6e-phrase": [type_phrase, simple_complexe],
    "fr-6e-accords": [_g(accord_participe, avec_avoir=True), accord_adjectif, pluriel_nom],
    "fr-6e-vocabulaire": [sens_propre_figure, niveau_langue, prefixe],
}
