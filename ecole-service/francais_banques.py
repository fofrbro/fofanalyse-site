"""
Banques de questions de français, écrites et vérifiées à la main.

Pour la grammaire, les homophones et le vocabulaire, il n'y a pas de
calcul : la bonne réponse est écrite ici, avec son explication. Les tests
vérifient que chaque mot ou groupe ciblé apparaît une seule fois dans sa
phrase, et que chaque phrase à trou a un seul trou.
"""

# --- Classes de mots (nature) : (phrase, mot, nature) -------------------------------

NATURES_CM1 = ["nom", "verbe", "adjectif", "déterminant", "pronom"]
NATURES_6E = NATURES_CM1 + ["adverbe", "préposition", "conjonction de coordination"]

NATURE = [
    ("Ma sœur lit un roman passionnant.", "Ma", "déterminant"),
    ("Ma sœur lit un roman passionnant.", "sœur", "nom"),
    ("Ma sœur lit un roman passionnant.", "lit", "verbe"),
    ("Ma sœur lit un roman passionnant.", "passionnant", "adjectif"),
    ("Nous mangeons des pommes rouges.", "Nous", "pronom"),
    ("Nous mangeons des pommes rouges.", "mangeons", "verbe"),
    ("Nous mangeons des pommes rouges.", "des", "déterminant"),
    ("Nous mangeons des pommes rouges.", "rouges", "adjectif"),
    ("Elle chante une jolie chanson.", "Elle", "pronom"),
    ("Elle chante une jolie chanson.", "jolie", "adjectif"),
    ("Elle chante une jolie chanson.", "chanson", "nom"),
    ("Les enfants jouent dans la cour.", "enfants", "nom"),
    ("Les enfants jouent dans la cour.", "jouent", "verbe"),
    ("Les enfants jouent dans la cour.", "Les", "déterminant"),
    ("Ce gros chien aboie.", "Ce", "déterminant"),
    ("Ce gros chien aboie.", "gros", "adjectif"),
    ("Ce gros chien aboie.", "aboie", "verbe"),
    ("Ils regardent un film drôle.", "Ils", "pronom"),
    ("Ils regardent un film drôle.", "drôle", "adjectif"),
    ("Mon frère range sa chambre.", "range", "verbe"),
    ("Mon frère range sa chambre.", "sa", "déterminant"),
    ("Mon frère range sa chambre.", "chambre", "nom"),
    ("Tu prends le bus vert.", "Tu", "pronom"),
    ("Tu prends le bus vert.", "vert", "adjectif"),
    ("Cette maison ancienne est grande.", "Cette", "déterminant"),
    ("Cette maison ancienne est grande.", "ancienne", "adjectif"),
    ("Cette maison ancienne est grande.", "est", "verbe"),
    ("Vous aimez les fraises.", "Vous", "pronom"),
    ("Vous aimez les fraises.", "fraises", "nom"),
    # Avec les classes de 6e
    ("Le chien court très vite.", "très", "adverbe"),
    ("Le chien court très vite.", "court", "verbe"),
    ("Paul et Léa partent demain.", "et", "conjonction de coordination"),
    ("Paul et Léa partent demain.", "demain", "adverbe"),
    ("Je pose le livre sur la table.", "sur", "préposition"),
    ("Je pose le livre sur la table.", "Je", "pronom"),
    ("Il pleut, mais nous sortons.", "mais", "conjonction de coordination"),
    ("Elle marche lentement vers l'école.", "lentement", "adverbe"),
    ("Elle marche lentement vers l'école.", "vers", "préposition"),
    ("Le gâteau de Mamie est délicieux.", "de", "préposition"),
    ("Le gâteau de Mamie est délicieux.", "délicieux", "adjectif"),
    ("Nous partirons avec nos cousins.", "avec", "préposition"),
    ("Nous partirons avec nos cousins.", "nos", "déterminant"),
    ("Il ne parle jamais en classe.", "jamais", "adverbe"),
    ("Il ne parle jamais en classe.", "en", "préposition"),
    ("Tu veux une pomme ou une poire ?", "ou", "conjonction de coordination"),
]

ASTUCES_NATURE = {
    "nom": "Un nom désigne une personne, un animal, une chose ou une idée ; on peut mettre « le », « la » ou « un » devant.",
    "verbe": "Un verbe se conjugue : on peut changer son temps (hier…, demain…).",
    "adjectif": "Un adjectif donne une précision sur le nom et s'accorde avec lui.",
    "déterminant": "Un déterminant se place devant le nom (le, une, mon, ces…).",
    "pronom": "Un pronom remplace un nom (je, tu, il, elle, nous, vous, ils, elles…).",
    "adverbe": "Un adverbe est invariable : il précise un verbe, un adjectif ou un autre adverbe (très, vite, demain…).",
    "préposition": "Une préposition est un petit mot invariable qui introduit un complément (à, de, sur, avec, vers, en…).",
    "conjonction de coordination": "Une conjonction de coordination relie deux mots ou deux groupes : mais, ou, et, donc, or, ni, car.",
}

# --- Fonctions : (phrase, groupe, fonction) --------------------------------------------

FONCTIONS_CM2 = ["sujet", "COD", "COI", "complément circonstanciel", "attribut du sujet"]
FONCTIONS_6E = FONCTIONS_CM2 + ["épithète", "complément du nom"]

FONCTION = [
    ("Le facteur apporte le courrier.", "Le facteur", "sujet"),
    ("Le facteur apporte le courrier.", "le courrier", "COD"),
    ("Léa téléphone à sa grand-mère.", "à sa grand-mère", "COI"),
    ("Léa téléphone à sa grand-mère.", "Léa", "sujet"),
    ("Chaque matin, Hugo promène son chien.", "Chaque matin", "complément circonstanciel"),
    ("Chaque matin, Hugo promène son chien.", "son chien", "COD"),
    ("Mon oncle est boulanger.", "boulanger", "attribut du sujet"),
    ("Les élèves écoutent la maîtresse.", "la maîtresse", "COD"),
    ("Les élèves écoutent la maîtresse.", "Les élèves", "sujet"),
    ("Nous parlons de nos vacances.", "de nos vacances", "COI"),
    ("Le chat dort sous la table.", "sous la table", "complément circonstanciel"),
    ("Ces fleurs semblent fanées.", "fanées", "attribut du sujet"),
    ("Pendant la récréation, les enfants courent.", "Pendant la récréation", "complément circonstanciel"),
    ("Mon frère devient grand.", "grand", "attribut du sujet"),
    ("Elle range ses affaires avec soin.", "avec soin", "complément circonstanciel"),
    ("Elle range ses affaires avec soin.", "ses affaires", "COD"),
    ("Les oiseaux chantent dans le jardin.", "Les oiseaux", "sujet"),
    ("Je pense à mes amis.", "à mes amis", "COI"),
    ("Hier, Sami a perdu ses clés.", "ses clés", "COD"),
    ("Hier, Sami a perdu ses clés.", "Hier", "complément circonstanciel"),
    # Avec les fonctions de 6e
    ("Il porte un pull rouge.", "rouge", "épithète"),
    ("La maison de mes voisins est grande.", "de mes voisins", "complément du nom"),
    ("La maison de mes voisins est grande.", "grande", "attribut du sujet"),
    ("Une petite fille lit un livre.", "petite", "épithète"),
    ("Le vélo de Sami est neuf.", "de Sami", "complément du nom"),
    ("Nous avons visité un château ancien.", "ancien", "épithète"),
    ("Le jus d'orange est frais.", "d'orange", "complément du nom"),
]

ASTUCES_FONCTION = {
    "sujet": "Le sujet fait l'action ou est ce dont on parle : « C'est … qui » + verbe.",
    "COD": "Le COD répond à « quoi ? » ou « qui ? » posé après le verbe, sans préposition.",
    "COI": "Le COI répond à « à qui ? », « à quoi ? », « de qui ? », « de quoi ? » posé après le verbe.",
    "complément circonstanciel": "Le complément circonstanciel dit où, quand, comment… On peut souvent le déplacer ou le supprimer.",
    "attribut du sujet": "L'attribut du sujet suit un verbe d'état (être, sembler, devenir, paraître, rester) et donne une qualité au sujet.",
    "épithète": "L'épithète est un adjectif placé juste à côté du nom, sans verbe entre les deux.",
    "complément du nom": "Le complément du nom précise un nom ; il est souvent introduit par « de » (la maison de mes voisins).",
}

# --- Homophones : (phrase avec ___, réponse, options) ------------------------------------

HOMOPHONES_CM1 = {
    ("a", "à"): ("Si tu peux dire « avait », écris « a » (verbe avoir). Sinon, écris « à ».", [
        ("Mon frère ___ un vélo neuf.", "a"), ("Il va ___ la piscine.", "à"), ("Léa ___ perdu sa clé.", "a"),
        ("Nous allons ___ Paris.", "à"), ("Elle ___ très faim.", "a"), ("Je pense ___ toi.", "à"),
        ("Sami ___ dix ans.", "a"), ("C'est ___ toi de jouer.", "à")]),
    ("et", "est"): ("Si tu peux dire « était », écris « est ». Si tu peux dire « et puis », écris « et ».", [
        ("Le ciel ___ bleu.", "est"), ("J'ai un chat ___ un chien.", "et"), ("Ma sœur ___ malade.", "est"),
        ("Il mange du pain ___ du fromage.", "et"), ("Ce livre ___ passionnant.", "est"),
        ("Paul ___ Léa sont amis.", "et")]),
    ("son", "sont"): ("Si tu peux dire « étaient », écris « sont ». Si tu peux dire « mon », écris « son ».", [
        ("Les enfants ___ dans la cour.", "sont"), ("Il prend ___ cartable.", "son"),
        ("Mes amis ___ gentils.", "sont"), ("Elle range ___ bureau.", "son"), ("Ils ___ en retard.", "sont")]),
    ("on", "ont"): ("Si tu peux dire « avaient », écris « ont ». Si tu peux dire « il », écris « on ».", [
        ("Mes parents ___ une voiture rouge.", "ont"), ("Ce soir, ___ va au cinéma.", "on"),
        ("Les élèves ___ fini leurs exercices.", "ont"), ("Demain, ___ partira tôt.", "on"),
        ("Mes voisins ___ un grand jardin.", "ont")]),
    ("ou", "où"): ("Si tu peux dire « ou bien », écris « ou ». « Où » indique un lieu ou un moment.", [
        ("Tu veux du jus ___ de l'eau ?", "ou"), ("Je sais ___ tu habites.", "où"),
        ("Il viendra lundi ___ mardi.", "ou"), ("La ville ___ je suis né est petite.", "où"),
        ("Tu préfères le rouge ___ le bleu ?", "ou")]),
}

HOMOPHONES_CM2 = {
    ("ce", "se"): ("« se » va avec un verbe (il se lave). « ce » va avec un nom (ce livre) ou veut dire « cela ».", [
        ("Il ___ lave les mains.", "se"), ("Regarde ___ chien !", "ce"), ("Elles ___ promènent au parc.", "se"),
        ("J'aime ___ dessin.", "ce"), ("Le chat ___ cache sous le lit.", "se")]),
    ("ces", "ses"): ("« ses » veut dire « les siens » (à lui, à elle). « ces » montre : ces livres-là.", [
        ("Léa range ___ jouets dans sa chambre.", "ses"), ("Regarde ___ nuages, là-bas !", "ces"),
        ("Il a oublié ___ lunettes.", "ses"), ("Tu vois ___ montagnes au loin ?", "ces")]),
    ("c'est", "s'est"): ("« s'est » vient d'un verbe en « se » (il s'est levé : se lever). « c'est » veut dire « cela est ».", [
        ("Il ___ blessé au genou.", "s'est"), ("Je crois que ___ l'heure.", "c'est"),
        ("Elle ___ endormie tôt.", "s'est"), ("Regarde, ___ ton bus !", "c'est")]),
    ("leur", "leurs"): ("Devant un verbe, « leur » ne prend jamais de s (je leur parle). Devant un nom au pluriel, « leurs » prend un s.", [
        ("Les enfants rangent ___ affaires.", "leurs"), ("Je ___ donne un conseil.", "leur"),
        ("Ils ont pris ___ vélos.", "leurs"), ("Nous ___ avons écrit une lettre.", "leur")]),
    ("la", "l'a", "là"): ("« l'a » peut se remplacer par « l'avait ». « là » indique un lieu (là-bas). Sinon, c'est « la ».", [
        ("Pose ton sac ___, près de la porte.", "là"), ("Sa trousse ? Il ___ perdue.", "l'a"),
        ("Je regarde ___ télévision.", "la"), ("Le chat ? Elle ___ caressé.", "l'a"), ("Je suis ___ !", "là")]),
}

# --- Vocabulaire -------------------------------------------------------------------------

SYNONYMES = [("content", "heureux", ["triste", "fatigué"]), ("commencer", "débuter", ["finir", "attendre"]),
             ("peur", "frayeur", ["joie", "colère"]), ("joli", "beau", ["laid", "grand"]),
             ("crier", "hurler", ["chuchoter", "dormir"]), ("regarder", "observer", ["écouter", "toucher"]),
             ("gentil", "aimable", ["méchant", "bavard"]), ("finir", "terminer", ["commencer", "continuer"]),
             ("maison", "habitation", ["jardin", "rue"]), ("rapide", "vif", ["lent", "lourd"])]
ANTONYMES = [("grand", "petit", ["haut", "gros"]), ("chaud", "froid", ["tiède", "brûlant"]),
             ("ouvrir", "fermer", ["entrer", "pousser"]), ("rapide", "lent", ["vif", "pressé"]),
             ("propre", "sale", ["neuf", "lavé"]), ("gagner", "perdre", ["jouer", "réussir"]),
             ("lourd", "léger", ["gros", "épais"]), ("allumer", "éteindre", ["brûler", "briller"]),
             ("courageux", "peureux", ["fort", "brave"]), ("vide", "plein", ["creux", "léger"])]
PREFIXES = [("possible", "impossible"), ("lisible", "illisible"), ("faire", "défaire"), ("content", "mécontent"),
            ("prudent", "imprudent"), ("connu", "inconnu"), ("poli", "impoli"), ("monter", "démonter"),
            ("régulier", "irrégulier"), ("patient", "impatient"), ("habiller", "déshabiller"),
            ("visible", "invisible"), ("buvable", "imbuvable"), ("légal", "illégal")]
FAMILLES = [("dent", ["dentiste", "dentifrice", "édenté"], "danse"),
            ("lait", ["laitier", "laitage", "allaiter"], "laid"),
            ("fleur", ["fleuriste", "fleurir", "floraison"], "flûte"),
            ("terre", ["terrain", "enterrer", "terrestre"], "terrible"),
            ("chant", ["chanter", "chanteur", "chanson"], "champ"),
            ("sel", ["salé", "saler", "salière"], "selle"),
            ("jardin", ["jardinier", "jardinage", "jardiner"], "jaune"),
            ("dent", ["dentaire", "dentelé", "dentition"], "dense")]

SENS = [("Il a un cœur de pierre.", "cœur de pierre", "sens figuré"),
        ("Le mur du château est en pierre.", "pierre", "sens propre"),
        ("Elle a la tête dans les nuages.", "la tête dans les nuages", "sens figuré"),
        ("Les nuages cachent le soleil.", "nuages", "sens propre"),
        ("Il dévore son livre.", "dévore", "sens figuré"),
        ("Le lion dévore sa proie.", "dévore", "sens propre"),
        ("Elle brûle d'impatience.", "brûle", "sens figuré"),
        ("Attention, le four brûle !", "brûle", "sens propre"),
        ("Ce film est un vrai navet.", "navet", "sens figuré"),
        ("Mamie fait pousser des navets.", "navets", "sens propre"),
        ("Il pleut des cordes.", "pleut des cordes", "sens figuré"),
        ("Le marin attache le bateau avec des cordes.", "cordes", "sens propre")]

NIVEAUX_LANGUE = [("Ce mec est sympa.", "familier"), ("Ce garçon est gentil.", "courant"),
                  ("Ce jeune homme est fort aimable.", "soutenu"), ("J'ai bouffé.", "familier"),
                  ("J'ai mangé.", "courant"), ("Je me suis restauré.", "soutenu"), ("Ça caille !", "familier"),
                  ("Il fait froid.", "courant"), ("Je me suis fait engueuler.", "familier"),
                  ("J'ai été grondé.", "courant"), ("On m'a réprimandé.", "soutenu"),
                  ("C'est une bagnole.", "familier"), ("C'est une voiture.", "courant")]

# --- La phrase -----------------------------------------------------------------------------

TYPES_PHRASE = [("Range ta chambre.", "injonctive"), ("Quelle belle journée !", "exclamative"),
                ("As-tu fini tes devoirs ?", "interrogative"), ("Le train part à huit heures.", "déclarative"),
                ("Ferme la porte, s'il te plaît.", "injonctive"), ("Comme tu as grandi !", "exclamative"),
                ("Où vas-tu ?", "interrogative"), ("Il pleut depuis ce matin.", "déclarative"),
                ("Est-ce que tu viens ?", "interrogative"), ("Ne cours pas dans le couloir.", "injonctive"),
                ("Que c'est beau !", "exclamative"), ("Les élèves lisent en silence.", "déclarative")]

PHRASES_VERBES = [("Le chat dort.", ["dort"]), ("Le chat dort et le chien joue.", ["dort", "joue"]),
                  ("Quand il pleut, je reste à la maison.", ["pleut", "reste"]),
                  ("Les enfants jouent dans la cour.", ["jouent"]),
                  ("Je pense que tu as raison.", ["pense", "as"]),
                  ("Ma sœur lit un livre passionnant.", ["lit"]), ("Il mange, puis il part.", ["mange", "part"]),
                  ("Demain matin, nous irons à la plage.", ["irons"]),
                  ("Le garçon qui court est mon frère.", ["court", "est"]), ("Elle aime chanter.", ["aime"]),
                  ("Nous voulons partir tôt.", ["voulons"]),
                  ("Je finis mes devoirs, ensuite je sors.", ["finis", "sors"])]
