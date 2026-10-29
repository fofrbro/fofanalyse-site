"""
Leçons de mathématiques de CM2 (programme de l'école élémentaire, cycle 3).

Même format que les leçons de CM1 (lecons.py) : ce qu'il faut retenir, puis
un exemple résolu, écrits pour un enfant de 10 ans.
"""

CHAPITRES = [
    {
        "id": "cm2-nombres", "titre": "Les nombres jusqu'au milliard", "domaine": "Nombres",
        "resume": "Lire, écrire, décomposer, comparer et arrondir les grands nombres.",
        "retenir": [
            "Un grand nombre se lit par classes de 3 chiffres, en partant de la droite : "
            "la classe des millions, celle des mille, puis celle des unités.",
            "45 207 380 se lit « quarante-cinq millions deux cent sept mille trois cent quatre-vingts ».",
            "Chaque classe s'écrit avec 3 chiffres : 3 millions 45 mille s'écrit 3 045 000.",
            "1 milliard = 1 000 millions = 1 000 000 000.",
            "Pour comparer : le nombre qui a le plus de chiffres est le plus grand ; sinon on compare "
            "chiffre par chiffre, en partant de la gauche.",
            "Pour arrondir au million : on regarde le chiffre des centaines de mille (5 ou plus → au-dessus).",
        ],
        "exemple": {
            "question": "Arrondis 45 207 380 au million le plus proche.",
            "etapes": ["45 207 380 est entre 45 000 000 et 46 000 000.",
                       "Le chiffre des centaines de mille est 2 : moins de 5.",
                       "J'arrondis en dessous : 45 207 380 ≈ 45 000 000."],
        },
    },
    {
        "id": "cm2-fractions", "titre": "Fractions et fractions décimales", "domaine": "Nombres",
        "resume": "Fractions décimales, passage aux nombres à virgule, encadrer et additionner des fractions.",
        "retenir": [
            "Une fraction décimale a pour dénominateur 10, 100 ou 1 000 : 7/10 = 0,7 ; 35/100 = 0,35 ; "
            "8/1 000 = 0,008.",
            "Fractions à connaître : 1/2 = 0,5 ; 1/4 = 0,25 ; 3/4 = 0,75 ; 1/5 = 0,2.",
            "Pour encadrer 17/5 entre deux entiers : 15 < 17 < 20, donc 3 < 17/5 < 4 "
            "(car 15/5 = 3 et 20/5 = 4).",
            "Pour additionner deux fractions de même dénominateur, on additionne les numérateurs "
            "et on garde le dénominateur : 2/7 + 3/7 = 5/7.",
            "Les 3/4 de 20 : je cherche le quart (20 ÷ 4 = 5), puis j'en prends 3 (3 × 5 = 15).",
        ],
        "exemple": {
            "question": "Écris 3/4 sous forme de nombre décimal.",
            "etapes": ["Je cherche une fraction égale avec 100 en bas : 4 × 25 = 100.",
                       "3/4 = 75/100 (je multiplie aussi le haut par 25).",
                       "75/100 = 0,75."],
        },
    },
    {
        "id": "cm2-decimaux", "titre": "Les nombres décimaux", "domaine": "Nombres",
        "resume": "Dixièmes, centièmes, millièmes : comparer, arrondir, additionner et soustraire.",
        "retenir": [
            "Après la virgule : les dixièmes, puis les centièmes, puis les millièmes. "
            "Dans 3,047 : 0 dixième, 4 centièmes, 7 millièmes.",
            "Ajouter des zéros à la fin de la partie décimale ne change pas le nombre : 2,5 = 2,50 = 2,500.",
            "Pour comparer, j'écris autant de chiffres après la virgule : 2,5 et 2,45 → 2,50 et 2,45, "
            "donc 2,5 > 2,45.",
            "Pour arrondir à l'unité, je regarde le chiffre des dixièmes ; au dixième, celui des centièmes.",
            "Pour additionner ou soustraire, j'aligne les virgules et je complète avec des zéros.",
        ],
        "exemple": {
            "question": "12,5 − 3,47",
            "etapes": ["J'aligne les virgules et je complète : 12,50 − 3,47.",
                       "Je calcule comme avec des entiers : 1 250 − 347 = 903.",
                       "Je remets la virgule : 9,03."],
        },
    },
    {
        "id": "cm2-multiplication", "titre": "Multiplier", "domaine": "Calcul",
        "resume": "Multiplier par 10, 100, 1 000 ; multiplier un décimal par un entier ; la multiplication posée.",
        "retenir": [
            "Multiplier par 10, 100 ou 1 000, c'est déplacer la virgule de 1, 2 ou 3 rangs vers la droite : "
            "3,47 × 100 = 347.",
            "Diviser par 10, 100 ou 1 000, c'est la déplacer vers la gauche : 3,5 ÷ 100 = 0,035.",
            "Pour multiplier un décimal par un entier, je multiplie sans la virgule, puis je la remets : "
            "le résultat a autant de chiffres après la virgule que le décimal.",
            "Multiplication posée par un nombre à deux chiffres : une ligne pour les unités, une ligne "
            "pour les dizaines (avec un 0 au début), puis j'additionne.",
        ],
        "exemple": {
            "question": "2,35 × 4",
            "etapes": ["Sans la virgule : 235 × 4 = 940.",
                       "2,35 a 2 chiffres après la virgule : 9,40.",
                       "9,40 = 9,4."],
        },
    },
    {
        "id": "cm2-division", "titre": "La division", "domaine": "Calcul",
        "resume": "Diviser par un nombre à deux chiffres, et obtenir un quotient décimal.",
        "retenir": [
            "Pour diviser par un nombre à deux chiffres, j'estime : pour 23, je pense à 20. "
            "Si mon essai est trop grand, j'essaie le nombre en dessous.",
            "Le reste est toujours plus petit que le diviseur.",
            "Vérification : quotient × diviseur + reste = dividende.",
            "Pour continuer après les unités : j'écris une virgule au quotient, et j'abaisse un 0 "
            "à côté du reste.",
            "47 ÷ 4 = 11,75 : on peut continuer jusqu'à ce que le reste soit 0.",
        ],
        "exemple": {
            "question": "47 ÷ 4 avec un quotient décimal",
            "etapes": ["En 4, 1 fois 4, il reste 0. J'abaisse le 7 : en 7, 1 fois 4, il reste 3.",
                       "J'écris la virgule au quotient. J'abaisse un 0 : en 30, 7 fois 4 (28), il reste 2.",
                       "J'abaisse un 0 : en 20, 5 fois 4 (20), il reste 0.",
                       "47 ÷ 4 = 11,75."],
        },
    },
    {
        "id": "cm2-proportionnalite", "titre": "La proportionnalité", "domaine": "Proportionnalité",
        "resume": "Passer par l'unité, utiliser les multiples, calculer des pourcentages simples.",
        "retenir": [
            "Deux quantités sont proportionnelles quand, si on multiplie l'une par un nombre, "
            "l'autre est multipliée par le même nombre (2 fois plus de cahiers → 2 fois plus cher).",
            "Passer par l'unité : 3 cahiers coûtent 6 €, donc 1 cahier coûte 2 €, donc 5 cahiers coûtent 10 €.",
            "Utiliser les multiples : 4 cahiers coûtent 8 €, donc 12 cahiers (3 fois plus) coûtent 24 €.",
            "50 %, c'est la moitié ; 25 %, le quart ; 75 %, les trois quarts ; 10 %, le dixième.",
        ],
        "exemple": {
            "question": "Calcule 30 % de 80.",
            "etapes": ["10 % de 80, c'est le dixième : 80 ÷ 10 = 8.",
                       "30 %, c'est 3 fois 10 % : 3 × 8 = 24."],
        },
    },
    {
        "id": "cm2-mesures", "titre": "Mesures et durées", "domaine": "Grandeurs et mesures",
        "resume": "Convertir avec des nombres décimaux, calculer des durées.",
        "retenir": [
            "Longueurs : km, hm, dam, m, dm, cm, mm. Chaque unité vaut 10 fois la suivante.",
            "Masses : kg, hg, dag, g, dg, cg, mg. Contenances : L, dL, cL, mL.",
            "Vers une plus petite unité, je multiplie : 2,5 km = 2 500 m. "
            "Vers une plus grande, je divise : 350 cm = 3,5 m.",
            "Un tableau de conversion aide : un chiffre par colonne, la virgule dans la colonne de l'unité.",
            "Durées : 1 h = 60 min. Pour calculer une durée, j'avance jusqu'à l'heure pile, puis je compte le reste.",
        ],
        "exemple": {
            "question": "Un film va de 14 h 35 à 16 h 10. Combien de temps dure-t-il ?",
            "etapes": ["De 14 h 35 à 15 h : 25 min.", "De 15 h à 16 h 10 : 1 h 10 min.",
                       "En tout : 1 h 35 min."],
        },
    },
    {
        "id": "cm2-aires", "titre": "Périmètres et aires", "domaine": "Grandeurs et mesures",
        "resume": "Calculer l'aire d'un rectangle, d'un carré, d'un triangle rectangle et d'une figure composée.",
        "retenir": [
            "Le périmètre, c'est la longueur du tour. L'aire, c'est la mesure de la surface.",
            "L'aire se mesure en cm², m²… : 1 cm², c'est un carré de 1 cm de côté.",
            "Aire du rectangle = longueur × largeur. Aire du carré = côté × côté.",
            "Un triangle rectangle est la moitié d'un rectangle : aire = (côté × côté) ÷ 2, "
            "avec les deux côtés de l'angle droit.",
            "Pour une figure composée, je la découpe en rectangles, ou je calcule un grand rectangle "
            "et j'enlève ce qui manque.",
        ],
        "exemple": {
            "question": "Un rectangle mesure 7 cm sur 4 cm. Quelle est son aire ?",
            "etapes": ["Aire = longueur × largeur.", "7 × 4 = 28 cm²."],
        },
    },
    {
        "id": "cm2-problemes", "titre": "Résoudre des problèmes", "domaine": "Problèmes",
        "resume": "Problèmes à plusieurs étapes, avec des nombres décimaux et des durées.",
        "retenir": [
            "Je lis l'énoncé deux fois et je repère la question.",
            "Je cherche les étapes : souvent, un calcul intermédiaire avant le calcul final.",
            "Avec de l'argent, j'aligne les virgules : 7,50 € + 2,30 € = 9,80 €.",
            "Je vérifie que ma réponse est logique (une monnaie rendue est plus petite que le billet).",
            "Je termine par une phrase réponse avec l'unité.",
        ],
        "exemple": {
            "question": "Une baguette coûte 1,20 €. J'en achète 3 et je paie avec 5 €. Combien me rend-on ?",
            "etapes": ["Prix des 3 baguettes : 3 × 1,20 = 3,60 €.", "Monnaie : 5 − 3,60 = 1,40 €.",
                       "Phrase réponse : on me rend 1,40 €."],
        },
    },
]
