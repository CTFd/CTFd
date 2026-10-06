# Setup CTFd en production — NCTF26 (ctf.tg)

> Checklist de configuration de la plateforme **après** que `make deploy` a mis le
> front en ligne (conteneurs Up). Se lit avec `deploy/RUNBOOK.md` (jour-J +
> incidents) et `deploy/DEPLOY-AWS.md` (infra). **Toutes les commandes depuis
> `deploy/`.**
>
> ⚠️ **Ne JAMAIS lancer `make local-seed` / `local/seed.py` contre la prod** :
> il crée `admin`/`admin` et `playtest`/`playtest` (comptes de la stack locale
> jetable). En prod = compromission immédiate.

État de départ : front up sur `http://13.37.197.230`, redirige vers `/setup`.

## 1. Domaine + HTTPS

Le domaine `ctf.tg` **n'est pas requis pour avancer** : il ne bloque que le HTTPS.
Tout le reste (setup, import, Lot-5, preflight, tests internes) se fait en HTTP sur
l'IP. On garde donc `ctf.tg` + HTTPS pour la **dernière étape, juste avant la
présélection**.

### 1a. Phase de test — maintenant, sans domaine

- **Simple (recommandé)** : rester en **HTTP sur `http://13.37.197.230`**. Zéro
  certificat, zéro DNS. On avance sur tout le reste.
- **Dérisquer la chaîne TLS une fois** (certbot est une panne classique le jour J) :
  utiliser un domaine gratuit/instantané qui résout déjà vers l'IP, sans rien
  enregistrer — `front/.env` : `CTF_DOMAIN=13.37.197.230.sslip.io` (ou `.nip.io`),
  puis `make tls-init` → vrai certificat Let's Encrypt. Prouve que le pipeline TLS
  marche ; on rebascule sur `ctf.tg` plus tard.

> ⚠️ Tant qu'on n'est pas sur `ctf.tg` + HTTPS : **ne PAS ouvrir les inscriptions
> publiques**. Garder `registration_visibility=private` (ou restreindre par
> `player_cidrs`) et `verify_emails=off`. Tester en interne : OK ; ouvrir au public
> sur une URL temporaire : non.

### 1b. Bascule finale — `ctf.tg` (avant la présélection)

1. **DNS** : enregistrement **A `ctf.tg` → 13.37.197.230** chez le registre `.tg`
   (peut être lent/manuel). Vérifier : `dig +short ctf.tg` renvoie l'IP.
2. **Config** (hors git, sur le front) : `terraform/terraform.tfvars`
   `domain_name = "ctf.tg"` ; `front/.env` `CTF_DOMAIN=ctf.tg` +
   `CERTBOT_EMAIL=<email d'ops CERT.tg>` (Let's Encrypt y envoie les avis
   d'expiration — pas une boîte perso jetable) + `REDIS_PASSWORD=<openssl rand -hex 32>`
   (obligatoire : le compose lance Redis avec `--requirepass`).
3. **TLS** : `make tls-init` si le domaine pointe **directement** sur le front (DNS only).
   **ctf.tg est proxifié par Cloudflare** (nuage orange) : utiliser à la place
   `CF_API_TOKEN=<jeton> make tls-cloudflare` (certificat d'origine Cloudflare 15 ans,
   mode SSL _Full (strict)_, TLS ≥ 1.2, vraies IP clients via `CF-Connecting-IP`), puis
   réserver 80/443 aux plages Cloudflare : `web_cidrs` dans `terraform.tfvars`
   (`scripts/cloudflare-ips.sh --tfvars`) + `terraform apply`. Détails :
   `deploy/scripts/cloudflare-origin-tls.sh`. Ancien mode (DNS only, sans Cloudflare) : `make tls-init`. Vérifier `https://ctf.tg/` (vitrine) et `https://arena.ctf.tg/` (CTFd) en 200, certificat valide.

   #### Domaines (depuis le 2026-10-06)

   | Hôte               | Rôle                                                              | Servi par                                                                                              |
   | ------------------ | ----------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------ |
   | `ctf.tg` (apex)    | vitrine statique (`deploy/front/vitrine/`)                        | nginx, `root /usr/share/nginx/vitrine`                                                                 |
   | `arena.ctf.tg`     | plateforme CTFd (joueurs, admin, API `/api/v1`, `/healthcheck`)   | nginx → `ctfd`                                                                                         |
   | `www.ctf.tg`       | redirection 301 vers l'apex                                       | règle Cloudflare + nginx                                                                               |
   | `challenge.ctf.tg` | ancien nom de la plateforme : redirection 301 vers `arena.ctf.tg` | règle Cloudflare (`cloudflare-zone-hardening.sh`) ; l'enregistrement DNS doit exister et être proxifié |

   Toute commande qui parle à l'API CTFd (`URL=`, `CTF_URL`, `ctf init`, `curl …/api/v1`) vise
   **`https://arena.<domaine>`** : l'apex sert la vitrine et répond 404/405 sur ces chemins.

   **Durcissement de la zone (plan Free) — `scripts/cloudflare-zone-hardening.sh`**
   (relançable ; `--check` = lecture seule ; jeton via
   `set -a; . ~/.config/nctf26/cloudflare.env; set +a`). Posé le 2026-09-25 :

   - HSTS 1 an + `nosniff` à la bordure (nginx les envoie déjà, la bordure les
     garantit aussi sur les pages d'erreur Cloudflare) ; TLS 1.2 mini, 0-RTT off.
   - **WAF managé** : le « Cloudflare Managed Free Ruleset » est déployé (il ne
     l'était pas : aucune règle managée n'était active). Vérifié : l'API CTFd
     (`PATCH /api/v1/configs`) passe.
   - **Rate limiting** (1 seule règle sur Free) : 30 `POST` / 10 s / IP sur
     `/login`, `/register`, `/reset_password`, `/confirm` → block 10 s. Attention
     aux CGNAT des opérateurs togolais : ne pas descendre en dessous (CTFd limite
     déjà à 10 / 5 s par IP côté application).
   - Redirection `www` → apex à la bordure (301) sans toucher l'origine.
   - **DNSSEC** : signé côté Cloudflare, statut `pending` tant que le **DS n'est
     pas posé au registre .tg** (nic.tg). DS à transmettre :
     `ctf.tg. 3600 IN DS 2371 13 2 C455E031E8A10295C75BD66250D7AB6C6024A8D158B39AEF16685B9483308926`
     (le script l'affiche). Sans DS, DNSSEC est sans effet.
   - **DMARC** `p=quarantine` avec rapports gérés par Cloudflare
     (`rua=…@dmarc-reports.cloudflare.net`, gratuit) ; SPF apex réparé (des
     guillemets parasites `''` cassaient l'enregistrement) et étendu à SES.
   - DNS nettoyé : `playground.ctf.tg` → `34.179.165.24` (IP Google Cloud qui
     n'appartient à personne de connu, ne répondait pas : **risque de takeover
     de sous-domaine**) supprimé ; CNAME Mailgun `email.ctf.tg` passé en
     DNS-only.
   - ⚠️ **Zone périmée sur les anciens serveurs** : `ns1.nic.tg`, `ns1.gouv.tg`,
     `ns2.gouv.tg` et `tld.cafe.tg` servent encore une vieille zone `ctf.tg`
     (`www` → `ctftogo.ctfd.io`, ancien hébergement CTFd.io) et se déclarent
     autoritaires. La délégation publique est bien Cloudflare, mais un résolveur
     de FAI togolais (constaté chez GVA) a renvoyé ces vieilles réponses pour
     `www.ctf.tg` (certificat `*.ctfd.io`, site tiers). **Cause confirmée le
     2026-09-25 : `ns1.nic.tg` et `tld.cafe.tg` sont aussi 2 des 8 serveurs du
     TLD `.tg` et répondent en autoritaire avec cette vieille zone au lieu de
     déléguer vers Cloudflare** (les 6 autres délèguent correctement). ~1
     résolution non cachée sur 4 échoue dans le monde, presque toutes chez
     Togo Telecom. **Demander à nic.tg de supprimer la zone `ctf.tg` de
     `ns1.nic.tg`, `tld.cafe.tg`, `ns1.gouv.tg`, `ns2.gouv.tg`** (demande prête
     hors git : `~/.config/nctf26/nic-tg-request.txt`). Contrôle avant/après :
     `deploy/scripts/dns-delegation-check.sh` (sortie 0 = tous les serveurs du
     TLD délèguent vers Cloudflare) — à mettre dans la check-list du jour J.

   **Règles WAF personnalisées à contrôler avant l'ouverture** (le script n'y
   touche pas ; tableau de bord Sécurité → WAF → Règles personnalisées) :

   - Bot Fight Mode **désactivé** et niveau de sécurité **medium** : sinon les
     scripts des joueurs (curl, python-requests, ctfcli) sont défiés ou bloqués,
     sans exception possible sur le plan Free.
   - Aucune règle limitant les méthodes HTTP : l'API CTFd utilise PATCH et DELETE
     (la règle héritée « Only Get & Post » a été désactivée le 2026-09-24).
   - Règle « CTFd API » (skip niveau de sécurité + Browser Integrity Check sur
     `/api/`) : conservée.
   - Règle « IP not from Togo » (bloque tout visiteur hors Togo) : **décision
     d'organisation**. Si le CTF est réservé au Togo, la garder ; sinon la
     désactiver. Dans tous les cas, les vérifications externes (CI, moniteurs)
     doivent passer par le tunnel SSH ou être faites depuis le Togo.
   - Les instances de challenge (ports 28000-28500) sont jointes par l'IP publique
     du front, pas par le nom : Cloudflare ne les voit pas, elles ne sont pas
     protégées par le proxy.
   - Plan Free : envoi limité à 100 Mo par requête (gros imports/fichiers de
     challenge : passer par le tunnel SSH), délai de réponse maximal 100 s.
     Coût du switch : quasi nul (les instances servies utilisent `FRONT_PUBLIC_IP:port`,
     pas le domaine). Sans DNS résolu, certbot échoue (challenge HTTP-01).

## 2. Setup initial CTFd (admin fort, PAS de seed local)

Faire le `/setup` **manuellement** avec un mot de passe fort, puis générer un
jeton API pour la suite scriptée :

1. Générer le mot de passe admin : `openssl rand -base64 24` (le **conserver** dans
   ton gestionnaire de secrets).
2. Ouvrir `https://arena.ctf.tg/setup` (ou HTTP tant que le TLS n'est pas prêt) et
   renseigner :
   - **CTF name** : `NCTF26`
   - **Admin** : login d'équipe CERT.tg + le mot de passe fort ci-dessus (jamais
     `admin`/`admin`)
   - **User mode** : **Teams** (équipes)
   - **Theme** : **hibris**
   - **Registration visibility** : `public` (présélection ouverte) — à passer
     `private` pour la finale
   - **Verify emails** : **ON** — mais seulement APRÈS avoir prouvé le SMTP
     (`make mail-test`), cf. §2bis. L'activer sans SMTP qui marche = lockout à
     l'inscription (le preflight le bloque en FAIL).
3. **Taille d'équipe** : 4 à 5 joueurs. Le maximum est le réglage CTFd `team_size`,
   le minimum vient du plugin `team_min_size` (config `team_size_min`) : une équipe
   incomplète peut s'inscrire et lire les énoncés, mais ne peut ni soumettre de flag
   ni lancer d'instance tant qu'elle n'a pas 4 membres.
   ```
   curl -H "Authorization: Token $CTFD_TOKEN" -H 'Content-Type: application/json' \
     -X PATCH $URL/api/v1/configs -d '{"team_size": 5, "team_size_min": 4}'
   ```
4. Une fois connecté admin : **Admin → Settings → Access Tokens** → créer un jeton.
   L'exporter pour les commandes suivantes (jamais en argument CLI en clair) :
   ```
   export CTFD_TOKEN=<jeton>
   export URL=https://arena.ctf.tg
   ```

## 2bis. E-mail (SMTP) — confirmations d'inscription + reset de mot de passe

**Décision : vérification e-mail ON.** L'inscription exige alors un mail de
confirmation reçu **et** cliqué. Conséquence directe : **si le SMTP ne marche pas
le soir J, personne ne peut valider son compte** (lockout massif). D'où l'ordre
imposé ci-dessous — on prouve l'envoi AVANT d'activer la vérification.

**Ordre à respecter (ne pas activer ON à l'aveugle) :**

1. **Domaine + auth** : `ctf.tg` résolu, **SPF + DKIM + DMARC** posés (§1b) — en
   **DNS-only** (voir l'encart plus bas). Sans DKIM, les confirmations partent en
   spam et bloquent des inscriptions.
2. **Renseigner le SMTP** dans `front/.env` (bloc ci-dessous) puis `make deploy`.
3. **PROUVER l'envoi** : `make mail-test TO=<toi>` (envoie un vrai mail depuis le
   conteneur front). Doit arriver **en boîte de réception**, pas en spam.
4. **Seulement alors** activer la vérification :
   `curl -H "Authorization: Token $CTFD_TOKEN" -X PATCH $URL/api/v1/configs -d '{"verify_emails": true}'`.
5. **`make preflight`** garde le coup : `verify_emails ON` sans SMTP configuré =
   **FAIL** bloquant (check `email/smtp`), et un rappel `MANUAL` de rejouer
   `mail-test`.

**Plafond journalier = le vrai facteur** (pas le quota mensuel) : ~300 joueurs
peuvent s'inscrire le même soir (ven 19h). Avec la vérification ON, un mail non
reçu = un joueur bloqué, donc il faut de la **marge**.

**Choix du fournisseur :**

| Fournisseur      | Gratuit                  | Plafond/jour                  | Note                                                                                                                                                                                                                                   |
| ---------------- | ------------------------ | ----------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Brevo** (reco) | ~9 000/mois              | **300/jour**                  | Le meilleur plafond **journalier** gratuit ; serveurs UE / RGPD (adapté à un event francophone). SMTP simple.                                                                                                                          |
| Mailjet          | 6 000/mois               | 200/jour                      | Plafond journalier plus bas.                                                                                                                                                                                                           |
| Resend           | 3 000/mois               | 100/jour                      | Trop bas pour une pointe de 300.                                                                                                                                                                                                       |
| SMTP2GO          | 1 000/mois               | ~33/jour                      | Trop bas.                                                                                                                                                                                                                              |
| **Amazon SES**   | ~gratuit via crédits AWS | **jusqu'à des milliers/jour** | Le bon choix **si vérification ON à 300 joueurs**. Natif AWS (on y est déjà), ~0,10 $/1000. **Mais** : sortie de sandbox à demander (1–3 jours ouvrés) + domaine `ctf.tg` vérifié (DKIM). À lancer **maintenant** vu le mois d'avance. |

**Recommandation (vérification ON à ~300) : Amazon SES.** La vérification rend le
plafond critique — un mail perdu = un joueur bloqué — donc on veut de la marge.
SES est natif AWS (on y est déjà), monte à des milliers/jour, ~0,10 $/1000. **À
lancer maintenant** (sortie de sandbox 1–3 j ouvrés + DKIM `ctf.tg`). **Brevo
(300/jour)** reste le plan de repli immédiat / pour tester la chaîne tout de
suite, viable si les inscriptions s'étalent sur le week-end (23–26 oct) plutôt
que toutes le vendredi soir.

**⚠️ Deliverabilité — indispensable quel que soit le fournisseur :** authentifie
le domaine d'envoi (**SPF + DKIM + DMARC sur `ctf.tg`**), sinon les mails de
confirmation partent en spam et bloquent des inscriptions. Ces enregistrements
DNS se posent en même temps que le A record de `ctf.tg` (§1b).

> ⚠️ **Enregistrements mail en DNS-only (nuage GRIS), jamais proxifiés.** Le
> domaine `ctf.tg` est derrière le proxy Cloudflare, mais les DKIM/SPF/DMARC et
> tout CNAME de tracking/sous-domaine d'envoi (Brevo/SES) doivent rester en
> **DNS only** — un enregistrement mail proxifié (orange) casse l'auth d'envoi
> (c'est ce qui casserait le vieux CNAME Mailgun `email.ctf.tg`, actuellement
> proxifié). Purger au passage les enregistrements Mailgun hérités inutilisés.

**Config CTFd (Brevo) — via `front/.env` (le secret reste hors git) :**

```
MAILFROM_ADDR=noreply@ctf.tg        # expéditeur (adresse validée / domaine authentifié)
MAIL_SERVER=smtp-relay.brevo.com
MAIL_PORT=587
MAIL_USEAUTH=true
MAIL_USERNAME=<e-mail de login Brevo>
MAIL_PASSWORD=<clé SMTP Brevo>      # onglet SMTP du compte — PAS la clé API. SECRET.
MAIL_TLS=true
```

**Config CTFd (Amazon SES) — via `front/.env` :**

```
MAILFROM_ADDR=noreply@ctf.tg        # identité vérifiée dans SES (domaine ctf.tg)
MAIL_SERVER=email-smtp.eu-west-3.amazonaws.com   # endpoint SMTP de TA région SES
MAIL_PORT=587
MAIL_USEAUTH=true
MAIL_USERNAME=<SMTP username SES>   # créé via SES > SMTP settings (≠ clé IAM console)
MAIL_PASSWORD=<SMTP password SES>   # dérivé à la création des identifiants SMTP. SECRET.
MAIL_TLS=true
```

Prérequis SES : domaine `ctf.tg` vérifié (DKIM signé) **et** sortie de sandbox
accordée (sinon envoi limité aux adresses vérifiées, 200/jour). Demander la prod
dès maintenant.

**État SES au 2026-09-25 (fait, région `eu-west-3`) :**

- Identité de domaine `ctf.tg` créée, **DKIM vérifié** (3 CNAME Easy DKIM en
  DNS-only chez Cloudflare), MAIL FROM personnalisé `ses.ctf.tg` (MX + SPF
  posés) → alignement SPF **et** DKIM pour DMARC.
- Utilisateur IAM `nctf26-ses-smtp` (droit `ses:SendEmail`/`SendRawEmail`
  restreint aux expéditeurs `*@ctf.tg`) ; identifiants SMTP dérivés dans
  `~/.config/nctf26/ses-smtp.env` (600, hors git) et déjà écrits dans
  `front/.env` (local + front). `make mail-test TO=success@simulator.amazonses.com`
  → **OK** (le simulateur SES marche même en sandbox).
- **Sortie de sandbox : demandée, AWS demande des précisions** (dossier support
  `179029768300189`, e-mail « RE: SES: Production Access » du 2026-09-25 ; l'API
  affiche `DENIED` tant que le dossier n'est pas clos). **Répondre dans la
  console** AWS → Support Center → dossier → « Reply » en collant le texte prêt
  dans `~/.config/nctf26/ses-case-reply.txt` (usage transactionnel, double
  opt-in, volumes, gestion des bounces/plaintes, exemple de mail). L'API Support
  exige un plan payant. Tant que `ProductionAccessEnabled` est `false`, seuls le
  simulateur et les adresses vérifiées reçoivent : l'adresse de l'opérateur a
  été ajoutée comme identité, **cliquer le lien de vérification SES reçu par
  e-mail**. Vérifier : `aws sesv2 get-account --region eu-west-3`.
- Bounces / plaintes : configuration set SES `nctf26` (rattaché à l'identité
  `ctf.tg`) → topic SNS `nctf26-ses-bounces` → e-mail de l'opérateur (**confirmer
  l'abonnement SNS reçu par e-mail**) ; liste de suppression au niveau du compte
  activée (BOUNCE + COMPLAINT).
- **Repli si la prod SES n'arrive pas : Brevo** (300/jour, config plus haut) — le
  domaine est déjà authentifié (SPF/DMARC) ; il restera à poser le DKIM Brevo en
  DNS-only et à écraser les `MAIL_*` SES dans `front/.env`.
- **Ne passer `verify_emails=ON` qu'une fois la prod SES accordée** ; le
  preflight le rappelle (WARN tant que c'est off).

Puis `make deploy` (le compose passe ces variables au conteneur CTFd). Étapes
manuelles côté opérateur : créer le compte Brevo, générer la **clé SMTP**,
valider l'expéditeur / authentifier `ctf.tg`, renseigner `front/.env`. On peut
aussi tout saisir dans **Admin → Config → Email** au lieu de `.env`.

> Laisser les `MAIL_*` vides = envoi désactivé → **garder `verify_emails=off`**
> (sinon l'inscription échoue faute de pouvoir envoyer le mail de confirmation).

## 3. Contenu

1. **Règlement dans /tos** (obligatoire, `make preflight` le vérifie) :
   ```
   make reglement-publish URL=$URL CTFD_TOKEN=$CTFD_TOKEN
   ```
2. **Champ « Université »** sur l'inscription (custom field) + **page d'accueil**
   (hero, `deploy/theme-home-hero.html`) : les poser via l'admin, ou via les
   étapes de `local/seed.py` réutilisables avec `CTFD_TOKEN` (elles ciblent l'URL
   fournie ; ne PAS relancer la partie /setup admin/admin).
3. **Import des challenges (ctfcli)** — cf. RUNBOOK §2 :
   ```
   python3 -m pip install --user ctfcli
   ctf init --url "$URL" --api-key "$CTFD_TOKEN"
   # installer les dossiers voulus (respecter les prérequis IA : ai0->ai1->ai2->ai3)
   ctf challenge install challenges/<cat>/<slug>   # ... pour chaque challenge retenu
   ```
   Les **86 servis implémentés sont `state: hidden`** → importés masqués (voulu).
   Ils ne deviennent jouables qu'après le Lot-5 (§4).

## 4. Lot-5 — rendre les servis jouables (AVANT de les publier)

Sur une machine **Docker** (arena ou poste), pour chaque servi : build image →
rejoue le solveur → flip `visible` si vert.

```
make lot5              # rapport pass/fail sur les 86 implémentés
make lot5 FLIP=1       # passe les OK en state: visible
```

Puis répercuter en prod : soit **ré-importer** les challenges passés `visible`
(ctfcli), soit basculer leur état dans **Admin → Challenges**. Côté arène, les
images doivent exister : `make check-arena` / `make push-images`.

> Sans Lot-5 vert, garder les servis `hidden`. Un servi visible sans image
> exploitable = joueurs bloqués.

## 5. Fenêtre + preflight (le gate)

1. **Calibrer les compteurs attendus** : `make preflight` a des défauts
   `EXPECT=369 challenges / CATS=20 catégories` (état du 23 septembre 2026). **Les ajuster au set réellement
   importé** (sinon FAIL sur les compteurs) :
   ```
   CTFD_TOKEN=$CTFD_TOKEN make preflight PHASE=preselection URL=$URL EXPECT=<n> CATS=<c>
   ```
2. **Fenêtre de présélection** (ven 23 19:00 → lun 26 00:00) :
   ```
   make presel-window APPLY=1 URL=$URL CTFD_TOKEN=$CTFD_TOKEN
   ```
3. **`make preflight` DOIT être 0 FAIL** avant d'ouvrir. Un FAIL = on ne bascule
   pas. Les `WARN`/`MANUAL` se lisent une par une (instancier, IA, images).

## 6. Sécurité avant ouverture

- [ ] **Resserrer `admin_cidrs`** : `196.170.0.0/15` est très large (~131k IP).
      Mettre l'IP fixe/VPN d'admin en `/32` si possible ; l'**agent SSM Online**
      reste la voie de secours si tu te verrouilles. `terraform apply` après
      changement.
- [ ] **Mot de passe admin fort** confirmé (aucun `admin`/`admin`, aucun compte
      `playtest` en prod).
- [ ] **HTTPS** actif (`https://ctf.tg` vitrine, `https://arena.ctf.tg` CTFd), redirection HTTP→HTTPS, `challenge.ctf.tg` → `arena.ctf.tg`.
- [ ] **Sauvegardes** : timer `ctfd-backup` armé (`make backup-status` < 15 min) ;
      un `make backup` manuel avant toute grosse manip.
- [ ] **IMDSv2**, pas de port arène/IA ouvert sur Internet (déjà en Terraform).

## 7. Piste IA — Amazon Bedrock (chemin par défaut)

**Backend IA finalisé : `ai_backend = "bedrock"`** (défaut dans
`terraform.tfvars`). Décision NCTF26 : le quota GPU EC2 « Running On-Demand G and
VT instances » a été **refusé le 23/09/2026** (case 179016552700802) → **aucun
nœud IA, aucune dépendance GPU**. La passerelle `ai-gateway` tourne sur le
**front** : elle garde le dialecte Ollama `/api/chat` côté challenges et, avec
`AI_BACKEND=bedrock`, traduit vers Bedrock Converse. IA à l'usage : ~0,1 USD /
1000 requêtes, pas de `g4dn`.

- [x] **Décision tranchée** : backend IA = Bedrock (quota GPU refusé le
      23/09/2026, case 179016552700802).
- [ ] **IAM** : la politique `bedrock:InvokeModel` est attachée au rôle du
      **front** ; IMDSv2 `hop-limit=2` pour que le conteneur lise le rôle ;
      région `eu-west-3`.
- [ ] `make check-bedrock` vert : chaque modèle du pool répond + quotas affichés.
      Par défaut les **4 modèles Nova** (Amazon Nova, eu-west-3), ~85 req/min
      cumulé ; chaque modèle a un petit quota par minute non ajustable (Nova
      20-25). Modèle « maison » stable par équipe, débordement sur les suivants,
      cooldown 20 s sur throttle ; au-delà du pool la passerelle répond 503
      « réessayez ». Vérifié en eu-west-3 : les 4 Nova répondent (chat + appel
      d'outil) sans formalité ; Claude Haiku 4.5 exige le formulaire « use case
      details » Anthropic (console Bedrock), Pixtral Large est limité à 1 req/min ;
      augmentation possible (ajustable) sur Nova 2 Lite global et Claude Haiku 4.5.
- [ ] Rejouer les solutions des 3 challenges IA à modèle (`ai1-naive-guard`,
      `ai3-tool-abuse`, `agent-tool-abuse`) contre le pool : les Nova résistent
      plus à l'injection que `llama3.1:8b`. Ajuster les prompts si un niveau
      devient insoluble ; modèles chat-only optionnels pour les niveaux sans
      outils : `bedrock_chat_models = "mistral.mistral-7b-instruct-v0:2=8"`
      (modèle plus naïf).
- [ ] `make phase-preselection` puis `make link` écrivent `AI_BACKEND` /
      `AI_BEDROCK_*` dans `front/.env` ; `make link` échoue si la passerelle ne
      répond pas. `/metrics` expose les compteurs du pool. Les cibles
      `wait-nodes` / `gpu` sautent le nœud IA absent en bedrock.

> **Repli historique — `ai_backend = "ollama"`** (nœud GPU `g4dn.xlarge`) :
> sélectionnable **uniquement si le quota GPU est un jour accordé** (l'appel du
> 24/09 reste déposé ; le statut `CASE_OPENED` de l'API n'est pas à jour, ne pas
> s'y fier). Non retenu pour NCTF26 — laissé étiqueté comme repli.

## 8. Divers repérés

- [ ] **heap-note** : committer le binaire recompilé (ou `make local-fix-heapnote`),
      sinon l'image `ctf-pwn-heap-note` ne se reconstruit pas sur l'arène.

---

**Ordre résumé** —
_Maintenant (test, HTTP sur l'IP, inscriptions fermées)_ : `/setup` admin fort
(teams, hibris) → jeton API → `reglement-publish` + hero + université → import
ctfcli → **Lot-5** (`make lot5 FLIP=1`) → calibrer + `make preflight`.
_Avant la présélection_ : DNS `ctf.tg` (+ `arena`, `www`, `challenge`) → `make tls-cloudflare` → `make preflight` 0 FAIL
→ resserrer `admin_cidrs` → `presel-window` → ouvrir les inscriptions.
