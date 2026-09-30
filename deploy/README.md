# Mettre en ligne fofanalyse.com

Un seul serveur (VPS Linux) sert tout, derrière **Caddy** qui obtient et
renouvelle seul les certificats HTTPS :

| Adresse | Contenu |
|---|---|
| `https://fofanalyse.com` | le site (dossier `www/`) et le formulaire de contact (`/api/contact`) |
| `https://www.fofanalyse.com` | redirection vers `fofanalyse.com` |
| `https://demo.fofanalyse.com` | l'agent Data Engineering en mode démo |

> En ligne depuis le 2026-09-30 : pages FR/EN, CV, page RAG et démo vérifiés
> en HTTPS (certificats Let's Encrypt obtenus par Caddy), parcours complet de
> la démo sur l'exemple « ventes » (INGEST, 1 500 lignes). **Le formulaire de
> contact n'envoie pas encore** : le SMTP sera configuré après le transfert
> du domaine chez OVH (voir l'étape 5).

## 1. Le serveur

VPS OVH « VPS-1 » (2 vCore, 4 Go de RAM, 40 Go NVMe, Gravelines), Ubuntu
26.04 LTS, utilisateur `ubuntu`, environ 55 € TTC par an. Installer le
système **avec la clé SSH publique** (espace client OVH, « Réinstaller mon
VPS ») : le mot de passe envoyé par lien n'est alors plus nécessaire, sauf
pour le changement imposé à la première connexion.

## 2. Le nom de domaine

Dans la zone DNS de `fofanalyse.com` (Viaduc pendant le transfert, puis
OVH), créer ou modifier :

| Type | Nom | Valeur |
|---|---|---|
| A | `@` (domaine nu) | `146.59.155.98` (remplace la page d'attente, 87.98.150.35) |
| A | `www` | `146.59.155.98` |
| A | `demo` | `146.59.155.98` |

**Ne pas toucher aux enregistrements MX** : ils acheminent le courrier de
`cheikhou@fofanalyse.com`.

À la fin du transfert, si OVH bascule le domaine sur ses propres serveurs
DNS, **recréer ces trois lignes chez OVH le jour même**, ainsi que la
messagerie (MX et SPF d'OVH), sinon le site et le courrier s'arrêtent.
Caddy lance l'obtention des certificats dès son démarrage : ne le démarrer
qu'une fois ces noms dirigés vers le serveur.

## 3. Préparer le serveur

Exécuté le 2026-09-30 sur le VPS (Ubuntu 26.04).

```bash
sudo apt update && sudo apt full-upgrade -y
```

Pare-feu : SSH et web seulement. Docker contourne `ufw` pour les ports
qu'il publie ; seul Caddy en publie (80 et 443), les autres services restent
internes.

```bash
sudo ufw allow OpenSSH && sudo ufw allow 80/tcp && sudo ufw allow 443 && sudo ufw --force enable
```

Connexion par clé uniquement, pas de root. Le fichier `00-…` est lu avant
celui d'OVH (`50-cloud-init.conf`) : la première valeur lue l'emporte. Sur
Ubuntu 26.04, SSH est lancé à la demande (`ssh.socket`) : chaque nouvelle
connexion lit la configuration, il n'y a rien à recharger.

```bash
printf 'PasswordAuthentication no\nKbdInteractiveAuthentication no\nPermitRootLogin no\n' | sudo tee /etc/ssh/sshd_config.d/00-securite.conf && sudo sshd -t
```

Vérifier depuis une **deuxième** fenêtre avant de fermer la première : la
clé ouvre la session, `ssh -o PubkeyAuthentication=no ubuntu@IP` répond
`Permission denied (publickey)`.

Docker, depuis les paquets d'Ubuntu (suivis par les mises à jour de sécurité
automatiques), utilisable sans `sudo` après reconnexion :

```bash
sudo apt install -y docker.io docker-compose-v2 git && sudo usermod -aG docker ubuntu
```

```bash
docker run --rm hello-world && docker compose version
```

## 4. Récupérer les deux dépôts, côte à côte

```bash
sudo mkdir -p /srv && sudo chown ubuntu:ubuntu /srv && cd /srv
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
# Formulaire de contact : boîte cheikhou@fofanalyse.com chez Viaduc
# (Nom-domaine.fr). Utiliser smtp.viaduc.fr et non smtp.fofanalyse.com :
# le certificat TLS n'est pas valable pour l'alias.
SMTP_HOST=smtp.viaduc.fr
SMTP_PORT=465
SMTP_SECURITY=ssl
SMTP_USER=cheikhou@fofanalyse.com
SMTP_PASSWORD=mot-de-passe-de-la-boite
CONTACT_FROM=cheikhou@fofanalyse.com
CONTACT_TO=cheikhou@fofanalyse.com

# Démo de l'agent (facultatif) : clé d'un projet OpenAI dédié, plafonné
OPENAI_API_KEY=cle-du-projet-openai-de-la-demo
```

```bash
chmod 600 .env
```

- **SMTP** : vérifié le 2026-09-29, `smtp.viaduc.fr` accepte le port 465
  (SSL, réglage par défaut) et le port 587 (`SMTP_SECURITY=starttls`), avec
  authentification. Le SPF de `fofanalyse.com` autorise déjà Viaduc
  (`include:spf.viaduc.fr`) : les messages ne partent pas en spam. Si votre
  espace client propose un mot de passe dédié aux applications, préférez-le
  au mot de passe principal.
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
