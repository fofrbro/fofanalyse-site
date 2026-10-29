"""
Module « Argent » : l'éducation financière, la même pour toutes les classes.

Comme en maths, les calculs d'argent (sommes, monnaie, budget, épargne,
comparaison de prix, soldes) sont tirés et résolus par le code, avec Decimal
pour les centimes. Les notions (besoins et envies, banque, d'où vient
l'argent) viennent de banques de questions vérifiées, au format de quiz.py.
"""

import math
from decimal import Decimal

from exercices import ecrire, ecrire_fixe, exercice, texte_decimal
from quiz import question_vers_exercice

# Pièces et billets en euros, en centimes
BILLETS = [5000, 2000, 1000, 500]
PIECES = [200, 100, 50, 20, 10, 5, 2, 1]


def euros(centimes: int) -> str:
    """1250 → « 12,50 € » ; 300 → « 3 € »."""
    valeur = Decimal(centimes) / 100
    return (ecrire_fixe(valeur, 2) if centimes % 100 else ecrire(centimes // 100)) + " €"


def nom_valeur(centimes: int, nombre: int = 1) -> str:
    """500, 2 → « billets de 5 € » ; 20, 1 → « pièce de 20 c »."""
    sorte = "billet" if centimes >= 500 else "pièce"
    valeur = f"{centimes // 100} €" if centimes >= 100 else f"{centimes} c"
    return f"{sorte}{'s' if nombre > 1 else ''} de {valeur}"


def reponse_euros(centimes: int) -> str:
    return texte_decimal(Decimal(centimes) / 100)


# --- 1. Pièces, billets et monnaie ------------------------------------------------------------------

def monnaie(rng, niveau):
    sorte = rng.choice(["somme", "rendre"] + (["moins"] if niveau >= 2 else []))
    if sorte == "somme":
        valeurs = [1000, 500, 200, 100] + ([50, 20, 10] if niveau >= 2 else []) + ([5, 2, 1] if niveau == 3 else [])
        choisies = sorted(rng.sample(valeurs, rng.randint(2, 3 if niveau == 1 else 4)), reverse=True)
        compte = {v: rng.randint(1, 4) for v in choisies}
        total = sum(v * n for v, n in compte.items())
        morceaux = [f"{n} {nom_valeur(v, n)}" for v, n in compte.items()]
        lignes = [f"{n} × {euros(v)} = {euros(n * v)}" for v, n in compte.items()]
        lignes.append(f"En tout : {' + '.join(euros(n * v) for v, n in compte.items())} = {euros(total)}")
        return exercice("nombre", f"Combien d'argent y a-t-il : {', '.join(morceaux)} ?", reponse_euros(total), lignes,
                        "Compte d'abord les billets, puis les pièces, du plus grand au plus petit.", unite="€",
                        reponse_texte=euros(total))
    if sorte == "rendre":
        if niveau == 1:
            prix = rng.randint(2, 18) * 100
        elif niveau == 2:
            prix = rng.randint(4, 38) * 50 + 50
        else:
            prix = rng.randint(150, 4800)
        billet = next(b for b in [500, 1000, 2000, 5000] if b > prix)
        rendu = billet - prix
        lignes = []
        if prix % 100:
            euro_suivant = (prix // 100 + 1) * 100
            lignes.append(f"De {euros(prix)} à {euros(euro_suivant)}, il faut {euros(euro_suivant - prix)}.")
            if euro_suivant < billet:
                lignes.append(f"De {euros(euro_suivant)} à {euros(billet)}, il faut {euros(billet - euro_suivant)}.")
            lignes.append(f"En tout, on rend {euros(rendu)}.")
        else:
            lignes.append(f"{euros(billet)} − {euros(prix)} = {euros(rendu)}.")
        lignes.append(f"Vérification : {euros(prix)} + {euros(rendu)} = {euros(billet)} ✓")
        return exercice("nombre", f"Tu achètes un objet à {euros(prix)} et tu paies avec un billet de {billet // 100} €. "
                        "Combien la marchande te rend-elle ?", reponse_euros(rendu), lignes,
                        "Avance comme la marchande : d'abord jusqu'à l'euro rond, puis jusqu'au billet.",
                        unite="€", reponse_texte=euros(rendu))
    montant = rng.randint(10, 190) * 10 if niveau == 2 else rng.randint(101, 1999)
    reste, utilises = montant, []
    for v in BILLETS + PIECES:
        n, reste = divmod(reste, v)
        if n:
            utilises.append((v, n))
    total = sum(n for _, n in utilises)
    lignes = [f"{n} {nom_valeur(v, n)}" for v, n in utilises]
    lignes.append(f"On prend toujours la plus grande pièce ou le plus grand billet possible : {total} en tout.")
    return exercice("nombre", f"Tu dois payer exactement {euros(montant)}. Combien de pièces et de billets, au minimum ?",
                    total, lignes, "Commence par le plus grand billet ou la plus grande pièce qui ne dépasse pas.")


# --- 2. Argent de poche et budget ---------------------------------------------------------------------

def budget(rng, niveau):
    sorte = rng.choice(["poche", "reste"] + (["epargne"] if niveau >= 2 else []) + (["famille"] if niveau == 3 else []))
    if sorte == "poche":
        par_semaine = rng.choice([2, 3, 4, 5, 6, 8, 10]) * 100 if niveau < 3 else rng.choice([250, 350, 450, 750])
        semaines = rng.randint(3, 8)
        total = par_semaine * semaines
        return exercice("nombre", f"Tu reçois {euros(par_semaine)} d'argent de poche par semaine. "
                        f"Combien auras-tu reçu en {semaines} semaines ?", reponse_euros(total),
                        [f"Chaque semaine : {euros(par_semaine)}.", f"{semaines} × {euros(par_semaine)} = {euros(total)}."],
                        "La même somme plusieurs fois : c'est une multiplication.", unite="€", reponse_texte=euros(total))
    if sorte == "reste":
        achats = [rng.randint(2, 9) * 100 + (rng.randint(1, 9) * 10 if niveau > 1 else 0) for _ in range(2)]
        depart = sum(achats) + rng.randint(1, 15) * 100
        reste = depart - sum(achats)
        objets = rng.sample(["un livre", "un goûter", "des autocollants", "un ballon", "des crayons", "une place de cinéma"], 2)
        return exercice("nombre", f"Tu as {euros(depart)}. Tu achètes {objets[0]} à {euros(achats[0])} et "
                        f"{objets[1]} à {euros(achats[1])}. Combien te reste-t-il ?", reponse_euros(reste),
                        [f"Dépenses : {euros(achats[0])} + {euros(achats[1])} = {euros(sum(achats))}.",
                         f"Il reste : {euros(depart)} − {euros(sum(achats))} = {euros(reste)}."],
                        "Additionne d'abord les dépenses, puis enlève-les.", unite="€", reponse_texte=euros(reste))
    if sorte == "epargne":
        par_semaine = rng.choice([2, 3, 4, 5, 6]) * 100
        prix = rng.randint(12, 60) * 100
        if prix % par_semaine == 0:
            prix += 100
        semaines = math.ceil(prix / par_semaine)
        objet = rng.choice(["un jeu", "un ballon de foot", "une montre", "un livre de dinosaures", "des rollers"])
        return exercice("nombre", f"Tu veux acheter {objet} à {euros(prix)}. Tu économises {euros(par_semaine)} par "
                        "semaine. Combien de semaines te faut-il, au minimum ?", semaines,
                        [f"En {semaines - 1} semaines : {semaines - 1} × {euros(par_semaine)} = "
                         f"{euros((semaines - 1) * par_semaine)} : pas assez.",
                         f"En {semaines} semaines : {semaines} × {euros(par_semaine)} = {euros(semaines * par_semaine)} : "
                         "c'est assez !", f"Il faut {semaines} semaines d'économies."],
                        "Combien de fois la somme de la semaine faut-il pour atteindre le prix ?", unite="semaines")
    revenu = rng.randint(18, 35) * 10000
    postes = {"le loyer": rng.randint(6, 10) * 10000, "les courses": rng.randint(30, 50) * 1000,
              "l'électricité et l'eau": rng.randint(8, 15) * 1000, "les transports": rng.randint(5, 15) * 1000}
    depenses = sum(postes.values())
    reste = revenu - depenses
    return exercice("nombre", f"Une famille gagne {euros(revenu)} par mois. Elle paie "
                    + ", ".join(f"{euros(v)} pour {k}" for k, v in postes.items())
                    + ". Combien lui reste-t-il pour le reste du mois ?", reponse_euros(reste),
                    [f"Dépenses : {' + '.join(euros(v) for v in postes.values())} = {euros(depenses)}.",
                     f"Reste : {euros(revenu)} − {euros(depenses)} = {euros(reste)}.",
                     "C'est le principe d'un budget : prévoir les dépenses selon ce que l'on gagne."],
                    "Additionne toutes les dépenses, puis enlève-les du revenu.", unite="€", reponse_texte=euros(reste))


# --- 3. Bien acheter --------------------------------------------------------------------------------------

def acheter(rng, niveau):
    sorte = rng.choice(["panier", "comparer"] + (["solde"] if niveau >= 2 else []))
    if sorte == "panier":
        n, prix, autre = rng.randint(2, 5), rng.randint(1, 4) * 100 + (50 if niveau > 1 else 0), rng.randint(3, 9) * 100
        total = n * prix + autre
        return exercice("nombre", f"Tu achètes {n} cahiers à {euros(prix)} chacun et une trousse à {euros(autre)}. "
                        "Combien paies-tu en tout ?", reponse_euros(total),
                        [f"Les cahiers : {n} × {euros(prix)} = {euros(n * prix)}.",
                         f"Avec la trousse : {euros(n * prix)} + {euros(autre)} = {euros(total)}."],
                        "Calcule d'abord le prix de tous les cahiers.", unite="€", reponse_texte=euros(total))
    if sorte == "solde":
        pourcent = rng.choice([10, 20, 25, 50]) if niveau == 2 else rng.choice([15, 20, 30, 40])
        prix = rng.randint(2, 12) * 2000
        remise = prix * pourcent // 100
        objet = rng.choice(["Un jeu vidéo", "Un vélo", "Une paire de baskets", "Un sac à dos"])
        return exercice("nombre", f"{objet} coûte {euros(prix)}. Il est soldé à −{pourcent} %. Quel est son nouveau prix ?",
                        reponse_euros(prix - remise),
                        [f"La remise : {pourcent} % de {euros(prix)} = {euros(prix)} × {pourcent} ÷ 100 = {euros(remise)}.",
                         f"Nouveau prix : {euros(prix)} − {euros(remise)} = {euros(prix - remise)}."],
                        "Calcule la remise, puis enlève-la du prix.", unite="€", reponse_texte=euros(prix - remise))
    if niveau == 3 and rng.random() < 0.5:
        prix_500 = rng.randint(10, 30) * 10
        prix_kg = prix_500 * 2 + rng.choice([-60, -40, -20, 20, 40])
        produit = rng.choice(["de pommes", "de riz", "de pâtes", "de cerises"])
        double = prix_500 * 2
        bonne = "le sachet de 1 kg" if prix_kg < double else "les 2 sachets de 500 g"
        return exercice("choix", f"Un sachet de 500 g {produit} coûte {euros(prix_500)} ; un sachet de 1 kg coûte "
                        f"{euros(prix_kg)}. Qu'est-ce qui revient le moins cher pour 1 kg ?", bonne,
                        [f"1 kg = 2 sachets de 500 g : 2 × {euros(prix_500)} = {euros(double)}.",
                         f"Le sachet de 1 kg : {euros(prix_kg)}.", f"Le moins cher pour 1 kg : {bonne}."],
                        "Compare le prix pour la même quantité : 1 kg.",
                        options=["le sachet de 1 kg", "les 2 sachets de 500 g"])
    lot = rng.choice([3, 4, 6])
    # produit, prix à l'unité possibles (en centimes) : des prix de magasin crédibles
    produit, prix_possibles = rng.choice([
        ("yaourts", [40, 50, 60, 70, 80]), ("cahiers", [150, 200, 250, 300, 350]),
        ("stylos", [80, 100, 120, 150, 200]), ("briques de jus", [50, 60, 80, 100, 120])])
    unite = rng.choice([p for p in prix_possibles if p % 50 == 0] if niveau == 1 else prix_possibles)
    seul = unite * lot
    ecart = rng.choice([10, 20, 30, 50]) if niveau > 1 else rng.choice([50, 100])
    prix_lot = seul + rng.choice([-1, 1]) * min(ecart, seul // 4 // 10 * 10 or 10)
    bonne = "le lot" if prix_lot < seul else "à l'unité"
    return exercice("choix", f"Des {produit} sont vendus {euros(unite)} l'unité, ou {euros(prix_lot)} le lot de {lot}. "
                    f"Pour {lot} {produit}, qu'est-ce qui est le moins cher ?", bonne,
                    [f"À l'unité : {lot} × {euros(unite)} = {euros(seul)}.", f"Le lot : {euros(prix_lot)}.",
                     f"Le moins cher : {bonne}. Un lot n'est pas toujours une bonne affaire : il faut calculer !"],
                    f"Calcule le prix de {lot} {produit} achetés un par un.", options=["le lot", "à l'unité"])


# --- 4 à 6. Les notions : questions vérifiées ------------------------------------------------------------

BESOINS = [
    ("Lequel de ces exemples est un besoin ?", "se nourrir", ["un jeu vidéo", "des bonbons"],
     "Un besoin est indispensable pour vivre ; une envie, non.", 1),
    ("Lequel de ces exemples est une envie ?", "un nouveau jouet", ["se soigner", "un manteau pour l'hiver"],
     "On peut vivre sans un nouveau jouet : c'est une envie.", 1),
    ("Qu'est-ce qu'épargner ?", "mettre de l'argent de côté pour plus tard", ["tout dépenser tout de suite", "emprunter de l'argent"],
     "L'épargne, ce sont les économies.", 1),
    ("Pourquoi épargner ?", "pour un projet ou pour un imprévu", ["pour ne jamais rien acheter", "parce que c'est obligatoire"],
     "Épargner permet d'acheter plus tard quelque chose de plus cher, ou de faire face à un imprévu.", 1),
    ("À quoi sert une tirelire ?", "à garder ses économies", ["à ranger ses jouets", "à payer au magasin"],
     "On y met l'argent qu'on économise.", 1),
    ("Quel est le but d'une publicité ?", "donner envie d'acheter", ["informer sans rien vendre", "raconter une histoire vraie"],
     "La publicité est faite pour vendre : on garde son esprit critique.", 2),
    ("Avant un achat important, que vaut-il mieux faire ?", "attendre un peu et comparer les prix",
     ["acheter tout de suite", "choisir le plus cher"], "Attendre permet de vérifier qu'on en a vraiment envie.", 2),
    ("Qu'est-ce qu'un budget ?", "prévoir ses dépenses selon l'argent qu'on a", ["un magasin", "une carte bancaire"],
     "Un budget aide à ne pas dépenser plus que ce qu'on a.", 2),
    ("Si tu dépenses plus que l'argent que tu as, que se passe-t-il ?", "tu n'as plus assez d'argent : il faut dépenser moins",
     ["tu gagnes de l'argent", "rien du tout"], "On ne peut pas dépenser l'argent qu'on n'a pas.", 2),
    ("Qu'est-ce qu'un achat impulsif ?", "un achat fait sur un coup de tête, sans réfléchir",
     ["un achat préparé à l'avance", "l'achat de nourriture"], "Les bonbons près des caisses sont là pour ça !", 3),
    ("Un produit d'une marque connue est-il toujours meilleur ?", "non, il faut comparer",
     ["oui, toujours", "oui, s'il passe à la télévision"], "Le prix d'une marque comprend souvent sa publicité.", 3),
    ("Dans un jeu en ligne « gratuit », les achats intégrés…", "coûtent de vrais euros",
     ["sont toujours gratuits", "sont payés par le jeu"], "Les pièces ou gemmes d'un jeu s'achètent avec de l'argent réel.", 3),
    ("Donner une partie de son argent à une association, c'est…", "de la solidarité",
     ["une dépense obligatoire", "un achat impulsif"], "Partager fait aussi partie d'une bonne gestion de son argent.", 3),
]

BANQUE = [
    ("Que sont les « espèces » ?", "les pièces et les billets", ["la carte bancaire", "les chèques"],
     "Payer en espèces, c'est payer avec des pièces et des billets.", 1),
    ("Quelle est la monnaie de la France ?", "l'euro", ["le franc", "le dollar"], "L'euro remplace le franc depuis 2002.", 1),
    ("Le code secret d'une carte bancaire…", "ne se donne à personne", ["se donne à ses amis", "s'écrit sur la carte"],
     "Avec la carte et le code, n'importe qui pourrait payer à ta place.", 1),
    ("À quoi sert une banque ?", "à garder l'argent et à faire des paiements", ["à vendre des jouets", "à soigner les gens"],
     "La banque garde l'argent sur des comptes.", 1),
    ("Qu'est-ce qu'un compte bancaire ?", "l'endroit où la banque enregistre ton argent", ["un magasin", "une tirelire en verre"],
     "On y dépose de l'argent et on en retire.", 1),
    ("Quelqu'un te demande ton code par message, en disant qu'il est ta banque. C'est…", "une arnaque : on ne répond pas",
     ["normal : il faut répondre vite", "un jeu"], "Une banque ne demande jamais un code par message ou par téléphone.", 2),
    ("Quand on paie avec une carte bancaire, l'argent…", "est retiré du compte", ["est gratuit", "est payé par le magasin"],
     "La carte est un moyen de payer avec l'argent du compte.", 2),
    ("À quoi sert un distributeur automatique de billets ?", "à retirer des espèces avec sa carte",
     ["à acheter des timbres", "à imprimer des billets"], "On tape son code secret en cachant le clavier.", 2),
    ("Qu'est-ce qu'un virement ?", "un transfert d'argent d'un compte à un autre", ["un billet", "une pièce"],
     "Le salaire arrive souvent par virement.", 2),
    ("Emprunter de l'argent, c'est…", "recevoir de l'argent qu'il faudra rendre", ["recevoir un cadeau", "gagner au loto"],
     "Ce qu'on emprunte doit être remboursé.", 3),
    ("Avant de payer quelque chose sur Internet, que faut-il faire ?", "demander à un adulte",
     ["donner le numéro de carte à tout le monde", "cliquer sur toutes les publicités"],
     "Un enfant ne paie jamais en ligne sans un adulte.", 3),
    ("Quelle institution fabrique les billets d'euro en France ?", "la Banque de France", ["la mairie", "La Poste"],
     "Elle les fabrique pour la zone euro, avec d'autres banques centrales.", 3),
    ("En quelle année les pièces et billets d'euro sont-ils arrivés en France ?", "2002", ["1992", "1789"],
     "Le 1er janvier 2002.", 3),
]

TRAVAIL = [
    ("Comment la plupart des adultes gagnent-ils de l'argent ?", "en travaillant", ["en le trouvant par terre", "la banque le donne"],
     "L'argent gagné en travaillant s'appelle le salaire.", 1),
    ("Qu'est-ce que le salaire ?", "l'argent reçu en échange de son travail", ["un cadeau d'anniversaire", "un impôt"],
     "Il est souvent versé chaque mois.", 1),
    ("Avant la monnaie, les gens échangeaient des objets. Comment s'appelle cet échange ?", "le troc",
     ["le commerce en ligne", "le prêt"], "Exemple : trois poules contre un sac de blé.", 1),
    ("À quoi peut servir l'argent de poche ?", "à apprendre à gérer son argent",
     ["à tout dépenser le premier jour", "à rien"], "On apprend à choisir, à attendre et à économiser.", 1),
    ("Un commerçant achète un objet 6 € et le revend 10 €. Combien gagne-t-il sur cet objet ?", "4 €", ["16 €", "6 €"],
     "10 − 6 = 4 € : c'est sa marge.", 2),
    ("Pourquoi un objet rare est-il souvent cher ?", "il y en a peu et beaucoup de gens le veulent",
     ["il est lourd", "il est vieux"], "Quand beaucoup de gens veulent quelque chose de rare, son prix monte.", 2),
    ("À quoi servent les impôts ?", "à financer les écoles, les hôpitaux, les routes…",
     ["à enrichir les commerçants", "à acheter des jouets aux enfants"], "Ce sont les services publics.", 2),
    ("Que veut dire « gagner sa vie » ?", "travailler pour gagner l'argent nécessaire pour vivre",
     ["gagner un jeu", "être en bonne santé"], "C'est une expression.", 2),
    ("Qu'est-ce qu'une personne au chômage ?", "une personne qui cherche un emploi",
     ["une personne en vacances", "une personne à la retraite"], "Elle peut recevoir une aide en attendant.", 2),
    ("Qu'est-ce que la TVA ?", "un impôt compris dans le prix de ce qu'on achète", ["une réduction", "un salaire"],
     "Taxe sur la valeur ajoutée : on la paie à chaque achat.", 3),
    ("Qu'est-ce qu'un entrepreneur ?", "quelqu'un qui crée et dirige une entreprise", ["un client", "un employé de banque"],
     "Il prend des risques pour créer une activité.", 3),
    ("Comment appelle-t-on la hausse des prix au fil du temps ?", "l'inflation", ["la réduction", "le troc"],
     "Avec l'inflation, la même somme permet d'acheter un peu moins.", 3),
    ("Que reçoit une personne à la retraite ?", "une pension", ["un salaire", "de l'argent de poche"],
     "Elle a arrêté de travailler et reçoit une pension de retraite.", 3),
]


def banque_de(questions):
    def generateur(rng, niveau):
        de_son_niveau = [q for q in questions if q[4] == niveau]
        pioche = de_son_niveau if rng.random() < 0.7 else questions
        return question_vers_exercice(rng.choice(pioche), False, rng)
    return generateur


CHAPITRES = [
    {"id": "arg-monnaie", "titre": "Pièces, billets et monnaie", "domaine": "Compter l'argent",
     "resume": "Compter une somme, rendre la monnaie, payer avec le moins de pièces possible.",
     "retenir": ["Billets : 5 €, 10 €, 20 €, 50 € (et plus). Pièces : 2 €, 1 €, puis 50, 20, 10, 5, 2 et 1 centimes.",
                 "1 € = 100 centimes. 2,50 € = 2 euros et 50 centimes.",
                 "Pour compter une somme, on commence par les billets, puis les pièces, du plus grand au plus petit.",
                 "Pour rendre la monnaie, on avance comme la marchande : jusqu'à l'euro rond, puis jusqu'au billet donné.",
                 "Pour payer avec le moins de pièces, on prend toujours la plus grande pièce ou le plus grand billet possible."],
     "exemple": {"question": "Tu paies 7,30 € avec un billet de 10 €. Combien te rend-on ?",
                 "etapes": ["De 7,30 € à 8 € : 0,70 €.", "De 8 € à 10 € : 2 €.", "En tout : 2,70 €."]}},
    {"id": "arg-budget", "titre": "Argent de poche et budget", "domaine": "Gérer son argent",
     "resume": "Calculer ce qui reste, économiser pour un projet, comprendre un budget.",
     "retenir": ["Un budget, c'est prévoir ses dépenses selon l'argent qu'on a.",
                 "Ce qui reste = l'argent qu'on a − les dépenses.",
                 "Pour un projet, on économise un peu chaque semaine : on calcule combien de semaines il faut.",
                 "Une famille aussi a un budget : salaire d'un côté, loyer, courses, factures de l'autre."],
     "exemple": {"question": "Tu économises 4 € par semaine pour un jeu à 30 €. Combien de semaines ?",
                 "etapes": ["7 semaines : 7 × 4 = 28 € : pas assez.", "8 semaines : 8 × 4 = 32 € : c'est assez.",
                            "Il faut 8 semaines."]}},
    {"id": "arg-acheter", "titre": "Bien acheter", "domaine": "Consommer",
     "resume": "Calculer un total, comparer deux offres, calculer un prix soldé.",
     "retenir": ["Pour comparer, on calcule le prix de la même quantité (le même nombre d'objets, ou 1 kg).",
                 "Un lot ou un grand paquet n'est pas toujours moins cher : il faut calculer.",
                 "Soldé à −20 % : on enlève 20 % du prix. 20 % de 40 € = 40 × 20 ÷ 100 = 8 €, donc 32 €.",
                 "Le moins cher n'est pas toujours le meilleur choix : on regarde aussi la qualité et si on en a vraiment besoin."],
     "exemple": {"question": "Yaourts : 0,60 € l'unité ou 3 € le lot de 4. Le moins cher pour 4 ?",
                 "etapes": ["À l'unité : 4 × 0,60 € = 2,40 €.", "Le lot : 3 €.", "À l'unité, c'est moins cher !"]}},
    {"id": "arg-besoins", "titre": "Besoins, envies et épargne", "domaine": "Gérer son argent",
     "resume": "Distinguer besoins et envies, épargner, résister à la publicité.",
     "retenir": ["Un besoin est indispensable (se nourrir, se loger, se soigner) ; une envie, non (un jouet, des bonbons).",
                 "Épargner, c'est mettre de l'argent de côté pour un projet ou un imprévu.",
                 "La publicité est faite pour donner envie d'acheter : on garde son esprit critique.",
                 "Avant un achat, on se demande : en ai-je besoin ? Puis-je attendre ? Est-ce moins cher ailleurs ?",
                 "Dans les jeux « gratuits », les achats intégrés coûtent de vrais euros."],
     "exemple": {"question": "Est-ce que des baskets de marque sont un besoin ?",
                 "etapes": ["Avoir des chaussures est un besoin.", "Une marque précise est une envie.",
                            "On peut choisir des chaussures moins chères qui font aussi bien l'affaire."]}},
    {"id": "arg-banque", "titre": "La banque et les moyens de payer", "domaine": "La banque",
     "resume": "Espèces, carte, virement ; le code secret ; se méfier des arnaques.",
     "retenir": ["On peut payer en espèces (pièces et billets), par carte bancaire ou par virement.",
                 "La banque garde l'argent sur un compte ; quand on paie par carte, l'argent est retiré du compte.",
                 "Le code secret ne se donne à personne. Une banque ne le demande jamais par message ou par téléphone.",
                 "Emprunter, c'est recevoir de l'argent qu'il faudra rendre.",
                 "Un enfant ne paie jamais sur Internet sans un adulte."],
     "exemple": {"question": "Tu reçois un message : « Votre carte est bloquée, donnez votre code. » Que fais-tu ?",
                 "etapes": ["Une banque ne demande jamais le code.", "C'est une arnaque : je ne réponds pas.",
                            "J'en parle à un adulte."]}},
    {"id": "arg-travail", "titre": "D'où vient l'argent ?", "domaine": "Comprendre l'économie",
     "resume": "Travail et salaire, troc et monnaie, prix, impôts.",
     "retenir": ["La plupart des adultes gagnent de l'argent en travaillant : c'est le salaire.",
                 "Avant la monnaie, on échangeait des objets : c'est le troc.",
                 "Un commerçant achète moins cher qu'il ne revend : la différence lui sert à payer ses frais et à vivre.",
                 "Les impôts (dont la TVA, comprise dans les prix) financent les écoles, les hôpitaux, les routes.",
                 "Quand quelque chose est rare et très demandé, son prix monte."],
     "exemple": {"question": "Pourquoi paie-t-on des impôts ?",
                 "etapes": ["L'école, l'hôpital, les routes coûtent de l'argent.",
                            "Chacun participe avec les impôts.", "Ce sont des services pour tous."]}},
]

GENERATEURS = {
    "arg-monnaie": [monnaie],
    "arg-budget": [budget],
    "arg-acheter": [acheter],
    "arg-besoins": [banque_de(BESOINS)],
    "arg-banque": [banque_de(BANQUE)],
    "arg-travail": [banque_de(TRAVAIL)],
}
