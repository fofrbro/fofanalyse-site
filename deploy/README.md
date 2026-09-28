# Mettre en ligne fofanalyse.com

Un seul serveur (VPS Linux) sert tout, derrière **Caddy** qui obtient et
renouvelle seul les certificats HTTPS :

| Adresse | Contenu |
|---|---|
| `https://fofanalyse.com` | le site (dossier `www/`) et le formulaire de contact (`/api/contact`) |
| `https://www.fofanalyse.com` | redirection vers `fofanalyse.com` |
| `https://demo.fofanalyse.com` | l'agent Data Engineering en mode démo |

> Ces fichiers n'ont pas encore été exécutés : Docker n'était pas
> disponible sur le poste de développement. Le site, le service de contact
> (tests automatisés, essai en navigateur avec envoi simulé) et le mode démo
> de l'agent sont testés. Premier déploiement : suivre les vérifications de
> l'étape 6.

## 1. Le serveur

VPS Linux, 2 vCPU, 2 à 4 Go de RAM, Ubuntu 24.04 (Hetzner, OVH…, environ
4 à 6 € par mois), connexion par clé SSH.

## 2. Le nom de domaine

Chez le registraire de `fofanalyse.com`, créer (ou modifier) :

| Type | Nom | Valeur |
|---|---|---|
| A | `@` (domaine nu) | adresse IPv4 du VPS |
| A | `www` | adresse IPv4 du VPS |
| A | `demo` | adresse IPv4 du VPS |

**Ne pas toucher aux enregistrements MX** : ils acheminent le courrier de
`cheikhou@fofanalyse.com`.

## 3. Préparer le serveur

```bash
apt update && apt upgrade -y
```

```bash
ufw allow OpenSSH && ufw allow 80 && ufw allow 443 && ufw enable
```

```bash
curl -fsSL https://get.docker.com | sh
```

## 4. Récupérer les deux dépôts, côte à côte

```bash
mkdir -p /srv && cd /srv
```

```bash
git clone https://github.com/fofrbro/fofanalyse-site.git
```

```bash
git clone https://github.com/fofrbro/data-engineering-agent.git
```

## 5. Les secrets du serveur

```bash
cd /srv/fofanalyse-site/deploy && nano .env
```

```
# Formulaire de contact : compte SMTP de la boîte cheikhou@fofanalyse.com
SMTP_HOST=smtp.fournisseur-de-messagerie.example
SMTP_PORT=465
SMTP_SECURITY=ssl
SMTP_USER=cheikhou@fofanalyse.com
SMTP_PASSWORD=mot-de-passe-d-application
CONTACT_FROM=cheikhou@fofanalyse.com
CONTACT_TO=cheikhou@fofanalyse.com

# Démo de l'agent (facultatif) : clé d'un projet OpenAI dédié, plafonné
OPENAI_API_KEY=cle-du-projet-openai-de-la-demo
```

```bash
chmod 600 .env
```

- **SMTP** : utiliser les paramètres de votre fournisseur de messagerie et,
  s'il en propose, un **mot de passe d'application** plutôt que le mot de
  passe principal.
- **OpenAI** : un projet dédié à la démo avec une **limite de dépense
  mensuelle** (par exemple 10 $). Sans clé, la démo fonctionne sans les
  fonctions LLM.

## 6. Lancer et vérifier

```bash
docker compose up -d --build
```

```bash
docker compose ps
```

```bash
docker compose logs caddy --tail 50
```

```bash
curl -I https://fofanalyse.com
```

```bash
curl -I https://demo.fofanalyse.com/health
```

Puis, dans un navigateur :

1. `https://fofanalyse.com` et `https://fofanalyse.com/en/` s'affichent,
   le CV se télécharge ;
2. le formulaire de contact envoie un message qui arrive dans votre boîte,
   avec « Répondre à » sur l'adresse saisie ;
3. `https://demo.fofanalyse.com` : charger un exemple, préparer le plan,
   valider le contrat, exécuter.

## 7. Mettre à jour

```bash
cd /srv/fofanalyse-site && git pull && cd ../data-engineering-agent && git pull
```

```bash
cd /srv/fofanalyse-site/deploy && docker compose up -d --build
```

Les pages du site sont servies directement depuis `www/` : un `git pull`
suffit à les publier.
