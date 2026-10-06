# Deploiement du CTF sur AWS

Infrastructure d'un CTF annuel a deux phases, concue pour que la facture suive
strictement l'usage.

**Calendrier 2026** — presélection du vendredi 23 au dimanche 25 octobre (~300
participants) ; finale jeudi 29 et vendredi 30 octobre (10 equipes, ~50
joueurs). Entre deux editions, les comptes sont supprimes et les equipes
changent : rien ne justifie de laisser une machine allumee.

## Le modele : une seule variable decide de tout

```
                          Internet
                              |
                      [ domaine du CTF ]
                              |
   +--------------------------v---------------------------+
   |  FRONT (ARM)  nginx+TLS | CTFd | MariaDB | Redis      |
   |               frps | dockerproxy                      |
   +---------+--------------------------------+-----------+
             | tunnel frp + Docker over ssh    | HTTP prive
   +---------v-----------+        +------------v----------+
   |  ARENA (x86)        |        |  NOEUD IA (GPU T4)    |
   |  Docker Swarm       |        |  Ollama               |
   |  1 instance/equipe  |        |  challenges IA        |
   +---------------------+        +-----------------------+
```

| `phase`        | Front        | Arena         | Noeud IA      | Cout            |
| -------------- | ------------ | ------------- | ------------- | --------------- |
| `off`          | —            | —             | —             | **0 USD d'EC2** |
| `setup`        | `t4g.small`  | —             | —             | ~0,02 USD/h     |
| `preselection` | `t4g.medium` | `c6i.4xlarge` | `g4dn.xlarge` | ~1,46 USD/h     |
| `final`        | `t4g.small`  | `c6i.2xlarge` | `g4dn.xlarge` | ~1,04 USD/h     |

Hors evenement, aucune instance EC2 n'existe. Seul subsiste le bucket S3 des
archives, pour environ 0,50 USD par mois.

**Estimation pour l'edition** : ~63 USD pour la preselection (48 h) + ~46 USD
pour la finale (48 h) + quelques jours de `setup`, soit environ **120 USD**.
Ce sont des estimations a partir des tarifs a la demande d'eu-west-3, pas des
montants factures. Si les epreuves ne tournent pas la nuit, un `season-down`
entre les deux journees divise ces montants par deux.

## A faire des maintenant : le quota GPU

Sur un compte AWS neuf, le quota _Running On-Demand G and VT instances_ est
souvent a zero, et une `g4dn.xlarge` en consomme 4 vCPU. La demande
d'augmentation prend plusieurs jours ouvres.

```bash
cd deploy
make check-gpu-quota      # echoue si le quota est insuffisant
```

Sans GPU, toute la categorie IA tombe.

## Installation, une fois

```bash
cd deploy
cp terraform/terraform.tfvars.example terraform/terraform.tfvars
```

Renseigner dans `terraform.tfvars` :

| Variable          | Role                                                                                                 |
| ----------------- | ---------------------------------------------------------------------------------------------------- |
| `ssh_public_key`  | votre cle publique SSH                                                                               |
| `admin_cidrs`     | **obligatoire**, l'IP publique de votre bureau ou VPN. Jamais `0.0.0.0/0` : c'est ce qui protege SSH |
| `domain_name`     | le domaine du CTF                                                                                    |
| `route53_zone_id` | zone Route53, si vous voulez que le DNS soit automatique                                             |

```bash
make init
make phase-setup          # cree le VPC, le front, et deploie CTFd
```

`phase-setup` attend la fin du provisionnement avant de deployer, puis affiche
ce qu'il reste a faire cote DNS.

### Le fichier `.env` du front

`make deploy` echoue tant qu'il n'existe pas. Sur le front :

```bash
make ssh-front
cd /opt/ctfd/CTFd/deploy/front
cp .env.example .env
openssl rand -hex 32      # -> SECRET_KEY
openssl rand -hex 24      # -> DB_PASSWORD
openssl rand -hex 24      # -> DB_ROOT_PASSWORD
# renseigner aussi CTF_DOMAIN et CERTBOT_EMAIL
```

Les autres champs (`WORKERS`, `INNODB_POOL`, `ARENA_HOST`, `DOCKER_HOST`,
`OLLAMA_URL`) sont ecrits par `make link` selon la phase. Ne les remplissez pas
a la main.

### TLS

Le front demarre en HTTP seul, le temps que le domaine pointe vers lui. Une
fois le DNS propage :

```bash
make tls-init                         # domaine en DNS only (pointe directement sur le front)
CF_API_TOKEN=... make tls-cloudflare  # domaine proxifie par Cloudflare (cas de ctf.tg)
```

L'apex sert la vitrine statique, la plateforme CTFd est sur `arena.<domaine>` :
toute commande qui parle a l'API CTFd vise `https://arena.<domaine>`.

La commande verifie d'abord que le domaine resout bien vers ce front — sinon
Let's Encrypt echouerait et consommerait un essai du quota horaire —, emet le
certificat, bascule nginx en HTTPS, et revient au HTTP si la configuration est
invalide. **Ne laissez pas l'evenement tourner en HTTP** : 300 joueurs y
enverraient leur mot de passe en clair.

Le renouvellement est automatique (service `certbot` du compose).

### Les images de challenge

L'arena est detruite et recreee a chaque changement de phase : son disque ne
conserve rien. Les images sont donc archivees dans le bucket S3, qui survit
aux editions, et rechargees au demarrage de l'arena.

```bash
make push-images          # depuis la machine ou vous construisez les images
make check-arena          # apres une phase : liste ce qui est reellement present
```

`push-images` prend les images locales nommees `ctf-*`.

## Rythme de l'edition

```bash
make phase-preselection   # 23 octobre au matin
make logs                 # pendant l'epreuve
make backup               # regulierement, pas seulement a la fin
make season-down          # 24 au soir : archive + sauvegarde verifiee + destruction

make phase-final          # 29 octobre au matin
make season-down          # 30 au soir
```

Entre le 24 et le 29, l'infrastructure est detruite : cinq jours d'instances
inutiles coutent plus cher que la reconstruction. Les resultats de la
preselection sont dans la sauvegarde et dans l'archive statique.

### Sauvegarde et restauration

`make backup` refuse de reussir sur un dump vide ou tronque : il verifie
l'integrite de l'archive, sa taille, et la presence de la table `users`. C'est
ce qui protege `season-down`, qui detruit le front juste apres.

```bash
make restore FILE=backups/ctfd-preselection-20261024-190000.sql.gz
```

Sans argument, `make restore` liste les sauvegardes disponibles dans S3.

### DNS

L'IP publique du front change a chaque cycle. Avec `route53_zone_id`
renseigne, Terraform gere l'enregistrement A avec un TTL de 60 s. Sinon, la
sortie `dns_action_required` affiche l'adresse a pointer manuellement apres
chaque `make phase-*` — a faire avant `make tls-init`.

## Securite

- Ni l'arena ni le noeud IA n'ont de port ouvert sur Internet. Les instances
  des equipes passent par un tunnel frp aboutissant sur le front ; Ollama n'est
  joignable que depuis le front.
- L'API d'administration de frpc ecoute sur `127.0.0.1`. Exposee, un conteneur
  de challenge compromis — ce qui est l'objectif d'un challenge pwn — pourrait
  reecrire les tunnels de toutes les equipes.
- IMDSv2 obligatoire avec `hop_limit = 1` : une execution de code dans un
  conteneur n'atteint pas les credentials IAM du noeud.
- Le role IAM de l'arena ne peut que **lire** le prefixe `images/`. Il ne peut
  ni ecrire dans le bucket, ni lire `backups/`.
- nginx positionne explicitement tous les en-tetes `X-Forwarded-*`, y compris
  `X-Forwarded-Host`. CTFd tourne avec `REVERSE_PROXY=true` et leur fait
  confiance : sans cela, un joueur pourrait empoisonner un lien de
  reinitialisation de mot de passe envoye a l'administrateur.
- Tout `Host` inconnu recoit un `444` une fois le TLS actif.
- Le bucket d'archives porte `prevent_destroy`, n'expose publiquement que le
  prefixe `site/`, et chiffre son contenu.
- Les sauvegardes contiennent les comptes et les hash de mots de passe des
  joueurs : `deploy/backups/` est dans le `.gitignore`.

### Limite connue, assumee

Le front pilote le demon Docker de l'arena. **Compromettre CTFd, qui est
expose sur Internet, donne donc root sur l'arena et sur les conteneurs de
toutes les equipes.** C'est inherent a un instancier : le service qui cree les
conteneurs doit pouvoir les creer. La mitigation realiste est de tenir CTFd a
jour, de garder le port du tunnel sur le reseau interne du compose, et de
considerer l'arena comme sacrifiable — elle est detruite apres chaque phase.

## Etat des lieux

Ce depot contient l'infrastructure et le front. Ne sont **pas** encore
implementes, et sont necessaires a l'evenement :

- l'instancier par equipe (`ctfd-whale` ou equivalent) ;
- le plugin `ai_challenges` (voir `ai-challenges-design.md`) ;
- les challenges eux-memes.

Les garde-fous contre la resolution par IA, et les regles d'ecriture des
challenges qui en decoulent, sont dans `anti-llm-guardrails.md`.
