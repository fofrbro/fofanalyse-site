"""
Leçons de mathématiques de 6e (collège, fin du cycle 3).

Même format que les leçons de CM1 et de CM2 : ce qu'il faut retenir, puis
un exemple résolu, écrits pour un élève de 11 ans.
"""

CHAPITRES = [
    {
        "id": "6e-decimaux", "titre": "Nombres décimaux", "domaine": "Nombres",
        "resume": "Fractions décimales, encadrer, ranger, multiplier par 10, 100 ou 0,1.",
        "retenir": [
            "Un nombre décimal peut s'écrire avec une fraction décimale : 3,47 = 347/100.",
            "Encadrer 7,356 au dixième : 7,3 < 7,356 < 7,4.",
            "Pour ranger des décimaux, j'écris autant de chiffres après la virgule, puis je compare "
            "rang par rang, de gauche à droite.",
            "× 10, × 100, × 1 000 : la virgule se déplace vers la droite. ÷ 10, ÷ 100 : vers la gauche.",
            "Multiplier par 0,1, c'est diviser par 10 ; multiplier par 0,01, c'est diviser par 100.",
        ],
        "exemple": {
            "question": "Range dans l'ordre croissant : 4,7 ; 4,65 ; 4,07.",
            "etapes": ["J'écris 2 chiffres après la virgule : 4,70 ; 4,65 ; 4,07.",
                       "Je compare les dixièmes : 0 < 6 < 7.",
                       "4,07 < 4,65 < 4,7."],
        },
    },
    {
        "id": "6e-operations", "titre": "Calculer avec des décimaux", "domaine": "Calcul",
        "resume": "Multiplier deux décimaux, diviser un décimal par un entier, l'ordre des calculs.",
        "retenir": [
            "Pour multiplier deux décimaux, je multiplie sans les virgules. Le résultat a autant de chiffres "
            "après la virgule que les deux nombres ensemble : 2,3 × 1,5 = 3,45.",
            "Pour diviser un décimal par un entier, je pose la division et j'écris la virgule au quotient "
            "quand j'abaisse le premier chiffre après la virgule.",
            "Dans un calcul sans parenthèses, la multiplication passe avant l'addition : 3 + 4 × 2 = 3 + 8 = 11.",
            "Les parenthèses passent en premier : (3 + 4) × 2 = 7 × 2 = 14.",
        ],
        "exemple": {
            "question": "2,3 × 1,5",
            "etapes": ["Sans les virgules : 23 × 15 = 345.",
                       "1 chiffre après la virgule + 1 chiffre = 2 chiffres.",
                       "2,3 × 1,5 = 3,45."],
        },
    },
    {
        "id": "6e-divisibilite", "titre": "Multiples, diviseurs, division euclidienne", "domaine": "Nombres",
        "resume": "Critères de divisibilité par 2, 3, 4, 5, 9 et 10 ; division euclidienne.",
        "retenir": [
            "24 est un multiple de 6 (24 = 6 × 4) : 6 est un diviseur de 24, et 24 est divisible par 6.",
            "Divisible par 2 : le chiffre des unités est pair. Par 5 : il est 0 ou 5. Par 10 : il est 0.",
            "Divisible par 3 : la somme des chiffres est dans la table de 3. Par 9 : dans la table de 9.",
            "Divisible par 4 : le nombre formé par les deux derniers chiffres est dans la table de 4.",
            "Division euclidienne : dividende = diviseur × quotient + reste, avec reste < diviseur.",
        ],
        "exemple": {
            "question": "4 572 est-il divisible par 9 ?",
            "etapes": ["Somme des chiffres : 4 + 5 + 7 + 2 = 18.",
                       "18 est dans la table de 9 (9 × 2).",
                       "Donc 4 572 est divisible par 9."],
        },
    },
    {
        "id": "6e-fractions", "titre": "Les fractions", "domaine": "Nombres",
        "resume": "Fraction-quotient, fractions égales, simplifier, additionner.",
        "retenir": [
            "La fraction a/b est le nombre qui, multiplié par b, donne a : 7 × 3/7 = 3. C'est aussi a ÷ b.",
            "On obtient une fraction égale en multipliant (ou en divisant) le numérateur et le dénominateur "
            "par le même nombre : 3/4 = 15/20.",
            "Simplifier, c'est diviser le haut et le bas par un même nombre : 18/24 = 3/4 (÷ 6).",
            "Pour additionner, il faut le même dénominateur : 1/4 + 3/8 = 2/8 + 3/8 = 5/8.",
            "Les 3/5 de 40 : 40 ÷ 5 = 8, puis 3 × 8 = 24.",
        ],
        "exemple": {
            "question": "Simplifie 18/24 au maximum.",
            "etapes": ["18 et 24 sont dans la table de 6 : 18 = 6 × 3 et 24 = 6 × 4.",
                       "Je divise le haut et le bas par 6 : 18/24 = 3/4.",
                       "3 et 4 n'ont plus de diviseur commun : c'est fini."],
        },
    },
    {
        "id": "6e-proportionnalite", "titre": "Proportionnalité et pourcentages", "domaine": "Proportionnalité",
        "resume": "Quatrième proportionnelle, appliquer un pourcentage, échelles.",
        "retenir": [
            "Situation de proportionnalité : je peux passer par l'unité, utiliser un coefficient, "
            "ou additionner deux colonnes d'un tableau.",
            "Appliquer un pourcentage : 15 % de 60, c'est 60 × 15 ÷ 100 = 9.",
            "Prix soldé : je calcule la réduction, puis je l'enlève du prix de départ.",
            "Échelle 1/100 : 1 cm sur le plan représente 100 cm (1 m) en vrai.",
        ],
        "exemple": {
            "question": "Un pull à 40 € est soldé à 25 %. Quel est son nouveau prix ?",
            "etapes": ["Réduction : 25 % de 40 = 40 × 25 ÷ 100 = 10 €.",
                       "Nouveau prix : 40 − 10 = 30 €."],
        },
    },
    {
        "id": "6e-aires-volumes", "titre": "Cercle, aires et volumes", "domaine": "Grandeurs et mesures",
        "resume": "Périmètre du cercle, aire du triangle et du disque, volume du pavé droit.",
        "retenir": [
            "Le diamètre d'un cercle mesure 2 rayons. Périmètre du cercle = diamètre × π, avec π ≈ 3,14.",
            "Aire du triangle = base × hauteur ÷ 2. Aire du disque = rayon × rayon × π.",
            "Pour les aires, chaque unité vaut 100 fois la suivante : 1 m² = 100 dm² = 10 000 cm².",
            "Volume du pavé droit = longueur × largeur × hauteur, en cm³ ou m³.",
            "1 L = 1 dm³ = 1 000 cm³.",
        ],
        "exemple": {
            "question": "Un cercle a un rayon de 5 cm. Calcule son périmètre (π ≈ 3,14).",
            "etapes": ["Diamètre : 5 × 2 = 10 cm.", "Périmètre : 10 × 3,14 = 31,4 cm."],
        },
    },
    {
        "id": "6e-angles", "titre": "Les angles", "domaine": "Espace et géométrie",
        "resume": "Reconnaître un angle aigu, droit, obtus ou plat ; calculer un angle manquant.",
        "retenir": [
            "Un angle se mesure en degrés (°) avec un rapporteur.",
            "Angle aigu : moins de 90°. Angle droit : 90°. Angle obtus : entre 90° et 180°. Angle plat : 180°.",
            "Quand un angle droit est partagé en deux, les deux angles font 90° ensemble.",
            "Quand un angle plat est partagé, les angles font 180° ensemble.",
        ],
        "exemple": {
            "question": "Un angle droit est partagé en deux angles. L'un mesure 35°. Combien mesure l'autre ?",
            "etapes": ["Un angle droit mesure 90°.", "90 − 35 = 55°."],
        },
    },
    {
        "id": "6e-problemes", "titre": "Résoudre des problèmes", "domaine": "Problèmes",
        "resume": "Problèmes à étapes avec des décimaux : choisir les informations utiles.",
        "retenir": [
            "Je lis l'énoncé, je repère la question, puis les informations utiles. "
            "Attention : certaines informations ne servent à rien !",
            "Je cherche les étapes et j'écris chaque calcul avec une phrase.",
            "Partager équitablement → division ; plusieurs fois la même quantité → multiplication.",
            "Je vérifie que l'ordre de grandeur est logique, puis j'écris une phrase réponse avec l'unité.",
        ],
        "exemple": {
            "question": "4 amis partagent une addition de 38,40 €. Combien paie chacun ?",
            "etapes": ["Partager en 4 parts égales → division.", "38,40 ÷ 4 = 9,60 €.",
                       "Phrase réponse : chacun paie 9,60 €."],
        },
    },
]
