"""
La voix de la maîtresse virtuelle (synthèse vocale d'OpenAI) et son oreille
(transcription de ce que dit l'enfant). Ce que la maîtresse dit est écrit
par le tuteur IA (tuteur.py) : explication de la leçon, réponses aux
questions, explications d'une correction. Ici, on ne fait que le dire.

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
URL_TRANSCRIPTION = "https://api.openai.com/v1/audio/transcriptions"
MAX_AUDIO_ENFANT = 1_500_000  # environ une minute d'enregistrement

# Voix proposées au parent dans « Suivi » (il peut les écouter avant de choisir).
VOIX_DISPONIBLES = ["coral", "sage", "shimmer", "nova", "ballad", "alloy", "verse"]
TYPES_AUDIO = {"audio/webm": "webm", "audio/ogg": "ogg", "audio/mp4": "mp4", "audio/mpeg": "mp3",
               "audio/wav": "wav", "audio/x-m4a": "m4a"}
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
    def __init__(self, cle: str | None, modele: str, voix: str, dossier: str,
                 modele_transcription: str = "gpt-4o-mini-transcribe"):
        self.cle = cle
        self.modele = modele
        self.modele_transcription = modele_transcription
        self.voix = voix
        self.dossier = Path(dossier)

    @property
    def active(self) -> bool:
        return bool(self.cle)

    def nom(self, texte: str, age: int, voix: str | None = None) -> str:
        return hashlib.sha256(json.dumps([self.modele, voix or self.voix, age, texte, 2]).encode()).hexdigest()

    def chemin(self, nom: str) -> Path | None:
        if not NOM_AUDIO.match(nom):
            return None
        return self.dossier / f"{nom}.mp3"

    def deja_lu(self, nom: str) -> bool:
        chemin = self.chemin(nom)
        return bool(chemin and chemin.exists())

    def consignes(self, age: int) -> str:
        return (f"Tu es une vraie maîtresse d'école française qui fait cours à un enfant de {age} ans, assis à côté de toi. "
                "Parle de façon naturelle et vivante, comme une personne et non comme une machine qui lit : "
                "intonation expressive, sourire dans la voix, petites pauses entre les idées, "
                "un peu plus lentement et en appuyant sur les mots importants et sur les nombres. "
                "Quand tu poses une question, laisse-la vraiment sonner comme une question. "
                "Ton chaleureux et encourageant, jamais moqueur ni enfantin à l'excès. "
                "Les mots anglais se prononcent avec un bon accent anglais ; l'arabe, en arabe standard bien articulé.")

    def generer(self, texte: str, age: int, voix: str | None = None) -> str:
        """Crée l'audio s'il n'existe pas encore. Renvoie son nom."""
        voix = voix or self.voix
        nom = self.nom(texte, age, voix)
        chemin = self.chemin(nom)
        if chemin.exists():
            return nom
        requete = urllib.request.Request(
            URL_VOIX, method="POST",
            data=json.dumps({"model": self.modele, "voice": voix, "input": texte,
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

    def transcrire(self, audio: bytes, type_mime: str) -> str:
        """Ce que l'enfant a dit au micro, en texte (pour le poser au tuteur)."""
        extension = TYPES_AUDIO.get(type_mime.split(";")[0].strip(), "webm")
        limite = "----ecole" + hashlib.sha256(audio[:64]).hexdigest()[:16]
        morceaux = []
        for nom, valeur in (("model", self.modele_transcription), ("language", "fr"), ("response_format", "json")):
            morceaux.append(f'--{limite}\r\nContent-Disposition: form-data; name="{nom}"\r\n\r\n{valeur}\r\n'.encode())
        morceaux.append(f'--{limite}\r\nContent-Disposition: form-data; name="file"; filename="question.{extension}"\r\n'
                        f'Content-Type: {type_mime.split(";")[0]}\r\n\r\n'.encode() + audio + b"\r\n")
        morceaux.append(f"--{limite}--\r\n".encode())
        requete = urllib.request.Request(URL_TRANSCRIPTION, method="POST", data=b"".join(morceaux), headers={
            "Authorization": f"Bearer {self.cle}", "Content-Type": f"multipart/form-data; boundary={limite}"})
        try:
            with urllib.request.urlopen(requete, timeout=60) as r:
                return json.loads(r.read()).get("text", "").strip()
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as e:
            raise VoixIndisponible(str(e)) from e

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
        modele_transcription=os.environ.get("ECOLE_TRANSCRIPTION_MODELE", "gpt-4o-mini-transcribe"),
    )
