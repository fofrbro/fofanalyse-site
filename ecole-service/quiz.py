"""
Matières « à connaissances » : sciences, histoire, géographie, anglais, EMC.

Ici, rien à calculer : chaque chapitre a sa leçon et une banque de
questions écrites et vérifiées à la main (fichiers quiz_*.py). Une question
est un tuple :

    (énoncé, bonne réponse, [mauvaises réponses], explication, niveau)

- bonne réponse en texte + mauvaises réponses → question à choix ;
- bonne réponse en liste (formes acceptées) + None → réponse à écrire
  (anglais surtout ; « a », « an » et « the » devant sont acceptés).
Le niveau (1 à 3) suit celui de l'élève dans le chapitre : on tire surtout
des questions de son niveau (7 fois sur 10), sinon dans tout le chapitre.
"""

import quiz_anglais
import quiz_emc
import quiz_geographie
import quiz_histoire
import quiz_sciences
from exercices import exercice

MODULES = {"sciences": quiz_sciences, "histoire": quiz_histoire, "geographie": quiz_geographie,
           "anglais": quiz_anglais, "emc": quiz_emc}
NOMS = {"sciences": "Sciences", "histoire": "Histoire", "geographie": "Géographie", "anglais": "Anglais",
        "emc": "EMC"}


def formes_anglaises(reponses: list[str]) -> list[str]:
    acceptees = list(reponses)
    for r in reponses:
        acceptees += [f"a {r}", f"an {r}", f"the {r}"]
    return acceptees


def question_vers_exercice(question, anglais: bool, rng):
    enonce, bonne, mauvaises, explication, _ = question
    if isinstance(bonne, list):
        acceptees = formes_anglaises(bonne) if anglais else bonne
        return exercice("texte", enonce, acceptees, [explication, f"Réponse : {bonne[0]}"],
                        "Relis la leçon : la réponse y est.", reponse_texte=bonne[0])
    options = [bonne, *mauvaises]
    rng.shuffle(options)
    return exercice("choix", enonce, bonne, [explication, f"Réponse : {bonne}"],
                    "Relis « À retenir » dans la leçon, puis élimine les réponses impossibles.", options=options)


def generateur(chapitre: dict, anglais: bool):
    questions = chapitre["questions"]

    def tirer(rng, niveau):
        de_son_niveau = [q for q in questions if q[4] == niveau]
        pioche = de_son_niveau if de_son_niveau and rng.random() < 0.7 else questions
        return question_vers_exercice(rng.choice(pioche), anglais, rng)

    tirer.__name__ = f"quiz_{chapitre['id']}"
    return tirer


def lecons_par_classe(matiere: str) -> dict[str, list[dict]]:
    """Les leçons (sans les questions), par classe, pour lecons.py."""
    return {classe: [{k: v for k, v in c.items() if k != "questions"} for c in chapitres]
            for classe, chapitres in MODULES[matiere].CHAPITRES.items()}


GENERATEURS = {c["id"]: [generateur(c, matiere == "anglais")]
               for matiere, module in MODULES.items()
               for chapitres in module.CHAPITRES.values() for c in chapitres}
