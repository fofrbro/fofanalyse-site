// Mon cahier : l'espace de révision (maths et français), du CM1 à la 6e.
// Le serveur (ecole-service) tire les exercices, vérifie les réponses et
// garde la progression ; le tuteur IA explique. Ici, seulement l'affichage.
// Script externe, sans style en ligne : compatible avec la CSP du site.
// Les textes venus du serveur et du tuteur sont insérés avec textContent.

const API = "/api/ecole";
const $ = (id) => document.getElementById(id);

const etat = {
  role: null, prenom: "", tuteur: false, voix: false,
  classe: "", classes: [],   // classe choisie par le parent, et toutes les classes
  chapitres: [], progres: {}, // chapitres de la classe et des classes d'avant
  matieres: {}, matiere: lireMemoire("matiere") || "maths",  // onglet choisi sur l'accueil
  chapitre: null,            // chapitre ouvert
  fil: [],                   // conversation avec le tuteur (chapitre ouvert)
  serie: [], position: 0, justes: 0, exercice: null,
};

function lireMemoire(cle) {
  try { return localStorage.getItem(`ecole-${cle}`); } catch { return null; }
}

function ecrireMemoire(cle, valeur) {
  try { localStorage.setItem(`ecole-${cle}`, valeur); } catch { /* navigation privée : tant pis */ }
}

const ACCENTS = ["é", "è", "ê", "à", "â", "ç", "ù", "û", "î", "ï", "ô", "ë"];

const SUGGESTIONS = [
  "Tu peux me réexpliquer avec un exemple ?",
  "Pourquoi on fait comme ça ?",
  "Donne-moi un exercice facile pour m'entraîner",
];

const BRAVO = ["Bravo !", "Super !", "Exact !", "Bien joué !", "Parfait !", "Champion !"];

// --- Outils -------------------------------------------------------------

function el(balise, classe, texte) {
  const e = document.createElement(balise);
  if (classe) e.className = classe;
  if (texte != null) e.textContent = texte;
  return e;
}

async function api(route, donnees) {
  const options = donnees === undefined
    ? { credentials: "same-origin" }
    : { method: "POST", credentials: "same-origin",
        headers: { "Content-Type": "application/json" }, body: JSON.stringify(donnees) };
  const r = await fetch(API + route, options);
  const resultat = await r.json().catch(() => ({}));
  if (r.status === 401 && route !== "/connexion") {
    etat.role = null;
    afficher("connexion");
    throw new Error(resultat.erreur || "Connecte-toi.");
  }
  if (!r.ok) {
    const e = new Error(resultat.erreur || `Erreur ${r.status}`);
    e.statut = r.status;
    throw e;
  }
  return resultat;
}

function afficher(vue) {
  for (const v of document.querySelectorAll(".vue")) v.hidden = v.id !== `vue-${vue}`;
  $("chargement").hidden = true;
  const connecte = vue !== "connexion";
  $("sortir").hidden = !connecte;
  $("etoiles-total").hidden = !connecte;
  $("lien-suivi").hidden = etat.role !== "parent";
  window.scrollTo(0, 0);
}

function pointsNiveau(niveau) {
  const span = el("span", "niveau");
  span.setAttribute("aria-label", `Niveau ${niveau} sur 3`);
  for (let i = 1; i <= 3; i++) span.append(el("i", i <= niveau ? "plein" : ""));
  span.append(document.createTextNode(` niveau ${niveau}`));
  return span;
}

function etoilesTotal() {
  const total = Object.values(etat.progres).reduce((s, p) => s + p.etoiles, 0);
  $("etoiles-total").textContent = `★ ${total}`;
}

// --- Maîtresse virtuelle : lecture à voix haute ----------------------------
// La voix d'OpenAI passe par le serveur (qui garde les audios en cache) ;
// sans elle, ou si elle ne répond pas, la voix du navigateur prend le relais.

const lecteur = new Audio();
let boutonEnCours = null;
let lectureEnCours = null;  // jeton de la lecture en cours : en changer arrête l'ancienne

function arreterLecture() {
  lectureEnCours = null;
  lecteur.pause();
  lecteur.removeAttribute("src");
  if ("speechSynthesis" in window) speechSynthesis.cancel();
  if (boutonEnCours) boutonEnCours.classList.remove("en-cours");
  boutonEnCours = null;
  for (const p of document.querySelectorAll("#cours p")) p.classList.remove("en-cours");
}

function audioDe(texte) {
  // L'adresse de l'audio (voix d'OpenAI, préparée par le serveur), ou null pour la voix de l'appareil.
  if (!etat.voix) return Promise.resolve(null);
  return api("/voix", { texte }).then((r) => r.audio).catch(() => null);
}

function jouer(url, jeton) {
  return new Promise((fini) => {
    lecteur.onended = lecteur.onerror = fini;
    lecteur.src = url;
    lecteur.play().catch(fini);
  }).then(() => lectureEnCours === jeton);
}

function direAvecLAppareil(texte, jeton) {
  return new Promise((fini) => {
    if (!("speechSynthesis" in window)) return fini();
    const phrase = new SpeechSynthesisUtterance(texte);
    phrase.lang = "fr-FR";
    phrase.rate = 0.95;
    const francaise = speechSynthesis.getVoices().find((v) => v.lang.startsWith("fr"));
    if (francaise) phrase.voice = francaise;
    phrase.onend = phrase.onerror = fini;
    speechSynthesis.speak(phrase);
  }).then(() => lectureEnCours === jeton);
}

async function dire(morceaux, bouton, quandMorceau) {
  // Dit les morceaux à la suite ; le suivant se prépare pendant que le précédent se dit.
  const memeBouton = bouton && boutonEnCours === bouton;
  arreterLecture();
  morceaux = morceaux.filter((m) => m && m.trim());
  if (memeBouton || !morceaux.length) return;  // deuxième clic : on arrête
  const jeton = {};
  lectureEnCours = jeton;
  boutonEnCours = bouton || null;
  bouton?.classList.add("en-cours");
  let prochain = audioDe(morceaux[0]);
  for (let i = 0; i < morceaux.length; i++) {
    const url = await prochain;
    if (lectureEnCours !== jeton) return;
    prochain = i + 1 < morceaux.length ? audioDe(morceaux[i + 1]) : null;
    quandMorceau?.(i);
    const continuer = url ? await jouer(url, jeton) : await direAvecLAppareil(morceaux[i], jeton);
    if (!continuer) return;
  }
  if (lectureEnCours === jeton) arreterLecture();
}

function lire(texte, bouton) {
  return dire([texte], bouton);
}

function boutonEcouter(texte, libelle = "🔊 Écouter") {
  const b = el("button", "ecouter petit", libelle);
  b.type = "button";
  b.addEventListener("click", () => lire(texte, b));
  return b;
}

function texteLecon(c) {
  return [c.titre + ".", c.resume, "À retenir.", ...c.retenir, "Exemple.", c.exemple.question, ...c.exemple.etapes]
    .join("\n");
}

function texteEnonce(ex) {
  let texte = ex.enonce;
  if (ex.arabe) texte += `\n${ex.arabe}`;
  if (ex.type === "choix") texte += `\nRéponses possibles : ${ex.options.join(", ou ")}.`;
  if (ex.type === "multi") texte += `\nÉcris : ${ex.champs.map((c) => c.label).join(", puis ")}.`;
  if (ex.unite && ex.type === "nombre") texte += `\nRéponds en ${ex.unite}.`;
  return texte;
}

// --- Le cours de la maîtresse ----------------------------------------------------
// L'IA prépare une vraie explication orale de la leçon (gardée par le serveur),
// dite avec la voix choisie ; les sous-titres suivent sa parole.

async function coursDeLaMaitresse(bouton) {
  if (boutonEnCours === bouton) return arreterLecture();
  const cours = $("cours");
  const chapitre = etat.chapitre;
  cours.hidden = false;
  cours.replaceChildren(el("p", "cours-attente", "La maîtresse prépare son explication…"));
  bouton.disabled = true;
  try {
    const r = await api("/explication", { chapitre: chapitre.id });
    if (etat.chapitre !== chapitre) return;
    const lignes = r.paragraphes.map((p) => el("p", null, p));
    cours.replaceChildren(el("p", "cours-titre", "👩‍🏫 La maîtresse t'explique"), ...lignes);
    bouton.disabled = false;
    dire(r.paragraphes, bouton, (i) => {
      lignes.forEach((l, j) => l.classList.toggle("en-cours", i === j));
      lignes[i].scrollIntoView({ block: "nearest", behavior: "smooth" });
    });
  } catch (err) {
    bouton.disabled = false;
    cours.replaceChildren(el("p", "cours-attente", err.statut === 503
      ? "La maîtresse a besoin de la clé OpenAI pour faire son cours. En attendant, je te lis la leçon."
      : err.message));
    if (err.statut === 503) lire(texteLecon(chapitre), bouton);
  }
}

$("ecouter-lecon").addEventListener("click", (e) => coursDeLaMaitresse(e.currentTarget));
$("ecouter-enonce").addEventListener("click", (e) => lire(texteEnonce(etat.exercice), e.currentTarget));
$("ecouter-autrement").addEventListener("click", (e) => lire($("autrement-texte").textContent, e.currentTarget));
window.addEventListener("hashchange", arreterLecture);

// --- Le micro : poser sa question à voix haute -------------------------------------

const micro = { enregistreur: null, morceaux: [], minuterie: null };

function typeAudioPossible() {
  if (!window.MediaRecorder) return null;
  return ["audio/webm;codecs=opus", "audio/webm", "audio/mp4", "audio/ogg"].find((t) => MediaRecorder.isTypeSupported(t)) || "";
}

async function basculerMicro() {
  const bouton = $("micro");
  if (micro.enregistreur) {
    micro.enregistreur.stop();
    return;
  }
  arreterLecture();
  let flux;
  try {
    flux = await navigator.mediaDevices.getUserMedia({ audio: true });
  } catch {
    etat.fil.push({ role: "assistant", content: "Je n'ai pas accès au micro. Autorise-le dans le navigateur, ou écris ta question.", erreur: true });
    return dessinerFil();
  }
  const type = typeAudioPossible();
  micro.enregistreur = new MediaRecorder(flux, type ? { mimeType: type } : undefined);
  micro.morceaux = [];
  micro.enregistreur.ondataavailable = (e) => e.data.size && micro.morceaux.push(e.data);
  micro.enregistreur.onstop = async () => {
    clearTimeout(micro.minuterie);
    flux.getTracks().forEach((t) => t.stop());
    const audio = new Blob(micro.morceaux, { type: micro.enregistreur.mimeType || "audio/webm" });
    micro.enregistreur = null;
    bouton.classList.remove("en-cours");
    bouton.textContent = "🎤 Parler";
    if (audio.size < 1000) return;
    bouton.disabled = true;
    try {
      const r = await fetch(`${API}/ecoute`, { method: "POST", credentials: "same-origin",
                                                headers: { "Content-Type": audio.type }, body: audio });
      const donnees = await r.json().catch(() => ({}));
      if (!r.ok) throw new Error(donnees.erreur || "Je n'ai pas réussi à t'entendre.");
      await demanderTuteur(donnees.texte);
    } catch (err) {
      etat.fil.push({ role: "assistant", content: err.message, erreur: true });
      dessinerFil();
    } finally {
      bouton.disabled = false;
    }
  };
  micro.enregistreur.start();
  micro.minuterie = setTimeout(() => micro.enregistreur?.stop(), 45000);
  bouton.classList.add("en-cours");
  bouton.textContent = "⏹ J'ai fini";
}

$("micro").addEventListener("click", basculerMicro);

// --- Connexion ----------------------------------------------------------

$("form-connexion").addEventListener("submit", async (e) => {
  e.preventDefault();
  const message = $("message-connexion");
  message.textContent = "";
  try {
    const r = await api("/connexion", { code: $("code").value });
    Object.assign(etat, { role: r.role, prenom: r.prenom, tuteur: r.tuteur, voix: r.voix, classe: r.classe });
    $("code").value = "";
    await chargerProgramme();
    router();
  } catch (err) {
    message.textContent = err.message;
  }
});

$("sortir").addEventListener("click", async () => {
  await api("/deconnexion", {}).catch(() => {});
  etat.role = null;
  location.hash = "";
  afficher("connexion");
});

// --- Accueil ------------------------------------------------------------

async function chargerProgramme() {
  const r = await api("/programme");
  Object.assign(etat, { chapitres: r.chapitres, progres: r.progres, classe: r.classe, classes: r.classes,
                        matieres: r.matieres });
  if (!etat.matieres[etat.matiere]) etat.matiere = "maths";
  etoilesTotal();
}

function titreChapitre(c) {
  return c.classe === etat.classe ? c.titre : `${c.titre} (${c.classe})`;
}

function chapitreConseille() {
  // Dans la classe en cours : le moins travaillé d'abord ; à égalité, celui où il réussit le moins.
  let meilleur = null, note = Infinity;
  for (const c of etat.chapitres.filter((x) => x.classe === etat.classe && x.matiere === etat.matiere)) {
    const p = etat.progres[c.id];
    const taux = p.faits ? p.etoiles / p.faits : 0;
    const score = (p.faits >= 8 ? 1 : 0) * 10 + taux + p.niveau;
    if (score < note) { note = score; meilleur = c; }
  }
  return meilleur;
}

function afficherAccueil() {
  $("bonjour").textContent = `Bonjour ${etat.prenom} !`;
  $("classe-actuelle").textContent = `Programme de ${etat.classe}`;
  const conseil = chapitreConseille();
  if (conseil) {
    const p = etat.progres[conseil.id];
    $("conseil-texte").textContent = p.faits
      ? `${conseil.titre} : tu peux encore progresser ici.`
      : `${conseil.titre} : tu n'as pas encore commencé ce chapitre.`;
    $("conseil-lien").href = `#${conseil.id}`;
    $("conseil").hidden = false;
  }
  const ongletCoran = el("a", "onglet", "Coran");
  ongletCoran.href = "#coran";
  const ongletDevoirs = el("a", "onglet", "📷 Mon devoir");
  ongletDevoirs.href = "#devoirs";
  $("onglets").replaceChildren(...Object.entries(etat.matieres).map(([id, nom]) => {
    const b = el("button", "onglet", nom);
    b.type = "button";
    b.setAttribute("role", "tab");
    b.setAttribute("aria-selected", String(id === etat.matiere));
    b.addEventListener("click", () => { etat.matiere = id; ecrireMemoire("matiere", id); afficherAccueil(); });
    return b;
  }), ongletCoran, ongletDevoirs);
  const deLaMatiere = etat.chapitres.filter((c) => c.matiere === etat.matiere);
  const actuels = deLaMatiere.filter((c) => c.classe === etat.classe);
  const zone = $("domaines");
  zone.replaceChildren();
  for (const d of [...new Set(actuels.map((c) => c.domaine))]) {
    zone.append(el("h2", null, d), grilleChapitres(actuels.filter((x) => x.domaine === d)));
  }

  // Les classes d'avant, repliées : pour réviser.
  const avant = etat.classes.slice(0, etat.classes.indexOf(etat.classe));
  const revisions = $("revisions");
  revisions.replaceChildren();
  if (avant.length) {
    const bloc = el("details", "revisions");
    bloc.append(el("summary", null, `Réviser ${avant.length > 1 ? "les années d'avant" : `le ${avant[0]}`}`));
    for (const classe of avant.reverse()) {
      if (avant.length > 1) bloc.append(el("h3", null, classe));
      bloc.append(grilleChapitres(deLaMatiere.filter((c) => c.classe === classe)));
    }
    revisions.append(bloc);
  }
  afficher("accueil");
}

function grilleChapitres(chapitres) {
  const grille = el("div", "chapitres");
  for (const c of chapitres) {
    const p = etat.progres[c.id];
    const a = el("a", "chapitre");
    a.href = `#${c.id}`;
    const bas = el("span", "chapitre-bas");
    bas.append(pointsNiveau(p.niveau), el("span", "etoiles", `★ ${p.etoiles}`));
    a.append(el("span", "chapitre-titre", c.titre), el("span", "chapitre-resume", c.resume), bas);
    grille.append(a);
  }
  return grille;
}

// --- Chapitre : leçon et tuteur -------------------------------------------

function afficherChapitre(c) {
  if (etat.chapitre?.id !== c.id) etat.fil = [];
  etat.chapitre = c;
  const p = etat.progres[c.id];
  const matiere = etat.matieres[c.matiere] || "";
  $("chap-domaine").textContent = c.classe === etat.classe ? `${matiere} · ${c.domaine}`
    : `Révision ${c.classe} · ${matiere} · ${c.domaine}`;
  $("chap-titre").textContent = c.titre;
  $("chap-resume").textContent = c.resume;
  $("chap-niveau").textContent = `Niveau ${p.niveau} sur 3 · ${p.faits} exercice${p.faits > 1 ? "s" : ""} fait${p.faits > 1 ? "s" : ""}`;
  $("chap-retenir").replaceChildren(...c.retenir.map((r) => el("li", null, r)));
  $("chap-exemple-q").textContent = c.exemple.question;
  $("chap-exemple-etapes").replaceChildren(...c.exemple.etapes.map((e) => el("li", null, e)));

  const actif = etat.tuteur;
  $("form-tuteur").hidden = !actif;
  $("suggestions").hidden = !actif;
  $("tuteur-intro").textContent = actif
    ? "Ton tuteur t'explique avec d'autres mots, ou avec un exemple."
    : "Le tuteur n'est pas encore branché. Tu peux quand même faire les exercices.";
  dessinerFil();
  $("suggestions").replaceChildren(...SUGGESTIONS.map((s) => {
    const b = el("button", "suggestion", s);
    b.type = "button";
    b.addEventListener("click", () => demanderTuteur(s));
    return b;
  }));
  afficher("chapitre");
}

function dessinerFil(attente = false) {
  const fil = $("fil");
  fil.replaceChildren(...etat.fil.map((m) => {
    const bulle = el("p", `bulle ${m.role === "user" ? "eleve" : "ia"}${m.erreur ? " erreur" : ""}`, m.content);
    if (m.role === "assistant" && !m.erreur) bulle.append(boutonEcouter(m.content));
    return bulle;
  }));
  if (attente) fil.append(el("p", "bulle ia attente", "Ton tuteur réfléchit…"));
}

async function demanderTuteur(question) {
  question = question.trim();
  if (!question) return;
  const historique = etat.fil.filter((m) => !m.erreur).slice(-6);
  etat.fil.push({ role: "user", content: question });
  $("question").value = "";
  dessinerFil(true);
  const bouton = $("form-tuteur").querySelector("button");
  bouton.disabled = true;
  try {
    const r = await api("/tuteur", { chapitre: etat.chapitre.id, question, historique });
    etat.fil.push({ role: "assistant", content: r.reponse, dire: true });
  } catch (err) {
    etat.fil.push({ role: "assistant", content: err.message, erreur: true });
  } finally {
    bouton.disabled = false;
    dessinerFil();
    // La maîtresse répond à voix haute
    const derniere = etat.fil[etat.fil.length - 1];
    if (derniere?.dire) {
      derniere.dire = false;
      const boutons = $("fil").querySelectorAll(".bulle.ia .ecouter");
      if (boutons.length) lire(derniere.content, boutons[boutons.length - 1]);
    }
  }
}

$("form-tuteur").addEventListener("submit", (e) => {
  e.preventDefault();
  demanderTuteur($("question").value);
});

// --- Exercices ------------------------------------------------------------

async function commencerSerie() {
  const c = etat.chapitre;
  $("commencer").disabled = true;
  try {
    const r = await api("/serie", { chapitre: c.id });
    Object.assign(etat, { serie: r.exercices, position: 0, justes: 0 });
    $("retour-lecon").href = `#${c.id}`;
    $("fin").hidden = true;
    $("carte").hidden = false;
    afficher("exercices");
    afficherExercice();
  } catch (err) {
    $("chap-niveau").textContent = err.message;
  } finally {
    $("commencer").disabled = false;
  }
}

$("commencer").addEventListener("click", commencerSerie);
$("encore").addEventListener("click", commencerSerie);

function afficherExercice() {
  arreterLecture();
  const ex = etat.serie[etat.position];
  etat.exercice = ex;
  const total = etat.serie.length;
  $("compteur").textContent = `${etat.position + 1} / ${total} · ★ ${etat.justes}`;
  $("piste").style.width = `${(100 * etat.position) / total}%`;
  $("carte").classList.remove("juste");

  const enonce = $("enonce");
  enonce.textContent = ex.enonce;
  $("arabe").hidden = !ex.arabe;
  $("arabe").textContent = ex.arabe || "";
  enonce.classList.toggle("grand", Boolean(ex.grand));

  const form = $("form-reponse");
  form.replaceChildren();
  form.classList.remove("rate");
  if (ex.type === "choix") {
    const options = el("div", "options");
    for (const o of ex.options) {
      const b = el("button", "option", o);
      b.type = "button";
      b.addEventListener("click", () => envoyer(o, b));
      options.append(b);
    }
    form.append(options);
  } else {
    const champs = ex.type === "multi" ? ex.champs : [{ label: ex.unite || "" }];
    champs.forEach((c, i) => {
      const bloc = el("span", "champ");
      const input = el("input", ex.type === "multi" ? "petit" : ex.type === "texte" ? "mot" : "");
      input.type = "text";
      if (ex.type === "texte") {
        Object.assign(input, { spellcheck: false, autocapitalize: "off" });
        input.setAttribute("autocorrect", "off");
      } else {
        input.inputMode = "decimal";
      }
      input.autocomplete = "off";
      input.id = `rep-${i}`;
      input.setAttribute("aria-label", c.label || "Ta réponse");
      bloc.append(input);
      if (c.label) bloc.append(el("span", "unite", c.label));
      form.append(bloc);
    });
    const verifier = el("button", "bouton", "Vérifier");
    verifier.type = "submit";
    form.append(verifier);
    if (ex.type === "texte") form.append(clavierAccents());
    setTimeout(() => $("rep-0")?.focus(), 50);
  }

  $("indice").hidden = true;
  $("indice").textContent = ex.indice;
  $("voir-indice").hidden = false;
  $("retour-reponse").textContent = "";
  $("retour-reponse").className = "retour-reponse";
  $("correction").hidden = true;
  $("autrement").hidden = true;
  $("boutons-suite").hidden = true;
  $("pas-compris").disabled = false;
}

function clavierAccents() {
  // Des lettres accentuées à portée de doigt : sur un clavier d'ordinateur, elles ne sont pas toujours faciles.
  const rangee = el("div", "accents");
  for (const lettre of ACCENTS) {
    const b = el("button", "accent", lettre);
    b.type = "button";
    b.setAttribute("aria-label", `Ajouter ${lettre}`);
    b.addEventListener("click", () => {
      const champ = $("rep-0");
      const debut = champ.selectionStart ?? champ.value.length, fin = champ.selectionEnd ?? debut;
      champ.value = champ.value.slice(0, debut) + lettre + champ.value.slice(fin);
      champ.focus();
      champ.setSelectionRange(debut + 1, debut + 1);
    });
    rangee.append(b);
  }
  return rangee;
}

$("voir-indice").addEventListener("click", () => {
  $("indice").hidden = false;
  $("voir-indice").hidden = true;
});

$("form-reponse").addEventListener("submit", (e) => {
  e.preventDefault();
  const ex = etat.exercice;
  const valeurs = [...$("form-reponse").querySelectorAll("input")].map((i) => i.value.trim());
  if (valeurs.some((v) => v === "")) {
    $("retour-reponse").className = "retour-reponse";
    $("retour-reponse").textContent = valeurs.length > 1 ? "Remplis toutes les cases." : "Écris ta réponse.";
    return;
  }
  envoyer(ex.type === "multi" ? valeurs : valeurs[0]);
});

async function envoyer(reponse, boutonOption) {
  const ex = etat.exercice;
  const zone = $("retour-reponse");
  let r;
  try {
    r = await api("/reponse", { id: ex.id, reponse });
  } catch (err) {
    zone.className = "retour-reponse faux";
    zone.textContent = err.message;
    return;
  }
  if (r.correct) {
    etat.justes += r.essais === 1 ? 1 : 0;
    zone.className = "retour-reponse ok";
    zone.textContent = (r.essais === 1 ? "★ " : "") + BRAVO[Math.floor(Math.random() * BRAVO.length)];
    $("carte").classList.add("juste");
    boutonOption?.classList.add("bonne");
  } else if (!r.termine) {
    zone.className = "retour-reponse faux";
    zone.textContent = r.essais === 1 ? "Pas tout à fait. Réessaie !" : "Encore un essai. Regarde l'indice.";
    if (r.essais === 2) { $("indice").hidden = false; $("voir-indice").hidden = true; }
    boutonOption && (boutonOption.disabled = true);
    const carte = $("carte");
    carte.classList.remove("secoue"); void carte.offsetWidth; carte.classList.add("secoue");
    return;
  } else {
    zone.className = "retour-reponse faux";
    zone.textContent = `La bonne réponse était ${r.reponse_texte}. Regarde comment on fait.`;
  }
  // Exercice terminé : on fige les réponses et on montre la correction
  $("form-reponse").classList.toggle("rate", !r.correct);
  for (const x of $("form-reponse").querySelectorAll("input, button")) x.disabled = true;
  $("voir-indice").hidden = true;
  $("correction-texte").textContent = r.explication;
  $("correction").hidden = false;
  $("pas-compris").hidden = !etat.tuteur;
  $("boutons-suite").hidden = false;
  $("suivant").textContent = etat.position + 1 < etat.serie.length ? "Question suivante" : "Voir mon score";
  if (r.nouveau_niveau) {
    const p = etat.progres[etat.chapitre.id];
    const monte = r.nouveau_niveau > p.niveau;
    p.niveau = r.nouveau_niveau;
    zone.textContent += monte ? ` Tu passes au niveau ${r.nouveau_niveau} !` : "";
  }
  $("suivant").focus();
}

$("pas-compris").addEventListener("click", async () => {
  const bouton = $("pas-compris");
  bouton.disabled = true;
  $("autrement").hidden = false;
  $("autrement-texte").textContent = "Ton tuteur réfléchit…";
  try {
    const r = await api("/autrement", { id: etat.exercice.id });
    $("autrement-texte").textContent = r.reponse;
    lire(r.reponse, $("ecouter-autrement"));
  } catch (err) {
    $("autrement-texte").textContent = err.message;
    bouton.disabled = false;
  }
});

$("suivant").addEventListener("click", async () => {
  etat.position += 1;
  if (etat.position < etat.serie.length) return afficherExercice();
  // Fin de la série
  $("piste").style.width = "100%";
  $("carte").hidden = true;
  const n = etat.serie.length, j = etat.justes;
  $("compteur").textContent = `${n} / ${n} · ★ ${j}`;
  $("fin-titre").textContent = j === n ? `Parfait, ${etat.prenom} !` : j >= n * 0.6 ? "Bien joué !" : "Continue, tu progresses !";
  $("fin-texte").textContent = `Tu as gagné ${j} étoile${j > 1 ? "s" : ""} sur ${n}.` +
    (j < n * 0.6 ? " Relis la leçon, ou pose une question à ton tuteur, puis refais une série." : "");
  $("fin").hidden = false;
  await chargerProgramme().catch(() => {});
});

// --- Suivi du parent -----------------------------------------------------------

const JOURS = ["di", "lu", "ma", "me", "je", "ve", "sa"];

function pourcent(ok, n) { return n ? Math.round((100 * ok) / n) : null; }

function pastille(p) {
  if (p === null) return el("span", "pastille neutre", "—");
  return el("span", `pastille ${p >= 70 ? "bien" : p < 50 ? "attention" : "neutre"}`, `${p} %`);
}

async function afficherSuivi() {
  const s = await api("/suivi");
  const titres = Object.fromEntries(etat.chapitres.map((c) => [c.id, titreChapitre(c)]));
  const classeDe = Object.fromEntries(etat.chapitres.map((c) => [c.id, c.classe]));
  // La classe en cours, plus les chapitres d'avant qui ont été révisés.
  const lignes = s.chapitres.filter((c) => classeDe[c.chapitre] === s.classe || c.faits > 0);

  $("choix-classe").replaceChildren(...s.classes.map((nom) => {
    const option = el("option", null, nom);
    option.value = nom;
    option.selected = nom === s.classe;
    return option;
  }));
  const total = s.chapitres.reduce((a, c) => a + c.faits, 0);
  const semaine = s.chapitres.reduce((a, c) => a + c.faits_7j, 0);
  const faibles = s.chapitres.filter((c) => c.faits >= 4 && pourcent(c.reussis, c.faits) < 50).map((c) => titres[c.chapitre]);
  $("suivi-resume").textContent =
    `${total} exercice${total > 1 ? "s" : ""} au total, dont ${semaine} ces 7 derniers jours. ` +
    (faibles.length ? `À revoir : ${faibles.join(", ")}. ` : "") +
    (s.tuteur ? `Tuteur : ${s.appels_ia_aujourdhui} appel${s.appels_ia_aujourdhui > 1 ? "s" : ""} aujourd'hui sur ${s.plafond_ia} autorisés.`
              : "Tuteur non branché (clé OpenAI absente).") +
    (s.voix ? ` Voix : ${s.appels_voix_aujourdhui} audio${s.appels_voix_aujourdhui > 1 ? "s" : ""} nouveau${s.appels_voix_aujourdhui > 1 ? "x" : ""} aujourd'hui sur ${s.plafond_voix} (ceux déjà écoutés sont gratuits).`
            : " Voix d'OpenAI non branchée : la page utilise la voix de l'appareil.");
  if (s.erreur_openai) {
    const quand = new Date(s.erreur_openai.quand * 1000).toLocaleString("fr-FR", { dateStyle: "short", timeStyle: "short" });
    $("suivi-resume").textContent += ` Dernier échec d'OpenAI (${s.erreur_openai.service}, ${quand}) : ${s.erreur_openai.cause}`;
  }

  const max = Math.max(1, ...s.jours.map((j) => j.exercices));
  $("activite").replaceChildren(...s.jours.map((j) => {
    const bloc = el("div", "jour");
    const barre = el("div", `jour-barre${j.exercices ? "" : " vide"}`);
    barre.style.height = `${Math.max(2, (100 * j.exercices) / max)}%`;
    if (j.exercices) barre.append(el("span", "jour-nombre", j.exercices));
    const date = new Date(`${j.jour}T12:00:00`);
    bloc.title = `${date.toLocaleDateString("fr-FR")} : ${j.exercices} exercice${j.exercices > 1 ? "s" : ""}`;
    bloc.append(barre, el("span", "jour-nom", JOURS[date.getDay()]));
    return bloc;
  }));

  $("suivi-chapitres").replaceChildren(...lignes.map((c) => {
    const tr = el("tr");
    const rates = el("ul", "rates");
    rates.append(...c.derniers_rates.map((r) => el("li", null, r)));
    const cellules = [
      el("td", null, titres[c.chapitre]),
      el("td", "nombre", `${c.niveau} / 3`),
      el("td", "nombre", String(c.faits)),
      el("td"), el("td", "nombre", c.faits_7j ? `${c.reussis_7j} / ${c.faits_7j}` : "—"), el("td"),
    ];
    cellules[3].append(pastille(pourcent(c.reussis, c.faits)));
    cellules[5].append(c.derniers_rates.length ? rates : document.createTextNode("—"));
    tr.append(...cellules);
    return tr;
  }));

  $("choix-voix").replaceChildren(...(s.voix_disponibles || []).map((v) => {
    const o = el("option", null, v.charAt(0).toUpperCase() + v.slice(1) + (v === s.voix_choisie ? " (choisie)" : ""));
    o.value = v;
    o.selected = v === s.voix_choisie;
    return o;
  }));
  $("essayer-voix").disabled = $("garder-voix").disabled = !s.voix;
  if (!s.voix) $("message-voix").textContent = "Ajoutez la clé OpenAI (ECOLE_OPENAI_API_KEY) pour avoir la voix naturelle.";

  const coranSuivi = $("suivi-coran");
  coranSuivi.replaceChildren(...(s.coran || []).map((c) => {
    const li = el("li", null, `${c.numero}. ${c.nom} : ${c.versets_appris} verset${c.versets_appris > 1 ? "s" : ""} sur ${c.versets}` +
      (c.versets_appris >= c.versets ? " ✓" : ""));
    li.append(el("span", "meta", `Dernier progrès : ${new Date(c.maj * 1000).toLocaleDateString("fr-FR")}`));
    return li;
  }));
  if (!(s.coran || []).length) coranSuivi.append(el("li", null, "Pas encore commencé."));

  const liste = $("suivi-questions");
  liste.replaceChildren(...s.questions.map((q) => {
    const li = el("li", q.bloquee ? "bloquee" : "", q.question);
    const date = new Date(q.cree_le * 1000).toLocaleString("fr-FR", { dateStyle: "short", timeStyle: "short" });
    li.append(el("span", "meta", `${titres[q.chapitre] || ""} · ${date}${q.bloquee ? " · bloqué par le filtre" : ""}`));
    return li;
  }));
  if (!s.questions.length) liste.append(el("li", null, "Aucune question pour l'instant."));
  afficher("suivi");
}

$("form-classe").addEventListener("submit", async (e) => {
  e.preventDefault();
  const message = $("message-classe");
  try {
    const r = await api("/classe", { classe: $("choix-classe").value });
    await chargerProgramme();
    await afficherSuivi();
    message.className = "message ok";
    message.textContent = `C'est fait : ${etat.prenom} suit maintenant le programme de ${r.classe}.`;
  } catch (err) {
    message.className = "message";
    message.textContent = err.message;
  }
});

$("essayer-voix").addEventListener("click", async (e) => {
  const voixEssayee = $("choix-voix").value;
  const bouton = e.currentTarget;
  arreterLecture();
  try {
    const r = await api("/voix", { voix: voixEssayee, texte: `Bonjour ${etat.prenom} ! Je suis ta maîtresse. `
      + "Aujourd'hui, on va découvrir les fractions ensemble. Tu es prêt ? C'est parti !" });
    const jeton = {};
    lectureEnCours = jeton;
    boutonEnCours = bouton;
    bouton.classList.add("en-cours");
    await jouer(r.audio, jeton);
    if (lectureEnCours === jeton) arreterLecture();
  } catch (err) {
    $("message-voix").textContent = err.message;
  }
});

$("garder-voix").addEventListener("click", async () => {
  try {
    const r = await api("/reglage-voix", { voix: $("choix-voix").value });
    $("message-voix").className = "message ok";
    $("message-voix").textContent = `C'est fait : la maîtresse parle maintenant avec la voix « ${r.voix} ».`;
    await afficherSuivi();
  } catch (err) {
    $("message-voix").className = "message";
    $("message-voix").textContent = err.message;
  }
});

let confirmer = false;
$("effacer").addEventListener("click", async () => {
  const bouton = $("effacer"), message = $("message-effacer");
  if (!confirmer) {
    confirmer = true;
    bouton.textContent = "Sûr ? Cliquer encore pour tout effacer";
    setTimeout(() => { confirmer = false; bouton.textContent = "Tout effacer"; }, 4000);
    return;
  }
  confirmer = false;
  bouton.textContent = "Tout effacer";
  try {
    await api("/effacer", { confirmation: "EFFACER" });
    message.className = "message ok";
    message.textContent = "Tout est effacé.";
    await chargerProgramme();
    await afficherSuivi();
  } catch (err) {
    message.className = "message";
    message.textContent = err.message;
  }
});

// --- Coran ------------------------------------------------------------------------
// Le texte et les récitations viennent du serveur, qui les tient de sources de
// référence (Tanzil, traduction Hamidullah, everyayah.com). Ici, rien n'est écrit
// ni lu par la synthèse vocale : seule la voix des récitants est utilisée.

const coran = { sourate: null, recitants: {}, sources: "", file: [], cache: false };
const lecteurCoran = new Audio();

function recitant() {
  const choisi = lireMemoire("recitant");
  return coran.recitants[choisi] ? choisi : "husary";
}

function audioVerset(sourate, verset) {
  return `${API}/coran/audio/${recitant()}/${sourate}/${verset}`;
}

function jouerFile(versets, repetitions = 1) {
  // versets : liste de numéros (0 = basmala), joués à la suite, chacun « repetitions » fois.
  arreterLecture();
  coran.file = versets.flatMap((v) => Array(repetitions).fill(v));
  jouerSuivant();
}

function jouerSuivant() {
  const v = coran.file.shift();
  if (v === undefined) return marquerVerset(null);
  marquerVerset(v);
  lecteurCoran.src = audioVerset(coran.sourate.numero, v);
  lecteurCoran.play().catch(() => {
    $("sourate-progres").textContent = "La récitation n'a pas pu être chargée. Réessaie dans un moment.";
  });
}

function arreterCoran() {
  coran.file = [];
  lecteurCoran.pause();
  marquerVerset(null);
}

lecteurCoran.addEventListener("ended", jouerSuivant);
lecteurCoran.addEventListener("error", () => { coran.file = []; marquerVerset(null); });

function marquerVerset(v) {
  for (const carte of document.querySelectorAll("#versets .verset")) {
    carte.classList.toggle("focus", Number(carte.dataset.n) === v);
  }
}

function carteVerset(verset, avecBoutons = true) {
  const carte = el("div", "verset");
  carte.dataset.n = verset.n;
  const arabe = el("p", "verset-arabe", verset.arabe);
  arabe.dir = "rtl";
  arabe.lang = "ar";
  carte.append(arabe);
  if ($("voir-traduction").checked) carte.append(el("p", "verset-fr", `${verset.n}. ${verset.francais}`));
  if (avecBoutons) {
    const bas = el("div", "verset-bas");
    bas.append(el("span", "numero-verset", String(verset.n)));
    for (const [libelle, fois] of [["▶ Écouter", 1], ["🔁 3 fois", 3]]) {
      const b = el("button", "ecouter petit", libelle);
      b.type = "button";
      b.addEventListener("click", () => jouerFile([verset.n], fois));
      bas.append(b);
    }
    carte.append(bas);
  }
  return carte;
}

async function afficherCoran() {
  arreterCoran();
  afficher("coran");
  $("coran-message").textContent = "Chargement…";
  try {
    const r = await api("/coran");
    Object.assign(coran, { recitants: r.recitants, sources: r.sources });
    $("coran-message").textContent = "";
    $("coran-sources").textContent = r.sources;
    $("liste-sourates").replaceChildren(...r.sourates.map((s) => {
      const a = el("a", "chapitre");
      a.href = `#coran-${s.numero}`;
      const nomArabe = el("span", "sourate-arabe", s.nom_arabe);
      nomArabe.dir = "rtl";
      nomArabe.lang = "ar";
      const fini = s.appris >= s.versets;
      a.append(el("span", "chapitre-titre", `${s.numero}. ${s.nom}`), nomArabe,
               el("span", "chapitre-resume", `${s.versets} versets · ${fini ? "apprise ✓" : `${s.appris} appris`}`));
      return a;
    }));
  } catch (err) {
    $("coran-message").textContent = err.message;
  }
}

async function afficherSourate(numero) {
  arreterCoran();
  if (!coran.sources) {
    const r = await api("/coran");
    Object.assign(coran, { recitants: r.recitants, sources: r.sources });
  }
  const s = await api(`/coran/${numero}`);
  coran.sourate = s;
  coran.cache = false;
  $("sourate-surtitre").textContent = `Sourate ${s.numero}`;
  $("sourate-titre").textContent = s.nom;
  $("sourate-nom-arabe").textContent = s.nom_arabe;
  $("sourate-sources").textContent = coran.sources;
  $("choix-recitant").replaceChildren(...Object.entries(coran.recitants).map(([id, nom]) => {
    const o = el("option", null, nom);
    o.value = id;
    o.selected = id === recitant();
    return o;
  }));
  $("voir-traduction").checked = lireMemoire("traduction") === "oui";
  dessinerSourate();
  $("quiz-coran").replaceChildren();
  $("quiz-coran-lancer").parentElement.hidden = s.versets.length < 3;
  afficher("sourate");
}

function dessinerSourate() {
  const s = coran.sourate;
  $("sourate-progres").textContent = s.appris >= s.versets.length
    ? `Tu connais toute la sourate ✓ Révise-la souvent pour ne pas l'oublier.`
    : `Versets appris : ${s.appris} sur ${s.versets.length}.`;
  $("versets").replaceChildren(...s.versets.map((v) => {
    const carte = carteVerset(v);
    carte.classList.toggle("appris", v.n <= s.appris);
    return carte;
  }));
  dessinerProfesseur();
}

function versetEnCours() {
  const s = coran.sourate;
  return s.versets[Math.min(s.appris, s.versets.length - 1)];
}

function dessinerProfesseur() {
  const s = coran.sourate;
  const fini = s.appris >= s.versets.length;
  const v = versetEnCours();
  $("prof-consigne").textContent = fini
    ? "Bravo ! Pour réviser, récite toute la sourate avec le récitant, puis seul."
    : `Verset ${v.n} : écoute-le, répète-le, puis récite-le sans regarder.`;
  const carte = carteVerset(v, false);
  carte.classList.remove("focus");
  if (coran.cache) carte.querySelector(".verset-arabe").classList.add("cache");
  $("prof-verset").replaceChildren(...carte.childNodes);
  $("prof-etapes").hidden = fini;
  $("prof-cacher").textContent = coran.cache ? "Montrer le verset" : "3. Réciter sans regarder";
}

$("prof-ecouter3").addEventListener("click", () => jouerFile([versetEnCours().n], 3));
$("prof-repeter").addEventListener("click", () => jouerFile([versetEnCours().n], 1));
$("prof-cacher").addEventListener("click", () => { coran.cache = !coran.cache; dessinerProfesseur(); });
$("prof-retenu").addEventListener("click", async () => {
  const s = coran.sourate;
  const appris = Math.min(s.appris + 1, s.versets.length);
  try {
    await api(`/coran/${s.numero}/progres`, { appris });
    s.appris = appris;
    coran.cache = false;
    dessinerSourate();
  } catch (err) {
    $("prof-consigne").textContent = err.message;
  }
});
$("prof-depuis-debut").addEventListener("click", () => {
  const s = coran.sourate;
  const jusqua = Math.max(1, Math.min(s.appris + 1, s.versets.length));
  jouerFile([...(s.basmala ? [0] : []), ...s.versets.slice(0, jusqua).map((v) => v.n)]);
});
$("ecouter-sourate").addEventListener("click", () => {
  const s = coran.sourate;
  jouerFile([...(s.basmala ? [0] : []), ...s.versets.map((v) => v.n)]);
});
$("arreter-coran").addEventListener("click", arreterCoran);
$("choix-recitant").addEventListener("change", (e) => { ecrireMemoire("recitant", e.target.value); arreterCoran(); });
$("voir-traduction").addEventListener("change", (e) => {
  ecrireMemoire("traduction", e.target.checked ? "oui" : "non");
  dessinerSourate();
});

$("quiz-coran-lancer").addEventListener("click", () => {
  // Les versets proposés sont ceux de la sourate, tels quels : rien n'est inventé.
  const versets = coran.sourate.versets;
  const i = Math.floor(Math.random() * (versets.length - 1));
  const bonne = versets[i + 1];
  const autres = versets.filter((v) => v.n !== bonne.n && v.n !== versets[i].n)
    .sort(() => Math.random() - 0.5).slice(0, 2);
  const options = [bonne, ...autres].sort(() => Math.random() - 0.5);
  const zone = $("quiz-coran");
  const consigne = el("p", "prof-consigne", `Après le verset ${versets[i].n} :`);
  const debut = carteVerset(versets[i], false);
  const liste = el("div", "options-versets");
  for (const v of options) {
    const b = el("button", "option-verset");
    b.type = "button";
    const arabe = el("p", "verset-arabe", v.arabe);
    arabe.dir = "rtl";
    arabe.lang = "ar";
    b.append(arabe);
    b.addEventListener("click", () => {
      b.classList.add(v.n === bonne.n ? "bonne" : "fausse");
      if (v.n === bonne.n) {
        consigne.textContent = `Bravo ! C'est le verset ${bonne.n}.`;
        jouerFile([bonne.n]);
      } else {
        consigne.textContent = "Ce n'est pas celui-là. Réécoute le verset et réessaie.";
      }
    });
    liste.append(b);
  }
  zone.replaceChildren(consigne, debut, liste);
});

// --- Devoirs en photo ----------------------------------------------------------------
// La photo est réduite ici (1 600 px au plus, JPEG) avant l'envoi. Le serveur ne renvoie la
// solution à l'enfant que si le parent l'a débloquée.

async function reduirePhoto(fichier) {
  const image = await createImageBitmap(fichier);
  const echelle = Math.min(1, 1600 / Math.max(image.width, image.height));
  const toile = document.createElement("canvas");
  toile.width = Math.round(image.width * echelle);
  toile.height = Math.round(image.height * echelle);
  toile.getContext("2d").drawImage(image, 0, 0, toile.width, toile.height);
  return new Promise((ok) => toile.toBlob(ok, "image/jpeg", 0.85));
}

function carteDevoir(d) {
  const carte = el("article", "devoir");
  const date = new Date(d.cree_le * 1000).toLocaleString("fr-FR", { dateStyle: "medium", timeStyle: "short" });
  const entete = el("div", "devoir-entete");
  entete.append(el("span", null, d.matiere || "Exercice"), el("span", null, date));
  const photo = el("img", "devoir-photo");
  photo.src = `${API}/devoirs/${d.id}/photo`;
  photo.alt = "Photo de l'exercice";
  photo.loading = "lazy";
  carte.append(entete, photo, el("h3", null, "L'énoncé"), el("p", null, d.enonce));

  const titreExplication = el("h3", null, "Comment t'y prendre ");
  titreExplication.append(boutonEcouter(d.explication, "🔊 La maîtresse t'explique"));
  carte.append(titreExplication, el("p", "explication", d.explication));

  if (etat.role === "parent") {
    carte.append(el("h3", null, "La solution (pour toi) — proposée par l'IA, à vérifier"), el("p", "solution", d.solution));
    const actions = el("div", "ligne");
    const basculer = el("button", "bouton secondaire",
      d.solution_visible ? `🔒 Cacher la solution à ${etat.prenom}` : `🔓 Autoriser ${etat.prenom} à voir la solution`);
    basculer.type = "button";
    basculer.addEventListener("click", async () => {
      const r = await api(`/devoirs/${d.id}/solution`, { visible: !d.solution_visible });
      carte.replaceWith(carteDevoir(r));
    });
    const effacer = el("button", "bouton danger", "Effacer");
    effacer.type = "button";
    effacer.addEventListener("click", async () => {
      if (!effacer.dataset.sur) { effacer.dataset.sur = "1"; effacer.textContent = "Sûr ? Cliquer encore"; return; }
      await api(`/devoirs/${d.id}/effacer`, {});
      carte.remove();
    });
    actions.append(basculer, effacer);
    carte.append(actions);
  } else if (d.solution) {
    carte.append(el("h3", null, "La solution (débloquée par ton parent)"), el("p", "solution", d.solution));
  } else {
    carte.append(el("p", "verrou", "🔒 La solution est réservée à ton parent. Essaie d'abord tout seul ! "
      + "Si tu bloques vraiment, demande-lui de la débloquer."));
  }
  return carte;
}

async function afficherDevoirs() {
  afficher("devoirs");
  $("devoirs-intro").textContent = etat.role === "parent"
    ? `Les exercices photographiés par ${etat.prenom}. Toi seul vois la solution ; tu peux la débloquer pour lui.`
    : "Photographie l'énoncé de ton exercice : ta maîtresse t'explique comment t'y prendre. La solution, elle, est réservée à ton parent.";
  const r = await api("/devoirs");
  $("liste-devoirs").replaceChildren(...r.devoirs.map(carteDevoir));
}

$("photo-devoir").addEventListener("change", async (e) => {
  const fichier = e.target.files[0];
  e.target.value = "";
  if (!fichier) return;
  const message = $("devoir-message");
  message.className = "message ok";
  message.textContent = "Je regarde ton exercice… (quelques secondes)";
  try {
    const photo = await reduirePhoto(fichier);
    const reponse = await fetch(`${API}/devoirs`, { method: "POST", credentials: "same-origin",
                                                  headers: { "Content-Type": "image/jpeg" }, body: photo });
    const d = await reponse.json().catch(() => ({}));
    if (!reponse.ok) throw new Error(d.erreur || `Erreur ${reponse.status}`);
    message.textContent = "";
    const carte = carteDevoir(d);
    $("liste-devoirs").prepend(carte);
    carte.querySelector(".ecouter")?.click();  // la maîtresse explique tout de suite
  } catch (err) {
    message.className = "message";
    message.textContent = err.message;
  }
});

// --- Navigation (#accueil, #fractions, #suivi…) -------------------------------

async function router() {
  if (!etat.role) return afficher("connexion");
  const cible = location.hash.slice(1);
  const chapitre = etat.chapitres.find((c) => c.id === cible);
  try {
    if (cible !== "coran" && !cible.startsWith("coran-")) arreterCoran();
    if (chapitre) afficherChapitre(chapitre);
    else if (cible === "coran") await afficherCoran();
    else if (cible === "devoirs") await afficherDevoirs();
    else if (/^coran-\d+$/.test(cible)) await afficherSourate(Number(cible.slice(6)));
    else if (cible === "suivi" && etat.role === "parent") await afficherSuivi();
    else { await chargerProgramme(); afficherAccueil(); }
  } catch (err) {
    if (etat.role) { $("chargement").hidden = false; $("chargement").textContent = err.message; }
  }
}

window.addEventListener("hashchange", router);

(async function demarrer() {
  try {
    const moi = await api("/moi");
    Object.assign(etat, { role: moi.role, prenom: moi.prenom, tuteur: moi.tuteur, voix: moi.voix, classe: moi.classe });
    await chargerProgramme();
  } catch {
    etat.role = null;
  }
  router();
})();
