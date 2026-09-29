// Page « Posez votre question » : RAG sur PostgreSQL + pgvector.
// Le navigateur calcule le vecteur de la question (modèle e5), l'API
// (Cloudflare Worker) cherche dans PostgreSQL puis fait rédiger la réponse.
// Script externe, sans style en ligne : compatible avec la CSP du site.
import { pipeline } from "https://cdn.jsdelivr.net/npm/@huggingface/transformers@3.0.2";

// --- Réglages -----------------------------------------------------------
// Adresse de l'API (Worker). En local, « npx wrangler dev » écoute sur 8787 ;
// en ligne, l'adresse donnée par « npx wrangler deploy ». Si elle change,
// la changer aussi dans connect-src (deploy/Caddyfile).
const API_LOCALE = "http://localhost:8787";
const API_EN_LIGNE = "https://fofanalyse-rag.fofanalyse.workers.dev";
const API_URL = ["localhost", "127.0.0.1"].includes(location.hostname) ? API_LOCALE : API_EN_LIGNE;
const MODELE_WEB = "Xenova/multilingual-e5-small"; // version navigateur du modèle e5
const SEUIL = 0.80;          // le seuil réel est appliqué en SQL ; ici, pour la jauge
const ECHELLE_MIN = 0.70;    // bas de la jauge (les scores e5 sont compressés)

const SUGGESTIONS = {
  profil: ["Quelle expérience avec PostgreSQL ?", "Quels projets sur Microsoft Fabric ?",
           "Où cherche-t-il un poste ?", "Parle-t-il anglais ?"],
  dp700: ["Comment réduire les petits fichiers d'une table Delta ?",
          "Comment masquer un numéro de carte bancaire ?",
          "Quand utiliser un eventhouse ?"],
};

const $ = (id) => document.getElementById(id);
const etat = $("etat");
let extracteur = null;   // promesse du modèle, créée une seule fois

function afficherEtat(message, erreur = false) {
  etat.textContent = message;
  etat.classList.toggle("erreur", erreur);
}

// --- 1. Appel à l'API -------------------------------------------------
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

// --- 2. Chargement du modèle dans le navigateur (au premier besoin) -----
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

// --- 3. Recherche ------------------------------------------------------
// Le navigateur ne calcule que le vecteur de la question.
// La recherche elle-même (opérateur <=> de pgvector) a lieu dans PostgreSQL.
async function rechercher(question, source) {
  const modele = await chargerModele();
  const sortie = await modele("query: " + question, { pooling: "mean", normalize: true });
  const vecteur = Array.from(sortie.data, (x) => Math.round(x * 1e6) / 1e6);
  const { passages } = await appelerApi("/rechercher", { vecteur, source });
  return passages;
}

// --- 4. Affichage ------------------------------------------------------
const echapper = (s) => s.replace(/[&<>"']/g, (c) =>
  ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));

// Mini-convertisseur Markdown : paragraphes, listes, gras, blocs de code.
function markdown(md) {
  const codes = [];
  md = md.replace(/```\w*\n([\s\S]*?)```/g, (_, code) => {
    codes.push(`<pre><code>${echapper(code.trimEnd())}</code></pre>`);
    return `\n\n\u0000${codes.length - 1}\u0000\n\n`;
  });
  return md.split(/\n{2,}/).map((bloc) => {
    bloc = bloc.trim();
    if (!bloc) return "";
    const code = bloc.match(/^\u0000(\d+)\u0000$/);
    if (code) return codes[+code[1]];
    const enLigne = (t) => echapper(t).replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>").replace(/\*(.+?)\*/g, "<em>$1</em>");
    if (bloc.split("\n").every((l) => l.startsWith("- ")))
      return "<ul>" + bloc.split("\n").map((l) => `<li>${enLigne(l.slice(2))}</li>`).join("") + "</ul>";
    return `<p>${enLigne(bloc)}</p>`;
  }).join("");
}

// Pour une question DP-700, la réponse est repliée : on peut réviser.
function contenu(p) {
  if (p.source !== "dp700") return markdown(p.texte);
  const texte = p.texte.replace(/^\*\*Question\*\*\s*/, "");
  const coupure = texte.search(/\*\*Bonnes? réponses?\*\*/);
  return markdown(texte.slice(0, coupure))
    + `<details><summary>Voir la réponse et l'explication</summary>${markdown(texte.slice(coupure))}</details>`;
}

function afficher(resultats) {
  const liste = $("resultats");
  liste.innerHTML = resultats.map((p, i) => {
    const largeur = Math.max(0, Math.min(1, (p.score - ECHELLE_MIN) / (1 - ECHELLE_MIN))) * 100;
    const repere = (SEUIL - ECHELLE_MIN) / (1 - ECHELLE_MIN) * 100;
    return `<li class="resultat">
      <span class="source">Extrait ${i + 1}, ${p.source === "profil" ? "profil" : "révisions DP-700"}</span>
      <h2>${echapper(p.titre)}</h2>
      <div class="mesure">
        <div class="jauge" role="img" aria-label="Score de similarité ${p.score.toFixed(3)}, seuil ${SEUIL}">
          <div class="barre" data-largeur="${largeur}"></div>
          <div class="repere" data-position="${repere}"></div>
        </div>
        <span class="score">${p.score.toFixed(3).replace(".", ",")}</span>
      </div>
      <div class="texte">${contenu(p)}</div>
    </li>`;
  }).join("");
  // Positions posées par le script (CSSOM) : la CSP interdit les attributs style.
  liste.querySelectorAll(".repere").forEach((r) => { r.style.left = r.dataset.position + "%"; });
  requestAnimationFrame(() => liste.querySelectorAll(".barre").forEach((b) => {
    b.style.width = b.dataset.largeur + "%";
  }));
}

// --- 5. Génération : le LLM rédige une réponse à partir des extraits ----
// On n'envoie que la question et les numéros des passages : la fonction
// relit elle-même les textes, le visiteur ne peut donc rien y injecter.
async function generer(question, resultats) {
  const zone = $("reponse");
  zone.hidden = false;
  zone.innerHTML = `<h2>Réponse</h2><p class="attente">Rédaction de la réponse…</p>`;
  try {
    const donnees = await appelerApi("/repondre", { question, ids: resultats.map((p) => p.id) });
    zone.innerHTML = `<h2>Réponse</h2>${markdown(donnees.reponse)}`
      + `<p class="note">Rédigée par un modèle de langage à partir des extraits numérotés ci-dessous.</p>`;
  } catch (err) {
    console.error(err);
    const motif = err.statut === 429 ? echapper(err.message) + " " : "";
    zone.innerHTML = `<h2>Réponse</h2><p class="attente">${motif}La réponse rédigée n'est pas disponible pour le moment. Les extraits ci-dessous restent valables.</p>`;
  }
}

// --- 6. Interactions ---------------------------------------------------
const champ = $("question");
const bouton = document.querySelector(".rechercher");
const sourceChoisie = () => document.querySelector('input[name="source"]:checked').value;

function majSuggestions() {
  const s = sourceChoisie();
  const liste = s === "tout" ? [...SUGGESTIONS.profil.slice(0, 2), ...SUGGESTIONS.dp700.slice(0, 2)] : SUGGESTIONS[s];
  $("suggestions").innerHTML = liste.map((q) => `<li><button type="button">${echapper(q)}</button></li>`).join("");
}
majSuggestions();
document.querySelectorAll('input[name="source"]').forEach((r) => r.addEventListener("change", majSuggestions));
$("suggestions").addEventListener("click", (e) => {
  if (e.target.tagName !== "BUTTON") return;
  champ.value = e.target.textContent;
  $("formulaire").requestSubmit();
});

// On commence à charger le modèle dès que le visiteur s'apprête à écrire.
champ.addEventListener("focus", () => chargerModele(), { once: true });

$("formulaire").addEventListener("submit", async (e) => {
  e.preventDefault();
  const question = champ.value.trim();
  if (!question) return;
  bouton.disabled = true;
  $("reponse").hidden = true;
  afficherEtat("Recherche en cours…");
  try {
    const resultats = await rechercher(question, sourceChoisie());
    afficher(resultats);
    $("extraits-titre").hidden = !resultats.length;
    afficherEtat(resultats.length
      ? `${resultats.length} passage${resultats.length > 1 ? "s" : ""} au-dessus du seuil de pertinence.`
      : "Aucun passage ne dépasse le seuil de pertinence. Reformulez avec des termes plus précis, ou changez de source.");
    // Pas d'extrait pertinent = pas d'appel au LLM : aucune réponse inventée, aucun coût.
    if (resultats.length) await generer(question, resultats);
  } catch (err) {
    console.error(err);
    if (err.statut === 429) {
      afficherEtat(err.message, true);   // limite d'usage : le modèle reste chargé
    } else {
      afficherEtat("La recherche n'a pas abouti. Vérifiez votre connexion, puis réessayez.", true);
      if (!err.statut) extracteur = null;  // échec réseau ou du modèle : on réessaiera de le charger
    }
  } finally {
    bouton.disabled = false;
  }
});
