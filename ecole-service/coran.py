"""
Le Coran : apprendre par cœur Al-Fâtiha et le Juz 'Amma, verset par verset.

Règle absolue : ni le code ni l'IA n'écrivent le texte du Coran.
- Le texte (lecture Hafs, écriture othmanie) vient de Tanzil, par l'API
  alquran.cloud ; la traduction est celle de Muhammad Hamidullah, citée
  telle quelle. Le serveur les télécharge une seule fois, vérifie le nombre
  de versets de chaque sourate, puis les garde dans /data/coran.
- Les récitations sont celles de vrais récitants (everyayah.com), téléchargées
  verset par verset à la première écoute, puis gardées sur le serveur.
- Le tuteur IA n'intervient pas ici : aucune explication n'est générée.

Ordre d'apprentissage : Al-Fâtiha, puis le Juz 'Amma de la fin vers le début
(An-Nâs, Al-Falaq, Al-Ikhlâs…), comme on l'apprend traditionnellement.
"""

import json
import os
import re
import threading
import time
import urllib.error
import urllib.request
from pathlib import Path

API = "https://api.alquran.cloud/v1"
AUDIO = "https://everyayah.com/data/{dossier}/{sourate:03d}{verset:03d}.mp3"

RECITANTS = {
    "husary": {"nom": "Mahmoud Khalil Al-Hussary", "dossier": "Husary_128kbps"},
    "alafasy": {"nom": "Mishary Rashid Alafasy", "dossier": "Alafasy_128kbps"},
}

# numéro, nom en français, nombre de versets (contrôlé à chaque téléchargement)
SOURATES = [
    (1, "Al-Fâtiha", 7), (114, "An-Nâs", 6), (113, "Al-Falaq", 5), (112, "Al-Ikhlâs", 4), (111, "Al-Masad", 5),
    (110, "An-Nasr", 3), (109, "Al-Kâfiroûn", 6), (108, "Al-Kawthar", 3), (107, "Al-Mâ'oûn", 7), (106, "Qouraych", 4),
    (105, "Al-Fîl", 5), (104, "Al-Houmaza", 9), (103, "Al-'Asr", 3), (102, "At-Takâthour", 8), (101, "Al-Qâri'a", 11),
    (100, "Al-'Âdiyât", 11), (99, "Az-Zalzala", 8), (98, "Al-Bayyina", 8), (97, "Al-Qadr", 5), (96, "Al-'Alaq", 19),
    (95, "At-Tîn", 8), (94, "Ach-Charh", 8), (93, "Ad-Douhâ", 11), (92, "Al-Layl", 21), (91, "Ach-Chams", 15),
    (90, "Al-Balad", 20), (89, "Al-Fajr", 30), (88, "Al-Ghâchiya", 26), (87, "Al-A'lâ", 19), (86, "At-Târiq", 17),
    (85, "Al-Bouroûj", 22), (84, "Al-Inchiqâq", 25), (83, "Al-Moutaffifîn", 36), (82, "Al-Infitâr", 19),
    (81, "At-Takwîr", 29), (80, "'Abasa", 42), (79, "An-Nâzi'ât", 46), (78, "An-Naba'", 40),
]
PAR_NUMERO = {s[0]: s for s in SOURATES}

SOURCES = ("Texte : Tanzil (tanzil.net), lecture Hafs, écriture othmanie, obtenu par l'API alquran.cloud. "
           "Traduction : Muhammad Hamidullah. Récitations : everyayah.com.")


SIGNES = re.compile("[\ufeff\u0640\u064b-\u065f\u0670\u06d6-\u06ed]")


def squelette(texte: str) -> str:
    """Le texte sans voyelles ni signes de lecture : pour comparer deux écritures de la basmala."""
    return SIGNES.sub("", texte)


def sans_basmala(texte: str, basmala: str) -> str:
    """Retire la basmala collée au début d'un 1er verset (les 4 premiers mots), si elle y est."""
    mots, mots_basmala = texte.split(), basmala.split()
    n = len(mots_basmala)
    if len(mots) > n and [squelette(m) for m in mots[:n]] == [squelette(m) for m in mots_basmala]:
        return " ".join(mots[n:])
    return texte


class CoranIndisponible(Exception):
    pass


def lire_json(url: str, delai=30) -> dict:
    requete = urllib.request.Request(url, headers={"User-Agent": "fofanalyse-ecole/1.0"})
    try:
        with urllib.request.urlopen(requete, timeout=delai) as r:
            return json.loads(r.read())
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as e:
        raise CoranIndisponible(str(e)) from e


def versets_par_sourate(reponses: list[dict]) -> dict[int, dict]:
    """Regroupe les réponses de l'API (une sourate ou un juz) : {sourate: {"nom": …, "versets": {n: texte}}}."""
    resultat = {}
    for reponse in reponses:
        data = reponse["data"]
        for ayah in data["ayahs"]:
            sourate = ayah.get("surah") or data  # réponse « juz » : la sourate est dans chaque verset
            numero = sourate["number"]
            entree = resultat.setdefault(numero, {"nom": sourate.get("name", ""), "versets": {}})
            entree["versets"][ayah["numberInSurah"]] = ayah["text"].replace("\ufeff", "").strip()
    return resultat


def assembler(arabe: dict[int, dict], francais: dict[int, dict]) -> dict:
    """Vérifie les deux éditions et sépare la basmala, que l'API colle au 1er verset des sourates."""
    basmala = arabe[1]["versets"][1]  # Al-Fâtiha, verset 1 : la basmala elle-même
    sourates = {}
    for numero, nom_fr, nombre in SOURATES:
        if numero not in arabe or numero not in francais:
            raise CoranIndisponible(f"sourate {numero} absente")
        textes, traductions = arabe[numero]["versets"], francais[numero]["versets"]
        if sorted(textes) != list(range(1, nombre + 1)) or sorted(traductions) != list(range(1, nombre + 1)):
            raise CoranIndisponible(f"sourate {numero} : {len(textes)} versets au lieu de {nombre}")
        if numero != 1:
            textes = {**textes, 1: sans_basmala(textes[1], basmala)}
        sourates[str(numero)] = {
            "numero": numero, "nom": nom_fr, "nom_arabe": arabe[numero]["nom"],
            "basmala": numero != 1,
            "versets": [{"n": n, "arabe": textes[n], "francais": traductions[n]} for n in range(1, nombre + 1)],
        }
    return {"basmala": basmala, "sourates": sourates, "sources": SOURCES, "telecharge_le": time.time()}


class Coran:
    def __init__(self, dossier: str, traduction: str = "fr.hamidullah", lire=lire_json):
        self.dossier = Path(dossier)
        self.traduction = traduction
        self.lire = lire
        self.verrou = threading.Lock()
        self.donnees = None

    @property
    def fichier(self) -> Path:
        return self.dossier / "texte.json"

    def texte(self) -> dict:
        """Le texte vérifié ; téléchargé à la première demande."""
        if self.donnees:
            return self.donnees
        with self.verrou:
            if not self.donnees and self.fichier.exists():
                self.donnees = json.loads(self.fichier.read_text(encoding="utf-8"))
            if not self.donnees:
                self.donnees = self.telecharger()
        return self.donnees

    def telecharger(self) -> dict:
        try:
            arabe = versets_par_sourate([self.lire(f"{API}/surah/1/quran-uthmani"),
                                         self.lire(f"{API}/juz/30/quran-uthmani")])
            francais = versets_par_sourate([self.lire(f"{API}/surah/1/{self.traduction}"),
                                            self.lire(f"{API}/juz/30/{self.traduction}")])
        except (KeyError, TypeError) as e:
            raise CoranIndisponible(f"réponse inattendue : {e}") from e
        donnees = assembler(arabe, francais)
        self.dossier.mkdir(parents=True, exist_ok=True)
        provisoire = self.fichier.with_suffix(".tmp")
        provisoire.write_text(json.dumps(donnees, ensure_ascii=False), encoding="utf-8")
        provisoire.replace(self.fichier)
        return donnees

    def audio(self, recitant: str, sourate: int, verset: int) -> Path:
        """Le fichier audio d'un verset ; téléchargé à la première écoute. Verset 0 = la basmala."""
        if recitant not in RECITANTS or sourate not in PAR_NUMERO or not 0 <= verset <= PAR_NUMERO[sourate][2]:
            raise ValueError("verset inconnu")
        if verset == 0:  # everyayah : la basmala est le premier verset d'Al-Fâtiha
            sourate, verset = 1, 1
        chemin = self.dossier / "audio" / recitant / f"{sourate:03d}{verset:03d}.mp3"
        if chemin.exists():
            return chemin
        url = AUDIO.format(dossier=RECITANTS[recitant]["dossier"], sourate=sourate, verset=verset)
        requete = urllib.request.Request(url, headers={"User-Agent": "fofanalyse-ecole/1.0"})
        try:
            with urllib.request.urlopen(requete, timeout=60) as r:
                contenu = r.read()
        except (urllib.error.URLError, TimeoutError) as e:
            raise CoranIndisponible(str(e)) from e
        if len(contenu) < 1000:
            raise CoranIndisponible("audio vide")
        chemin.parent.mkdir(parents=True, exist_ok=True)
        provisoire = chemin.with_suffix(".tmp")
        provisoire.write_bytes(contenu)
        provisoire.replace(chemin)
        return chemin


def depuis_environnement(db: str) -> Coran:
    return Coran(os.environ.get("ECOLE_CORAN_DOSSIER", str(Path(db).parent / "coran")),
                 os.environ.get("ECOLE_CORAN_TRADUCTION", "fr.hamidullah"))
