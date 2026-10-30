# Espace de révision du CM1 à la 6e (« Mon cahier »)

`https://fofanalyse.com/ecole/` : un espace privé où Mouaz révise toutes les
matières de sa classe (CM1, CM2 ou 6e) : maths, français, sciences, histoire,
géographie, anglais et enseignement moral et civique, plus une rubrique
d'arabe. Pour chaque chapitre : une leçon courte, des séries de 8 exercices
interactifs qui s'adaptent à son niveau, une correction pas à pas, et un
tuteur IA qui réexplique quand il ne comprend pas. Le parent voit le suivi.

## Le principe : le code calcule, l'IA explique

Un modèle de langage peut se tromper dans un calcul. Ici, il ne calcule jamais
la bonne réponse :

| Qui | Fait quoi |
|---|---|
| `exercices.py`, `exercices_cm2.py`, `exercices_6e.py` | tirent chaque exercice au hasard, le résolvent (Decimal pour les virgules), écrivent la correction étape par étape |
| `conjugaison.py` | calcule les formes des verbes (1er et 2e groupes, 15 irréguliers, 8 temps, accord avec « être ») |
| `francais.py`, `francais_banques.py` | exercices de français : conjugaison et accords calculés, grammaire, homophones et vocabulaire tirés de banques vérifiées à la main |
| `quiz.py`, `quiz_*.py` | sciences, histoire, géographie, anglais, EMC : leçons et banques de questions écrites et vérifiées à la main |
| `arabe.py` | rubrique d'arabe : table des 28 lettres, formes attachées, voyelles, mots et phrases vocalisés |
| `coran.py` | Coran : télécharge et vérifie le texte et la traduction, garde les récitations ; rien n'est généré |
| `catalogue.py` | réunit les générateurs de toutes les classes et tire une série |
| `stockage.py` | garde la classe choisie, les réponses et le niveau de chaque chapitre (SQLite) |
| `tuteur.py` | réexplique *autrement*, en recevant la leçon, la bonne réponse calculée et la réponse de l'enfant ; il connaît sa classe et son âge |
| `lecons.py`, `lecons_cm2.py`, `lecons_6e.py`, `lecons_francais.py` | les leçons, classe par classe, affichées sur la page et données au tuteur comme référence (à la manière d'un RAG) |

## Classes et chapitres

**CM1** (10 chapitres) — Nombres : les grands nombres, les fractions, les
nombres décimaux. Calcul : addition et soustraction posées, tables et calcul
mental, multiplication posée, division. Grandeurs et mesures : les mesures,
le périmètre. Problèmes en une ou deux étapes.

**CM2** (9 chapitres) — Nombres jusqu'au milliard, fractions et fractions
décimales, décimaux jusqu'aux millièmes. Multiplier (décimal × entier,
× 10/100/1 000, multiplication posée), division (diviseur à deux chiffres,
quotient décimal). Proportionnalité et pourcentages simples. Mesures et
durées, périmètres et aires. Problèmes à étapes avec des décimaux.

**6e** (8 chapitres) — Nombres décimaux (fractions décimales, encadrer,
ranger, × 0,1), calculer avec des décimaux (produit, division, ordre des
calculs), multiples et diviseurs (critères, division euclidienne), fractions
(quotient, fractions égales, simplifier, additionner), proportionnalité
(pourcentages, échelles), cercle, aires et volumes, angles, problèmes.

**Français** (6 chapitres par classe, onglet « Français » sur l'accueil) —
CM1 : présent, futur et imparfait, passé composé, classes de mots,
homophones (a/à, et/est, son/sont, on/ont, ou/où), accords dans le groupe
nominal. CM2 : temps simples (dont passé simple et conditionnel), temps
composés, fonctions, homophones (ce/se, ces/ses, c'est/s'est, leur/leurs,
la/l'a/là), participe passé (-é/-er, accord avec être), vocabulaire. 6e :
conjugaison à tous les temps, classes de mots (adverbe, préposition,
conjonction), fonctions (épithète, complément du nom), la phrase, accords
du participe passé, vocabulaire (sens propre ou figuré, niveaux de langue).

Les réponses s'écrivent au clavier : les accents comptent (c'est de
l'orthographe), pas la casse ni le point final. Une rangée de lettres
accentuées aide à les taper. Les verbes à radical changeant (acheter,
appeler, préférer, payer…) ne sont pas proposés : le moteur ne les couvre
pas, plutôt que de risquer une forme fausse.

**Sciences, histoire, géographie, anglais, EMC** (onglets sur l'accueil) —
3 chapitres par matière et par classe (2 en EMC), qui suivent les thèmes du
programme du cycle 3 : par exemple, en histoire, « Et avant la France ? »,
« Le temps des rois », « La Révolution et l'Empire » au CM1. Chaque chapitre a
sa leçon et au moins 10 questions réparties sur les 3 niveaux. Il n'y a rien
à calculer : la bonne réponse est écrite dans la banque, avec son
explication. En anglais, le vocabulaire se tape au clavier (« a », « an »,
« the » acceptés devant le mot).

**Argent** (onglet « Argent », le même pour toutes les classes) — éducation
financière en 6 chapitres : pièces, billets et monnaie ; argent de poche et
budget ; bien acheter (comparer deux offres, soldes) ; besoins, envies et
épargne ; la banque et les moyens de payer (code secret, arnaques, paiement
en ligne) ; d'où vient l'argent (salaire, troc, impôts, prix). Les trois
premiers sont des calculs tirés et résolus par le code (`argent.py`, en
centimes) ; les trois autres, des questions vérifiées.

**Arabe** (onglet « Arabe », le même pour toutes les classes) — 7 chapitres :
les lettres (en trois groupes : nom, son, points), les lettres attachées
(début, milieu, fin d'un mot), les voyelles (fatha, kasra, damma, voyelles
longues, soukoun), premiers mots et chiffres, saluer et se présenter. Les
questions sont construites à partir de la table des lettres et de listes de
mots vocalisés avec leur transcription. Le texte arabe s'affiche en grand,
de droite à gauche, et la voix le lit. La police arabe est celle de
l'appareil (aucune ressource externe), agrandie pour être lisible.

**Coran** (onglet « Coran ») — Al-Fâtiha, puis le Juz 'Amma de la fin vers le
début (An-Nâs, Al-Falaq, Al-Ikhlâs… jusqu'à An-Naba'), 38 sourates.

- Règle absolue : ni le code ni l'IA n'écrivent le texte du Coran, et la voix
  de synthèse ne le lit jamais. Le tuteur IA n'intervient pas.
- Texte : Tanzil (lecture Hafs, écriture othmanie), par l'API alquran.cloud ;
  traduction de Muhammad Hamidullah, citée telle quelle. Le serveur les
  télécharge à la première visite, vérifie le nombre de versets de chaque
  sourate (refus si une seule ne correspond pas), sépare la basmala que l'API
  colle au 1er verset, puis garde le tout dans `/data/coran/texte.json`.
- Récitations : Mahmoud Khalil Al-Hussary (par défaut) ou Mishary Rashid
  Alafasy, verset par verset depuis everyayah.com, téléchargées à la première
  écoute puis gardées dans `/data/coran/audio`.
- Le professeur : pour chaque verset, 1) écouter 3 fois, 2) écouter puis
  répéter, 3) réciter sans regarder (le verset est flouté), 4) « Je l'ai
  retenu », puis réciter depuis le début avec le récitant. Un quiz « Quel
  verset vient ensuite ? » propose de vrais versets de la sourate. La
  progression est gardée et visible dans le suivi ; « Tout effacer » ne
  l'efface pas.

**À relire par un adulte** : ces contenus sont écrits à la main ; le code
vérifie leur cohérence (pas de doublon, la bonne réponse n'est pas parmi
les mauvaises, chaque niveau est représenté), pas leur exactitude.

**Changer de classe** : le parent choisit la classe dans « Suivi » (rien à
redéployer). `ECOLE_CLASSE` ne sert qu'au tout premier démarrage. Les
chapitres des classes d'avant restent ouverts, repliés sous « Réviser » sur
l'accueil, avec leurs niveaux et leurs étoiles.

Chaque chapitre a 3 niveaux. Seuls les derniers exercices du niveau en cours
comptent (fenêtre glissante) : on monte quand les 6 derniers sont justes du
premier coup, ou au moins 7 des 8 derniers ; on redescend quand 3 ou moins
des 6 derniers sont justes du premier coup. Le compte repart de zéro à chaque
changement de niveau. Il faut donc au moins 6 exercices par niveau (12 pour
atteindre le niveau 3), et une erreur ancienne ne bloque plus la progression.

## Accès

- **Code élève** (`ECOLE_CODE_ELEVE`) : leçons, exercices, tuteur.
- **Code parent** (`ECOLE_CODE_PARENT`) : tout cela, plus le suivi (activité
  sur 14 jours, réussite par chapitre, derniers exercices ratés, questions
  posées au tuteur) et le bouton « Tout effacer ».

La session est un cookie signé (HMAC), `HttpOnly`, `Secure`, `SameSite=Strict`,
valable 30 jours. Au-delà de 8 codes faux en 15 minutes depuis une même
adresse, la connexion est bloquée un quart d'heure.

## La maîtresse virtuelle

Une maîtresse qui fait cours, et non un lecteur de texte.

- **« 👩‍🏫 La maîtresse m'explique »** (sur chaque leçon) : le tuteur IA écrit
  une vraie explication orale de la leçon (accroche, points « À retenir » dans
  l'ordre, l'exemple de la leçon étape par étape, une petite question à la
  fin), sans inventer d'autre calcul ni d'autre fait. Elle est gardée en base
  (table `explications`) : chaque leçon n'est expliquée par l'IA qu'une fois
  par classe. Elle est dite paragraphe par paragraphe (le suivant se prépare
  pendant que le précédent se dit), avec des sous-titres qui suivent.
- **🎤 Parler** : l'enfant pose sa question à voix haute ; elle est transcrite
  (`gpt-4o-mini-transcribe`), passe par le filtre de modération comme une
  question écrite, et la maîtresse répond à voix haute.
- **« Je n'ai pas compris »** : l'explication du tuteur est dite à voix haute.
  L'énoncé d'un exercice peut toujours être lu (🔊), pour les lecteurs débutants.
- **La voix** : `gpt-4o-mini-tts`, avec une consigne de jeu naturel
  (intonation, pauses, sourire dans la voix). Le parent écoute et choisit la
  voix dans « Suivi » (coral, sage, shimmer, nova, ballad, alloy, verse).
- Tout utilise la clé du tuteur (`ECOLE_OPENAI_API_KEY`). Les audios sont
  gardés dans `/data/voix` : un texte déjà dit ne coûte plus rien. Plafonds :
  `ECOLE_VOIX_PAR_JOUR` (audios nouveaux) et `ECOLE_IA_PAR_JOUR` (cours,
  questions et transcriptions). Sans clé, la page lit la leçon avec la voix
  de l'appareil.
- Coût (tarifs OpenAI de 2025, à vérifier) : un cours complet coûte de
  l'ordre de quelques centimes la première fois, puis plus rien.

## Nouvelles questions écrites par l'IA

Les chapitres calculés (maths, conjugaison et accords, calculs d'argent,
arabe) tirent de nouveaux exercices à chaque série. Les chapitres à questions
fixes (sciences, histoire, géographie, anglais, EMC, grammaire, homophones et
vocabulaire en français, notions d'argent) peuvent être enrichis :

- dans « Suivi », le bouton « ➕ Nouvelles » d'un chapitre fait écrire par
  l'IA des questions **à partir de la seule leçon** du chapitre, en lui
  donnant les questions déjà posées pour éviter les doublons ;
- le code contrôle leur forme (une seule bonne réponse, réponses toutes
  différentes, pas de doublon), puis **une seconde lecture par l'IA** refuse
  au moindre doute (réponse fausse ou absente de la leçon, ambiguïté, faute) ;
- **le parent garde ou refuse** chaque question (ou « Tout garder ») ; une
  case permet de valider automatiquement les questions vérifiées ;
- les questions gardées remplacent jusqu'à la moitié de chaque série du
  chapitre ; la progression n'est jamais effacée.

Chaque génération compte deux appels dans `ECOLE_IA_PAR_JOUR`.
`ECOLE_MODELE_DEVOIRS`, s'il est réglé, sert aussi ici.

## Devoirs en photo

Onglet « 📷 Mon devoir » : l'enfant photographie l'énoncé d'un exercice.

- La page réduit la photo (1 600 px au plus, JPEG) avant l'envoi ; le
  serveur vérifie que c'est bien une image, la passe au filtre de
  modération (qui accepte aussi les images), puis la confie au modèle de
  vision d'OpenAI.
- L'IA renvoie l'énoncé recopié, une **explication pour l'enfant** (ce qu'on
  lui demande, la règle utile, la méthode, un indice, **sans la réponse**),
  que la maîtresse lui dit à voix haute, et une **solution complète pour le
  parent**.
- La solution n'est jamais envoyée à la session de l'enfant tant que le
  parent ne l'a pas débloquée (bouton « Autoriser … à voir la solution »,
  réversible). Le parent peut aussi effacer un devoir et sa photo.
- La solution est proposée par l'IA : à vérifier, surtout pour les calculs.
  `ECOLE_MODELE_DEVOIRS` permet d'utiliser un modèle plus fort pour cette
  partie seulement (par exemple `gpt-4o`), plus cher mais plus fiable.
- Photos dans `/data/devoirs`, devoirs dans la table `devoirs`. Chaque photo
  compte comme un appel dans `ECOLE_IA_PAR_JOUR`.

## Garde-fous du tuteur

- Consignes strictes : français simple, 120 mots au plus, méthode de l'école
  française, uniquement le travail scolaire, aucune information personnelle
  demandée, renvoi vers un adulte si l'enfant semble inquiet.
- Filtre de modération d'OpenAI (gratuit) sur chaque question : un message
  bloqué reçoit une réponse fixe, et apparaît en rouge dans le suivi parent.
- Questions limitées à 400 caractères, historique limité aux 6 derniers
  messages, plafond d'appels par jour (`ECOLE_IA_PAR_JOUR`, 60 par défaut).
- Une clé OpenAI à part (`ECOLE_OPENAI_API_KEY`), dans un projet qui a sa
  propre limite de dépense mensuelle.

Coût (tarifs OpenAI de 2025, à vérifier) : avec `gpt-4o-mini`, une explication coûte de l'ordre d'un dixième de
centime ; 60 questions par jour pendant un mois restent sous 2 €.

## Données

Rien d'autre que le travail scolaire, dans `/data/ecole.db` (volume
`ecole_data`) : exercices proposés et réponses, niveaux, questions au tuteur.
Le prénom vient de `ECOLE_PRENOM`. Les questions au
tuteur passent par OpenAI (leçon, exercice et question, sans nom de famille).

## En local

```bash
cd ecole-service
pip install -r requirements.txt
python -m pytest -q
```

Pour essayer la page avec l'API, lancer le service puis servir `www/` par
le même serveur (la page appelle `/api/ecole/` sur sa propre adresse) ;
en ligne, c'est Caddy qui assemble les deux.

## Ajouter une classe plus tard (5e…)

1. `lecons_5e.py` (même format) et `exercices_5e.py` (un `GENERATEURS` dont
   les identifiants commencent par `5e-`, pour rester uniques).
2. Une ligne dans `CLASSES` (`lecons.py`) et une dans `catalogue.py`.
3. Les tests vérifient d'eux-mêmes chaque générateur à chaque niveau.

## Ajouter une matière plus tard

1. Une leçon dans le fichier de la classe (même format : `retenir` et `exemple`).
2. Pour les maths : un générateur dans le fichier d'exercices de la classe, ajouté à son `GENERATEURS`.
   Pour le français, les sciences ou l'histoire, où il n'y a pas de calcul à
   garantir, on peut écrire des banques de questions vérifiées à la main
   (QCM), ou laisser le tuteur proposer des questions à partir de la leçon.
3. Un test dans `test_ecole.py`.
