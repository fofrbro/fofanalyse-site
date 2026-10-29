# Espace de révision du CM1 à la 6e (« Mon cahier de maths »)

`https://fofanalyse.com/ecole/` : un espace privé où Mouaz révise les maths de
sa classe (CM1, CM2 ou 6e). Pour chaque chapitre : une leçon courte, des séries de 8 exercices
interactifs qui s'adaptent à son niveau, une correction pas à pas, et un
tuteur IA qui réexplique quand il ne comprend pas. Le parent voit le suivi.

## Le principe : le code calcule, l'IA explique

Un modèle de langage peut se tromper dans un calcul. Ici, il ne calcule jamais
la bonne réponse :

| Qui | Fait quoi |
|---|---|
| `exercices.py`, `exercices_cm2.py`, `exercices_6e.py` | tirent chaque exercice au hasard, le résolvent (Decimal pour les virgules), écrivent la correction étape par étape |
| `catalogue.py` | réunit les générateurs de toutes les classes et tire une série |
| `stockage.py` | garde la classe choisie, les réponses et le niveau de chaque chapitre (SQLite) |
| `tuteur.py` | réexplique *autrement*, en recevant la leçon, la bonne réponse calculée et la réponse de l'enfant ; il connaît sa classe et son âge |
| `lecons.py`, `lecons_cm2.py`, `lecons_6e.py` | les leçons, classe par classe, affichées sur la page et données au tuteur comme référence (à la manière d'un RAG) |

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

**Changer de classe** : le parent choisit la classe dans « Suivi » (rien à
redéployer). `ECOLE_CLASSE` ne sert qu'au tout premier démarrage. Les
chapitres des classes d'avant restent ouverts, repliés sous « Réviser » sur
l'accueil, avec leurs niveaux et leurs étoiles.

Chaque chapitre a 3 niveaux. Il monte d'un niveau après au moins 6 exercices
réussis à 85 % du premier coup, et redescend après au moins 4 exercices
réussis à 40 % ou moins.

## Accès

- **Code élève** (`ECOLE_CODE_ELEVE`) : leçons, exercices, tuteur.
- **Code parent** (`ECOLE_CODE_PARENT`) : tout cela, plus le suivi (activité
  sur 14 jours, réussite par chapitre, derniers exercices ratés, questions
  posées au tuteur) et le bouton « Tout effacer ».

La session est un cookie signé (HMAC), `HttpOnly`, `Secure`, `SameSite=Strict`,
valable 30 jours. Au-delà de 8 codes faux en 15 minutes depuis une même
adresse, la connexion est bloquée un quart d'heure.

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
