"""
Service « École » de fofanalyse.com : l'espace de révision (maths et
français), du CM1 à la 6e. Le parent choisit la classe dans le suivi ; les chapitres des
classes d'avant restent ouverts pour réviser.

Servi par Caddy sous https://fofanalyse.com/api/ecole/ ; la page est dans
www/ecole/. Accès privé par code : un code élève, un code parent (le parent
voit en plus le suivi). Aucune donnée personnelle hormis le prénom affiché.

Configuration (deploy/.env) :
  ECOLE_CODE_ELEVE, ECOLE_CODE_PARENT   codes d'accès (obligatoires)
  ECOLE_SECRET                          clé de signature des sessions (obligatoire)
  ECOLE_OPENAI_API_KEY                  clé du projet OpenAI du tuteur (facultatif)
  ECOLE_OPENAI_MODEL                    modèle (défaut : gpt-4o-mini)
  ECOLE_IA_PAR_JOUR                     plafond d'appels au tuteur par jour (défaut : 60)
  ECOLE_VOIX                            voix de la maîtresse virtuelle (défaut : coral)
  ECOLE_VOIX_MODELE                     modèle de synthèse vocale (défaut : gpt-4o-mini-tts)
  ECOLE_VOIX_PAR_JOUR                   plafond d'audios nouveaux par jour (défaut : 200 ; le cache est gratuit)
  ECOLE_PRENOM                          prénom de l'élève (défaut : Mouaz)
  ECOLE_CLASSE                          classe au premier démarrage : CM1, CM2 ou 6e (défaut : CM1) ;
                                        ensuite, le parent la change dans le suivi
  ECOLE_DB                              fichier SQLite (défaut : /data/ecole.db)
  ECOLE_SECURE_COOKIE                   true en ligne (HTTPS), false en local
"""

import base64
import hashlib
import re
import hmac
import json
import os
import secrets
import time
from collections import defaultdict, deque

from starlette.applications import Starlette
from starlette.concurrency import run_in_threadpool
from starlette.requests import Request
from starlette.responses import FileResponse, JSONResponse
from starlette.routing import Route

import catalogue
import exercices as E
import lecons
from stockage import Stockage
import coran as Q
import voix as V
from tuteur import DERNIERE_ERREUR, REPONSE_BLOQUEE, TuteurIndisponible, depuis_environnement

COOKIE = "ecole_session"
DUREE_SESSION = 30 * 86400
CHAMPS_PUBLICS = ("type", "enonce", "grand", "unite", "champs", "options", "indice", "arabe")


class Config:
    def __init__(self, env=os.environ):
        self.code_eleve = env.get("ECOLE_CODE_ELEVE", "")
        self.code_parent = env.get("ECOLE_CODE_PARENT", "")
        self.secret = env.get("ECOLE_SECRET", "")
        self.prenom = env.get("ECOLE_PRENOM", "Mouaz")
        self.classe = env.get("ECOLE_CLASSE", "CM1")
        self.ia_par_jour = int(env.get("ECOLE_IA_PAR_JOUR", "60"))
        self.voix_par_jour = int(env.get("ECOLE_VOIX_PAR_JOUR", "200"))
        self.db = env.get("ECOLE_DB", "/data/ecole.db")
        self.cookie_securise = env.get("ECOLE_SECURE_COOKIE", "true").lower() != "false"
        if len(self.secret) < 16 or len(self.code_eleve) < 4 or len(self.code_parent) < 4:
            raise RuntimeError("ECOLE_SECRET (16 caractères min.), ECOLE_CODE_ELEVE et ECOLE_CODE_PARENT "
                               "(4 caractères min.) doivent être définis dans deploy/.env")
        if self.code_eleve == self.code_parent:
            raise RuntimeError("ECOLE_CODE_ELEVE et ECOLE_CODE_PARENT doivent être différents")
        if self.classe not in lecons.CLASSES:
            raise RuntimeError(f"ECOLE_CLASSE doit valoir {', '.join(lecons.CLASSES)}")


def erreur(message, statut=400):
    return JSONResponse({"erreur": message}, status_code=statut)


# --- Sessions signées -----------------------------------------------------

def signer(secret: str, contenu: dict) -> str:
    corps = base64.urlsafe_b64encode(json.dumps(contenu).encode()).decode().rstrip("=")
    signature = hmac.new(secret.encode(), corps.encode(), hashlib.sha256).hexdigest()
    return f"{corps}.{signature}"


def verifier_session(secret: str, valeur: str | None) -> dict | None:
    if not valeur or "." not in valeur:
        return None
    corps, signature = valeur.rsplit(".", 1)
    attendu = hmac.new(secret.encode(), corps.encode(), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(signature, attendu):
        return None
    try:
        contenu = json.loads(base64.urlsafe_b64decode(corps + "=" * (-len(corps) % 4)))
    except ValueError:
        return None
    if contenu.get("exp", 0) < time.time() or contenu.get("role") not in ("eleve", "parent"):
        return None
    return contenu


def decouper_pour_la_voix(texte: str, taille: int = 700) -> list[str]:
    """Un cours en paragraphes courts : le premier se dit vite, les suivants se préparent pendant ce temps."""
    resultat = []
    for paragraphe in (p.strip() for p in re.split(r"\n\s*\n", texte) if p.strip()):
        phrases, courant = re.split(r"(?<=[.!?…])\s+", paragraphe), ""
        for phrase in phrases:
            if courant and len(courant) + len(phrase) > taille:
                resultat.append(courant)
                courant = ""
            courant = f"{courant} {phrase}".strip()
        if courant:
            resultat.append(courant)
    return resultat


def creer_app(config: Config | None = None, tuteur=None, voix=None, coran=None) -> Starlette:
    config = config or Config()
    tuteur = tuteur or depuis_environnement()
    voix = voix or V.depuis_environnement(config.db)
    coran = coran or Q.depuis_environnement(config.db)
    stock = Stockage(config.db)
    echecs = defaultdict(deque)  # adresse IP → instants des codes faux

    def adresse(request: Request) -> str:
        transmise = request.headers.get("x-forwarded-for", "")
        return transmise.split(",")[0].strip() or (request.client.host if request.client else "?")

    def session(request: Request):
        return verifier_session(config.secret, request.cookies.get(COOKIE))

    def classe() -> str:
        choisie = stock.reglage("classe", config.classe)
        return choisie if choisie in lecons.CLASSES else config.classe

    def chapitres_ouverts() -> dict:
        """Les chapitres de la classe et des classes d'avant, par identifiant."""
        return {c["id"]: c for c in lecons.chapitres_jusqua(classe())}

    def profil(role) -> dict:
        return {"role": role, "prenom": config.prenom, "tuteur": tuteur.actif, "voix": voix.active,
                "classe": classe()}

    def voix_choisie() -> str:
        choisie = stock.reglage("voix", voix.voix)
        return choisie if choisie in V.VOIX_DISPONIBLES else voix.voix

    def pour_tuteur(chapitre=None) -> dict:
        infos = {"classe": classe(), "age": lecons.CLASSES[classe()]["age"]}
        if chapitre:
            infos["matiere"] = lecons.MATIERES[lecons.PAR_ID[chapitre]["matiere"]]
        return infos

    async def corps_json(request: Request) -> dict | None:
        if "application/json" not in request.headers.get("content-type", ""):
            return None
        brut = await request.body()
        if len(brut) > 32_000:
            return None
        try:
            donnees = json.loads(brut)
        except ValueError:
            return None
        return donnees if isinstance(donnees, dict) else None

    def protege(role_requis=None):
        def decorateur(fonction):
            async def route(request: Request):
                s = session(request)
                if not s:
                    return erreur("Connecte-toi avec ton code.", 401)
                if role_requis and s["role"] != role_requis:
                    return erreur("Réservé au parent.", 403)
                request.state.role = s["role"]
                return await fonction(request)
            return route
        return decorateur

    # --- Connexion --------------------------------------------------------

    async def connexion(request: Request):
        ip = adresse(request)
        file = echecs[ip]
        while file and file[0] < time.time() - 900:
            file.popleft()
        if len(file) >= 8:
            return erreur("Trop d'essais. Attends un quart d'heure.", 429)
        donnees = await corps_json(request) or {}
        code = str(donnees.get("code", ""))[:64].strip()
        if hmac.compare_digest(code.encode(), config.code_parent.encode()):
            role = "parent"
        elif hmac.compare_digest(code.encode(), config.code_eleve.encode()):
            role = "eleve"
        else:
            file.append(time.time())
            return erreur("Ce code n'est pas le bon.", 401)
        r = JSONResponse(profil(role))
        r.set_cookie(COOKIE, signer(config.secret, {"role": role, "exp": int(time.time()) + DUREE_SESSION}),
                     max_age=DUREE_SESSION, httponly=True, secure=config.cookie_securise,
                     samesite="strict", path="/api/ecole")
        return r

    async def deconnexion(request: Request):
        r = JSONResponse({"ok": True})
        r.delete_cookie(COOKIE, path="/api/ecole")
        return r

    @protege()
    async def moi(request: Request):
        return JSONResponse(profil(request.state.role))

    # --- Leçons et exercices ------------------------------------------------

    @protege()
    async def programme(request: Request):
        chapitres = lecons.chapitres_jusqua(classe())
        return JSONResponse({"classe": classe(), "classes": list(lecons.CLASSES), "matieres": lecons.MATIERES,
                             "chapitres": chapitres,
                             "progres": stock.progres_eleve([c["id"] for c in chapitres])})

    @protege()
    async def serie(request: Request):
        donnees = await corps_json(request) or {}
        chapitre = donnees.get("chapitre")
        if chapitre not in chapitres_ouverts():
            return erreur("Chapitre inconnu.")
        niveau = stock.niveau(chapitre)
        liste = []
        for ex in catalogue.serie(chapitre, niveau, 8, prenom=config.prenom):
            id_ = secrets.token_urlsafe(12)
            stock.enregistrer_exercice(id_, chapitre, niveau, ex)
            liste.append({"id": id_, **{k: ex.get(k) for k in CHAMPS_PUBLICS}})
        return JSONResponse({"chapitre": chapitre, "niveau": niveau, "exercices": liste})

    @protege()
    async def reponse(request: Request):
        donnees = await corps_json(request) or {}
        ligne = stock.exercice(str(donnees.get("id", "")))
        if not ligne:
            return erreur("Exercice introuvable.", 404)
        if ligne["termine"]:
            return erreur("Cet exercice est déjà terminé.", 409)
        reponse_eleve = donnees.get("reponse")
        if isinstance(reponse_eleve, list):
            reponse_eleve = [str(r)[:20] for r in reponse_eleve[:8]]
        else:
            reponse_eleve = str(reponse_eleve or "")[:60]
        ex = ligne["donnees"]
        correct = E.verifier(ex, reponse_eleve)
        etat = stock.noter_essai(ligne["id"], correct, reponse_eleve)
        resultat = {"correct": correct, "essais": etat["essais"], "termine": etat["termine"]}
        if etat["termine"]:
            resultat["reponse_texte"] = ex["reponse_texte"]
            resultat["explication"] = ex["explication"]
            nouveau = stock.ajuster_niveau(etat["chapitre"])
            if nouveau:
                resultat["nouveau_niveau"] = nouveau
        return JSONResponse(resultat)

    # --- Tuteur IA -----------------------------------------------------------

    async def appeler_tuteur(fonction, *args, **options):
        if not tuteur.actif:
            return erreur("Le tuteur n'est pas encore branché.", 503)
        if not stock.compter_appel_ia(config.ia_par_jour):
            return erreur("Le tuteur se repose pour aujourd'hui. Reviens demain !", 429)
        try:
            texte = await run_in_threadpool(fonction, *args, **options)
        except TuteurIndisponible:
            return erreur("Le tuteur ne répond pas. Réessaie dans un moment.", 502)
        return JSONResponse({"reponse": texte})

    @protege()
    async def poser_question(request: Request):
        donnees = await corps_json(request) or {}
        chapitre = donnees.get("chapitre")
        question = str(donnees.get("question", "")).strip()
        historique = donnees.get("historique") if isinstance(donnees.get("historique"), list) else []
        if chapitre not in chapitres_ouverts() or not question:
            return erreur("Écris ta question.")
        if len(question) > 400:
            return erreur("Ta question est trop longue : 400 caractères au maximum.")
        if tuteur.actif and not await run_in_threadpool(tuteur.message_autorise, question):
            stock.noter_question(chapitre, question, bloquee=True)
            return JSONResponse({"reponse": REPONSE_BLOQUEE})
        stock.noter_question(chapitre, question)
        return await appeler_tuteur(tuteur.repondre, lecons.lecon_en_texte(chapitre), question, historique,
                                    **pour_tuteur(chapitre))

    @protege()
    async def autrement(request: Request):
        donnees = await corps_json(request) or {}
        ligne = stock.exercice(str(donnees.get("id", "")))
        if not ligne or not ligne["termine"]:
            return erreur("Termine d'abord l'exercice.", 409)
        reponse_eleve = json.loads(ligne["derniere_reponse"] or '""')
        return await appeler_tuteur(tuteur.reexpliquer, lecons.lecon_en_texte(ligne["chapitre"]),
                                    ligne["donnees"], reponse_eleve, **pour_tuteur(ligne["chapitre"]))

    # --- Maîtresse virtuelle (voix) ---------------------------------------------

    @protege()
    async def lire_a_voix_haute(request: Request):
        donnees = await corps_json(request) or {}
        texte = V.pour_la_voix(str(donnees.get("texte", ""))[:V.MAX_TEXTE])
        if not texte:
            return erreur("Rien à lire.")
        if not voix.active:
            return erreur("La voix n'est pas branchée.", 503)
        age = pour_tuteur()["age"]
        # Le parent peut écouter une autre voix avant de la choisir
        quelle = donnees.get("voix") if request.state.role == "parent" and donnees.get("voix") in V.VOIX_DISPONIBLES \
            else voix_choisie()
        nom = voix.nom(texte, age, quelle)
        if not voix.deja_lu(nom):
            if not stock.compter_appel_voix(config.voix_par_jour):
                return erreur("La maîtresse a assez parlé pour aujourd'hui. Reviens demain !", 429)
            try:
                nom = await run_in_threadpool(voix.generer, texte, age, quelle)
            except V.VoixIndisponible:
                return erreur("La voix ne répond pas. Réessaie dans un moment.", 502)
        return JSONResponse({"audio": f"/api/ecole/voix/{nom}"})

    @protege()
    async def expliquer(request: Request):
        """Le cours de la maîtresse sur une leçon : écrit par l'IA une seule fois, puis gardé."""
        donnees = await corps_json(request) or {}
        chapitre = donnees.get("chapitre")
        if chapitre not in chapitres_ouverts():
            return erreur("Chapitre inconnu.")
        texte = stock.explication(chapitre, classe())
        if not texte:
            reponse = await appeler_tuteur(tuteur.expliquer_lecon, lecons.lecon_en_texte(chapitre), **pour_tuteur(chapitre))
            if reponse.status_code != 200:
                return reponse
            texte = json.loads(reponse.body)["reponse"]
            stock.garder_explication(chapitre, classe(), texte)
        return JSONResponse({"paragraphes": decouper_pour_la_voix(texte)})

    @protege()
    async def ecouter(request: Request):
        """L'enfant parle au micro : on transcrit sa question, la page la pose ensuite au tuteur."""
        type_mime = request.headers.get("content-type", "")
        if not type_mime.startswith("audio/"):
            return erreur("Enregistrement audio attendu.")
        audio = await request.body()
        if not audio or len(audio) > V.MAX_AUDIO_ENFANT:
            return erreur("L'enregistrement est vide ou trop long : une minute au maximum.")
        if not voix.active:
            return erreur("Le micro a besoin de la clé OpenAI du tuteur.", 503)
        if not stock.compter_appel_ia(config.ia_par_jour):
            return erreur("Le tuteur se repose pour aujourd'hui. Reviens demain !", 429)
        try:
            texte = await run_in_threadpool(voix.transcrire, audio, type_mime)
        except V.VoixIndisponible:
            return erreur("Je n'ai pas réussi à t'entendre. Réessaie ou écris ta question.", 502)
        if not texte:
            return erreur("Je n'ai rien entendu. Parle un peu plus fort, près du micro.", 422)
        return JSONResponse({"texte": texte[:400]})

    @protege()
    async def audio(request: Request):
        chemin = voix.chemin(request.path_params["nom"])
        if not chemin or not chemin.exists():
            return erreur("Audio introuvable.", 404)
        return FileResponse(chemin, media_type="audio/mpeg",
                            headers={"Cache-Control": "private, max-age=2592000, immutable"})

    # --- Coran ------------------------------------------------------------------
    # Le texte et les récitations viennent de sources de référence (voir coran.py) ;
    # rien n'est généré, et le tuteur IA n'intervient pas.

    async def texte_coran():
        try:
            return await run_in_threadpool(coran.texte)
        except Q.CoranIndisponible:
            return None

    @protege()
    async def coran_sommaire(request: Request):
        texte = await texte_coran()
        if not texte:
            return erreur("Le texte du Coran n'a pas encore pu être téléchargé par le serveur. Réessaie plus tard.", 503)
        progres = stock.coran_progres()
        return JSONResponse({
            "sources": texte["sources"],
            "recitants": {k: v["nom"] for k, v in Q.RECITANTS.items()},
            "sourates": [{"numero": n, "nom": nom, "nom_arabe": texte["sourates"][str(n)]["nom_arabe"],
                          "versets": total, "appris": progres.get(n, {}).get("versets_appris", 0)}
                         for n, nom, total in Q.SOURATES],
        })

    @protege()
    async def coran_sourate(request: Request):
        texte = await texte_coran()
        numero = request.path_params["numero"]
        if not texte:
            return erreur("Le texte du Coran n'est pas encore disponible.", 503)
        if numero not in Q.PAR_NUMERO:
            return erreur("Sourate inconnue.", 404)
        return JSONResponse({**texte["sourates"][str(numero)], "texte_basmala": texte["basmala"],
                             "appris": stock.coran_progres().get(numero, {}).get("versets_appris", 0)})

    @protege()
    async def coran_progresser(request: Request):
        numero = request.path_params["numero"]
        donnees = await corps_json(request) or {}
        appris = donnees.get("appris")
        if numero not in Q.PAR_NUMERO or not isinstance(appris, int) or not 0 <= appris <= Q.PAR_NUMERO[numero][2]:
            return erreur("Progression invalide.")
        stock.noter_coran(numero, appris)
        return JSONResponse({"appris": appris})

    @protege()
    async def coran_audio(request: Request):
        p = request.path_params
        try:
            chemin = await run_in_threadpool(coran.audio, p["recitant"], p["sourate"], p["verset"])
        except ValueError:
            return erreur("Verset inconnu.", 404)
        except Q.CoranIndisponible:
            return erreur("La récitation n'a pas pu être téléchargée. Réessaie dans un moment.", 502)
        return FileResponse(chemin, media_type="audio/mpeg",
                            headers={"Cache-Control": "private, max-age=2592000, immutable"})

    # --- Parent ------------------------------------------------------------------

    @protege("parent")
    async def suivi(request: Request):
        ids = [c["id"] for c in lecons.chapitres_jusqua(classe())]
        return JSONResponse({**stock.suivi_parent(ids), "plafond_ia": config.ia_par_jour, "tuteur": tuteur.actif,
                             "voix": voix.active, "appels_voix_aujourdhui": stock.appels_voix_aujourdhui(),
                             "voix_choisie": voix_choisie(), "voix_disponibles": V.VOIX_DISPONIBLES,
                             "erreur_openai": DERNIERE_ERREUR or None,
                             "plafond_voix": config.voix_par_jour,
                             "classe": classe(), "classes": list(lecons.CLASSES),
                             "coran": [{"numero": n, "nom": nom, "versets": total, **progres}
                                       for n, progres in sorted(stock.coran_progres().items())
                                       for _, nom, total in [Q.PAR_NUMERO[n]]]})

    @protege("parent")
    async def changer_voix(request: Request):
        donnees = await corps_json(request) or {}
        if donnees.get("voix") not in V.VOIX_DISPONIBLES:
            return erreur("Voix inconnue.")
        stock.regler("voix", donnees["voix"])
        return JSONResponse({"voix": donnees["voix"]})

    @protege("parent")
    async def changer_classe(request: Request):
        donnees = await corps_json(request) or {}
        nouvelle = donnees.get("classe")
        if nouvelle not in lecons.CLASSES:
            return erreur("Classe inconnue.")
        stock.regler("classe", nouvelle)
        return JSONResponse({"classe": nouvelle})

    @protege("parent")
    async def effacer(request: Request):
        donnees = await corps_json(request) or {}
        if donnees.get("confirmation") != "EFFACER":
            return erreur("Confirmation manquante.")
        stock.tout_effacer()
        return JSONResponse({"ok": True})

    async def sante(request: Request):
        return JSONResponse({"ok": True})

    p = "/api/ecole"
    return Starlette(routes=[
        Route(f"{p}/health", sante),
        Route(f"{p}/connexion", connexion, methods=["POST"]),
        Route(f"{p}/deconnexion", deconnexion, methods=["POST"]),
        Route(f"{p}/moi", moi),
        Route(f"{p}/programme", programme),
        Route(f"{p}/serie", serie, methods=["POST"]),
        Route(f"{p}/reponse", reponse, methods=["POST"]),
        Route(f"{p}/tuteur", poser_question, methods=["POST"]),
        Route(f"{p}/autrement", autrement, methods=["POST"]),
        Route(f"{p}/voix", lire_a_voix_haute, methods=["POST"]),
        Route(f"{p}/explication", expliquer, methods=["POST"]),
        Route(f"{p}/ecoute", ecouter, methods=["POST"]),
        Route(f"{p}/reglage-voix", changer_voix, methods=["POST"]),
        Route(f"{p}/coran", coran_sommaire),
        Route(f"{p}/coran/{{numero:int}}", coran_sourate),
        Route(f"{p}/coran/{{numero:int}}/progres", coran_progresser, methods=["POST"]),
        Route(f"{p}/coran/audio/{{recitant}}/{{sourate:int}}/{{verset:int}}", coran_audio),
        Route(f"{p}/voix/{{nom}}", audio),
        Route(f"{p}/suivi", suivi),
        Route(f"{p}/classe", changer_classe, methods=["POST"]),
        Route(f"{p}/effacer", effacer, methods=["POST"]),
    ])

