"""
La maîtresse virtuelle : elle lit à voix haute les leçons, les énoncés, les
corrections et les réponses du tuteur, avec la synthèse vocale d'OpenAI.

- Le texte est d'abord réécrit pour l'oral (« 47 × 23 » → « 47 fois 23 »,
  « 3/4 » → « 3 quarts », « cm² » → « centimètres carrés »).
- Chaque audio est gardé sur le disque (volume ecole_data) : un texte déjà
  lu ne coûte plus rien. Seuls les audios nouveaux comptent dans le plafond
  du jour.
- Sans clé OpenAI, la page se rabat sur la voix du navigateur.
"""

import hashlib
import json
import os
import re
import urllib.error
import urllib.request
from pathlib import Path

URL_VOIX = "https://api.openai.com/v1/audio/speech"
MAX_TEXTE = 1500
MAX_FICHIERS = 3000  # au-delà, les audios les plus anciens sont effacés
NOM_AUDIO = re.compile(r"^[0-9a-f]{64}$")

UNITES = {
    "km²": "kilomètres carrés", "hm²": "hectomètres carrés", "dam²": "décamètres carrés",
    "m²": "mètres carrés", "dm²": "décimètres carrés", "cm²": "centimètres carrés", "mm²": "millimètres carrés",
    "cm³": "centimètres cubes", "dm³": "décimètres cubes", "m³": "mètres cubes",
}
DENOMINATEURS = {2: ("demi", "demis"), 3: ("tiers", "tiers"), 4: ("quart", "quarts"),
                 10: ("dixième", "dixièmes"), 100: ("centième", "centièmes"), 1000: ("millième", "millièmes")}
SYMBOLES = [
    ("×", " fois "), ("+", " plus "), ("÷", " divisé par "), ("−", " moins "), ("≈", " environ "), ("≤", " inférieur ou égal à "),
    ("≥", " supérieur ou égal à "), ("<", " plus petit que "), (">", " plus grand que "), ("=", " égale "),
    ("→", ", "), ("✓", ""), ("★", ""), ("°", " degrés"), ("%", " pour cent"), ("π", " pi "),
]


def fraction_orale(m: re.Match) -> str:
    a, b = int(m.group(1)), int(m.group(2))
    if b in DENOMINATEURS:
        singulier, pluriel = DENOMINATEURS[b]
        return f"{a} {singulier if a == 1 else pluriel}"
    return f"{a} sur {b}"


def pour_la_voix(texte: str) -> str:
    """Réécrit un texte de maths pour qu'il se lise bien à voix haute."""
    t = texte.replace("\n", ". ")
    # « 36 408 » → « 36408 » : sinon la voix lit deux nombres
    while re.search(r"(\d)[  ](\d{3})(?!\d)", t):
        t = re.sub(r"(\d)[  ](\d{3})(?!\d)", r"\1\2", t)
    for unite, mots in UNITES.items():
        t = re.sub(rf"(?<![A-Za-zé]){unite}", mots, t)
    t = re.sub(r"(?<![\d,])(\d+)/(\d+)", fraction_orale, t)
    t = re.sub(r"…/(\d+)", r"combien sur \1", t)
    # « … » dans un calcul : une case à trouver ; ailleurs (« nous … ») : un simple silence
    t = re.sub(r"(?<=[=×+−÷<>]) ?…|…(?= ?[=×+−÷<>])", " combien ", t)
    t = t.replace("…", "…, ")
    t = t.replace("___", "…, ")
    for symbole, mots in SYMBOLES:
        t = t.replace(symbole, mots)
    t = re.sub(r"\.\s*\.", ".", t)
    return re.sub(r"\s+", " ", t).strip()


class VoixIndisponible(Exception):
    pass


class Voix:
    def __init__(self, cle: str | None, modele: str, voix: str, dossier: str):
        self.cle = cle
        self.modele = modele
        self.voix = voix
        self.dossier = Path(dossier)

    @property
    def active(self) -> bool:
        return bool(self.cle)

    def nom(self, texte: str, age: int) -> str:
        return hashlib.sha256(json.dumps([self.modele, self.voix, age, texte]).encode()).hexdigest()

    def chemin(self, nom: str) -> Path | None:
        if not NOM_AUDIO.match(nom):
            return None
        return self.dossier / f"{nom}.mp3"

    def deja_lu(self, nom: str) -> bool:
        chemin = self.chemin(nom)
        return bool(chemin and chemin.exists())

    def consignes(self, age: int) -> str:
        return (f"Tu es une maîtresse d'école française, chaleureuse et calme, qui parle à un enfant de {age} ans. "
                "Parle lentement et articule bien, surtout les nombres. Ton encourageant, jamais moqueur. "
                "Prononce les mots anglais avec un bon accent anglais, et l'arabe en arabe standard, "
                "en articulant chaque lettre.")

    def generer(self, texte: str, age: int) -> str:
        """Crée l'audio s'il n'existe pas encore. Renvoie son nom."""
        nom = self.nom(texte, age)
        chemin = self.chemin(nom)
        if chemin.exists():
            return nom
        requete = urllib.request.Request(
            URL_VOIX, method="POST",
            data=json.dumps({"model": self.modele, "voice": self.voix, "input": texte,
                             "instructions": self.consignes(age), "response_format": "mp3"}).encode(),
            headers={"Authorization": f"Bearer {self.cle}", "Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(requete, timeout=60) as r:
                audio = r.read()
        except (urllib.error.URLError, TimeoutError) as e:
            raise VoixIndisponible(str(e)) from e
        if not audio:
            raise VoixIndisponible("audio vide")
        self.dossier.mkdir(parents=True, exist_ok=True)
        provisoire = chemin.with_suffix(".tmp")
        provisoire.write_bytes(audio)
        provisoire.replace(chemin)
        self.nettoyer()
        return nom

    def nettoyer(self):
        fichiers = sorted(self.dossier.glob("*.mp3"), key=lambda f: f.stat().st_mtime)
        for f in fichiers[:max(0, len(fichiers) - MAX_FICHIERS)]:
            f.unlink(missing_ok=True)


def depuis_environnement(db: str) -> Voix:
    return Voix(
        cle=os.environ.get("ECOLE_OPENAI_API_KEY") or None,
        modele=os.environ.get("ECOLE_VOIX_MODELE", "gpt-4o-mini-tts"),
        voix=os.environ.get("ECOLE_VOIX", "coral"),
        dossier=os.environ.get("ECOLE_VOIX_DOSSIER", str(Path(db).parent / "voix")),
    )
