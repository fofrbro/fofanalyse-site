# Espace de révision CM1 (« Mon cahier de maths »)

`https://fofanalyse.com/ecole/` : un espace privé où Mouaz révise les maths de
CM1. Pour chaque chapitre : une leçon courte, des séries de 8 exercices
interactifs qui s'adaptent à son niveau, une correction pas à pas, et un
tuteur IA qui réexplique quand il ne comprend pas. Le parent voit le suivi.

## Le principe : le code calcule, l'IA explique

Un modèle de langage peut se tromper dans un calcul. Ici, il ne calcule jamais
la bonne réponse :

| Qui | Fait quoi |
|---|---|
| `exercices.py` | tire chaque exercice au hasard, le résout, écrit la correction étape par étape (retenues comprises) |
| `stockage.py` | garde les réponses et le niveau de chaque chapitre (SQLite) |
| `tuteur.py` | réexplique *autrement*, en recevant la leçon, la bonne réponse calculée et la réponse de l'enfant |
| `lecons.py` | les 10 leçons du programme, affichées sur la page et données au tuteur comme référence (à la manière d'un RAG) |

## Chapitres

Nombres : les grands nombres, les fractions, les nombres décimaux.
Calcul : addition et soustraction posées, tables et calcul mental,
multiplication posée, division. Grandeurs et mesures : les mesures, le
périmètre. Problèmes : résoudre des problèmes en une ou deux étapes.

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

## Ajouter une matière plus tard

1. Une leçon dans `lecons.py` (même format : `retenir` et `exemple`).
2. Pour les maths : un générateur dans `exercices.py`, ajouté à `GENERATEURS`.
   Pour le français, les sciences ou l'histoire, où il n'y a pas de calcul à
   garantir, on peut écrire des banques de questions vérifiées à la main
   (QCM), ou laisser le tuteur proposer des questions à partir de la leçon.
3. Un test dans `test_ecole.py`.
