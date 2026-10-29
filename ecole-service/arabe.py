"""
Rubrique « Arabe » : l'alphabet, les lettres attachées, les voyelles, les
premiers mots et les premières phrases. Elle ne dépend pas de la classe.

Comme ailleurs, le code construit les questions à partir de données
vérifiées : la table des 28 lettres (nom, son, points, liaison) et des
listes de mots et de phrases vocalisés, avec leur transcription. Les
lettres attachées sont dessinées avec le trait d'union arabe (tatwîl « ـ »),
que le navigateur relie à la lettre.

Transcription utilisée pour un enfant francophone : H (h profond), S, D, T, Z
(lettres emphatiques, en majuscule), ' (le 'ayn), â, î, oû (voyelles longues).
"""

from exercices import exercice

FATHA, KASRA, DAMMA, SOUKOUN = "َ", "ِ", "ُ", "ْ"
TATWIL = "ـ"

# lettre, nom, son (libellé court, sa transcription est le début), son (explication), points, position des points
LETTRES = [
    ("ا", "alif", "â", "a long (elle sert surtout de voyelle longue)", 0, None),
    ("ب", "ba", "b", "b", 1, "dessous"),
    ("ت", "ta", "t", "t", 2, "dessus"),
    ("ث", "tha", "th", "th, comme « think » en anglais", 3, "dessus"),
    ("ج", "jim", "dj", "dj", 1, "dessous"),
    ("ح", "Ha", "H (h profond)", "h profond, soufflé du fond de la gorge", 0, None),
    ("خ", "kha", "kh", "kh, comme la jota espagnole", 1, "dessus"),
    ("د", "dal", "d", "d", 0, None),
    ("ذ", "dhal", "dh", "dh, comme « this » en anglais", 1, "dessus"),
    ("ر", "ra", "r", "r roulé", 0, None),
    ("ز", "zay", "z", "z", 1, "dessus"),
    ("س", "sin", "s", "s", 0, None),
    ("ش", "chin", "ch", "ch", 3, "dessus"),
    ("ص", "Sad", "S (s emphatique)", "s emphatique (prononcé avec la langue plus en arrière)", 0, None),
    ("ض", "Dad", "D (d emphatique)", "d emphatique", 1, "dessus"),
    ("ط", "Ta", "T (t emphatique)", "t emphatique", 0, None),
    ("ظ", "Za", "Z (dh emphatique)", "dh emphatique", 1, "dessus"),
    ("ع", "'ayn", "' (son de gorge)", "son du fond de la gorge, sans équivalent en français", 0, None),
    ("غ", "ghayn", "gh", "gh, comme un r grasseyé", 1, "dessus"),
    ("ف", "fa", "f", "f", 1, "dessus"),
    ("ق", "qaf", "q", "k prononcé du fond de la gorge", 2, "dessus"),
    ("ك", "kaf", "k", "k", 0, None),
    ("ل", "lam", "l", "l", 0, None),
    ("م", "mim", "m", "m", 0, None),
    ("ن", "noun", "n", "n", 1, "dessus"),
    ("ه", "ha", "h", "h léger, comme « hello » en anglais", 0, None),
    ("و", "waw", "w", "w (ou voyelle longue « oû »)", 0, None),
    ("ي", "ya", "y", "y (ou voyelle longue « î »)", 2, "dessous"),
]
PAR_LETTRE = {l[0]: l for l in LETTRES}


def transcription(lettre: str) -> str:
    """La transcription seule (« S (s emphatique) » → « S »), pour lire les syllabes."""
    return PAR_LETTRE[lettre][2].split(" ")[0]
NON_LIANTES = set("اد ذ ر ز و".replace(" ", ""))  # ne s'attachent jamais à la lettre suivante

GROUPES = {"ar-lettres-1": "ابتثجحخدذرز", "ar-lettres-2": "سشصضطظعغ", "ar-lettres-3": "فقكلمنهوي"}

# mot vocalisé, transcription, sens, thème
MOTS = [
    ("شُكْرًا", "choukran", "merci", "politesse"), ("نَعَمْ", "na'am", "oui", "politesse"),
    ("لَا", "lâ", "non", "politesse"), ("مَرْحَبًا", "marHaban", "bienvenue, bonjour", "politesse"),
    ("أُمّ", "oumm", "mère", "famille"), ("أَب", "ab", "père", "famille"), ("أَخ", "akh", "frère", "famille"),
    ("أُخْت", "oukht", "sœur", "famille"), ("بَيْت", "bayt", "maison", "objets"), ("كِتَاب", "kitâb", "livre", "objets"),
    ("قَلَم", "qalam", "crayon, stylo", "objets"), ("بَاب", "bâb", "porte", "objets"),
    ("مَدْرَسَة", "madrasa", "école", "objets"), ("قِطّ", "qiTT", "chat", "animaux"), ("كَلْب", "kalb", "chien", "animaux"),
    ("أَسَد", "asad", "lion", "animaux"), ("حِصَان", "HiSân", "cheval", "animaux"), ("سَمَكَة", "samaka", "poisson", "animaux"),
    ("مَاء", "mâ'", "eau", "nourriture"), ("خُبْز", "khoubz", "pain", "nourriture"), ("حَلِيب", "Halîb", "lait", "nourriture"),
    ("تُفَّاحَة", "touffâHa", "pomme", "nourriture"), ("شَمْس", "chams", "soleil", "nature"), ("قَمَر", "qamar", "lune", "nature"),
    ("أَحْمَر", "aHmar", "rouge", "couleurs"), ("أَزْرَق", "azraq", "bleu", "couleurs"), ("أَخْضَر", "akhDar", "vert", "couleurs"),
    ("أَصْفَر", "aSfar", "jaune", "couleurs"), ("أَبْيَض", "abyaD", "blanc", "couleurs"), ("أَسْوَد", "aswad", "noir", "couleurs"),
]
NOMBRES = [("وَاحِد", "wâHid", 1), ("اِثْنَان", "ithnân", 2), ("ثَلَاثَة", "thalâtha", 3), ("أَرْبَعَة", "arba'a", 4),
           ("خَمْسَة", "khamsa", 5), ("سِتَّة", "sitta", 6), ("سَبْعَة", "sab'a", 7), ("ثَمَانِيَة", "thamâniya", 8),
           ("تِسْعَة", "tis'a", 9), ("عَشَرَة", "'achara", 10)]
CHIFFRES = "٠١٢٣٤٥٦٧٨٩"

PHRASES = [
    ("السَّلَامُ عَلَيْكُمْ", "as-salâmou 'alaykoum", "bonjour (la paix soit sur vous)"),
    ("وَعَلَيْكُمُ السَّلَام", "wa 'alaykoumou s-salâm", "réponse à « as-salâmou 'alaykoum »"),
    ("صَبَاحُ الْخَيْر", "SabâHou l-khayr", "bonjour (le matin)"), ("مَسَاءُ الْخَيْر", "masâ'ou l-khayr", "bonsoir"),
    ("مَعَ السَّلَامَة", "ma'a s-salâma", "au revoir"), ("اِسْمِي", "ismî", "je m'appelle"),
    ("مَا اسْمُكَ؟", "mâ smouka ?", "comment t'appelles-tu ? (à un garçon)"),
    ("كَيْفَ حَالُكَ؟", "kayfa Hâlouka ?", "comment vas-tu ? (à un garçon)"),
    ("أَنَا بِخَيْر", "anâ bikhayr", "je vais bien"), ("مِنْ فَضْلِكَ", "min faDlika", "s'il te plaît (à un garçon)"),
    ("عَفْوًا", "'afwan", "de rien"), ("أَنَا تِلْمِيذ", "anâ tilmîdh", "je suis élève"),
]


def melanger(rng, bonne, autres, n=3):
    options = [bonne] + rng.sample([a for a in autres if a != bonne], n - 1)
    rng.shuffle(options)
    return options


def avec_arabe(ex: dict, texte_arabe: str) -> dict:
    """Le texte arabe à afficher en grand sous l'énoncé (et à lire à voix haute)."""
    ex["arabe"] = texte_arabe
    return ex


# --- Les lettres ---------------------------------------------------------------------------------

def lettres(groupe: str):
    def generateur(rng, niveau):
        pool = [PAR_LETTRE[l] for l in groupe]
        if niveau == 1:
            pool = pool[:max(4, len(pool) // 2 + 1)]
        lettre, nom, son, explication_son, points, position = rng.choice(pool)
        noms = [p[1] for p in pool]
        sorte = rng.choice(["nom", "lettre"] + (["son"] if niveau >= 2 else []) + (["points"] * 2 if niveau == 3 else []))
        rappel = f"{lettre} s'appelle « {nom} » ; elle se prononce {explication_son}."
        if sorte == "lettre":
            return exercice("choix", f"Quelle est la lettre « {nom} » ?", lettre,
                            [rappel], "Pense à sa forme et à ses points.",
                            options=melanger(rng, lettre, [p[0] for p in pool]))
        if sorte == "son":
            return avec_arabe(exercice("choix", "Quel son fait cette lettre ?", son, [rappel],
                                       "Dis son nom à voix haute : il commence par son son.",
                                       options=melanger(rng, son, [p[2] for p in pool])), lettre)
        if sorte == "points":
            texte = "aucun point" if not points else f"{points} point{'s' if points > 1 else ''} {position}"
            autres = ["aucun point", "1 point dessus", "1 point dessous", "2 points dessus", "2 points dessous", "3 points dessus"]
            return exercice("choix", f"Combien de points a la lettre « {nom} », et où ?", texte,
                            [rappel, f"« {nom} » ({lettre}) : {texte}."],
                            "Imagine la lettre : les points sont-ils au-dessus ou en dessous ?",
                            options=melanger(rng, texte, autres))
        return avec_arabe(exercice("choix", "Comment s'appelle cette lettre ?", nom, [rappel],
                                   "Regarde sa forme et compte ses points.", options=melanger(rng, nom, noms)), lettre)
    generateur.__name__ = f"lettres_{groupe}"
    return generateur


# --- Les lettres attachées ------------------------------------------------------------------------

def forme(lettre: str, place: str) -> str:
    liante = lettre not in NON_LIANTES
    if place == "début":
        return lettre + TATWIL if liante else lettre
    if place == "milieu":
        return TATWIL + lettre + (TATWIL if liante else "")
    return TATWIL + lettre


def lettres_attachees(rng, niveau):
    if niveau >= 2 and rng.random() < 0.35:
        bonne = PAR_LETTRE[rng.choice(sorted(NON_LIANTES))]
        autres = [l[1] for l in LETTRES if l[0] not in NON_LIANTES]
        return exercice("choix", "Laquelle de ces lettres ne s'attache jamais à la lettre qui la suit ?", bonne[1],
                        ["Six lettres ne s'attachent pas à gauche : alif (ا), dal (د), dhal (ذ), ra (ر), zay (ز), waw (و).",
                         f"« {bonne[1]} » ({bonne[0]}) en fait partie."],
                        "Pense aux six lettres qui « coupent » le mot.", options=melanger(rng, bonne[1], autres))
    pool = LETTRES[1:] if niveau < 3 else LETTRES
    if niveau == 1:
        pool = [l for l in pool if l[0] in "بتنيسشفقكلمه"]
    lettre, nom = rng.choice(pool)[:2]
    place = rng.choice(["début", "milieu", "fin"])
    dessin = forme(lettre, place)
    ou = {"début": "au début", "milieu": "au milieu", "fin": "à la fin"}[place]
    return avec_arabe(exercice("choix", f"Quelle lettre est écrite ici, {ou} d'un mot ?", nom,
                               [f"C'est « {nom} » : seule, elle s'écrit {lettre}.",
                                "Les lettres changent un peu de forme selon leur place, mais gardent leurs points."],
                               "Regarde les points : ils ne changent jamais de place.",
                               options=melanger(rng, nom, [l[1] for l in pool])), dessin)


# --- Les voyelles ----------------------------------------------------------------------------------

VOYELLES = [(FATHA, "a", "fatha"), (KASRA, "i", "kasra"), (DAMMA, "ou", "damma")]
LONGUES = [(FATHA + "ا", "â"), (KASRA + "ي", "î"), (DAMMA + "و", "oû")]
CONSONNES = [l for l in LETTRES if l[0] != "ا"]


def voyelles(rng, niveau):
    lettre, nom = rng.choice(CONSONNES)[:2]
    son = transcription(lettre)
    if niveau == 1 or (niveau == 2 and rng.random() < 0.4):
        signe, voyelle, nom_signe = rng.choice(VOYELLES)
        bonne = son + voyelle
        return avec_arabe(exercice("choix", "Comment se lit cette syllabe ?", bonne,
                                   [f"La lettre est « {nom} » ({son}).",
                                    f"Le signe est une {nom_signe} : il se lit « {voyelle} ».", f"On lit : {bonne}."],
                                   "Petit trait au-dessus : a ; en dessous : i ; petite boucle au-dessus : ou.",
                                   options=[son + v for _, v, _ in VOYELLES]), lettre + signe)
    if niveau == 2:
        suite, longue = rng.choice(LONGUES)
        bonne = son + longue
        return avec_arabe(exercice("choix", "Comment se lit cette syllabe longue ?", bonne,
                                   [f"La lettre est « {nom} » ({son}).",
                                    "Fatha + alif = â ; kasra + ya = î ; damma + waw = oû.", f"On lit : {bonne}."],
                                   "La lettre qui suit allonge la voyelle.",
                                   options=[son + l for _, l in LONGUES]), lettre + suite)
    deuxieme, nom2 = rng.choice([c for c in CONSONNES if c[0] != lettre])[:2]
    son2 = transcription(deuxieme)
    signe, voyelle, nom_signe = rng.choice(VOYELLES)
    bonne = son + voyelle + son2
    return avec_arabe(exercice("choix", "Comment se lit cette syllabe ?", bonne,
                               [f"« {nom} » avec une {nom_signe} : {son}{voyelle}.",
                                f"« {nom2} » porte un soukoun (petit rond) : pas de voyelle, on prononce juste {son2}.",
                                f"On lit : {bonne}."],
                               "Le petit rond (soukoun) veut dire : pas de voyelle.",
                               options=[son + v + son2 for _, v, _ in VOYELLES]), lettre + signe + deuxieme + SOUKOUN)


# --- Les mots et les chiffres -----------------------------------------------------------------------

def mots(rng, niveau):
    sorte = rng.choice(["sens", "arabe"] + (["lire", "nombre", "chiffre"] if niveau >= 2 else []))
    if sorte == "nombre":
        arabe_mot, transcription, valeur = rng.choice(NOMBRES if niveau == 3 else NOMBRES[:5])
        return avec_arabe(exercice("choix", "Quel nombre est écrit ici ?", str(valeur),
                                   [f"{arabe_mot} se lit « {transcription} » : c'est {valeur}."],
                                   "Lis le mot à voix haute.",
                                   options=melanger(rng, str(valeur), [str(n[2]) for n in NOMBRES])), arabe_mot)
    if sorte == "chiffre":
        valeur = rng.randint(0, 9)
        return avec_arabe(exercice("choix", "Quel chiffre est-ce ?", str(valeur),
                                   [f"{CHIFFRES[valeur]} = {valeur}.",
                                    "Ces chiffres « indiens » sont utilisés au Moyen-Orient ; au Maghreb, on écrit souvent 0, 1, 2, 3…",
                                    "Les nombres s'écrivent de gauche à droite, même dans un texte arabe."],
                                   "Compare avec les chiffres que tu connais : certains se ressemblent.",
                                   options=melanger(rng, str(valeur), [str(n) for n in range(10)])), CHIFFRES[valeur])
    pool = MOTS if niveau > 1 else [m for m in MOTS if m[3] in ("politesse", "famille", "animaux")]
    arabe_mot, transcription, sens, _ = rng.choice(pool)
    rappel = [f"{arabe_mot} se lit « {transcription} » et veut dire « {sens} »."]
    if sorte == "arabe":
        return exercice("choix", f"Comment dit-on « {sens} » en arabe ?", arabe_mot, rappel,
                        "Lis chaque mot à voix haute.", options=melanger(rng, arabe_mot, [m[0] for m in pool]))
    if sorte == "lire":
        return avec_arabe(exercice("choix", "Comment se lit ce mot ?", transcription, rappel,
                                   "Lis lettre par lettre, avec les voyelles.",
                                   options=melanger(rng, transcription, [m[1] for m in pool])), arabe_mot)
    return avec_arabe(exercice("choix", "Que veut dire ce mot ?", sens, rappel, "Lis-le d'abord à voix haute.",
                               options=melanger(rng, sens, [m[2] for m in pool])), arabe_mot)


def phrases(rng, niveau):
    pool = PHRASES if niveau > 1 else PHRASES[:6]
    arabe_phrase, transcription, sens = rng.choice(pool)
    rappel = [f"{arabe_phrase} se lit « {transcription} » : {sens}."]
    if niveau == 3 and rng.random() < 0.5:
        return avec_arabe(exercice("choix", "Comment se lit cette phrase ?", transcription, rappel,
                                   "Lis mot par mot, de droite à gauche.",
                                   options=melanger(rng, transcription, [p[1] for p in pool])), arabe_phrase)
    if rng.random() < 0.5:
        return exercice("choix", f"Comment dit-on « {sens} » en arabe ?", arabe_phrase, rappel,
                        "Lis chaque proposition à voix haute.", options=melanger(rng, arabe_phrase, [p[0] for p in pool]))
    return avec_arabe(exercice("choix", "Que veut dire cette phrase ?", sens, rappel, "Lis-la d'abord à voix haute.",
                               options=melanger(rng, sens, [p[2] for p in pool])), arabe_phrase)


# --- Leçons ------------------------------------------------------------------------------------------

def ligne_lettres(groupe):
    return " · ".join(f"{PAR_LETTRE[l][0]} {PAR_LETTRE[l][1]} ({transcription(l)})" for l in groupe)


CHAPITRES = [
    {"id": "ar-lettres-1", "titre": "Les lettres (1) : de alif à zay", "domaine": "L'alphabet",
     "resume": "Les 11 premières lettres de l'alphabet arabe.",
     "retenir": ["L'arabe s'écrit et se lit de droite à gauche. L'alphabet a 28 lettres, sans majuscules.",
                 ligne_lettres(GROUPES["ar-lettres-1"]),
                 "ب, ت et ث ont la même forme : seuls les points changent (1 dessous, 2 dessus, 3 dessus). De même pour ج, ح, خ.",
                 "Dans la transcription, une majuscule (H, S, D, T, Z) indique un son plus profond ou plus appuyé qu'en français."],
     "exemple": {"question": "Comment distinguer ب de ت ?",
                 "etapes": ["Les deux ont la même forme, comme une petite barque.",
                            "ب (ba) a un point en dessous ; ت (ta) a deux points au-dessus."]}},
    {"id": "ar-lettres-2", "titre": "Les lettres (2) : de sin à ghayn", "domaine": "L'alphabet",
     "resume": "Huit lettres, dont les lettres emphatiques.",
     "retenir": [ligne_lettres(GROUPES["ar-lettres-2"]),
                 "س et ش ont la même forme : ش a trois points au-dessus. ص et ض, ط et ظ, ع et غ vont aussi par deux.",
                 "ص, ض, ط, ظ sont des lettres emphatiques : on les prononce avec la langue plus en arrière.",
                 "ع ('ayn) est un son du fond de la gorge qui n'existe pas en français : écoute-le bien avec le bouton « Écouter »."],
     "exemple": {"question": "Comment distinguer ع de غ ?",
                 "etapes": ["Elles ont la même forme.", "غ (ghayn) a un point au-dessus ; ع ('ayn) n'en a pas."]}},
    {"id": "ar-lettres-3", "titre": "Les lettres (3) : de fa à ya", "domaine": "L'alphabet",
     "resume": "Les 9 dernières lettres de l'alphabet.",
     "retenir": [ligne_lettres(GROUPES["ar-lettres-3"]),
                 "ف (fa) a un point au-dessus, ق (qaf) deux points au-dessus.",
                 "و (waw) et ي (ya) servent aussi de voyelles longues : oû et î.",
                 "ن (noun) a un point au-dessus, ي (ya) deux points en dessous."],
     "exemple": {"question": "Comment distinguer ف de ق ?",
                 "etapes": ["Leur tête est ronde.", "ف (fa) a un point au-dessus ; ق (qaf) en a deux."]}},
    {"id": "ar-formes", "titre": "Les lettres attachées", "domaine": "L'écriture",
     "resume": "Une lettre change de forme au début, au milieu et à la fin d'un mot.",
     "retenir": ["En arabe, les lettres d'un mot s'attachent entre elles, comme en écriture cursive.",
                 "Une lettre a jusqu'à quatre formes : seule, au début, au milieu, à la fin. Ses points ne changent jamais.",
                 "Six lettres ne s'attachent jamais à la lettre qui suit : ا د ذ ر ز و.",
                 "Exemple avec ب : seule ب, au début بـ, au milieu ـبـ, à la fin ـب."],
     "exemple": {"question": "Pourquoi le mot دار (maison) a-t-il ses lettres séparées ?",
                 "etapes": ["د (dal) ne s'attache pas à la lettre suivante.", "ا (alif) non plus.",
                            "Les trois lettres restent donc séparées."]}},
    {"id": "ar-voyelles", "titre": "Les voyelles", "domaine": "La lecture",
     "resume": "Fatha, kasra, damma, voyelles longues et soukoun : lire des syllabes.",
     "retenir": ["Les voyelles courtes sont de petits signes : fatha (trait au-dessus) = a ; kasra (trait en dessous) = i ; damma (petite boucle au-dessus) = ou.",
                 "بَ = ba ; بِ = bi ; بُ = bou.",
                 "Voyelles longues : fatha + alif = â (بَا = bâ) ; kasra + ya = î (بِي = bî) ; damma + waw = oû (بُو = boû).",
                 "Le soukoun (petit rond) indique l'absence de voyelle : بَتْ = bat."],
     "exemple": {"question": "Comment lire كِتَاب ?",
                 "etapes": ["كِ = ki (kaf + kasra).", "تَا = tâ (ta + fatha + alif).", "ب = b.", "On lit : kitâb (livre)."]}},
    {"id": "ar-mots", "titre": "Premiers mots et chiffres", "domaine": "Le vocabulaire",
     "resume": "Politesse, famille, objets, animaux, nourriture, couleurs, nombres de 1 à 10.",
     "retenir": ["شُكْرًا (choukran) = merci ; نَعَمْ (na'am) = oui ; لَا (lâ) = non.",
                 "أُمّ (oumm) = mère ; أَب (ab) = père ; أَخ (akh) = frère ; أُخْت (oukht) = sœur.",
                 "كِتَاب (kitâb) = livre ; قَلَم (qalam) = crayon ; بَيْت (bayt) = maison ; قِطّ (qiTT) = chat.",
                 "1 à 5 : وَاحِد (wâHid), اِثْنَان (ithnân), ثَلَاثَة (thalâtha), أَرْبَعَة (arba'a), خَمْسَة (khamsa).",
                 "Chiffres utilisés au Moyen-Orient : ٠ ١ ٢ ٣ ٤ ٥ ٦ ٧ ٨ ٩ (0 à 9)."],
     "exemple": {"question": "Que veut dire قَمَر ?",
                 "etapes": ["قَ = qa ; مَ = ma ; ر = r.", "On lit : qamar.", "Cela veut dire « lune »."]}},
    {"id": "ar-phrases", "titre": "Saluer et se présenter", "domaine": "Le vocabulaire",
     "resume": "Dire bonjour, au revoir, merci, se présenter.",
     "retenir": ["السَّلَامُ عَلَيْكُمْ (as-salâmou 'alaykoum) = bonjour ; on répond وَعَلَيْكُمُ السَّلَام (wa 'alaykoumou s-salâm).",
                 "صَبَاحُ الْخَيْر (SabâHou l-khayr) = bonjour le matin ; مَسَاءُ الْخَيْر (masâ'ou l-khayr) = bonsoir.",
                 "اِسْمِي (ismî) = je m'appelle : اِسْمِي مُعَاذ = je m'appelle Mouaz.",
                 "كَيْفَ حَالُكَ؟ (kayfa Hâlouka) = comment vas-tu ? — أَنَا بِخَيْر (anâ bikhayr) = je vais bien.",
                 "مَعَ السَّلَامَة (ma'a s-salâma) = au revoir ; عَفْوًا ('afwan) = de rien."],
     "exemple": {"question": "Comment te présenter ?",
                 "etapes": ["Je dis : السَّلَامُ عَلَيْكُمْ (bonjour).", "Puis : اِسْمِي مُعَاذ (je m'appelle Mouaz)."]}},
]

GENERATEURS = {
    "ar-lettres-1": [lettres(GROUPES["ar-lettres-1"])],
    "ar-lettres-2": [lettres(GROUPES["ar-lettres-2"])],
    "ar-lettres-3": [lettres(GROUPES["ar-lettres-3"])],
    "ar-formes": [lettres_attachees],
    "ar-voyelles": [voyelles],
    "ar-mots": [mots],
    "ar-phrases": [phrases],
}
