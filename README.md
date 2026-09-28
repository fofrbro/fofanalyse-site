# fofanalyse.com

Site professionnel de Cheikhou FOFANA, Data Engineer · Analytics Engineer.
Site statique en français et en anglais : HTML et CSS, sans framework, sans
JavaScript, sans cookie ni traceur, sans ressource externe.

```
index.html        page en français
en/index.html     page en anglais
assets/           style.css, favicon.svg (et plus tard photo.jpg)
cv/cv.html        source du CV publié (sans numéro de téléphone)
cv/CV_Cheikhou_Fofana_Data_Engineer.pdf   CV téléchargeable
```

## Voir le site en local

```bash
python -m http.server 8080 --bind 127.0.0.1
```

puis ouvrir http://127.0.0.1:8080.

## Régénérer le CV en PDF

Après modification de `cv/cv.html`, avec Microsoft Edge (Windows,
PowerShell), depuis ce dossier :

```powershell
& "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" --headless --disable-gpu --no-pdf-header-footer --print-to-pdf="$PWD\cv\CV_Cheikhou_Fofana_Data_Engineer.pdf" "file:///$($PWD -replace '\\','/')/cv/cv.html"
```

Vérifier que le PDF tient sur une page.

## À compléter

- **Photo** : déposer `assets/photo.jpg` (carrée, environ 400 × 400 px), puis
  remplacer l'emplacement « CF » dans les deux pages (commentaires
  « À COMPLÉTER » / « TO DO »).
- **Projet RAG** : description détaillée et lien de démo
  (`rag.fofanalyse.com`) dans les deux pages.
- **Liens GitHub** : `github.com/fofrbro/data-engineering-agent` répondra
  une fois le dépôt de l'agent poussé.

## Mise en ligne

Prévue sur le même VPS que les démos, servi par Caddy (HTTPS automatique) :
voir le guide de déploiement de l'agent (`deploy/README.md`).
