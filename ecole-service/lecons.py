"""
Leçons de mathématiques, classe par classe : CM1 ici, CM2 et 6e dans
lecons_cm2.py et lecons_6e.py.

Chaque leçon est courte et écrite pour un enfant de 9 ans : ce qu'il faut
retenir, puis un exemple résolu. Elle sert deux fois : elle s'affiche sur
la page, et elle est donnée au tuteur IA comme référence, pour qu'il
explique avec les mêmes mots et la même méthode que la leçon.

Pour une nouvelle classe : un fichier lecons_xxx.py, ses générateurs
d'exercices, et une ligne dans CLASSES ci-dessous et dans catalogue.py.
"""

import lecons_6e
import lecons_cm2

CHAPITRES_CM1 = [
    {
        "id": "nombres", "titre": "Les grands nombres", "domaine": "Nombres",
        "resume": "Lire, décomposer, comparer et arrondir les nombres jusqu'au million.",
        "retenir": [
            "Un nombre se lit par classes de 3 chiffres : la classe des mille, puis celle des unités. "
            "36 408 se lit « trente-six mille quatre cent huit ».",
            "Chaque chiffre a une valeur selon sa place : unités, dizaines, centaines, milliers, "
            "dizaines de mille, centaines de mille.",
            "Pour comparer deux nombres : celui qui a le plus de chiffres est le plus grand. "
            "S'ils ont autant de chiffres, on compare chiffre par chiffre, en partant de la gauche.",
            "Pour arrondir à la centaine : on regarde le chiffre des dizaines. "
            "5 ou plus → on arrondit au-dessus ; moins de 5 → en dessous.",
            "« Le chiffre des centaines » de 4 568, c'est 5. « Le nombre de centaines », c'est 45.",
        ],
        "exemple": {
            "question": "Décompose 52 070.",
            "etapes": ["5 dizaines de mille = 50 000", "2 milliers = 2 000", "0 centaine",
                       "7 dizaines = 70", "0 unité", "50 000 + 2 000 + 70 = 52 070"],
        },
    },
    {
        "id": "addsous", "titre": "Addition et soustraction posées", "domaine": "Calcul",
        "resume": "Poser une addition et une soustraction avec des retenues.",
        "retenir": [
            "On aligne les chiffres en colonnes : unités sous unités, dizaines sous dizaines…",
            "On commence toujours par la colonne des unités, à droite.",
            "Addition : si une colonne fait 10 ou plus, on écrit le chiffre des unités et on retient 1 "
            "en haut de la colonne suivante.",
            "Soustraction : si le chiffre du haut est trop petit, on lui ajoute 10, et on ajoute "
            "la retenue 1 au chiffre du bas de la colonne suivante.",
            "Pour vérifier une soustraction, on additionne le résultat et le nombre enlevé : "
            "on doit retrouver le premier nombre.",
        ],
        "exemple": {
            "question": "8 042 − 3 657",
            "etapes": ["Unités : 2 − 7, impossible → 12 − 7 = 5, je retiens 1.",
                       "Dizaines : 4 − (5 + 1), impossible → 14 − 6 = 8, je retiens 1.",
                       "Centaines : 0 − (6 + 1), impossible → 10 − 7 = 3, je retiens 1.",
                       "Milliers : 8 − (3 + 1) = 4.",
                       "Résultat : 4 385. Vérification : 4 385 + 3 657 = 8 042 ✓"],
        },
    },
    {
        "id": "tables", "titre": "Tables et calcul mental", "domaine": "Calcul",
        "resume": "Connaître ses tables, multiplier par 10 et 100, calculer vite dans sa tête.",
        "retenir": [
            "Les tables de multiplication de 2 à 9 doivent se réciter sans hésiter.",
            "On peut changer l'ordre : 7 × 8 = 8 × 7.",
            "Astuce : si tu connais 7 × 5 = 35, alors 7 × 6 = 35 + 7 = 42.",
            "Multiplier par 10, c'est écrire un 0 à la fin : 24 × 10 = 240. Par 100 : deux 0.",
            "La division est l'inverse de la multiplication : 6 × 8 = 48, donc 48 ÷ 6 = 8.",
            "Pour calculer un complément à 100, on avance par bonds : de 37 à 40 (3), puis de 40 à 100 (60) : 63.",
        ],
        "exemple": {
            "question": "8 × 7",
            "etapes": ["8 × 5 = 40", "8 × 2 = 16", "40 + 16 = 56, donc 8 × 7 = 56."],
        },
    },
    {
        "id": "multiplication", "titre": "La multiplication posée", "domaine": "Calcul",
        "resume": "Multiplier par un nombre à un chiffre, puis à deux chiffres.",
        "retenir": [
            "On multiplie chaque chiffre du haut par le chiffre du bas, en commençant par les unités.",
            "On ajoute la retenue après avoir multiplié, jamais avant.",
            "Pour multiplier par un nombre à deux chiffres, on fait deux lignes : "
            "une pour les unités, une pour les dizaines.",
            "Sur la deuxième ligne, on écrit d'abord un 0 dans la colonne des unités, "
            "car on multiplie par des dizaines.",
            "On additionne les deux lignes pour trouver le résultat.",
        ],
        "exemple": {
            "question": "47 × 23",
            "etapes": ["Ligne 1 : 47 × 3 = 141",
                       "Ligne 2 : 47 × 20 → j'écris un 0, puis 47 × 2 = 94 → 940",
                       "J'additionne : 141 + 940 = 1 081"],
        },
    },
    {
        "id": "division", "titre": "La division", "domaine": "Calcul",
        "resume": "Partager en parts égales et poser une division avec un diviseur à un chiffre.",
        "retenir": [
            "Diviser, c'est partager en parts égales ou chercher combien de fois un nombre est contenu dans un autre.",
            "Dans 17 ÷ 5 : 17 est le dividende, 5 le diviseur, 3 le quotient et 2 le reste.",
            "Le reste est toujours plus petit que le diviseur.",
            "On commence par la gauche. À chaque étape : « combien de fois ? », on soustrait, "
            "puis on abaisse le chiffre suivant.",
            "Vérification : quotient × diviseur + reste = dividende.",
        ],
        "exemple": {
            "question": "Pose la division 978 ÷ 4.",
            "etapes": ["En 9, combien de fois 4 ? 2 fois (2 × 4 = 8), il reste 1. J'abaisse le 7 : cela fait 17.",
                       "En 17, combien de fois 4 ? 4 fois (4 × 4 = 16), il reste 1. J'abaisse le 8 : cela fait 18.",
                       "En 18, combien de fois 4 ? 4 fois (4 × 4 = 16), il reste 2.",
                       "Quotient : 244, reste : 2. Vérification : 244 × 4 + 2 = 978 ✓"],
        },
    },
    {
        "id": "fractions", "titre": "Les fractions", "domaine": "Nombres",
        "resume": "Comprendre, comparer et utiliser les fractions simples.",
        "retenir": [
            "Dans 3/4 : le 4 (dénominateur) dit en combien de parts égales on coupe l'unité ; "
            "le 3 (numérateur) dit combien de parts on prend.",
            "1/2 se lit « un demi », 1/3 « un tiers », 1/4 « un quart », 1/10 « un dixième ».",
            "Même dénominateur : la plus grande fraction est celle qui a le plus grand numérateur (3/5 > 2/5).",
            "Numérateur 1 : plus on coupe en beaucoup de parts, plus la part est petite (1/3 > 1/8).",
            "Une fraction est égale à 1 quand le numérateur et le dénominateur sont égaux (4/4 = 1).",
            "Les 3/4 de 12 : je cherche le quart (12 ÷ 4 = 3), puis j'en prends 3 (3 × 3 = 9).",
        ],
        "exemple": {
            "question": "Les 2/3 de 18",
            "etapes": ["Le tiers de 18 : 18 ÷ 3 = 6.", "Les 2/3 : 2 × 6 = 12."],
        },
    },
    {
        "id": "decimaux", "titre": "Les nombres décimaux", "domaine": "Nombres",
        "resume": "Dixièmes et centièmes, comparer et additionner des nombres à virgule.",
        "retenir": [
            "La virgule sépare la partie entière de la partie décimale : dans 4,37, la partie entière est 4.",
            "Juste après la virgule : les dixièmes (1/10). Ensuite : les centièmes (1/100).",
            "4,37 = 4 unités, 3 dixièmes et 7 centièmes.",
            "Pour comparer : d'abord la partie entière, puis les dixièmes, puis les centièmes. "
            "Attention : 2,5 est plus grand que 2,45, car 5 dixièmes > 4 dixièmes.",
            "Pour additionner ou soustraire, on aligne les virgules les unes sous les autres.",
        ],
        "exemple": {
            "question": "Range 2,5 et 2,45.",
            "etapes": ["Parties entières : 2 et 2, pareilles.",
                       "Dixièmes : 5 et 4. 5 > 4.",
                       "Donc 2,45 < 2,5, même si 2,45 a plus de chiffres."],
        },
    },
    {
        "id": "mesures", "titre": "Les mesures", "domaine": "Grandeurs et mesures",
        "resume": "Longueurs, masses, contenances, durées et monnaie : changer d'unité.",
        "retenir": [
            "Longueurs : 1 km = 1 000 m ; 1 m = 100 cm ; 1 cm = 10 mm.",
            "Masses : 1 kg = 1 000 g.",
            "Contenances : 1 L = 100 cL = 1 000 mL.",
            "Durées : 1 h = 60 min ; 1 min = 60 s. Attention, les heures ne comptent pas par 100 !",
            "Monnaie : 1 € = 100 centimes.",
            "Pour passer d'une grande unité à une petite, on multiplie. Pour l'inverse, on divise.",
        ],
        "exemple": {
            "question": "2 h 30 min = ? min",
            "etapes": ["1 h = 60 min, donc 2 h = 120 min.", "120 + 30 = 150 min."],
        },
    },
    {
        "id": "perimetre", "titre": "Le périmètre", "domaine": "Grandeurs et mesures",
        "resume": "Calculer le tour d'un polygone, d'un rectangle et d'un carré.",
        "retenir": [
            "Le périmètre est la longueur du tour d'une figure.",
            "Polygone : on additionne la longueur de tous les côtés.",
            "Rectangle : 2 longueurs + 2 largeurs, ou (longueur + largeur) × 2.",
            "Carré : 4 côtés égaux, donc côté × 4.",
            "Tous les côtés doivent être dans la même unité avant d'additionner.",
        ],
        "exemple": {
            "question": "Un rectangle mesure 12 m sur 8 m. Quel est son périmètre ?",
            "etapes": ["12 + 8 + 12 + 8 = 40 m", "Ou : (12 + 8) × 2 = 40 m"],
        },
    },
    {
        "id": "problemes", "titre": "Résoudre des problèmes", "domaine": "Problèmes",
        "resume": "Lire un énoncé, choisir les opérations, rédiger la réponse.",
        "retenir": [
            "1. Je lis l'énoncé deux fois. 2. Je repère la question. 3. Je cherche les informations utiles.",
            "Gagner, ajouter, en tout → addition. Perdre, enlever, reste → soustraction.",
            "Plusieurs fois la même quantité → multiplication. Partager en parts égales → division.",
            "Un problème peut demander deux étapes : je fais un calcul intermédiaire avant le calcul final.",
            "Je fais un dessin ou un schéma si je suis bloqué.",
            "Je termine par une phrase réponse, avec l'unité : « Il reste 54 billes. »",
        ],
        "exemple": {
            "question": "Un paquet coûte 3 €. Papa en achète 6 et paie avec 20 €. Combien lui rend-on ?",
            "etapes": ["Prix des 6 paquets : 6 × 3 = 18 €.", "Monnaie : 20 − 18 = 2 €.",
                       "Phrase réponse : on rend 2 € à Papa."],
        },
    },
]

# Les classes dans l'ordre de la scolarité, avec l'âge habituel (pour le tuteur).
CLASSES = {
    "CM1": {"age": 9, "chapitres": CHAPITRES_CM1},
    "CM2": {"age": 10, "chapitres": lecons_cm2.CHAPITRES},
    "6e": {"age": 11, "chapitres": lecons_6e.CHAPITRES},
}

for _classe, _infos in CLASSES.items():
    for _chapitre in _infos["chapitres"]:
        _chapitre["classe"] = _classe

CHAPITRES = [c for infos in CLASSES.values() for c in infos["chapitres"]]
PAR_ID = {c["id"]: c for c in CHAPITRES}


def chapitres_jusqua(classe: str) -> list[dict]:
    """Les chapitres de la classe, précédés de ceux des classes d'avant (pour réviser)."""
    noms = list(CLASSES)
    return [c for nom in noms[:noms.index(classe) + 1] for c in CLASSES[nom]["chapitres"]]


def lecon_en_texte(chapitre_id: str) -> str:
    """La leçon en texte simple, pour la donner au tuteur."""
    c = PAR_ID[chapitre_id]
    lignes = [f"Leçon : {c['titre']} ({c['resume']})", "À retenir :"]
    lignes += [f"- {r}" for r in c["retenir"]]
    lignes += [f"Exemple : {c['exemple']['question']}"] + [f"  {e}" for e in c["exemple"]["etapes"]]
    return "\n".join(lignes)
