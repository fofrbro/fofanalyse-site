// Mon cahier de maths : l'espace de révision de CM1.
// Le serveur (ecole-service) tire les exercices, vérifie les réponses et
// garde la progression ; le tuteur IA explique. Ici, seulement l'affichage.
// Script externe, sans style en ligne : compatible avec la CSP du site.
// Les textes venus du serveur et du tuteur sont insérés avec textContent.

const API = "/api/ecole";
const $ = (id) => document.getElementById(id);

const etat = {
  role: null, prenom: "", tuteur: false,
  chapitres: [], progres: {},
  chapitre: null,            // chapitre ouvert
  fil: [],                   // conversation avec le tuteur (chapitre ouvert)
  serie: [], position: 0, justes: 0, exercice: null,
};

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

// --- Connexion ----------------------------------------------------------

$("form-connexion").addEventListener("submit", async (e) => {
  e.preventDefault();
  const message = $("message-connexion");
  message.textContent = "";
  try {
    const r = await api("/connexion", { code: $("code").value });
    Object.assign(etat, { role: r.role, prenom: r.prenom, tuteur: r.tuteur });
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
  etat.chapitres = r.chapitres;
  etat.progres = r.progres;
  etoilesTotal();
}

function chapitreConseille() {
  // Le moins travaillé d'abord ; à égalité, celui où il réussit le moins.
  let meilleur = null, note = Infinity;
  for (const c of etat.chapitres) {
    const p = etat.progres[c.id];
    const taux = p.faits ? p.etoiles / p.faits : 0;
    const score = (p.faits >= 8 ? 1 : 0) * 10 + taux + p.niveau;
    if (score < note) { note = score; meilleur = c; }
  }
  return meilleur;
}

function afficherAccueil() {
  $("bonjour").textContent = `Bonjour ${etat.prenom} !`;
  const conseil = chapitreConseille();
  if (conseil) {
    const p = etat.progres[conseil.id];
    $("conseil-texte").textContent = p.faits
      ? `${conseil.titre} : tu peux encore progresser ici.`
      : `${conseil.titre} : tu n'as pas encore commencé ce chapitre.`;
    $("conseil-lien").href = `#${conseil.id}`;
    $("conseil").hidden = false;
  }
  const zone = $("domaines");
  zone.replaceChildren();
  const domaines = [...new Set(etat.chapitres.map((c) => c.domaine))];
  for (const d of domaines) {
    zone.append(el("h2", null, d));
    const grille = el("div", "chapitres");
    for (const c of etat.chapitres.filter((x) => x.domaine === d)) {
      const p = etat.progres[c.id];
      const a = el("a", "chapitre");
      a.href = `#${c.id}`;
      const bas = el("span", "chapitre-bas");
      bas.append(pointsNiveau(p.niveau), el("span", "etoiles", `★ ${p.etoiles}`));
      a.append(el("span", "chapitre-titre", c.titre), el("span", "chapitre-resume", c.resume), bas);
      grille.append(a);
    }
    zone.append(grille);
  }
  afficher("accueil");
}

// --- Chapitre : leçon et tuteur -------------------------------------------

function afficherChapitre(c) {
  if (etat.chapitre?.id !== c.id) etat.fil = [];
  etat.chapitre = c;
  const p = etat.progres[c.id];
  $("chap-domaine").textContent = c.domaine;
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
  fil.replaceChildren(...etat.fil.map((m) =>
    el("p", `bulle ${m.role === "user" ? "eleve" : "ia"}${m.erreur ? " erreur" : ""}`, m.content)));
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
    etat.fil.push({ role: "assistant", content: r.reponse });
  } catch (err) {
    etat.fil.push({ role: "assistant", content: err.message, erreur: true });
  } finally {
    bouton.disabled = false;
    dessinerFil();
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
  const ex = etat.serie[etat.position];
  etat.exercice = ex;
  const total = etat.serie.length;
  $("compteur").textContent = `${etat.position + 1} / ${total} · ★ ${etat.justes}`;
  $("piste").style.width = `${(100 * etat.position) / total}%`;
  $("carte").classList.remove("juste");

  const enonce = $("enonce");
  enonce.textContent = ex.enonce;
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
      const input = el("input", ex.type === "multi" ? "petit" : "");
      input.type = "text";
      input.inputMode = "decimal";
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
  const titres = Object.fromEntries(etat.chapitres.map((c) => [c.id, c.titre]));
  const total = s.chapitres.reduce((a, c) => a + c.faits, 0);
  const semaine = s.chapitres.reduce((a, c) => a + c.faits_7j, 0);
  const faibles = s.chapitres.filter((c) => c.faits >= 4 && pourcent(c.reussis, c.faits) < 50).map((c) => titres[c.chapitre]);
  $("suivi-resume").textContent =
    `${total} exercice${total > 1 ? "s" : ""} au total, dont ${semaine} ces 7 derniers jours. ` +
    (faibles.length ? `À revoir : ${faibles.join(", ")}. ` : "") +
    (s.tuteur ? `Tuteur : ${s.appels_ia_aujourdhui} appel${s.appels_ia_aujourdhui > 1 ? "s" : ""} aujourd'hui sur ${s.plafond_ia} autorisés.`
              : "Tuteur non branché (clé OpenAI absente).");

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

  $("suivi-chapitres").replaceChildren(...s.chapitres.map((c) => {
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

// --- Navigation (#accueil, #fractions, #suivi…) -------------------------------

async function router() {
  if (!etat.role) return afficher("connexion");
  const cible = location.hash.slice(1);
  const chapitre = etat.chapitres.find((c) => c.id === cible);
  try {
    if (chapitre) afficherChapitre(chapitre);
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
    Object.assign(etat, { role: moi.role, prenom: moi.prenom, tuteur: moi.tuteur });
    await chargerProgramme();
  } catch {
    etat.role = null;
  }
  router();
})();
