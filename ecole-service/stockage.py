"""
Progression de l'élève, dans un fichier SQLite (volume Docker ecole_data).

Rien d'autre que le travail scolaire : la classe choisie par le parent, les
exercices proposés, les réponses, le niveau atteint dans chaque chapitre, le
nombre d'appels au tuteur et les messages que le filtre de sécurité a bloqués
(pour que le parent les voie).
"""

import json
import sqlite3
import threading
import time
from datetime import datetime, timedelta, timezone

SCHEMA = """
CREATE TABLE IF NOT EXISTS exercices (
    id TEXT PRIMARY KEY,
    chapitre TEXT NOT NULL,
    niveau INTEGER NOT NULL,
    donnees TEXT NOT NULL,
    essais INTEGER NOT NULL DEFAULT 0,
    reussi_premier INTEGER,           -- 1 : juste au premier essai ; 0 : non ; NULL : pas encore répondu
    termine INTEGER NOT NULL DEFAULT 0,
    derniere_reponse TEXT,
    cree_le REAL NOT NULL,
    termine_le REAL
);
CREATE INDEX IF NOT EXISTS exercices_chapitre ON exercices (chapitre, termine_le);

CREATE TABLE IF NOT EXISTS niveaux (
    chapitre TEXT PRIMARY KEY,
    niveau INTEGER NOT NULL,
    depuis REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS appels_ia (
    jour TEXT PRIMARY KEY,
    nombre INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS reglages (
    cle TEXT PRIMARY KEY,
    valeur TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS questions_tuteur (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chapitre TEXT,
    question TEXT NOT NULL,
    bloquee INTEGER NOT NULL DEFAULT 0,
    cree_le REAL NOT NULL
);
"""

MAX_ESSAIS = 3


def aujourdhui() -> str:
    return datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d")


class Stockage:
    def __init__(self, chemin: str):
        self.verrou = threading.Lock()
        self.db = sqlite3.connect(chemin, check_same_thread=False)
        self.db.row_factory = sqlite3.Row
        self.db.execute("PRAGMA journal_mode=WAL")
        self.db.executescript(SCHEMA)

    # --- Réglages -------------------------------------------------------

    def reglage(self, cle, defaut=None):
        ligne = self.db.execute("SELECT valeur FROM reglages WHERE cle = ?", (cle,)).fetchone()
        return ligne["valeur"] if ligne else defaut

    def regler(self, cle, valeur):
        with self.verrou, self.db:
            self.db.execute("INSERT INTO reglages (cle, valeur) VALUES (?, ?) "
                            "ON CONFLICT (cle) DO UPDATE SET valeur = excluded.valeur", (cle, valeur))

    # --- Exercices ------------------------------------------------------

    def enregistrer_exercice(self, id_, chapitre, niveau, ex):
        with self.verrou, self.db:
            self.db.execute("INSERT INTO exercices (id, chapitre, niveau, donnees, cree_le) VALUES (?, ?, ?, ?, ?)",
                            (id_, chapitre, niveau, json.dumps(ex, ensure_ascii=False), time.time()))

    def exercice(self, id_):
        ligne = self.db.execute("SELECT * FROM exercices WHERE id = ?", (id_,)).fetchone()
        if not ligne:
            return None
        resultat = dict(ligne)
        resultat["donnees"] = json.loads(resultat["donnees"])
        return resultat

    def noter_essai(self, id_, correct: bool, reponse) -> dict:
        """Enregistre un essai. Renvoie l'état de l'exercice après cet essai."""
        with self.verrou, self.db:
            ligne = self.db.execute("SELECT essais, termine, chapitre FROM exercices WHERE id = ?", (id_,)).fetchone()
            essais = ligne["essais"] + 1
            termine = 1 if (correct or essais >= MAX_ESSAIS) else 0
            self.db.execute(
                """UPDATE exercices SET essais = ?, termine = ?, derniere_reponse = ?,
                   reussi_premier = COALESCE(reussi_premier, ?),
                   termine_le = CASE WHEN ? THEN ? ELSE termine_le END
                   WHERE id = ?""",
                (essais, termine, json.dumps(reponse, ensure_ascii=False), 1 if correct else 0,
                 termine, time.time(), id_))
        return {"essais": essais, "termine": bool(termine), "chapitre": ligne["chapitre"]}

    # --- Niveaux --------------------------------------------------------

    def niveau(self, chapitre) -> int:
        ligne = self.db.execute("SELECT niveau FROM niveaux WHERE chapitre = ?", (chapitre,)).fetchone()
        return ligne["niveau"] if ligne else 1

    def ajuster_niveau(self, chapitre) -> int | None:
        """Monte d'un niveau après 6 exercices au moins, réussis à 85 % du premier coup ;
        descend après 4 exercices au moins, réussis à 40 % ou moins.
        Renvoie le nouveau niveau s'il a changé."""
        with self.verrou, self.db:
            ligne = self.db.execute("SELECT niveau, depuis FROM niveaux WHERE chapitre = ?", (chapitre,)).fetchone()
            niveau, depuis = (ligne["niveau"], ligne["depuis"]) if ligne else (1, 0)
            stats = self.db.execute(
                "SELECT COUNT(*) n, COALESCE(SUM(reussi_premier), 0) ok FROM exercices "
                "WHERE chapitre = ? AND termine = 1 AND termine_le > ?", (chapitre, depuis)).fetchone()
            n, ok = stats["n"], stats["ok"]
            nouveau = niveau
            if n >= 6 and ok / n >= 0.85 and niveau < 3:
                nouveau = niveau + 1
            elif n >= 4 and ok / n <= 0.40 and niveau > 1:
                nouveau = niveau - 1
            if nouveau != niveau or not ligne:
                self.db.execute("INSERT INTO niveaux (chapitre, niveau, depuis) VALUES (?, ?, ?) "
                                "ON CONFLICT (chapitre) DO UPDATE SET niveau = excluded.niveau, depuis = excluded.depuis",
                                (chapitre, nouveau, time.time() if nouveau != niveau else 0))
            return nouveau if nouveau != niveau else None

    # --- Tuteur ---------------------------------------------------------

    def compter_appel_ia(self, plafond: int) -> bool:
        """Compte un appel au modèle. False si le plafond du jour est atteint."""
        jour = aujourdhui()
        with self.verrou, self.db:
            ligne = self.db.execute("SELECT nombre FROM appels_ia WHERE jour = ?", (jour,)).fetchone()
            nombre = ligne["nombre"] if ligne else 0
            if nombre >= plafond:
                return False
            self.db.execute("INSERT INTO appels_ia (jour, nombre) VALUES (?, 1) "
                            "ON CONFLICT (jour) DO UPDATE SET nombre = nombre + 1", (jour,))
            return True

    def noter_question(self, chapitre, question, bloquee=False):
        with self.verrou, self.db:
            self.db.execute("INSERT INTO questions_tuteur (chapitre, question, bloquee, cree_le) VALUES (?, ?, ?, ?)",
                            (chapitre, question[:500], 1 if bloquee else 0, time.time()))

    # --- Tableaux de bord -------------------------------------------------

    def progres_eleve(self, chapitres) -> dict:
        """Pour l'élève : niveau et étoiles (exercices réussis) par chapitre."""
        lignes = self.db.execute(
            "SELECT chapitre, COUNT(*) n, COALESCE(SUM(reussi_premier), 0) ok FROM exercices "
            "WHERE termine = 1 GROUP BY chapitre").fetchall()
        par_chapitre = {l["chapitre"]: (l["n"], l["ok"]) for l in lignes}
        return {c: {"niveau": self.niveau(c), "faits": par_chapitre.get(c, (0, 0))[0],
                    "etoiles": par_chapitre.get(c, (0, 0))[1]} for c in chapitres}

    def suivi_parent(self, chapitres) -> dict:
        maintenant = time.time()
        semaine = maintenant - 7 * 86400
        resultat = []
        for c in chapitres:
            total = self.db.execute(
                "SELECT COUNT(*) n, COALESCE(SUM(reussi_premier), 0) ok, MAX(termine_le) dernier "
                "FROM exercices WHERE chapitre = ? AND termine = 1", (c,)).fetchone()
            recent = self.db.execute(
                "SELECT COUNT(*) n, COALESCE(SUM(reussi_premier), 0) ok FROM exercices "
                "WHERE chapitre = ? AND termine = 1 AND termine_le > ?", (c, semaine)).fetchone()
            rates = self.db.execute(
                "SELECT donnees FROM exercices WHERE chapitre = ? AND termine = 1 AND reussi_premier = 0 "
                "ORDER BY termine_le DESC LIMIT 3", (c,)).fetchall()
            resultat.append({
                "chapitre": c, "niveau": self.niveau(c),
                "faits": total["n"], "reussis": total["ok"],
                "faits_7j": recent["n"], "reussis_7j": recent["ok"],
                "dernier": total["dernier"],
                "derniers_rates": [json.loads(r["donnees"])["enonce"] for r in rates],
            })
        jours = []
        for i in range(13, -1, -1):
            debut = datetime.now().astimezone().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=i)
            fin = debut + timedelta(days=1)
            n = self.db.execute("SELECT COUNT(*) n FROM exercices WHERE termine = 1 AND termine_le >= ? AND termine_le < ?",
                                (debut.timestamp(), fin.timestamp())).fetchone()["n"]
            jours.append({"jour": debut.strftime("%Y-%m-%d"), "exercices": n})
        questions = [dict(q) for q in self.db.execute(
            "SELECT chapitre, question, bloquee, cree_le FROM questions_tuteur ORDER BY id DESC LIMIT 30")]
        appels = self.db.execute("SELECT nombre FROM appels_ia WHERE jour = ?", (aujourdhui(),)).fetchone()
        return {"chapitres": resultat, "jours": jours, "questions": questions,
                "appels_ia_aujourdhui": appels["nombre"] if appels else 0}

    def tout_effacer(self):
        """Efface le travail de l'élève ; la classe choisie reste."""
        with self.verrou, self.db:
            for table in ("exercices", "niveaux", "questions_tuteur"):
                self.db.execute(f"DELETE FROM {table}")
