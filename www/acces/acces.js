// Page « RAG et habilitations ». Le navigateur choisit un profil et calcule
// le vecteur de la question ; l'API (Cloudflare Worker) signe un jeton, puis
// ne renvoie que les documents autorisés pour ce profil (Row-Level Security
// PostgreSQL). Script externe, sans style en ligne : compatible avec la CSP.
import { pipeline } from "https://cdn.jsdelivr.net/npm/@huggingface/transformers@3.0.2";

// --- Réglages -----------------------------------------------------------
// En local, « npx wrangler dev --port 8788 » ; en ligne, l'adresse donnée par
// « npx wrangler deploy » (à reporter aussi dans connect-src, deploy/Caddyfile).
const API_LOCALE = "http://localhost:8788";
const API_EN_LIGNE = "https://fofanalyse-acces.fofanalyse.workers.dev";
const API_URL = ["localhost", "127.0.0.1"].includes(location.hostname) ? API_LOCALE : API_EN_LIGNE;
const MODELE_WEB = "Xenova/multilingual-e5-small";
const SEUIL = 0.80;
const ECHELLE_MIN = 0.70;

// Affichage seulement : les habilitations qui comptent sont celles du serveur,
// lues dans le jeton qu'il signe.
const PROFILS = {
  confiserie: [
    ["operateur", "Opérateur de ligne", ["tous"]],
    ["chef_equipe", "Chef d'équipe", ["tous", "encadrement", "production"]],
    ["resp_qualite", "Responsable qualité", ["tous", "encadrement", "qualite"]],
    ["resp_rh", "Responsable RH", ["tous", "encadrement", "rh"]],
    ["directeur", "Directeur", ["tous", "encadrement", "production", "qualite", "rh", "direction"]],
  ],
  mairie: [
    ["agent_accueil", "Agent d'accueil", ["public", "agents"]],
    ["officier_ec", "Officier d'état civil", ["public", "agents", "etat_civil"]],
    ["resp_rh", "Responsable RH", ["public", "agents", "rh"]],
    ["dgs", "Directeur général des services", ["public", "agents", "etat_civil", "rh", "direction"]],
    ["maire", "Maire", ["public", "agents", "direction", "elus"]],
  ],
};

const SUGGESTIONS = {
  confiserie: [
    "Quel est le chiffre d'affaires 2025 ?",
    "Que faire si le détecteur de métaux éjecte un produit ?",
    "Quel est le salaire d'un chef d'équipe ?",
    "Quel est le score du dernier audit IFS ?",
    "Y a-t-il un projet de réorganisation de l'équipe de nuit ?",
  ],
  mairie: [
    "Quel est le budget voté pour 2026 ?",
    "Comment faire une carte d'identité ?",
    "Quelles économies sont prévues pour le budget 2027 ?",
    "Quel est le taux d'absentéisme des agents ?",
    "Y a-t-il un projet de vente du terrain des Peupliers ?",
  ],
};

const $ = (id) => document.getElementById(id);
const etat = $("etat");
let extracteur = null;
let jeton = null;

const orgChoisie = () => document.querySelector('input[name="org"]:checked').value;
const profilChoisi = () => document.querySelector('input[name="profil"]:checked')?.value;

function afficherEtat(message, erreur = false) {
  etat.textContent = message;
  etat.classList.toggle("erreur", erreur);
}

const echapper = (s) => String(s).replace(/[&<>"']/g, (c) =>
  ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));

// Mini-convertisseur Markdown : paragraphes, listes, gras.
function markdown(md) {
  return md.split(/\n{2,}/).map((bloc) => {
    bloc = bloc.trim();
    if (!bloc) return "";
    const enLigne = (t) => echapper(t).replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>");
    if (bloc.split("\n").every((l) => l.startsWith("- "))) {
      return "<ul>" + bloc.split("\n").map((l) => `<li>${enLigne(l.slice(2))}</li>`).join("") + "</ul>";
    }
    return `<p>${enLigne(bloc)}</p>`;
  }).join("");
}

// --- API ------------------------------------------------------------------
async function appelerApi(route, donnees) {
  const r = await fetch(API_URL + route, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(donnees),
  });
  const resultat = await r.json().catch(() => ({}));
  if (!r.ok) {
    const erreur = new Error(resultat.erreur || `HTTP ${r.status}`);
    erreur.statut = r.status;
    throw erreur;
  }
  return resultat;
}

async function seConnecter() {
  jeton = null;
  const profil = profilChoisi();
  if (!profil) return;
  $("session").textContent = "Connexion…";
  try {
    const r = await appelerApi("/connexion", { org: orgChoisie(), profil });
    jeton = r.jeton;
    $("session").innerHTML = `Connecté en tant que <strong>${echapper(r.profil.nom)}</strong> · habilitations : ${r.profil.groupes.map(echapper).join(", ")}`;
  } catch (err) {
    $("session").textContent = err.statut === 429 ? err.message : "Connexion impossible pour le moment.";
  }
}

// Appel avec jeton ; une session expirée est renouvelée une fois.
async function appelerConnecte(route, donnees) {
  if (!jeton) await seConnecter();
  try {
    return await appelerApi(route, { ...donnees, jeton });
  } catch (err) {
    if (err.statut !== 401) throw err;
    await seConnecter();
    return appelerApi(route, { ...donnees, jeton });
  }
}

// --- Modèle d'embedding dans le navigateur ---------------------------------
function chargerModele() {
  if (!extracteur) {
    const fichiers = {};
    extracteur = pipeline("feature-extraction", MODELE_WEB, {
      dtype: "q8",
      progress_callback: (p) => {
        if (p.status !== "progress" || !p.total) return;
        fichiers[p.file] = [p.loaded, p.total];
        const [lu, total] = Object.values(fichiers).reduce(([a, b], [c, d]) => [a + c, b + d], [0, 0]);
        afficherEtat(`Chargement du modèle, premier usage uniquement : ${Math.round(100 * lu / total)} %`);
      },
    });
  }
  return extracteur;
}

async function vectoriser(question) {
  const modele = await chargerModele();
  const sortie = await modele("query: " + question, { pooling: "mean", normalize: true });
  return Array.from(sortie.data, (x) => Math.round(x * 1e6) / 1e6);
}

// --- Affichage ----------------------------------------------------------------
function afficherProfils() {
  const org = orgChoisie();
  $("profils").innerHTML = PROFILS[org].map(([code, nom, groupes], i) => `
    <label class="profil">
      <input type="radio" name="profil" value="${code}"${i === 0 ? " checked" : ""}>
      <span class="carte">
        <span class="nom">${echapper(nom)}</span>
        <span class="groupes">${groupes.map((g) => `<span class="groupe">${echapper(g)}</span>`).join("")}</span>
      </span>
    </label>`).join("");
  $("suggestions").innerHTML = SUGGESTIONS[org].map((q) => `<li><button type="button">${echapper(q)}</button></li>`).join("");
  $("question").placeholder = "Par exemple : " + SUGGESTIONS[org][0].toLowerCase();
  reinitialiser();
}

function reinitialiser() {
  $("decision").hidden = true;
  $("reponse").hidden = true;
  $("extraits-titre").hidden = true;
  $("resultats").innerHTML = "";
  $("comparaison").hidden = true;
  afficherEtat("");
}

const badge = (niveau) => `<span class="niveau ${echapper(niveau)}">${echapper(niveau)}</span>`;

function afficherDecision(decision) {
  const zone = $("decision");
  zone.className = "decision " + decision.type;
  if (decision.type === "refus") {
    zone.innerHTML = `<strong>Accès refusé</strong>${echapper(decision.message)}`;
  } else if (decision.type === "partiel") {
    zone.innerHTML = `<strong>Réponse partielle</strong>${echapper(decision.message)}`;
  } else if (decision.type === "rien") {
    zone.innerHTML = "<strong>Aucune information</strong>Aucun document accessible à votre profil ne répond à cette question.";
  }
  zone.hidden = decision.type === "ok";
}

function afficherPassages(passages) {
  const liste = $("resultats");
  const repere = (SEUIL - ECHELLE_MIN) / (1 - ECHELLE_MIN) * 100;
  liste.innerHTML = passages.map((p, i) => {
    const largeur = Math.max(0, Math.min(1, (p.score - ECHELLE_MIN) / (1 - ECHELLE_MIN))) * 100;
    return `<li class="resultat">
      <span class="source">Document ${i + 1}</span>${badge(p.niveau)}
      <h2>${echapper(p.titre)}</h2>
      <div class="mesure">
        <div class="jauge" role="img" aria-label="Score de similarité ${p.score.toFixed(3)}, seuil ${SEUIL}">
          <div class="barre" data-largeur="${largeur}"></div>
          <div class="repere" data-position="${repere}"></div>
        </div>
        <span class="score">${p.score.toFixed(3).replace(".", ",")}</span>
      </div>
      <div class="texte">${markdown(p.texte)}</div>
    </li>`;
  }).join("");
  liste.querySelectorAll(".repere").forEach((r) => { r.style.left = r.dataset.position + "%"; });
  requestAnimationFrame(() => liste.querySelectorAll(".barre").forEach((b) => { b.style.width = b.dataset.largeur + "%"; }));
  $("extraits-titre").hidden = passages.length === 0;
}

async function generer(question, passages) {
  const zone = $("reponse");
  zone.hidden = false;
  zone.innerHTML = `<h2>Réponse</h2><p class="attente">Rédaction de la réponse…</p>`;
  try {
    const r = await appelerConnecte("/repondre", { question, ids: passages.map((p) => p.id) });
    zone.innerHTML = `<h2>Réponse</h2>${markdown(r.reponse)}<p class="note">Rédigée par un modèle de langage à partir des seuls documents autorisés ci-dessous.</p>`;
  } catch (err) {
    const motif = err.statut === 429 ? echapper(err.message) + " " : "";
    zone.innerHTML = `<h2>Réponse</h2><p class="attente">${motif}La réponse rédigée n'est pas disponible pour le moment. Les documents ci-dessous restent valables.</p>`;
  }
}

function afficherComparaison(profils) {
  $("lignes-comparaison").innerHTML = profils.map((l) => {
    let resultat;
    if (l.passages.length) {
      resultat = "<ul>" + l.passages.map((p) => `<li>${echapper(p.titre)}${badge(p.niveau)}</li>`).join("") + "</ul>";
      if (l.decision.type === "partiel") resultat += `<p class="refuse">${echapper(l.decision.message)}</p>`;
    } else if (l.decision.type === "refus") {
      resultat = `<span class="refuse">${echapper(l.decision.message)}</span>`;
    } else {
      resultat = `<span class="vide">Aucune information</span>`;
    }
    return `<tr><td>${echapper(l.profil)}</td><td>${resultat}</td></tr>`;
  }).join("");
  $("comparaison").hidden = false;
}

// --- Interactions -------------------------------------------------------------
const champ = $("question");
const bouton = document.querySelector(".rechercher");
const boutonComparer = $("comparer");

afficherProfils();
seConnecter();

document.querySelectorAll('input[name="org"]').forEach((r) => r.addEventListener("change", () => {
  afficherProfils();
  seConnecter();
}));
$("profils").addEventListener("change", () => {
  reinitialiser();
  seConnecter();
});
$("suggestions").addEventListener("click", (e) => {
  if (e.target.tagName !== "BUTTON") return;
  champ.value = e.target.textContent;
  $("formulaire").requestSubmit();
});
champ.addEventListener("focus", () => chargerModele(), { once: true });

$("formulaire").addEventListener("submit", async (e) => {
  e.preventDefault();
  const question = champ.value.trim();
  if (!question) return;
  bouton.disabled = true;
  reinitialiser();
  afficherEtat("Recherche dans les documents autorisés…");
  try {
    const r = await appelerConnecte("/rechercher", { vecteur: await vectoriser(question) });
    afficherEtat(r.passages.length
      ? `${r.passages.length} document${r.passages.length > 1 ? "s" : ""} autorisé${r.passages.length > 1 ? "s" : ""} au-dessus du seuil de pertinence.`
      : "");
    afficherDecision(r.decision);
    afficherPassages(r.passages);
    // Pas de document autorisé = pas d'appel au LLM.
    if (r.passages.length) await generer(question, r.passages);
  } catch (err) {
    console.error(err);
    afficherEtat(err.statut === 429 ? err.message : "La recherche n'a pas abouti. Vérifiez votre connexion, puis réessayez.", true);
    if (!err.statut) extracteur = null;
  } finally {
    bouton.disabled = false;
  }
});

boutonComparer.addEventListener("click", async () => {
  const question = champ.value.trim();
  if (!question) {
    afficherEtat("Saisissez ou choisissez d'abord une question.", true);
    return;
  }
  boutonComparer.disabled = true;
  afficherEtat("Comparaison des profils…");
  try {
    const r = await appelerApi("/comparer", { org: orgChoisie(), vecteur: await vectoriser(question) });
    afficherComparaison(r.profils);
    afficherEtat("");
    $("comparaison").scrollIntoView({ behavior: "smooth", block: "start" });
  } catch (err) {
    console.error(err);
    afficherEtat(err.statut === 429 ? err.message : "La comparaison n'a pas abouti. Réessayez.", true);
  } finally {
    boutonComparer.disabled = false;
  }
});
