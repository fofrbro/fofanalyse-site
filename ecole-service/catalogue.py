"""
Le catalogue des générateurs d'exercices, toutes classes et matières
réunies, et le tirage d'une série. Les générateurs sont dans exercices.py
(maths de CM1 et outils communs), exercices_cm2.py, exercices_6e.py et
francais.py.
"""

import random

import exercices
import exercices_6e
import exercices_cm2
import francais

GENERATEURS = {**exercices.GENERATEURS, **exercices_cm2.GENERATEURS, **exercices_6e.GENERATEURS,
               **francais.GENERATEURS}


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
    """Une série d'exercices sans doublon d'énoncé."""
    rng = rng or random.Random()
    vus, resultat = set(), []
    for _ in range(nombre * 6):
        ex = generer(chapitre, niveau, rng, prenom)
        if ex["enonce"] in vus:
            continue
        vus.add(ex["enonce"])
        resultat.append(ex)
        if len(resultat) == nombre:
            break
    return resultat
