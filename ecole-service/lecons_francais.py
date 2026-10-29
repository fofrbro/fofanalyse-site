"""
Leçons de français, du CM1 à la 6e (cycle 3) : conjugaison, grammaire,
orthographe et vocabulaire. Même format que les leçons de maths.
"""

CM1 = [
    {
        "id": "fr-cm1-present", "titre": "Le présent", "domaine": "Conjugaison",
        "resume": "Conjuguer au présent les verbes en -er, en -ir (finir) et les verbes fréquents.",
        "retenir": [
            "1er groupe (verbes en -er, comme chanter) : je chante, tu chantes, il chante, nous chantons, "
            "vous chantez, ils chantent.",
            "2e groupe (comme finir) : je finis, tu finis, il finit, nous finissons, vous finissez, ils finissent.",
            "Être : je suis, tu es, il est, nous sommes, vous êtes, ils sont.",
            "Avoir : j'ai, tu as, il a, nous avons, vous avez, ils ont.",
            "Le verbe s'accorde avec son sujet : « Les enfants jouent » (ils jouent).",
            "Verbes en -cer et -ger : nous commençons, nous mangeons.",
        ],
        "exemple": {"question": "Conjugue « finir » au présent avec « nous ».",
                    "etapes": ["« finir » est du 2e groupe.", "Avec « nous », la terminaison est -issons.",
                               "Nous finissons."]},
    },
    {
        "id": "fr-cm1-temps", "titre": "Le futur et l'imparfait", "domaine": "Conjugaison",
        "resume": "Parler de ce qui se passera (futur) et de ce qui se passait (imparfait).",
        "retenir": [
            "Futur : infinitif + -ai, -as, -a, -ons, -ez, -ont. Je chanterai, nous finirons.",
            "Futurs à apprendre : je serai, j'aurai, j'irai, je ferai, je viendrai, je pourrai, je verrai.",
            "Imparfait : -ais, -ais, -ait, -ions, -iez, -aient pour tous les verbes. Je chantais, nous finissions.",
            "Le radical de l'imparfait est celui de « nous » au présent : nous faisons → je faisais. "
            "Sauf être : j'étais.",
        ],
        "exemple": {"question": "Conjugue « aller » au futur avec « nous ».",
                    "etapes": ["Au futur, « aller » a un radical irrégulier : ir-.", "ir + ons = irons.",
                               "Nous irons."]},
    },
    {
        "id": "fr-cm1-passe-compose", "titre": "Le passé composé", "domaine": "Conjugaison",
        "resume": "Auxiliaire avoir ou être au présent, plus le participe passé.",
        "retenir": [
            "Passé composé = auxiliaire « avoir » ou « être » au présent + participe passé : j'ai chanté.",
            "Participes passés : -é pour le 1er groupe (chanté), -i pour le 2e (fini).",
            "Participes à connaître : été, eu, fait, dit, pris, vu, mis, lu, venu, parti, pu, voulu, su.",
            "Avec « être » (aller, venir, partir, arriver, tomber, rester…), le participe s'accorde avec le sujet : "
            "elle est partie, ils sont venus.",
        ],
        "exemple": {"question": "Conjugue « aller » au passé composé avec « elle ».",
                    "etapes": ["« aller » se conjugue avec « être » : elle est.", "Participe passé : allé.",
                               "Le sujet est féminin : allée.", "Elle est allée."]},
    },
    {
        "id": "fr-cm1-nature", "titre": "Les classes de mots", "domaine": "Grammaire",
        "resume": "Reconnaître le nom, le verbe, l'adjectif, le déterminant et le pronom.",
        "retenir": [
            "Le nom désigne une personne, un animal, une chose : on peut mettre « le », « un » devant.",
            "Le déterminant se place devant le nom : le, la, un, une, des, mon, ce, ces…",
            "L'adjectif précise le nom et s'accorde avec lui : un chat noir, une robe noire.",
            "Le verbe se conjugue : il change avec le temps (je mange, je mangerai).",
            "Le pronom remplace un nom : je, tu, il, elle, nous, vous, ils, elles.",
        ],
        "exemple": {"question": "Dans « Le petit chat dort », quelle est la classe de « petit » ?",
                    "etapes": ["« petit » donne une précision sur le nom « chat ».",
                               "On peut dire « la petite chatte » : il s'accorde.", "C'est un adjectif."]},
    },
    {
        "id": "fr-cm1-homophones", "titre": "Les homophones", "domaine": "Orthographe",
        "resume": "a / à, et / est, son / sont, on / ont, ou / où.",
        "retenir": [
            "a / à : si on peut dire « avait », c'est « a » (il a faim → il avait faim).",
            "et / est : si on peut dire « était », c'est « est » ; si on peut dire « et puis », c'est « et ».",
            "son / sont : si on peut dire « étaient », c'est « sont » ; si on peut dire « mon », c'est « son ».",
            "on / ont : si on peut dire « avaient », c'est « ont » ; si on peut dire « il », c'est « on ».",
            "ou / où : si on peut dire « ou bien », c'est « ou » ; « où » indique un lieu ou un moment.",
        ],
        "exemple": {"question": "Mon frère ___ un vélo neuf. (a ou à ?)",
                    "etapes": ["J'essaie : « Mon frère avait un vélo neuf. » Ça marche.",
                               "C'est le verbe avoir : j'écris « a »."]},
    },
    {
        "id": "fr-cm1-accords", "titre": "Les accords dans le groupe nominal", "domaine": "Orthographe",
        "resume": "Le pluriel des noms et l'accord de l'adjectif.",
        "retenir": [
            "Au pluriel, on ajoute en général un s : un ami → des amis.",
            "-eau et -eu prennent un x : des bateaux, des jeux. -al devient -aux : des chevaux.",
            "Les noms qui finissent par s, x ou z ne changent pas : des souris, des prix, des nez.",
            "7 noms en -ou prennent un x : bijou, caillou, chou, genou, hibou, joujou, pou.",
            "L'adjectif s'accorde avec le nom : au féminin, on ajoute souvent un e ; au pluriel, un s. "
            "Des robes vertes.",
        ],
        "exemple": {"question": "Accorde « blanc » : des maisons …",
                    "etapes": ["« maisons » est féminin pluriel.", "blanc → blanche au féminin.",
                               "Des maisons blanches."]},
    },
]

CM2 = [
    {
        "id": "fr-cm2-temps-simples", "titre": "Les temps simples", "domaine": "Conjugaison",
        "resume": "Présent, futur, imparfait, passé simple, conditionnel et impératif.",
        "retenir": [
            "Passé simple, 3e personne : il chanta, ils chantèrent (1er groupe) ; il finit, ils finirent (2e groupe) ; "
            "il fut, il eut, il fit, il prit, il vint.",
            "Conditionnel présent : radical du futur + terminaisons de l'imparfait : je chanterais, j'irais.",
            "Impératif : pas de sujet, 3 personnes : chante, chantons, chantez. Pas de s à « tu » pour le 1er groupe.",
            "Futur et imparfait : voir les leçons de CM1, ils servent toujours.",
        ],
        "exemple": {"question": "Conjugue « venir » au passé simple avec « ils ».",
                    "etapes": ["« venir » est irrégulier : il vint, ils vinrent.", "Ils vinrent."]},
    },
    {
        "id": "fr-cm2-temps-composes", "titre": "Les temps composés", "domaine": "Conjugaison",
        "resume": "Passé composé et plus-que-parfait.",
        "retenir": [
            "Passé composé : auxiliaire au présent + participe passé (j'ai mangé, je suis parti).",
            "Plus-que-parfait : auxiliaire à l'imparfait + participe passé (j'avais mangé, j'étais parti).",
            "Avec « être », le participe passé s'accorde avec le sujet : elles étaient arrivées.",
            "Avec « avoir », il ne s'accorde pas avec le sujet : elles avaient mangé.",
        ],
        "exemple": {"question": "Conjugue « partir » au plus-que-parfait avec « elles ».",
                    "etapes": ["« partir » se conjugue avec « être ».", "« être » à l'imparfait : elles étaient.",
                               "Participe accordé au féminin pluriel : parties.", "Elles étaient parties."]},
    },
    {
        "id": "fr-cm2-fonctions", "titre": "Les fonctions dans la phrase", "domaine": "Grammaire",
        "resume": "Sujet, COD, COI, complément circonstanciel, attribut du sujet.",
        "retenir": [
            "Le sujet fait l'action : « C'est … qui » + verbe.",
            "Le COD répond à « quoi ? » ou « qui ? » après le verbe : Hugo promène son chien.",
            "Le COI répond à « à qui ? », « de quoi ? »… : Léa téléphone à sa grand-mère.",
            "Le complément circonstanciel dit où, quand, comment ; on peut le déplacer ou le supprimer.",
            "L'attribut du sujet suit un verbe d'état (être, sembler, devenir, paraître, rester) : Mon oncle est boulanger.",
        ],
        "exemple": {"question": "Dans « Chaque matin, Hugo promène son chien », quelle est la fonction de « son chien » ?",
                    "etapes": ["Hugo promène quoi ? Son chien.", "Pas de préposition : c'est le COD."]},
    },
    {
        "id": "fr-cm2-homophones", "titre": "Les homophones (suite)", "domaine": "Orthographe",
        "resume": "ce / se, ces / ses, c'est / s'est, leur / leurs, la / l'a / là.",
        "retenir": [
            "ce / se : « se » va avec un verbe (il se lave) ; « ce » va avec un nom (ce livre).",
            "ces / ses : « ses » = les siens (ses jouets) ; « ces » montre (ces nuages-là).",
            "c'est / s'est : « s'est » vient d'un verbe en « se » (il s'est levé) ; « c'est » = cela est.",
            "leur / leurs : devant un verbe, « leur » ne prend jamais de s (je leur parle).",
            "la / l'a / là : « l'a » = l'avait ; « là » indique un lieu ; sinon « la ».",
        ],
        "exemple": {"question": "Il ___ blessé au genou. (c'est ou s'est ?)",
                    "etapes": ["Le verbe est « se blesser » : il s'est blessé.", "J'écris « s'est »."]},
    },
    {
        "id": "fr-cm2-participe", "titre": "Le participe passé", "domaine": "Orthographe",
        "resume": "-é ou -er ? Et l'accord du participe passé avec être.",
        "retenir": [
            "-é ou -er ? Je remplace par « vendre » ou « vendu ». Il va manger (vendre) ; il a mangé (vendu).",
            "Après une préposition (à, de, pour, sans), le verbe est à l'infinitif : pour manger.",
            "Avec « être », le participe passé s'accorde avec le sujet : elle est partie, ils sont venus.",
            "Avec « avoir », le participe passé ne s'accorde pas avec le sujet : elles ont mangé.",
        ],
        "exemple": {"question": "Les filles sont (arriver) …",
                    "etapes": ["Auxiliaire « être » : le participe s'accorde avec le sujet.",
                               "« Les filles » est féminin pluriel.", "Les filles sont arrivées."]},
    },
    {
        "id": "fr-cm2-vocabulaire", "titre": "Le vocabulaire", "domaine": "Vocabulaire",
        "resume": "Synonymes, contraires, préfixes et familles de mots.",
        "retenir": [
            "Un synonyme a un sens proche (content → heureux) ; un contraire a un sens opposé (grand → petit).",
            "Un préfixe se place devant le radical et change le sens : possible → impossible, faire → défaire.",
            "im- devant m, b, p (impoli) ; il- devant l (illisible) ; ir- devant r (irrégulier).",
            "Les mots d'une même famille ont le même radical et un sens commun : dent, dentiste, dentifrice.",
        ],
        "exemple": {"question": "Forme le contraire de « lisible ».",
                    "etapes": ["Le mot commence par l : le préfixe est il-.", "lisible → illisible."]},
    },
]

SIXIEME = [
    {
        "id": "fr-6e-conjugaison", "titre": "Conjuguer à tous les temps", "domaine": "Conjugaison",
        "resume": "Indicatif (présent, futur, imparfait, passé simple, passé composé, plus-que-parfait), "
                  "conditionnel et impératif.",
        "retenir": [
            "Passé simple à toutes les personnes : je chantai, tu chantas, il chanta, nous chantâmes, "
            "vous chantâtes, ils chantèrent.",
            "2e groupe et beaucoup d'irréguliers : -is, -is, -it, -îmes, -îtes, -irent (je finis, nous finîmes).",
            "Être : je fus, nous fûmes ; avoir : j'eus, nous eûmes ; venir : je vins, nous vînmes.",
            "Temps composés : auxiliaire + participe passé ; accord avec le sujet quand l'auxiliaire est « être ».",
        ],
        "exemple": {"question": "Conjugue « finir » au passé simple avec « nous ».",
                    "etapes": ["2e groupe : -îmes avec « nous ».", "Nous finîmes."]},
    },
    {
        "id": "fr-6e-classes", "titre": "Les classes de mots", "domaine": "Grammaire",
        "resume": "Mots variables et invariables : adverbe, préposition, conjonction de coordination.",
        "retenir": [
            "Variables : nom, déterminant, adjectif, pronom, verbe.",
            "Invariables : l'adverbe (très, vite, demain, lentement), la préposition (à, de, sur, avec, vers, en) "
            "et la conjonction de coordination (mais, ou, et, donc, or, ni, car).",
            "Beaucoup d'adverbes finissent par -ment : lentement, doucement.",
        ],
        "exemple": {"question": "Dans « Elle marche lentement vers l'école », quelle est la classe de « vers » ?",
                    "etapes": ["« vers » ne change jamais (invariable).", "Il introduit le complément « l'école ».",
                               "C'est une préposition."]},
    },
    {
        "id": "fr-6e-fonctions", "titre": "Les fonctions", "domaine": "Grammaire",
        "resume": "Fonctions dans la phrase et dans le groupe nominal : épithète, complément du nom.",
        "retenir": [
            "Dans la phrase : sujet, COD, COI, complément circonstanciel, attribut du sujet.",
            "Dans le groupe nominal : l'épithète est un adjectif collé au nom (un pull rouge).",
            "Le complément du nom précise un nom, souvent avec « de » : la maison de mes voisins.",
            "Attention : après un verbe d'état, l'adjectif est attribut (le pull est rouge), pas épithète.",
        ],
        "exemple": {"question": "Dans « Le vélo de Sami est neuf », quelle est la fonction de « de Sami » ?",
                    "etapes": ["« de Sami » précise le nom « vélo ».", "C'est un complément du nom."]},
    },
    {
        "id": "fr-6e-phrase", "titre": "La phrase", "domaine": "Grammaire",
        "resume": "Types de phrases ; phrase simple et phrase complexe.",
        "retenir": [
            "Déclarative : elle informe. Interrogative : elle pose une question (?). "
            "Exclamative : elle exprime une émotion (!). Injonctive : elle donne un ordre ou un conseil.",
            "Une phrase simple a un seul verbe conjugué ; une phrase complexe en a plusieurs.",
            "Un infinitif (chanter) ne compte pas comme verbe conjugué.",
        ],
        "exemple": {"question": "« Quand il pleut, je reste à la maison » : simple ou complexe ?",
                    "etapes": ["Verbes conjugués : « pleut » et « reste ».", "Deux verbes : phrase complexe."]},
    },
    {
        "id": "fr-6e-accords", "titre": "Les accords", "domaine": "Orthographe",
        "resume": "Participe passé avec être et avoir, accords dans le groupe nominal.",
        "retenir": [
            "Avec « être », le participe passé s'accorde avec le sujet : les filles sont parties.",
            "Avec « avoir », il ne s'accorde pas avec le sujet : les filles ont mangé une glace.",
            "L'adjectif s'accorde en genre et en nombre avec le nom : des chemises blanches.",
            "Pluriels particuliers : des chevaux, des bijoux, des pneus, des travaux.",
        ],
        "exemple": {"question": "Les voitures sont (partir) …",
                    "etapes": ["Auxiliaire « être » : accord avec le sujet.", "« Les voitures » : féminin pluriel.",
                               "Les voitures sont parties."]},
    },
    {
        "id": "fr-6e-vocabulaire", "titre": "Le vocabulaire", "domaine": "Vocabulaire",
        "resume": "Sens propre et sens figuré, niveaux de langue, préfixes.",
        "retenir": [
            "Sens propre : le sens premier, concret (le lion dévore sa proie). "
            "Sens figuré : une image (il dévore son livre).",
            "Niveaux de langue : familier (entre copains), courant (tous les jours), soutenu (très soigné).",
            "Un préfixe change le sens du mot : in-, im-, il-, ir-, dé-, mé-.",
        ],
        "exemple": {"question": "« Il a un cœur de pierre » : sens propre ou figuré ?",
                    "etapes": ["Son cœur n'est pas vraiment en pierre.", "C'est une image : sens figuré."]},
    },
]

PAR_CLASSE = {"CM1": CM1, "CM2": CM2, "6e": SIXIEME}
