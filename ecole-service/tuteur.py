"""
Le tuteur IA : il explique, il ne calcule pas à la place du code.

Deux usages :
- répondre aux questions de l'élève sur une leçon (la leçon lui est donnée
  comme référence, à la manière d'un RAG) ;
- réexpliquer un exercice autrement, quand l'élève s'est trompé : il reçoit
  l'énoncé, la bonne réponse et les étapes calculées en Python, et la
  réponse fausse de l'élève, pour l'aider à voir son erreur.

Garde-fous : messages courts et bornés, historique limité, plafond d'appels
par jour, filtre de modération d'OpenAI sur chaque message de l'enfant,
consignes strictes (rester sur le travail scolaire, ne jamais demander
d'information personnelle, renvoyer vers un adulte en cas de souci).
"""

import json
import os
import urllib.error
import urllib.request

URL_CHAT = "https://api.openai.com/v1/chat/completions"
URL_MODERATION = "https://api.openai.com/v1/moderations"

MAX_QUESTION = 400
MAX_HISTORIQUE = 6

REPONSE_BLOQUEE = ("Je ne peux pas t'aider avec ce message. Si quelque chose te tracasse, "
                   "parles-en à Papa ou à un adulte de confiance. On reprend les maths ?")


def consignes(prenom: str, classe: str = "CM1", age: int = 9, matiere: str = "Mathématiques") -> str:
    return f"""Tu es le tuteur de {prenom}, un élève de {classe} ({age} ans), en France. La leçon du jour est
en {matiere.lower()}.
Tu l'aides à comprendre ses leçons et ses exercices, sur le site que son papa a créé pour lui.

Ta façon de parler :
- Tu tutoies {prenom}, en français simple, avec des phrases courtes. Pas de mots compliqués.
- 120 mots au maximum (sauf pour un cours complet, quand on te le demande). Une idée à la fois.
- Tes réponses sont souvent dites à voix haute : écris comme on parle, sans symboles ni listes.
- Tu es patient et encourageant, sans en faire trop. Une erreur, c'est normal : on apprend en se trompant.
- Tu utilises des exemples concrets de la vie d'un enfant (billes, bonbons, pizza, argent de poche, récré).
- Tu peux écrire les calculs ou les exemples ligne par ligne. Pas de tableau, pas de LaTeX, pas de lien.
- En français, l'orthographe compte : tes réponses sont sans faute, et tu respectes les accents.

Ta méthode :
- Tu suis la méthode de la leçon fournie (c'est celle de l'école française) et ses mots. La leçon peut
  venir d'une classe d'avant : {prenom} révise. Reste alors au niveau de cette leçon.
- Pour un exercice, tu guides avec une question ou un indice avant de tout donner, sauf si on te demande
  d'expliquer une correction : alors tu montres les étapes.
- Quand une bonne réponse t'est fournie, elle est juste : appuie-toi dessus, ne refais pas un autre calcul.
- Si {prenom} demande juste la réponse d'un devoir, aide-le à la trouver lui-même au lieu de la donner.

Tes limites :
- Tu parles uniquement de l'école (la matière de la leçon surtout, et les autres matières de {classe}
  si on te le demande).
  Pour toute autre demande, réponds gentiment que tu es là pour les leçons, et propose de reprendre.
- Tu ne demandes jamais d'information personnelle (nom de famille, adresse, école, photos, mots de passe).
- Si {prenom} semble triste, inquiet, en danger, ou parle de quelque chose de grave, tu ne poses pas
  de questions : tu lui dis avec douceur d'en parler tout de suite à son papa ou à un adulte de confiance.
- Tu ne prétends pas être un humain."""


class TuteurIndisponible(Exception):
    pass


class Tuteur:
    def __init__(self, cle: str | None, modele: str, prenom: str):
        self.cle = cle
        self.modele = modele
        self.prenom = prenom

    @property
    def actif(self) -> bool:
        return bool(self.cle)

    def _post(self, url, donnees, delai=30):
        requete = urllib.request.Request(
            url, data=json.dumps(donnees).encode(), method="POST",
            headers={"Authorization": f"Bearer {self.cle}", "Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(requete, timeout=delai) as r:
                return json.loads(r.read())
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as e:
            raise TuteurIndisponible(str(e)) from e

    def message_autorise(self, texte: str) -> bool:
        """Filtre de modération d'OpenAI (gratuit). En cas de panne, on laisse passer :
        les consignes du tuteur restent le second garde-fou."""
        try:
            r = self._post(URL_MODERATION, {"model": "omni-moderation-latest", "input": texte}, delai=10)
            return not r["results"][0]["flagged"]
        except (TuteurIndisponible, KeyError, IndexError):
            return True

    def _discuter(self, messages, classe, age, matiere, longueur=350) -> str:
        r = self._post(URL_CHAT, {
            "model": self.modele,
            "messages": [{"role": "system", "content": consignes(self.prenom, classe, age, matiere)}] + messages,
            "max_completion_tokens": longueur,
            "temperature": 0.4,
        })
        try:
            return r["choices"][0]["message"]["content"].strip()
        except (KeyError, IndexError, AttributeError) as e:
            raise TuteurIndisponible("réponse inattendue") from e

    def repondre(self, lecon: str, question: str, historique: list[dict], classe="CM1", age=9,
                 matiere="Mathématiques") -> str:
        messages = [{"role": "user", "content": f"Voici la leçon de référence (ne la recopie pas) :\n{lecon}"},
                    {"role": "assistant", "content": "D'accord, je m'appuie sur cette leçon."}]
        for m in historique[-MAX_HISTORIQUE:]:
            if m.get("role") in ("user", "assistant") and isinstance(m.get("content"), str):
                messages.append({"role": m["role"], "content": m["content"][:800]})
        messages.append({"role": "user", "content": question[:MAX_QUESTION]})
        return self._discuter(messages, classe, age, matiere)

    def expliquer_lecon(self, lecon: str, classe="CM1", age=9, matiere="Mathématiques") -> str:
        """Le cours de la maîtresse, à dire à voix haute : il suit la leçon, sans rien inventer."""
        consigne = (
            f"{lecon}\n\n"
            f"Fais maintenant le cours de cette leçon à {self.prenom}, à voix haute, comme une maîtresse en classe. "
            "Ce texte sera lu par une voix de synthèse, alors :\n"
            "- parle naturellement, à l'oral, en tutoyant ; phrases courtes ;\n"
            f"- commence par accrocher {self.prenom} avec une situation de la vie de tous les jours ;\n"
            "- explique les points « À retenir » dans l'ordre, avec tes mots, sans en ajouter ni en oublier ;\n"
            "- reprends l'exemple de la leçon, étape par étape ; n'invente pas d'autre calcul ni d'autre fait ;\n"
            "- écris tout en toutes lettres comme on le dit : « sept fois huit font cinquante-six », "
            "« trois quarts », jamais de symboles, de listes, de titres ni d'émojis ;\n"
            "- termine par une petite question pour vérifier qu'il a compris, puis encourage-le à faire les exercices ;\n"
            "- entre 180 et 260 mots, en 4 à 6 paragraphes séparés par une ligne vide."
        )
        return self._discuter([{"role": "user", "content": consigne}], classe, age, matiere, longueur=900)

    def reexpliquer(self, lecon: str, ex: dict, reponse_eleve, classe="CM1", age=9,
                    matiere="Mathématiques") -> str:
        if isinstance(reponse_eleve, list):
            reponse_eleve = " ; ".join(f"{r} {c['label']}" for r, c in zip(reponse_eleve, ex["champs"] or []))
        contexte = (
            f"{lecon}\n\n"
            f"Exercice : {ex['enonce']}{(' (en ' + ex['unite'] + ')') if ex.get('unite') else ''}\n"
            f"Réponse de {self.prenom} : {reponse_eleve}\n"
            f"Bonne réponse (calculée, juste) : {ex['reponse_texte']}\n"
            f"Correction officielle :\n{ex['explication']}\n\n"
            f"{self.prenom} n'a pas compris. Explique-lui autrement que la correction officielle : "
            f"devine d'où vient probablement son erreur (sans le gronder), puis montre la méthode "
            f"avec une image ou un exemple concret. Termine par une petite question pour vérifier qu'il a compris."
        )
        return self._discuter([{"role": "user", "content": contexte}], classe, age, matiere, longueur=450)


def depuis_environnement() -> Tuteur:
    return Tuteur(
        cle=os.environ.get("ECOLE_OPENAI_API_KEY") or None,
        modele=os.environ.get("ECOLE_OPENAI_MODEL", "gpt-4o-mini"),
        prenom=os.environ.get("ECOLE_PRENOM", "Mouaz"),
    )
