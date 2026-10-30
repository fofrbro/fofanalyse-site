"""
Le catalogue des générateurs d'exercices, toutes classes et matières
réunies, et le tirage d'une série. Les générateurs sont dans exercices.py
(maths de CM1 et outils communs), exercices_cm2.py, exercices_6e.py,
francais.py et quiz.py (sciences, histoire, géographie, anglais, EMC).
"""

import random

import arabe
import argent
import exercices
import exercices_6e
import exercices_cm2
import francais
import quiz

GENERATEURS = {**exercices.GENERATEURS, **exercices_cm2.GENERATEURS, **exercices_6e.GENERATEURS,
               **francais.GENERATEURS, **quiz.GENERATEURS, **arabe.GENERATEURS,
               **argent.GENERATEURS}


# Chapitres à questions fixes, que l'IA peut enrichir (bouton « Nouvelles questions » du parent).
# Les chapitres calculés (maths, conjugaison, calculs d'argent, arabe) se renouvellent déjà seuls.
CHAPITRES_QUESTIONS_IA = set(quiz.GENERATEURS) | {
    "fr-cm1-nature", "fr-cm1-homophones", "fr-cm2-fonctions", "fr-cm2-homophones", "fr-cm2-vocabulaire",
    "fr-6e-classes", "fr-6e-fonctions", "fr-6e-phrase", "fr-6e-vocabulaire",
    "arg-besoins", "arg-banque", "arg-travail",
}


def question_ia_valide(q, enonces_existants: set[str]) -> dict | None:
    """Contrôle par le code d'une question écrite par l'IA : complète, une seule bonne réponse,
    des réponses toutes différentes, pas de doublon. Renvoie la question nettoyée, ou None."""
    if not isinstance(q, dict):
        return None
    enonce, bonne = str(q.get("enonce", "")).strip(), str(q.get("bonne", "")).strip()
    mauvaises = [str(m).strip() for m in q.get("mauvaises", []) if str(m).strip()] if isinstance(q.get("mauvaises"), list) else []
    explication = str(q.get("explication", "")).strip()
    niveau = q.get("niveau") if q.get("niveau") in (1, 2, 3) else 2
    options = [bonne, *mauvaises]
    if not (8 <= len(enonce) <= 300 and bonne and explication and 2 <= len(mauvaises) <= 3):
        return None
    if len({o.lower() for o in options}) != len(options) or any(len(o) > 120 for o in options):
        return None
    if " ".join(enonce.lower().split()) in enonces_existants:
        return None
    return {"enonce": enonce, "bonne": bonne, "mauvaises": mauvaises[:3], "explication": explication[:400], "niveau": niveau}


def generer(chapitre: str, niveau: int, rng: random.Random | None = None, prenom: str = "Mouaz") -> dict:
    rng = rng or random.Random()
    niveau = max(1, min(3, niveau))
    choix = [g for g in GENERATEURS[chapitre] if getattr(g, "niveau_min", 1) <= niveau]
    g = rng.choice(choix)
    if getattr(g, "avec_prenom", False):
        return g(rng, niveau, prenom)
    return g(rng, niveau)


def serie(chapitre: str, niveau: int, nombre: int = 8, rng: random.Random | None = None,
          prenom: str = "Mouaz") -> list[dict]:
    """Une série d'exercices sans doublon (même énoncé et même texte arabe affiché)."""
    rng = rng or random.Random()
    vus, resultat = set(), []
    for _ in range(nombre * 6):
        ex = generer(chapitre, niveau, rng, prenom)
        cle = (ex["enonce"], ex.get("arabe"))
        if cle in vus:
            continue
        vus.add(cle)
        resultat.append(ex)
        if len(resultat) == nombre:
            break
    return resultat
