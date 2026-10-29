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
