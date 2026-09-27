# King of the Hill — exploitation (KotH)

Le KotH est composé de deux morceaux :

1. **Le plugin CTFd `koth`** (`CTFd/plugins/koth/`) — dérive le jeton par équipe,
   affiche la page joueur (menu **King of the Hill**), et fait tourner un
   **scorer** qui attribue des points via des `Awards` (donc visibles sur le
   scoreboard kart sans rien d'autre).
2. **Un ou plusieurs services « colline »** partagés (`challenges/koth/throne/`,
   image `ctf-koth-throne`) — un seul conteneur que toutes les équipes attaquent.

Aucune table SQL nouvelle, aucune migration : le scoring passe par les `Awards`
du cœur de CTFd.

## Test en local (une commande)

Sur une machine avec Docker, après `make local-up` (+ `make local-seed`) :

```bash
cd deploy
make local-koth
```

Ça construit et lance **deux collines** (`profil koth`), génère un secret scorer
de dev et recrée le conteneur CTFd avec `KOTH_HILLS` + `KOTH_SCORER_SECRET` — le
plugin s'active alors (`KOTH_TICK=15 s` en local) :

- **The Throne** (HTTP) — `http://localhost:28900` : fuite XFF → tenue du trône
  par re-signature.
- **The Citadel** (SSH « root-wars ») — `ssh player@localhost -p 28901` (mot de
  passe `player`) : deviens root, écris ton jeton dans `/koth/king`, tiens-le.

Ouvre le menu **King of the Hill** dans CTFd, récupère le jeton de ton équipe,
puis tiens une colline :

```bash
challenges/koth/throne/solution/solve.sh  http://localhost:28900 <ton-jeton>
challenges/koth/citadel/solution/solve.sh localhost 28901 <ton-jeton>   # needs sshpass
```

Le plugin score **toutes** les collines de `KOTH_HILLS` en parallèle : une hill
peut être HTTP (Throne) ou une box SSH root-wars (Citadel), tant qu'elle expose
un `/king` lisible par le scorer.

Le score de l'équipe doit monter d'un cran de `points` à chaque tick tant que le
trône est tenu. `make local-down` / `make local-reset` arrêtent aussi la colline.
Le reste de ce document décrit le déploiement **arène** (prod).

## Secrets (trois, séparés)

| Secret               | Où                          | Rôle                                                         |
| -------------------- | --------------------------- | ------------------------------------------------------------ |
| `HILL_KEY`           | conteneur colline seulement | autorise une revendication ; **cible de l'exploit**          |
| `KOTH_SCORER_SECRET` | CTFd **et** colline         | lecture de `/king` par CTFd uniquement (`X-Scorer-Token`)    |
| `KOTH_GLOBAL_SECRET` | CTFd seulement              | dérive le jeton par équipe (défaut : `CTF_TEAM_FLAG_SECRET`) |

Générer : `openssl rand -hex 32` pour chacun. `HILL_KEY` peut être laissé vide
(la colline en génère un aléatoire au démarrage) ; le fixer le rend stable entre
redémarrages.

## Déployer une colline

```bash
docker build -t ctf-koth-throne challenges/koth/throne
# via le compose de la colline (challenges/koth/throne/docker-compose.yml) :
KOTH_SCORER_SECRET=<...> KOTH_THRONE_HILL_KEY=<...> docker compose up -d
```

La colline écoute en interne sur `:8080` (jamais publiée directement). Exposez-la
aux joueurs via le reverse-proxy front / FRP, comme les autres services servis.

### Collines boot2root (Armory · Foundry · Vault) — root/user, points pleins/moitié

Trois collines SSH boot2root ajoutent une nuance au scoring : **deux fichiers roi**
par colline.

| Fichier                 | Qui l'écrit              | Points / tick |
| ----------------------- | ------------------------ | ------------- |
| `/home/player/king.txt` | le login `player`        | **moitié**    |
| `/root/king.txt`        | root seul (`/root` 0700) | **pleins**    |

Une équipe qui n'a qu'un accès SSH tient au niveau **user** (moitié). Après un
**passage root** elle écrit `/root/king.txt` et marque **plein**. Le fichier le
plus récent gagne (root l'emporte à égalité), donc tenir = réécrire son fichier
plus vite que les rivaux, et **rester root** pour garder le plein tarif. Chaque
colline a **un** vecteur d'escalade distinct, modeste, pour que la plupart des
équipes atteignent le jeu de tenue :

| Colline     | Image                        | Escalade                                         |
| ----------- | ---------------------------- | ------------------------------------------------ |
| The Armory  | `ctf-koth-boot2root-armory`  | SUID `find` → `find … -exec /bin/sh -p \; -quit` |
| The Foundry | `ctf-koth-boot2root-foundry` | `sudo` NOPASSWD `python3`                        |
| The Vault   | `ctf-koth-boot2root-vault`   | capabilité `cap_setuid+ep` sur `/opt/keymaster`  |

Construire la **base d'abord**, puis chaque colline :

```bash
docker build -t ctf-koth-boot2root-base:latest    challenges/koth/boot2root/base
docker build -t ctf-koth-boot2root-armory:latest  challenges/koth/boot2root/armory
docker build -t ctf-koth-boot2root-foundry:latest challenges/koth/boot2root/foundry
docker build -t ctf-koth-boot2root-vault:latest   challenges/koth/boot2root/vault
```

Le scorer (root) expose `/king` sur `:8082` avec un champ `level` (`root`/`user`)
que le plugin traduit en points pleins/moitié. Ajouter les collines à
`KOTH_HILLS` (`url` = le scorer, `player_url` = l'endpoint SSH), comme la Citadel.
`make local-koth` en câble une (The Armory) en local sur le port 28902.
Détails et solveurs : `challenges/koth/boot2root/README.md`.

## Colline « Réseau Fortune » (finale — le réseau le plus riche tient la couronne)

`challenges/koth/reseau-fortune/` est une colline **économique** : une arène MLM
fictive (KékéliCash) partagée par toutes les équipes. Chaque équipe rejoint avec
son **jeton KotH** (`POST /api/join {token}`), reçoit un compte distributeur seedé
et cherche une faille de logique métier pour enrichir son réseau (numéro non
vérifié = sybil, mais le jeu honnête perd de l'argent ; bugs : prime non
idempotente, remboursement sans reprise de commission). Le `/king` renvoie le
jeton de **l'équipe la plus riche à l'instant t** ; le scorer couronne donc le
réseau le plus riche. Aucun flag, aucun SMS, argent fictif.

```bash
docker build -t ctf-koth-reseau-fortune challenges/koth/reseau-fortune
# via son compose : SCORER_SECRET=$KOTH_SCORER_SECRET  (interne :8080)
```

Entrée `KOTH_HILLS` (finale) — points modérés, l'arène étant très rentable une
fois la faille trouvée :

```json
{
  "id": "koth-reseau-fortune",
  "name": "Réseau Fortune",
  "url": "http://koth-reseau-fortune:8080",
  "player_url": "https://ctf.exemple.tg/koth-reseau-fortune",
  "points": 3
}
```

Griefing borné (on n'aide que le code de parrainage qu'on nomme, on ne débite que
ses propres comptes). Poser un **rate-limit au front** sur `/api/*` pour que le
gagnant soit la meilleure automatisation, pas le plus gros débit. Leviers de
durcissement (TOCTOU, cycle de parrainage) : voir `solution/README.md`. Finale
uniquement (à 300 en présélection, préférer la version jeopardy isolée
`challenges/web/reseau-pyramide/`).

## Déploiement AWS en une commande (`make arena-koth`)

Après `make link` : `make arena-koth` construit/charge les 4 images sur l'arena
(`make arena-build-images ONLY="koth/throne koth/citadel koth/boot2root/armory koth/reseau-fortune" PUSH=1`
si elles manquent), lance les collines en boucle locale de l'arena, les expose via
un **second client frpc** (`frpc-koth`, proxies fixes 28490-28495 dans `allowPorts`
de frps — le frpc principal est réécrit par l'instancier) et écrit
`KOTH_SCORER_SECRET` / `KOTH_HILLS` / `KOTH_TICK` dans `front/.env` (ctfd recréé,
instancier borné à `WHALE_PORT_RANGE_END=28480`). `STATUS=1` = état, `DOWN=1` =
retrait. Le plugin lit `/king` sur `FRONT_PRIV:2849x` ; les joueurs attaquent
`FRONT_IP:2849x` (voir RUNBOOK §3).

## Configurer le plugin CTFd

Variables d'environnement sur le conteneur **CTFd** :

```bash
KOTH_SCORER_SECRET=<le même que la colline>
# KOTH_GLOBAL_SECRET=<...>          # sinon reprend CTF_TEAM_FLAG_SECRET
KOTH_TICK=30                        # secondes entre deux passes de scoring
# KOTH_FRESH_WINDOW=60              # défaut 2*TICK ; une revendication plus vieille ne compte plus
KOTH_HILLS='[
  {"id":"koth-throne","name":"The Throne",
   "url":"http://koth-throne:8080",
   "player_url":"https://ctf.exemple.tg/koth-throne",
   "points":5}
]'
```

> `scorer_secret` (optionnel, par colline) surcharge `KOTH_SCORER_SECRET` pour
> **cette** colline. Utile pour la Citadel (SSH root-wars) : le scorer y tourne
> en root et un joueur devenu root pourrait lire son `SCORER_SECRET` ; lui donner
> un secret dédié évite qu'il serve aussi à lire le `/king` du Throne.

- `url` = adresse **interne** (réseau compose) que CTFd interroge.
- `player_url` = ce que les joueurs voient / attaquent (via le front).
- `points` = points attribués **par tick** au tenant du trône.

Le plugin ne score que si `KOTH_SCORER_SECRET`, `KOTH_GLOBAL_SECRET` et au moins
une colline valide sont présents (`is_active()`), et un seul worker gunicorn
tient le scorer (verrou `fcntl`), comme le reaper de l'instancier.

## Présélection vs finale — calibrer le plafond de points

Le plugin score **toutes** les collines de `KOTH_HILLS` en même temps ; on ajuste
la liste selon la phase. Le plafond d'une équipe qui tiendrait une colline **du
début à la fin** est `points × (durée / tick)`. Il faut le caler par rapport aux
épreuves jeopardy pour que le KotH complète le classement sans l'écraser.

| Phase        | Durée | `points` | `tick` | Plafond 1 colline            |
| ------------ | ----- | -------- | ------ | ---------------------------- |
| Présélection | 53 h  | **1**    | 60 s   | `1 × 3180` = **3 180**       |
| Présélection | 53 h  | 3        | 30 s   | `3 × 6360` = 19 080 _(trop)_ |
| Finale       | 24 h  | **5**    | 30 s   | `5 × 2880` = **14 400**      |
| Finale       | 24 h  | 10       | 30 s   | `10 × 2880` = 28 800         |

(La présélection dure **53 h** : ven 23 oct 19:00 → lun 26 oct 00:00, cf.
`deploy/event-windows.env`. `durée / tick` = 190 800 s / `tick`.)

- **Présélection (~300 joueurs, 53 h non-stop)** : la colline tourne deux nuits ;
  un `points` élevé la rendrait dominante. Vise `points=1`, `KOTH_TICK=60` →
  plafond ~3 180, l'ordre de grandeur d'une poignée d'épreuves _medium_. C'est un
  bonus d'assiduité, pas la moitié du classement.
- **Finale (10 équipes, 24 h)** : format spectacle, on peut monter (`points=5`,
  `tick=30` → ~14 400) et/ou ajouter une 2ᵉ colline pour des retournements plus
  nerveux. `KOTH_FRESH_WINDOW` court (= `2×tick`) rend la tenue plus disputée.

Le total réel est presque toujours **bien en dessous** du plafond : il suppose une
seule équipe tenant le trône sans interruption, alors qu'en pratique il change de
mains. Le plafond est la borne haute à ne pas laisser déraper. Sur une colline
**boot2root**, une équipe qui ne tient qu'au niveau **user** marque **moitié**
moins (le plafond ci-dessus suppose un maintien **root** de bout en bout).

## Suivi en direct (page admin)

Le plugin ajoute **King of the Hill** au menu admin (`/plugins/koth/admin`) :
état de chaque colline (en ligne / hors ligne, tenant courant, jeton tronqué,
règne, nb de retournements), points déjà distribués et **plafond restant** à
l'instant T, plus le top 10 par colline (vue admin, non gelée). C'est la vue
d'opérateur pendant l'épreuve — aucune action, lecture seule, rafraîchie toutes
les 5 s.

### Fil du trône (feed live)

Le scorer tient, par colline, un anneau des derniers changements de trône
(prise, reprise, colline libérée). La **page joueur** et la page admin l'affichent
en **fil d'événements en direct** (« _beta_ reprend The Throne — à l'instant »),
un nouvel item clignotant à son arrivée. C'est ce qui rend le KotH vivant sur un
écran de salle. Le fil respecte le **gel** : masqué pour les non-admins au-delà
de `freeze`, comme le badge des tenants (il révèle qui tient la colline). Exposé
par `/plugins/koth/api/state` (clé `events`) et `/plugins/koth/api/admin`.

## Gel du scoreboard

Le classement **KotH public** (page joueur + badge « colline tenue » sur le
Grand Prix) respecte le gel du scoreboard comme le reste : au-delà de l'instant
`freeze`, les non-admins ne voient plus évoluer les points KotH ni qui tient la
colline (le scorer, lui, continue de compter en base). Les admins voient en
direct. Rien à configurer : c'est le même `freeze` que les épreuves jeopardy.

## Vérifier en vrai (bring-up arène)

1. `docker build` la colline, la lancer avec `SCORER_SECRET`.
2. Régler les `KOTH_*` sur CTFd, redémarrer CTFd.
3. Ouvrir le menu **King of the Hill** en tant qu'équipe → le jeton s'affiche.
4. Lancer `challenges/koth/throne/solution/solve.sh <player_url> <jeton>` →
   vérifier que la page montre l'équipe sur le trône et que son score monte d'un
   cran de `points` à chaque tick.
5. Arrêter le solveur > `FRESH_WINDOW` → le scoring s'arrête (trône « expiré »).

## Notes de sécurité

- `/king` n'est jamais lisible sans `X-Scorer-Token` : les équipes ne peuvent pas
  lire le trône directement (la page CTFd le montre, tronqué).
- Le jeton d'équipe est une **identité**, pas un secret exploitable : planter le
  jeton d'une autre équipe la ferait scorer, elle — aucun intérêt à tricher.
- La colline ne connaît aucune équipe et ne dérive aucun jeton : compromettre la
  colline n'expose pas le mapping jeton→équipe (il vit dans CTFd).
