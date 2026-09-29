# fofanalyse.com

Site professionnel de Cheikhou FOFANA, Data Engineer · Analytics Engineer.
Site statique en français et en anglais : HTML et CSS, sans framework, sans
JavaScript, sans cookie ni traceur, sans ressource externe. Le formulaire
de contact passe par un petit service à soi, sans service tiers.

```
www/                    pages publiques (seul dossier servi en ligne)
  index.html            accueil en français
  contact.html          formulaire de contact, pages contact-envoye / contact-erreur
  en/                   version anglaise (index, contact, contact-sent, contact-error)
  assets/               style.css, favicon.svg (et plus tard photo.jpg)
  cv/                   CV téléchargeable en PDF (sans numéro de téléphone)
cv-source/cv.html       source du CV publié
contact-service/        service du formulaire de contact (FastAPI, tests)
deploy/                 mise en ligne : Docker, Caddy, guide pas à pas
```

## Voir le site en local

```bash
python -m http.server 8080 --bind 127.0.0.1 --directory www
```

puis ouvrir http://127.0.0.1:8080 (le formulaire de contact a besoin du
service : il répond seulement en ligne ou avec un serveur local qui sert
les deux).

## Formulaire de contact

`contact-service/contact.py` reçoit le formulaire (sans JavaScript), le
vérifie et l'envoie par SMTP dans la boîte `cheikhou@fofanalyse.com`, avec
« Répondre à » sur l'adresse du visiteur. Aucun message n'est conservé.

- champ piège invisible contre les robots (envoi ignoré, page de succès) ;
- 3 messages par adresse IP et par heure, 50 par jour pour tout le site ;
- champs bornés, aucune injection possible dans les en-têtes de l'e-mail ;
- en cas d'échec, la page d'erreur donne l'adresse e-mail directe.

Tests (SMTP simulé, aucun envoi réel) :

```bash
cd contact-service && python -m pytest -q
```

## Régénérer le CV en PDF

Après modification de `cv-source/cv.html`, avec Microsoft Edge (Windows,
PowerShell), depuis ce dossier :

```powershell
& "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" --headless --disable-gpu --no-pdf-header-footer --print-to-pdf="$PWD\www\cv\CV_Cheikhou_Fofana_Data_Engineer.pdf" "file:///$($PWD -replace '\\','/')/cv-source/cv.html"
```

Vérifier que le PDF tient sur une page.

## À compléter

- **Page RAG** (`www/rag/`) : une fois le Worker déployé
  (`npx wrangler deploy`), remplacer `fofanalyse-rag.A-REMPLACER.workers.dev`
  par son adresse dans `www/rag/rag.js` et dans la CSP `/rag/*` de
  `deploy/Caddyfile`. En local, la page appelle `http://localhost:8787`
  (`npx wrangler dev`).
- **Liens GitHub** : `github.com/fofrbro/data-engineering-agent` répondra
  une fois le dépôt de l'agent poussé.

## Mise en ligne

Voir [deploy/README.md](deploy/README.md) : un seul serveur, Caddy pour le
HTTPS, le site, le formulaire de contact et la démo de l'agent.
