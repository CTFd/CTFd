# Runbook d'exploitation — CTF 2026

Procédure d'exécution de bout en bout : préparation, jours J, incidents, clôture.
Toutes les commandes se lancent **depuis `deploy/`** sauf mention contraire.

- **Présélection** : ven. 23 – dim. 25 octobre (~300 joueurs, par équipe, distant)
- **Finale** : jeu. 29 – ven. 30 octobre (~50 joueurs)
- Légende : 🧑 action humaine · 🤖 automatisable · ⏱ délai incompressible

> Règle d'or : la présélection **filtre**, la finale **décide**. Priorité des risques :
> effondrement infra ≫ compromission plateforme ≫ usage d'un LLM.

---

## 0. Prérequis opérateur (une seule fois)

> **Raccourci** : `cd deploy && make menu` (ou `./nctf`) ouvre un **lanceur
> interactif** — il demande ce que tu veux (local, phases AWS, pendant l'épreuve,
> clôture) et lance le `make` correspondant, en te demandant l'URL et le jeton
> admin au besoin. `./nctf --dry-run` montre les commandes sans les exécuter.
> Pour la fenêtre de présélection : `make presel-window` (ajoute `APPLY=1` pour
> l'appliquer ; sur la prod, `URL=https://… CTFD_TOKEN=…` en plus — le seed
> n'utilise admin/admin que sur la stack locale), ou
> `deploy/preselection-window.sh --apply`. Le seed pose aussi `/tos` et le
> champ « Université » ; `make preflight` refuse s'ils manquent.

- [ ] 🧑 AWS CLI configurée (`aws sts get-caller-identity` répond), profil avec droits EC2/S3/IAM/DynamoDB/Bedrock (ServiceQuotas seulement pour le repli GPU ollama).
- [ ] 🧑 `terraform` ≥ 1.6, `ssh`, `jq` installés sur le poste.
- [ ] 🧑 `deploy/terraform/terraform.tfvars` renseigné (au minimum `admin_cidrs` — **obligatoire, sans défaut**), à partir de `terraform.tfvars.example`.
- [ ] 🧑 Clé SSH d'admin déclarée dans les variables.
- [ ] 🧑 `deploy/front/.env` : `CTF_DOMAIN`, `CERTBOT_EMAIL`, `CTF_TEAM_FLAG_SECRET` (secret maître des flags — **hors git**, généré une fois : `openssl rand -hex 32`).

### État distant Terraform (recommandé avant le jour J)

Pour qu'un `apply` interrompu le matin du 23 soit reprenable et qu'aucun apply concurrent ne corrompe l'état :

```
make state-bootstrap                                              # crée bucket S3 + verrou DynamoDB (état local, une fois)
cp terraform/backend.tf.example terraform/backend.tf
terraform -chdir=terraform/bootstrap output -raw backend_hcl > terraform/backend.hcl
make init                                                        # répondre "yes" pour migrer l'état local -> S3
```

Sans cette étape, l'état reste **local** sur le poste (fonctionne, mais non reprenable ailleurs).

---

### Validation locale complète — AVANT tout `make phase-*` 🧑🤖

Toute la plateforme tourne sur votre machine (Docker), avec les mêmes images,
le même code et les mêmes plugins qu'en production. Cinq commandes, zéro coût
AWS, et vous voyez exactement ce que verront les participants :

```
cd deploy
make local-up               # CTFd + MariaDB + Redis  ->  http://localhost:8000
make local-build-images     # les images ctf-* des 20 challenges servis
make local-seed             # setup NCTF26, mode équipes, thème hibris, accueil, 36 challenges
make local-smoke            # pages, thème, assets, API, chaîne IA verrouillée
make local-playtest         # spawn -> solveur de référence -> soumission, challenge par challenge
```

- [ ] `local-smoke` : tout passe (aucune trace CTFd, tous les assets en 200).
- [ ] `local-playtest` : aucun `FAIL`. Les `STUB` (ai3, agent-tool-abuse) se rejouent à la
      main avec `make local-up-ai` (Ollama sur CPU) : c'est le pré-test adverse du §6.
- [ ] Parcours manuel en tant que `playtest`/`playtest` : accueil, board, démarrer une
      instance, soumettre, scoreboard, une 404.

Détails, verdicts et différences assumées avec la prod : `deploy/local/README.md`.
Sans Docker, le filet minimal reste `pytest tests/test_theme_hibris.py` (5 s).

---

## 1. J-30 → J-14 — Délais incompressibles 🧑⏱

Ces points, pas le code, peuvent faire rater le 23 octobre.

- [ ] **Backend IA = Bedrock** (décision NCTF26 : le quota GPU EC2 a été **refusé le 23/09/2026** → aucun nœud GPU, aucune dépendance GPU). `make check-bedrock` depuis le poste : les 4 modèles Nova répondent en eu-west-3. Repli historique : `make check-gpu-quota` + `ai_backend = "ollama"` (nœud GPU g4dn.xlarge) uniquement si le quota GPU est un jour accordé, cf. DEPLOY-AWS §2.
- [ ] ⏱ **Finale sur site ou distante** — deadline **18 septembre** (appro salle/switch/machines). Défaut si non tranché : portables perso sur VLAN contrôlé + téléphones en caisse.
- [ ] **Domaine** acheté/réservé ; décider Route53 (DNS auto) ou manuel.
- [ ] **Usage IA** : (A) mesurer la compétence _sans_ assistance → IA autorisée en présélection, finale contrôlée [**recommandé**], ou (B) autorisée partout.
- [ ] **Juridique/RH** : notice de collecte (logs, prompts finale, conservation 30 j).

---

## 2. J-14 → J-7 — Répétition (front `setup`) 🤖🧑

Objectif : tout valider sur une petite infra avant de dimensionner pour 300.

```
make init                # (si pas déjà fait)
make phase-setup         # front seul, ~0,02 USD/h
make wait-front          # attend la fin du cloud-init
```

Puis DNS + TLS :

- [ ] 🧑 Pointer `CTF_DOMAIN` vers l'IP publique du front (`make phase-setup` affiche l'action DNS requise ; automatique si Route53).
- [ ] `make deploy` puis `make tls-init` ; vérifier `https://$CTF_DOMAIN/` répond.

### Import des challenges (ctfcli) 🤖

> ⚠ Pas encore de cible `make import`. Procédure manuelle, sur le front :

```
make ssh-front
cd /opt/ctfd/CTFd
python3 -m pip install --user ctfcli
export CTFCLI_TOKEN=<token admin CTFd>          # Admin > Settings > Access Tokens
export CTF_URL=https://$CTF_DOMAIN
ctf init --url "$CTF_URL" --api-key "$CTFCLI_TOKEN"
for d in challenges/*/*/; do ctf challenge install "$d" || echo "ECHEC: $d"; done
```

- [ ] 🤖 Vérifier l'import des **26** challenges (11 statiques + 15 servis).
- [ ] 🤖 **Chaîne IA de prérequis** : ai0 visible ; ai1/ai2/ai3 verrouillés tant qu'ai0 n'est pas résolu (403 sur `/attempt`). Résoudre ai0 avec un compte test → ai1 se débloque, etc.
- [ ] 🤖 Scoring dynamique : le score d'un challenge baisse quand un compte test le résout.
- [ ] 🤖 `make push-images` : images de challenge disponibles pour l'arena au prochain démarrage.

### Instancier par équipe (Lot 2) — validation live ⚠

- [ ] `make link` (relie front↔arena↔IA et vérifie ; en bedrock, écrit `AI_BACKEND` / `AI_BEDROCK_*`). Doit passer les deux checks `check-arena` et IA.
- [ ] Un compte test clique « Démarrer » sur un challenge servi → obtient `front_ip:port`, s'y connecte, exploite, soumet son flag propre, scoreboard OK.
- [ ] Vérifier reap : après TTL (1 h) ou `destroy`, l'instance et son port frp disparaissent (`make check-arena`).
- [ ] **Migration MariaDB** : confirmer que les tables `team_instance`/`frp_port` sont créées et que `FOR UPDATE SKIP LOCKED` fonctionne sur la version MariaDB déployée.

### Piste IA (Lot 3) — validation live ⚠

- [ ] Résoudre ai0 → débloquer ai1 → discuter via la console → la passerelle d'admission (`ai-gateway`, front:8600) garde le dialecte Ollama `/api/chat` côté challenges et, avec `AI_BACKEND=bedrock`, traduit vers Bedrock Converse → `/verify` valide le flag.
- [ ] `make check-bedrock` vert : chaque modèle du pool répond + quotas OK (par défaut les 4 modèles Nova en eu-west-3, ~85 req/min cumulé ; modèle « maison » stable par équipe, débordement sur les suivants, cooldown 20 s sur throttle).
- [ ] **IAM** : le rôle du front porte la politique `bedrock:InvokeModel` ; IMDSv2 `hop-limit=2` pour que le conteneur lise le rôle ; région `eu-west-3`.
- [ ] Vérifier les bornes : rate-limit par équipe, budget tokens, 503 « modèle occupé » normalisé sous charge.
- [ ] `make gpu` montre l'activité (compteurs du pool par modèle ; `/metrics` de la passerelle) ; les tentatives sont loggées (rotation en place).

### Test de charge (300) 🤖

- [ ] Basculer temporairement `make phase-preselection`, puis, **avant de poser les fenêtres** (`/attempt` et `/spawn` répondent 403 hors `start`/`end`) : `make backup`, puis `make loadtest URL=https://… CTFD_TOKEN=…` (300 équipes `lt-*` simulées : login, challenges, 1 flag juste + 3 faux / 20 s, scoreboard 12 s, KotH 10 s ; 5 min de montée, 15 min de plateau) et `make loadtest-instancer URL=…` (50 équipes / 10 min). Verdict VERT/ROUGE en fin de run, rapport `deploy/loadtest/out/*-summary.html` (seuils : p95 < 800 ms, 0 % de 5xx, flags justes 100 %, 429 observé). Outil : `deploy/loadtest/README.md`.
- [ ] Avec les chiffres : figer `WORKERS`, la taille du front (ROADMAP « Savings Plan / taille du front ») et `POLL_MS` du scoreboard si le front souffre ; noter le run dans `infra-audit.md` (section « Test de charge »).
- [ ] Après le test : `make loadtest-purge URL=…` puis **`make restore FILE=…`** du dump pris avant (les solves de charge ont fait décroître les valeurs dynamiques et pris les first bloods). Puis `make phase-setup` (ou `season-down`) pour ne pas payer.

### Répétition générale 🧑🤖

- [ ] 20-30 personnes internes, 3 h, sur l'infra de prod. **C'est ici qu'on fixe les vraies valeurs** de rate-limit et de quotas IA, pas à l'intuition.
- [ ] Rejouer le pré-test adverse (playtest) sur les challenges du haut de tableau (cf. `anti-llm-guardrails.md` §4.9/§8 ; audit statique de départ dans `challenge-audit.md`).

### Config CTFd + règlement 🧑

- [ ] Mode équipes ; taille max d'équipe ; scoring dynamique ; compteurs de solves masqués ; scoreboard gelable ; fenêtre synchrone ; ToS obligatoire.
- [ ] **Thème** : activer le thème custom **`hibris`** (aligné vitrine CERT.tg, drapeau Togo,
      glitch léger, sans marque CTFd ; pied de page « Organisé par CERT.tg » + « Powered by
      Hibris · ramses.dagban.tg »). Il est présent dans `CTFd/themes/hibris/`. L'activer une
      fois, au choix : - UI : _Admin → Config → Theme_ → sélectionner `hibris` ; - ou API : `curl -H "Authorization: Token <admin>" -H 'Content-Type: application/json' \`
      `-X PATCH https://$CTF_DOMAIN/api/v1/configs -d '{"ctf_theme":"hibris"}'`.
      CTFd 3.7 avertit sur les thèmes custom (SSTI via éditeur admin) : on l'installe par le
      système de fichiers (voie sûre), pas via l'éditeur. Vérifier le rendu (accueil, board,
      scoreboard, login, **pages d'erreur 404/403/429/500/502**) à la phase `setup` — cf. la
      note de compatibilité templates 3.7.7.
- [ ] **Accueil « waou »** : l'accueil de CTFd est une _page CMS_, pas un template du thème —
      par défaut elle trahit CTFd. Coller le bloc `deploy/theme-home-hero.html` dans
      _Admin → Pages → page « / » (route vide/index) → éditeur → bouton `</>` (HTML)_, puis
      _Save_. Bloc autonome (styles préfixés `.nctf-*`, mêmes couleurs/polices que le thème,
      titre `NCTF26` + glitch). Ajuster dates, chiffres et liens si besoin. Objectif : un
      participant ne doit pas deviner que c'est du CTFd.
- [ ] **Règlement** publié AVANT l'ouverture des inscriptions (§6 garde-fous). L'extrait « intégrité » (partage de flags = disqualification des deux équipes, les journaux font foi) est dans `deploy/reglement.md` : `make reglement-publish URL=… CTFD_TOKEN=…` le pousse dans la page `/tos` que l'inscription référence ; `make local-seed` le fait sur la stack locale.
- [ ] **Inscription** : la page `/register` du thème hibris impose une **case « J'ai lu et j'accepte le règlement »** (lien vers `/tos`, obligatoire pour créer le compte) et un **champ « Université » en liste déroulante** (champ user requis, créé par `make local-seed` / `ensure_university_field`, ou à la main dans Admin → Config → Fields en prod). La liste déroulante contient les **établissements reconnus 2025-2026** (source edusup.gouv.tg, arrêté du 30/09/2025 : 4 publics + 92 privés + « Autre / N/A »), dans `CTFd/themes/hibris/templates/components/universites_options.html` — éditer ce seul fichier pour toute mise à jour, puis redémarrer CTFd.

---

## 3. J-7 — Bascule présélection 🧑

```
make phase-preselection      # crée l'arena ; aucun nœud IA en bedrock (IA à l'usage, ~0,1 USD / 1000 req)
make wait-front              # front prêt
make wait-arena             # arena prête (le nœud IA absent est sauté en bedrock)
make link                   # relie tout, vérifie l'arena ; écrit AI_BACKEND / AI_BEDROCK_*
make deploy && make tls-init # si le front a été recréé
make check-arena            # images de challenge présentes
make arena-build-images MISSING=1 PUSH=1   # construit SUR l'arena les images des servis `visible` absentes, les publie dans S3
make arena-koth             # King of the Hill : 4 collines sur l'arena + tunnel frps (28490-28495) + plugin CTFd ; STATUS=1 / DOWN=1
make check-bedrock          # pool Bedrock : chaque modèle + quotas (remplace la validation du nœud IA)
CTFD_TOKEN=… make preflight PHASE=preselection   # check-list : DOIT être vert (0 FAIL)
```

- [ ] 🧑 `make preflight PHASE=preselection` vert (secrets, fenêtres 53 h, 203 challenges,
      19 catégories, collines KotH en ligne). Un FAIL = on ne bascule pas. Les WARN se
      lisent une par une ; les 3 lignes `MANUAL` (instancier, IA, images) se font à la main.
- [ ] 🧑 **Quota vCPU** : l'arena de présélection est une `c6i.4xlarge` (16 vCPU) ; le quota
      « Running On-Demand Standard » (L-1216C47A) de ce compte est à **16** (demande à 48
      déposée le 2026-09-27). Tant qu'il n'est pas monté, garder
      `arena_instance_type_override = "c6i.2xlarge"` dans `terraform.tfvars` (8 vCPU).
- [ ] 🧑 `make arena-koth STATUS=1` : 4 collines en ligne, `/king` répond via frps sur
      28490/28493/28494/28495, page `/plugins/koth/` OK. Les joueurs attaquent
      `FRONT_IP:28490` (Throne), `:28491` (Citadel ssh), `:28492` (Armory ssh), `:28493`
      (Réseau Fortune) ; l'instancier est borné à 28000-28480.
- [ ] 🧑 `make check-bedrock` vert : le pool Bedrock répond (4 modèles Nova en eu-west-3) et
      les quotas sont OK. L'IA passe par le rôle IAM du front (`bedrock:InvokeModel`), pas par
      un nœud GPU.
- [ ] 🧑 Repointer le DNS si l'IP a changé ; vérifier HTTPS.
- [ ] 🧑 Ouvrir les inscriptions.
- [ ] 🧑 Dernier `season`-test : un compte réel résout un challenge de chaque type.

> **Repli historique — `ai_backend = "ollama"`** (nœud GPU `g4dn.xlarge`, uniquement si un
> jour le quota GPU est accordé ; hors chemin critique NCTF26). Le levier `phase-preselection`
> crée alors **arena + nœud IA** (~1,46 USD/h) ; `make wait-arena` attend aussi l'IA
> (télécharge le modèle Ollama) ; `make link` vérifie arena **+ IA** ; à J-30 on aura d'abord
> lancé `make check-gpu-quota`. Supervision de repli : `make gpu` = file Ollama, `make ssh-ai`.

---

## 4. Jours J présélection (23-25 oct) 🧑

Cadence pendant l'épreuve :

| Quand                    | Commande              | Attendu                                                                                                                            |
| ------------------------ | --------------------- | ---------------------------------------------------------------------------------------------------------------------------------- |
| automatique (15 min)     | _timer `ctfd-backup`_ | dump **vérifié** → `s3://…/backups/auto/` ; uploads + export natif 1×/h ; état sur la page **Ops**                                 |
| toutes les ~2 h          | `make backup-status`  | « dernier dump OK : il y a < 15 min » — sinon `make backup-now` puis `make logs`                                                   |
| avant toute manipulation | `make backup`         | dump **vérifié** manuel (gzip -t + table users) envoyé sur S3, conservé sans expiration                                            |
| en continu (écran 2)     | page admin **Ops**    | `/plugins/ops/admin` : tout vert (DB, Redis, dernier dump < 15 min, reaper, collines, 5xx = 0)                                     |
| en continu (2ᵉ terminal) | `make logs`           | pas d'erreur 5xx en rafale                                                                                                         |
| si piste IA active       | `make gpu`            | compteurs du pool par modèle ; cooldown 20 s = quota Bedrock atteint, ne doit pas être permanent (repli ollama : file non saturée) |
| au moindre doute         | `make cost`           | rappel de ce qui est facturé                                                                                                       |

- [ ] 🧑 24 au soir : `make season-down` (**sauvegarde vérifiée + archive S3 + destruction EC2**).
- [ ] 🧑 **Ligne de coupe automatique** à la fermeture : inviter 14-16 équipes (marge + wildcards). Litiges d'intégrité traités **après** la finale.

---

## 5. Playbooks d'incident 🚑

Diagnostic d'abord : `make cost` (qu'est-ce qui tourne ?), `make logs`, `make ssh-*` puis `sudo cat /var/log/cloud-init-output.log`.

**Front injoignable (HTTP KO)**

1. `make ssh-front` → `cd /opt/ctfd/CTFd && docker compose ps`.
2. Conteneur ctfd down → `docker compose up -d` ; logs → `docker compose logs ctfd`.
3. cloud-init pas fini → attendre / `make wait-front`.
4. Nginx/TLS cassé → revérifier `make tls-init` (DNS doit résoudre vers l'IP du front).

**CTFd ne joint pas le Docker de l'arena** (instancier KO — **risque #1**)

1. `make link` (réétablit le tunnel ssh dockerproxy + frpc).
2. Échec du check → `make ssh-arena`, vérifier le démon Docker et l'overlay `--attachable`.
3. Vérifier que `-p 127.0.0.1:P` fonctionne côté arena et que la plage frp (28000-28500) n'est pas épuisée (501 instances max).

**Connexion joueur `front_ip:port` échoue**

1. frpc admin joignable via le tunnel ? `PUT /api/config` + reload effectifs ?
2. `allowPorts` frps couvre la plage ; le forward 7400 via dockerproxy est up.

**Piste IA : 503 permanents / pool Bedrock en cooldown (repli ollama : GPU saturé)**

1. `make gpu` : compteurs par modèle. Cooldown 20 s = throttle Bedrock atteint (petit quota par minute non ajustable, Nova ~20-25, ~85 cumulé ; le pool déborde sur les modèles suivants). Un cooldown permanent → réduire les quotas d'admission (`AI_*` dans l'env de `ai-gateway`) sans rebuild.
2. `make check-bedrock` depuis le poste : si la passerelle ne lit pas le rôle → vérifier IMDSv2 `hop-limit=2` et la politique `bedrock:InvokeModel` sur le rôle du front (eu-west-3).
3. Arène→front:8600 injoignable → vérifier la règle SG et l'injection `OLLAMA_URL`/`AI_PROXY_TOKEN` (la passerelle garde le dialecte Ollama sur front:8600).
4. **Repli ollama** : Ollama down → `make ssh-ai`, redémarrer le service ; vérifier le modèle téléchargé.

**Partage de flags (menu admin Anti-triche, ou ligne `ANTICHEAT` dans `logs/submissions.log`)**

1. Ouvrir `/plugins/anticheat/admin` : l'incident donne soumetteur, propriétaire du flag, challenge, IP, horodatage. Une paire qui revient (`2×`, `3×`) est du partage avéré ; une occurrence isolée peut être un copier-coller entre deux onglets d'une même personne membre… d'une seule équipe — vérifier.
2. **Ne rien bannir à chaud.** Exporter le CSV (bouton) et l'archiver avec l'horodatage ; appliquer le barème du règlement (avertissement au 1ᵉʳ, décision jury au 2ᵉ). Sanction = action manuelle dans Admin → Teams (`banned`), jamais le plugin.
3. Faux positifs connus : aucun par construction (un flag `team_hmac` d'une autre équipe ne s'invente pas). Si un même compte apparaît des deux côtés, c'est une équipe recomposée : rebâtir l'index avec **Recalculer tout** après tout changement d'équipe ou rotation de `CTF_TEAM_FLAG_SECRET`.
4. Réponse aux joueurs : uniquement par le canal officiel, jamais via une notification CTFd (globale).
5. **Flags statiques (177 épreuves, même flag pour tous)** : aucun incident possible par construction. Le signal est la section **Validations synchrones** de la même page : paires d'équipes qui valident les mêmes épreuves à quelques secondes d'écart, plusieurs fois, pondérées par la rareté de l'épreuve (`1 / nb de solveurs`), et adresses IP communes. C'est circonstanciel : **rapport pour le jury après coup**, jamais une sanction à chaud. Une ligne rouge = score ≥ 0,5 ou IP commune ; regarder qui valide en premier (l'équipe « source ») et l'écart médian.

**Disque plein (« no space left »)**

- Les logs de tentatives IA sont en rotation bornée (pas la cause). Supprimer artefacts/anciens backups locaux ; sur l'arena, purger images/conteneurs morts. Les deletes réussissent même disque plein.

**Corruption / perte de données** → **restaurer**

1. **Qui décide** : le responsable de plateforme, après un mot au jury. **Geler le
   scoreboard** d'abord (Admin → Config → `freeze` = maintenant) : les joueurs ne
   voient plus bouger le classement pendant l'opération, et rien n'est perdu côté
   scoring (les soumissions continuent d'être enregistrées).
2. **Quel dump** : `make backup-status` donne l'heure du dernier dump automatique OK
   (`/opt/ctfd/backups/ctfd-auto-*.sql.gz`, aussi dans `s3://…/backups/auto/`).
   Prendre le **dernier dump antérieur à l'incident**, pas le plus récent. Avant
   d'écraser : `make backup` (figer l'état corrompu, il peut servir au jury).
3. **Restaurer** :

```
make backup                                   # d'abord figer l'état courant
make restore FILE=backups/<dump>.sql.gz       # restaure sur le front (mot de passe : `restaurer`)
make backup-status                            # le timer a repris, un nouveau dump doit apparaître
```

4. **Vérifier** : `/scoreboard` cohérent, page **Ops** verte (DB, Redis, dernier
   dump), awards KotH présents sur la page admin KotH, une instance test se spawne.
5. **Annoncer** aux joueurs, par le canal officiel : fenêtre perdue (entre le dump
   et l'incident), consigne de re-soumettre les flags trouvés dans cet intervalle,
   puis lever le gel.
6. **RTO mesuré à la répétition (Lot 5)** : _à remplir_ — durée de
   `make restore` sur un dump de la taille de la répétition à 300 VU
   (objectif < 10 min).

Perte des **uploads** (fichiers des challenges) : `uploads-auto-*.tgz` (1×/h) à
extraire dans le volume `ctfd_uploads` ; l'`export-auto-*.zip` est un export natif
importable par Admin → Backup → Import si la base elle-même est irrécupérable.

**Apply Terraform interrompu / à moitié raté**

- Avec état distant : relancer simplement `make phase-<...>` (verrou DynamoDB + état S3 rendent l'apply reprenable). Si un verrou traîne (process tué) : `terraform -chdir=terraform force-unlock <LOCK_ID>` après avoir confirmé qu'aucun apply ne tourne.
- Base branch/infra saine mais ressource bloquée : `terraform -chdir=terraform apply` seul re-converge.

---

## 6. Entre-deux (24 → 29 oct) 🧑

- [ ] Infra **détruite** (`season-down` déjà fait le 24 au soir — 5 jours d'instances inutiles coûtent plus que la reconstruction).
- [ ] Résultats de présélection = dans la sauvegarde S3 + l'archive statique (`make archive`).
- [ ] Logistique finale (convocations, salle/VLAN si sur site).

---

## 7. Finale (29-30 oct) 🧑

```
make phase-final            # taille réduite (~50 joueurs) ; aucun nœud IA en bedrock
make wait-front && make wait-arena && make link   # wait-arena saute le nœud IA en bedrock
make deploy && make tls-init
make check-arena
make check-bedrock          # pool Bedrock : chaque modèle + quotas (repli ollama : voir §3)
CTFD_TOKEN=… make preflight PHASE=finale         # fenêtre 24 h, inscriptions fermées
```

- [ ] 🧑 `make preflight PHASE=finale` vert après `finale-window.sh --apply` (fenêtre 24 h,
      `registration_visibility=private`, KotH finale à `points=5`).
- [ ] 🧑 Si sur site : réseau contrôlé, egress liste blanche, machines/VLAN, téléphones en caisse.
- [ ] 🧑 **Écran de la salle** : ouvrir `https://<domaine>/scoreboard?big=1` dans un navigateur dédié (aucun compte connecté), touche `f` pour le plein écran. Top 14 en gros, peloton agrégé, bandeau first bloods, feux de départ, podium et confettis à l'arrivée ; rafraîchi toutes les 12 s, aucune interaction requise. Les joueurs, eux, voient leur propre kart surligné « toi » (ou épinglé sous le peloton s'ils sont hors du top 12) sur `/scoreboard`. Captures : `deploy/docs/scoreboard/` (`race-player-pinned.png`, `race-player-top.png`, `race-big-screen.png`, `race-mobile-400.png`).
- [ ] 🧑 **Classement repart de zéro** (présélection à 0 %).
- [ ] 🧑 Défense devant jury (poids additif faible ≤ 10 %, jamais un gate).
- [ ] 🧑 `make backup` régulier ; `make season-down` le 30 au soir.

---

## 8. Clôture & archives 🧑🤖

```
make archive                # scoreboards figés + write-ups sur S3 (site statique)
make season-down            # si pas déjà détruit
```

- [ ] 🤖 Writeups officiels : `make writeups-prepare URL=… TOKEN=…` **avant** la clôture (pages en brouillon, 404 pour les joueurs, relecture admin possible via l'API), puis à la clôture `make writeups-publish URL=… TOKEN=…` — refusé tant que `end` n'est pas passé (`FORCE=1` pour passer outre, en connaissance de cause). `/writeups` = index (menu) + une page par catégorie ; flags réels masqués, solveurs jamais publiés. `make archive` embarque la même version en HTML statique (`site/<phase>/writeups/`).
- [ ] 🧑 Décider avant : writeups **complets** ou seulement les catégories jouées (`WRITEUPS_ARGS="--categories web,pwn"`) ; le crédit `author:` du challenge.yml est repris tel quel.
- [ ] 🤖🧑 **Rapport anti-triche** : `make anticheat-report URL=… CTFD_TOKEN=…` avant `season-down` (les rapports lisent la base vivante) → `deploy/reports/<horodatage>/` : `incidents.csv` (flags `team_hmac` d'une autre équipe, preuve directe), `sync.csv` + `sync.json` (validations synchrones et IP communes, circonstanciel), empreintes SHA-256. Archiver le dossier avec le dump de clôture ; le jury statue sur ces pièces, après audition des équipes (règlement §3 et §5).
- [ ] 🧑 Rapport de clôture (agrégé, sans accusation nominative depuis la scène).
- [ ] 🤖 Exploiter les logs de charge pour dimensionner l'édition suivante.

---

## Annexe — carte des commandes

| Commande                                                           | Rôle                                                                           |
| ------------------------------------------------------------------ | ------------------------------------------------------------------------------ |
| `make init` / `make state-bootstrap`                               | init Terraform / état distant S3+DynamoDB                                      |
| `make check-bedrock`                                               | pool Bedrock : chaque modèle + quotas (chemin IA par défaut)                   |
| `make check-gpu-quota`                                             | quota GPU — repli ollama uniquement (refusé pour NCTF26)                       |
| `make phase-setup / -preselection / -final / season-down`          | leviers de coût                                                                |
| `make wait-front / wait-arena`                                     | attente provisionnement (wait-arena saute le nœud IA en bedrock)               |
| `make deploy / tls-init / link`                                    | déploiement CTFd / HTTPS / liaison front↔arena↔IA (link écrit AI*BEDROCK*\*) |
| `make check-arena / push-images`                                   | images de challenge sur l'arena                                                |
| `make backup / restore FILE=... / archive`                         | sauvegarde vérifiée / restauration / archive S3                                |
| `make writeups-prepare / writeups-publish URL=... TOKEN=...`       | writeups en brouillon / publiés à la clôture                                   |
| `make reglement-publish / anticheat-report URL=... CTFD_TOKEN=...` | règlement dans `/tos` / rapports anti-triche pour le jury                      |
| `make loadtest URL=... / loadtest-instancer / loadtest-purge`      | test de charge k6 (300 équipes simulées) / instancier / nettoyage              |
| `make logs / gpu / cost`                                           | supervision (gpu = compteurs du pool Bedrock par modèle)                       |
| `make ssh-front / ssh-arena / ssh-ai`                              | shells (ssh-ai = repli ollama uniquement)                                      |
| `make destroy`                                                     | détruit l'EC2 (le bucket d'archives survit)                                    |
