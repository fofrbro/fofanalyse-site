"""Tests du service École : générateurs, API, tuteur simulé (aucun appel réel à OpenAI).

    cd ecole-service && python -m pytest -q
"""

import random
import re
from decimal import Decimal

import pytest
from starlette.testclient import TestClient

import catalogue
import exercices as E
import lecons
from app import Config, creer_app
from tuteur import REPONSE_BLOQUEE, TuteurIndisponible

ENV = {"ECOLE_CODE_ELEVE": "hibou", "ECOLE_CODE_PARENT": "papa-2026", "ECOLE_SECRET": "x" * 32,
       "ECOLE_SECURE_COOKIE": "false"}


# --- Générateurs ------------------------------------------------------------------

def valeur_attendue(ex):
    if ex["type"] == "multi":
        return [Decimal(r) for r in ex["reponse"]]
    return ex["reponse"] if ex["type"] == "choix" else Decimal(ex["reponse"])


@pytest.mark.parametrize("chapitre", list(catalogue.GENERATEURS))
@pytest.mark.parametrize("niveau", [1, 2, 3])
def test_chaque_generateur_donne_des_exercices_complets(chapitre, niveau):
    rng = random.Random(f"{chapitre}{niveau}")
    for _ in range(300):
        ex = catalogue.generer(chapitre, niveau, rng)
        assert ex["enonce"] and ex["indice"] and ex["explication"] and ex["reponse_texte"]
        assert ex["type"] in ("nombre", "multi", "choix", "texte")
        if ex["type"] == "choix":
            assert ex["reponse"] in ex["options"] and len(set(ex["options"])) == len(ex["options"])
            assert E.verifier(ex, ex["reponse"])
        elif ex["type"] == "multi":
            assert len(ex["champs"]) == len(ex["reponse"])
            assert E.verifier(ex, list(ex["reponse"]))
        elif ex["type"] == "texte":
            assert E.verifier(ex, ex["reponse_texte"].rstrip(" !").upper())  # la casse ne compte pas
            assert all(E.verifier(ex, r) for r in ex["reponse"])
            assert not E.verifier(ex, "") and not E.verifier(ex, "zzz")
        else:
            assert E.verifier(ex, ex["reponse"].replace(".", ","))
            assert Decimal(ex["reponse"]) >= 0
        assert "None" not in ex["enonce"] + ex["explication"]
        assert "E+" not in ex["enonce"] + ex["explication"] + ex["reponse_texte"]


def test_les_calculs_poses_sont_justes():
    rng = random.Random(7)
    for _ in range(3000):
        a, b = rng.randint(10, 999_999), rng.randint(10, 999_999)
        assert E.etapes_addition(a, b)[-1] == f"Résultat : {E.ecrire(a + b)}"
        grand, petit = max(a, b), min(a, b)
        if grand != petit:
            assert E.etapes_soustraction(grand, petit)[-1].startswith(f"Résultat : {E.ecrire(grand - petit)}.")
        k = rng.randint(2, 9)
        assert E.etapes_multiplication_1(a, k)[-1] == f"Résultat : {E.ecrire(a * k)}"
        n = rng.randint(10, 9999)
        q, r = divmod(n, k)
        assert f"{E.ecrire(q)} × {k}" in E.etapes_division(n, k)[-1]


def test_soustraction_chiffre_par_chiffre():
    """Les chiffres écrits colonne par colonne doivent former le résultat."""
    rng = random.Random(3)
    for _ in range(2000):
        a = rng.randint(100, 99_999)
        b = rng.randint(1, a - 1)
        ecrits = []
        for ligne in E.etapes_soustraction(a, b)[:-1]:
            m = re.search(r"= (\d+)(, je retiens 1)?\.$", ligne) or re.search(r"j'abaisse le (\d)\.$", ligne)
            ecrits.append(m.group(1))
        assert int("".join(reversed(ecrits))) == a - b


def test_addition_chiffre_par_chiffre():
    rng = random.Random(4)
    for _ in range(2000):
        a, b = rng.randint(1, 99_999), rng.randint(1, 99_999)
        ecrits = [re.search(r"j'écris (\d+)", l).group(1) for l in E.etapes_addition(a, b)[:-1]]
        assert int("".join(reversed(ecrits))) == a + b


def test_lecture_des_reponses():
    assert E.lire("36 408") == 36408
    assert E.lire("36 408") == 36408
    assert E.lire("2,5") == Decimal("2.5") == E.lire("2.50")
    assert E.lire("deux") is None and E.lire("") is None and E.lire("1e400") is not None
    ex = E.exercice("nombre", "1,5 + 1", "2.5", ["…"], "…")
    assert E.verifier(ex, "2,5") and E.verifier(ex, "2,50") and not E.verifier(ex, "25")


def test_series_sans_doublon():
    s = catalogue.serie("tables", 1, 8, random.Random(1))
    assert len(s) == 8 and len({e["enonce"] for e in s}) == 8


def test_chaque_chapitre_a_sa_lecon():
    assert set(catalogue.GENERATEURS) == set(lecons.PAR_ID)
    assert len(lecons.PAR_ID) == len(lecons.CHAPITRES)  # identifiants uniques d'une classe à l'autre
    for c in lecons.CHAPITRES:
        assert c["classe"] in lecons.CLASSES
        assert c["retenir"] and c["exemple"]["etapes"]
        assert c["titre"] in lecons.lecon_en_texte(c["id"])


# --- API ------------------------------------------------------------------------------

class FauxTuteur:
    actif = True

    def __init__(self):
        self.appels = []

    def message_autorise(self, texte):
        return "interdit" not in texte

    def repondre(self, lecon, question, historique, classe, age, matiere):
        self.appels.append(("repondre", lecon, question, historique, classe))
        return "Voici une explication."

    def reexpliquer(self, lecon, ex, reponse, classe, age, matiere):
        self.appels.append(("reexpliquer", ex, reponse))
        return "Essayons autrement."


@pytest.fixture
def client(tmp_path):
    env = {**ENV, "ECOLE_DB": str(tmp_path / "ecole.db"), "ECOLE_IA_PAR_JOUR": "3"}
    tuteur = FauxTuteur()
    c = TestClient(creer_app(Config(env), tuteur), base_url="http://test")
    c.tuteur = tuteur
    return c


def se_connecter(client, code="hibou"):
    r = client.post("/api/ecole/connexion", json={"code": code})
    assert r.status_code == 200, r.text
    return r.json()


def test_configuration_obligatoire():
    with pytest.raises(RuntimeError):
        Config({"ECOLE_SECRET": "court"})
    with pytest.raises(RuntimeError):
        Config({**ENV, "ECOLE_CODE_PARENT": "hibou"})


def test_acces_refuse_sans_code(client):
    assert client.get("/api/ecole/programme").status_code == 401
    assert client.post("/api/ecole/connexion", json={"code": "faux"}).status_code == 401
    assert client.get("/api/ecole/health").json() == {"ok": True}


def test_session_falsifiee_refusee(client):
    client.cookies.set("ecole_session", "eyJyb2xlIjoicGFyZW50IiwiZXhwIjo5OTk5OTk5OTk5fQ.abc", path="/api/ecole")
    assert client.get("/api/ecole/moi").status_code == 401


def test_trop_de_codes_faux(client):
    for _ in range(8):
        client.post("/api/ecole/connexion", json={"code": "faux"})
    assert client.post("/api/ecole/connexion", json={"code": "hibou"}).status_code == 429


def test_parcours_eleve(client):
    assert se_connecter(client) == {"role": "eleve", "prenom": "Mouaz", "tuteur": True, "voix": False,
                                    "classe": "CM1"}
    prog = client.get("/api/ecole/programme").json()
    assert len(prog["chapitres"]) == 16 and prog["progres"]["tables"]["niveau"] == 1
    assert {c["matiere"] for c in prog["chapitres"]} == {"maths", "francais"}

    serie = client.post("/api/ecole/serie", json={"chapitre": "tables"}).json()
    assert len(serie["exercices"]) == 8
    premier = serie["exercices"][0]
    assert "reponse" not in premier and "explication" not in premier

    # Mauvaise réponse : pas de correction tout de suite
    r = client.post("/api/ecole/reponse", json={"id": premier["id"], "reponse": "-1"}).json()
    assert r == {"correct": False, "essais": 1, "termine": False}
    # Au 3e essai raté, la correction s'affiche
    client.post("/api/ecole/reponse", json={"id": premier["id"], "reponse": "-1"})
    r = client.post("/api/ecole/reponse", json={"id": premier["id"], "reponse": "-1"}).json()
    assert r["termine"] and r["explication"] and r["reponse_texte"]
    assert client.post("/api/ecole/reponse", json={"id": premier["id"], "reponse": "1"}).status_code == 409

    # « Explique-moi autrement » reçoit la bonne réponse calculée et la réponse de l'élève
    r = client.post("/api/ecole/autrement", json={"id": premier["id"]})
    assert r.json() == {"reponse": "Essayons autrement."}
    nom, ex, reponse = client.tuteur.appels[-1]
    assert reponse == "-1" and ex["reponse_texte"]

    # L'élève n'a pas accès au suivi parent
    assert client.get("/api/ecole/suivi").status_code == 403


def test_bonne_reponse_et_montee_de_niveau(client, tmp_path):
    se_connecter(client)
    import sqlite3, json as js
    for _ in range(1):
        serie = client.post("/api/ecole/serie", json={"chapitre": "addsous"}).json()
        db = sqlite3.connect(tmp_path / "ecole.db")
        nouveau = None
        for e in serie["exercices"]:
            juste = js.loads(db.execute("SELECT donnees FROM exercices WHERE id = ?", (e["id"],)).fetchone()[0])["reponse"]
            r = client.post("/api/ecole/reponse", json={"id": e["id"], "reponse": juste}).json()
            assert r["correct"] and r["termine"] and r["essais"] == 1
            nouveau = nouveau or r.get("nouveau_niveau")
    assert nouveau == 2
    assert client.get("/api/ecole/programme").json()["progres"]["addsous"] == {"niveau": 2, "faits": 8, "etoiles": 8}


def test_tuteur_plafond_et_moderation(client):
    se_connecter(client)
    r = client.post("/api/ecole/tuteur", json={"chapitre": "fractions", "question": "C'est quoi un quart ?",
                                               "historique": [{"role": "user", "content": "bonjour"}]})
    assert r.json() == {"reponse": "Voici une explication."}
    _, lecon, question, historique, classe = client.tuteur.appels[-1]
    assert "Les fractions" in lecon and question == "C'est quoi un quart ?"

    r = client.post("/api/ecole/tuteur", json={"chapitre": "fractions", "question": "un mot interdit"})
    assert r.json() == {"reponse": REPONSE_BLOQUEE}
    assert client.post("/api/ecole/tuteur", json={"chapitre": "fractions", "question": "x" * 401}).status_code == 400

    client.post("/api/ecole/tuteur", json={"chapitre": "fractions", "question": "Et un tiers ?"})
    client.post("/api/ecole/tuteur", json={"chapitre": "fractions", "question": "Et un demi ?"})
    r = client.post("/api/ecole/tuteur", json={"chapitre": "fractions", "question": "Encore ?"})
    assert r.status_code == 429  # plafond de 3 appels par jour dans ce test

    se_connecter(client, "papa-2026")
    suivi = client.get("/api/ecole/suivi").json()
    bloquees = [q for q in suivi["questions"] if q["bloquee"]]
    assert len(bloquees) == 1 and bloquees[0]["question"] == "un mot interdit"
    assert suivi["appels_ia_aujourdhui"] == 3


def test_tuteur_en_panne_ou_absent(client, tmp_path):
    se_connecter(client)

    def panne(*a, **k):
        raise TuteurIndisponible("délai dépassé")
    client.tuteur.repondre = panne
    r = client.post("/api/ecole/tuteur", json={"chapitre": "tables", "question": "7 × 8 ?"})
    assert r.status_code == 502

    client.tuteur.actif = False
    r = client.post("/api/ecole/tuteur", json={"chapitre": "tables", "question": "7 × 8 ?"})
    assert r.status_code == 503
    # Les exercices marchent sans tuteur
    assert client.post("/api/ecole/serie", json={"chapitre": "tables"}).status_code == 200


def test_suivi_et_effacement_parent(client):
    se_connecter(client)
    serie = client.post("/api/ecole/serie", json={"chapitre": "division"}).json()
    for _ in range(3):
        client.post("/api/ecole/reponse", json={"id": serie["exercices"][0]["id"], "reponse": "0"})
    se_connecter(client, "papa-2026")
    suivi = client.get("/api/ecole/suivi").json()
    division = next(c for c in suivi["chapitres"] if c["chapitre"] == "division")
    assert division["faits"] == 1 and division["reussis"] == 0 and len(division["derniers_rates"]) == 1
    assert len(suivi["jours"]) == 14 and suivi["jours"][-1]["exercices"] == 1
    assert client.post("/api/ecole/effacer", json={}).status_code == 400
    assert client.post("/api/ecole/effacer", json={"confirmation": "EFFACER"}).json() == {"ok": True}
    assert client.get("/api/ecole/suivi").json()["chapitres"][0]["faits"] == 0


def test_requetes_non_json_refusees(client):
    se_connecter(client)
    r = client.post("/api/ecole/serie", content="chapitre=tables",
                    headers={"content-type": "application/x-www-form-urlencoded"})
    assert r.status_code == 400


def test_division_decimale_posee():
    for n, d in [(47, 4), (9, 4), (978, 8), (113, 5)]:
        lignes = E.etapes_division_decimale(n, d)
        assert lignes[-1].startswith(f"Résultat : {n} ÷ {d} = {E.ecrire(Decimal(n) / d)}.")
    lignes = E.etapes_division_decimale(Decimal("45.6"), 4)
    assert "J'abaisse le 6" in " ".join(lignes) and lignes[-1].startswith("Résultat : 45,6 ÷ 4 = 11,4.")
    # Diviseur à deux chiffres : on prend assez de chiffres au départ
    assert E.etapes_division(1234, 25)[0].startswith("12 est plus petit que 25 : je prends les trois premiers")


def test_classe_reglee_par_le_parent(client):
    se_connecter(client)
    prog = client.get("/api/ecole/programme").json()
    assert prog["classe"] == "CM1" and prog["classes"] == ["CM1", "CM2", "6e"]
    assert client.post("/api/ecole/serie", json={"chapitre": "cm2-decimaux"}).status_code == 400
    assert client.post("/api/ecole/classe", json={"classe": "CM2"}).status_code == 403

    se_connecter(client, "papa-2026")
    assert client.post("/api/ecole/classe", json={"classe": "5e"}).status_code == 400
    assert client.post("/api/ecole/classe", json={"classe": "CM2"}).json() == {"classe": "CM2"}

    se_connecter(client)
    prog = client.get("/api/ecole/programme").json()
    classes = [c["classe"] for c in prog["chapitres"]]
    assert prog["classe"] == "CM2" and set(classes) == {"CM1", "CM2"}
    assert classes.index("CM2") > classes.index("CM1") or classes[0] == "CM1"
    assert client.post("/api/ecole/serie", json={"chapitre": "cm2-decimaux"}).status_code == 200
    # Les chapitres de CM1 restent ouverts pour réviser
    assert client.post("/api/ecole/serie", json={"chapitre": "fractions"}).status_code == 200
    # Pas encore la 6e
    assert client.post("/api/ecole/serie", json={"chapitre": "6e-fractions"}).status_code == 400

    client.post("/api/ecole/tuteur", json={"chapitre": "fractions", "question": "C'est quoi un quart ?"})
    assert client.tuteur.appels[-1][-1] == "CM2"

    # « Tout effacer » garde la classe choisie
    se_connecter(client, "papa-2026")
    client.post("/api/ecole/effacer", json={"confirmation": "EFFACER"})
    assert client.get("/api/ecole/suivi").json()["classe"] == "CM2"


def test_classe_de_depart_et_consignes(tmp_path):
    with pytest.raises(RuntimeError):
        Config({**ENV, "ECOLE_CLASSE": "CE2"})
    env = {**ENV, "ECOLE_DB": str(tmp_path / "e.db"), "ECOLE_CLASSE": "6e"}
    c = TestClient(creer_app(Config(env), FauxTuteur()), base_url="http://test")
    assert se_connecter(c)["classe"] == "6e"
    assert len(c.get("/api/ecole/programme").json()["chapitres"]) == len(lecons.CHAPITRES)
    from tuteur import consignes
    assert "élève de 6e (11 ans)" in consignes("Mouaz", "6e", 11)


# --- Maîtresse virtuelle (voix) ---------------------------------------------------------

def test_texte_reecrit_pour_la_voix():
    from voix import pour_la_voix
    assert pour_la_voix("47 × 23 = 1 081") == "47 fois 23 égale 1081"
    assert pour_la_voix("3/4 + 1/4 = 4/4") == "3 quarts plus 1 quart égale 4 quarts"
    assert pour_la_voix("Les 2/3 de 18") == "Les 2 tiers de 18"
    assert pour_la_voix("12/9 − 1/9 = …/9") == "12 sur 9 moins 1 sur 9 égale combien sur 9"
    assert pour_la_voix("Aire : 28 cm²") == "Aire : 28 centimètres carrés"
    assert pour_la_voix("36 408 ≈ 36 000 ✓") == "36408 environ 36000"
    assert pour_la_voix("Ligne 1\nLigne 2") == "Ligne 1. Ligne 2"
    assert pour_la_voix("2,5 km") == "2,5 km"
    assert pour_la_voix("191 = 14 × … + …") == "191 égale 14 fois combien plus combien"
    assert "combien" not in pour_la_voix("Conjugue « finir » au présent : nous …")


class FausseVoix:
    def __init__(self, dossier):
        from voix import Voix
        self.vraie = Voix("cle", "modele", "coral", str(dossier))
        self.active = True
        self.generes = []

    def nom(self, texte, age):
        return self.vraie.nom(texte, age)

    def chemin(self, nom):
        return self.vraie.chemin(nom)

    def deja_lu(self, nom):
        return self.vraie.deja_lu(nom)

    def generer(self, texte, age):
        self.generes.append((texte, age))
        nom = self.nom(texte, age)
        self.vraie.dossier.mkdir(parents=True, exist_ok=True)
        self.chemin(nom).write_bytes(b"ID3 faux mp3")
        return nom


def test_voix_cache_et_plafond(tmp_path):
    env = {**ENV, "ECOLE_DB": str(tmp_path / "ecole.db"), "ECOLE_VOIX_PAR_JOUR": "2"}
    voix = FausseVoix(tmp_path / "voix")
    c = TestClient(creer_app(Config(env), FauxTuteur(), voix), base_url="http://test")
    assert c.post("/api/ecole/voix", json={"texte": "Bonjour"}).status_code == 401
    assert se_connecter(c)["voix"] is True

    r = c.post("/api/ecole/voix", json={"texte": "7 × 8"}).json()
    assert voix.generes == [("7 fois 8", 9)]
    audio = c.get(r["audio"])
    assert audio.status_code == 200 and audio.headers["content-type"] == "audio/mpeg"

    # Déjà lu : servi depuis le cache, sans nouvel appel ni décompte
    assert c.post("/api/ecole/voix", json={"texte": "7 × 8"}).json() == r
    assert len(voix.generes) == 1
    c.post("/api/ecole/voix", json={"texte": "Deuxième texte"})
    assert c.post("/api/ecole/voix", json={"texte": "Troisième texte"}).status_code == 429
    assert c.post("/api/ecole/voix", json={"texte": "7 × 8"}).status_code == 200  # le cache reste gratuit

    assert c.get("/api/ecole/voix/" + "0" * 64).status_code == 404
    assert c.get("/api/ecole/voix/..%2Fecole.db").status_code == 404
    assert c.post("/api/ecole/voix", json={"texte": "   "}).status_code == 400

    se_connecter(c, "papa-2026")
    suivi = c.get("/api/ecole/suivi").json()
    assert suivi["appels_voix_aujourdhui"] == 2 and suivi["plafond_voix"] == 2


def test_voix_absente_sans_cle(client):
    se_connecter(client)
    assert client.post("/api/ecole/voix", json={"texte": "Bonjour"}).status_code == 503


# --- Français -------------------------------------------------------------------------------

def test_conjugaison_juste():
    import conjugaison as C
    assert C.simple("commencer", "present")[3] == "commençons"
    assert C.simple("manger", "imparfait") == ["mangeais", "mangeais", "mangeait", "mangions", "mangiez", "mangeaient"]
    assert C.simple("manger", "passe_simple")[5] == "mangèrent"
    assert C.simple("finir", "present")[5] == "finissent" and C.simple("finir", "passe_simple")[3] == "finîmes"
    assert C.simple("voir", "imparfait")[3] == "voyions" and C.simple("être", "imparfait")[0] == "étais"
    assert C.simple("aller", "futur")[0] == "irai" and C.simple("venir", "conditionnel")[3] == "viendrions"
    assert C.imperatif("chanter") == ["chante", "chantons", "chantez"] and C.imperatif("pouvoir") is None
    assert C.compose("aller", "passe_compose", 2, True) == ["est allée"]
    assert C.compose("partir", "plus_que_parfait", 5, False) == ["étaient partis"]
    assert C.compose("manger", "passe_compose", 0) == ["ai mangé"]
    assert C.table("aimer", "passe_compose")[0] == "j'ai aimé"


def test_reponses_ecrites():
    ex = E.exercice("texte", "…", ["est allée", "elle est allée"], ["…"], "…")
    assert E.verifier(ex, "Est allée.") and E.verifier(ex, "  elle   est allée ")
    assert not E.verifier(ex, "est allee")  # les accents comptent
    ex = E.exercice("texte", "…", ["j'ai mangé"], ["…"], "…")
    assert E.verifier(ex, "J’ai mangé")  # apostrophe typographique acceptée


def test_banques_de_francais():
    import francais as F
    import francais_banques as B
    for phrase, mot, nature in B.NATURE:
        assert F.mot_present_une_fois(phrase, mot), (phrase, mot)
        assert nature in B.NATURES_6E and nature in B.ASTUCES_NATURE
    for phrase, groupe, fonction in B.FONCTION:
        assert F.mot_present_une_fois(phrase, groupe), (phrase, groupe)
        assert fonction in B.FONCTIONS_6E and fonction in B.ASTUCES_FONCTION
    for banque in (B.HOMOPHONES_CM1, B.HOMOPHONES_CM2):
        for options, (astuce, phrases) in banque.items():
            for phrase, bonne in phrases:
                assert phrase.count("___") == 1 and bonne in options, phrase
    for phrase, expression, _ in B.SENS:
        assert expression in phrase
    for mot, contraire in B.PREFIXES:
        assert contraire.endswith(mot)
    for phrase, verbes in B.PHRASES_VERBES:
        assert all(F.mot_present_une_fois(phrase, v) for v in verbes), phrase


def test_tuteur_connait_la_matiere(client):
    se_connecter(client)
    client.post("/api/ecole/tuteur", json={"chapitre": "fr-cm1-present", "question": "C'est quoi un verbe ?"})
    assert "Le présent" in client.tuteur.appels[-1][1]
