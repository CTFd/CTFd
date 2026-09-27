# Pilotage du CTF. Toutes les commandes se lancent depuis deploy/.
#
# Calendrier 2026 :
#   preselection  vendredi 23 - dimanche 25 octobre  (~300 joueurs)
#   finale        jeudi 29 - vendredi 30 octobre   (~50 joueurs, 10 equipes)
#
# Hors de ces fenetres la phase est `off` : aucune instance EC2 n'existe.

SHELL       := /usr/bin/env bash
.SHELLFLAGS := -o errexit -o pipefail -c

TF          := terraform -chdir=terraform
SSH_OPTS    := -o StrictHostKeyChecking=accept-new -o ConnectTimeout=10
REPO_URL    ?= https://github.com/hi3ris/CTFd.git
REPO_BRANCH ?= claude/ctf-platform-free-ptiggj

# Les sorties Terraform sont lues paresseusement (=), jamais au chargement du
# Makefile : sinon un `make phase-preselection` capturerait les valeurs
# d'AVANT son propre apply et deploierait vers l'ancienne machine.
tfout      = $(shell $(TF) output -raw $(1) 2>/dev/null)
FRONT_IP    = $(call tfout,front_public_ip)
ARENA_IP    = $(call tfout,arena_public_ip)
AI_IP       = $(call tfout,ai_public_ip)
ARENA_PRIV  = $(call tfout,arena_private_ip)
FRONT_PRIV  = $(call tfout,front_private_ip)
AI_PRIV     = $(call tfout,ai_private_ip)
BUCKET      = $(call tfout,archive_bucket)
REGION      = $(call tfout,aws_region)
PHASE       = $(call tfout,phase)
AI_BACKEND       = $(call tfout,ai_backend)
BEDROCK_MODELS   = $(call tfout,bedrock_models)
BEDROCK_CHAT     = $(call tfout,bedrock_chat_models)
WHALE_PORT_START = $(call tfout,whale_port_range_start)
WHALE_PORT_END   = $(call tfout,whale_port_range_end)

FRONT_SSH = ssh $(SSH_OPTS) ubuntu@$(FRONT_IP)
ARENA_SSH = ssh $(SSH_OPTS) ubuntu@$(ARENA_IP)
AI_SSH    = ssh $(SSH_OPTS) ubuntu@$(AI_IP)

COMPOSE = docker compose -f deploy/front/docker-compose.prod.yml --env-file deploy/front/.env

# Attente maximale d'un provisionnement, en secondes. Au-dela, on echoue au
# lieu de boucler : le matin du 23 octobre, une boucle infinie silencieuse est
# pire qu'une erreur.
WAIT_TIMEOUT ?= 1800

.PHONY: menu
menu: ## Lanceur interactif : demande ce que tu veux et lance le make correspondant
	@./nctf

.PHONY: presel-window
presel-window: ## Affiche/pose la fenetre de la preselection (ven 23 oct 19h -> lun 26 oct 00h) ; APPLY=1 pour l'appliquer
	@./preselection-window.sh $(if $(APPLY),--apply) $(if $(URL),--url $(URL))

.PHONY: help
help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
	  | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

# --- Preparatifs ------------------------------------------------------------

.PHONY: init
init: ## Initialise Terraform (une fois). Utilise l'etat distant si backend.hcl existe.
	@if [ -f terraform/backend.tf ]; then \
	   if [ ! -f terraform/backend.hcl ]; then \
	     echo "ERREUR : backend.tf present mais backend.hcl manquant -> l'init S3 serait interactif."; \
	     echo "  Genere-le : terraform -chdir=terraform/bootstrap output -raw backend_hcl > terraform/backend.hcl"; \
	     exit 1; \
	   fi; \
	   echo "Etat distant (backend.hcl) -> init S3 verrouille."; \
	   $(TF) init -backend-config=backend.hcl; \
	 else \
	   echo "Etat LOCAL (pas de backend.tf). Pour l'etat distant : make state-bootstrap."; \
	   $(TF) init; \
	 fi

.PHONY: state-bootstrap
# Le bootstrap a ses propres variables : si tu surcharges project_name / aws_region
# dans terraform/terraform.tfvars, passe les MEMES valeurs ici, sinon le bucket
# d'etat portera un nom different des ressources deployees.
#   make state-bootstrap PROJECT_NAME=monctf AWS_REGION=eu-west-1
PROJECT_NAME ?= ctf
AWS_REGION   ?= eu-west-3
state-bootstrap: ## (une fois) Cree le bucket S3 d'etat + la table de verrou DynamoDB
	terraform -chdir=terraform/bootstrap init
	terraform -chdir=terraform/bootstrap apply \
	  -var 'project_name=$(PROJECT_NAME)' -var 'aws_region=$(AWS_REGION)'
	@echo; echo "=== Etat distant provisionne. Pour l'activer : ==="; \
	 echo "  1. cp terraform/backend.tf.example terraform/backend.tf"; \
	 echo "  2. terraform -chdir=terraform/bootstrap output -raw backend_hcl > terraform/backend.hcl"; \
	 echo "  3. make init   (repondre 'yes' pour migrer l'etat local vers S3)"

.PHONY: check-gpu-quota
check-gpu-quota: ## Verifie le quota GPU AWS (repli ollama uniquement ; refuse pour NCTF26, non requis en bedrock).
	@REGION=$$($(TF) output -raw aws_region 2>/dev/null); REGION=$${REGION:-eu-west-3}; \
	 echo "Quota 'Running On-Demand G and VT instances' dans $$REGION :"; \
	 V=$$(aws service-quotas get-service-quota --region "$$REGION" \
	      --service-code ec2 --quota-code L-DB2E81BA \
	      --query 'Quota.Value' --output text 2>/dev/null) || \
	   { echo "  (AWS CLI indisponible ou non configuree)"; exit 1; }; \
	 echo "  $$V vCPU"; \
	 echo; \
	 if awk -v v="$$V" 'BEGIN{exit (v>=4)?0:1}'; then \
	   echo "OK : une g4dn.xlarge (4 vCPU) tient dans ce quota."; \
	 else \
	   echo "INSUFFISANT. Une g4dn.xlarge consomme 4 vCPU de ce quota."; \
	   echo "Demandez une augmentation a >= 8 des maintenant :"; \
	   echo "  https://$$REGION.console.aws.amazon.com/servicequotas/home/services/ec2/quotas/L-DB2E81BA"; \
	   echo "Le traitement prend souvent plusieurs jours ouvres."; \
	   exit 1; \
	 fi

.PHONY: request-gpu-quota
request-gpu-quota: ## Demande l'augmentation du quota GPU (repli ollama seulement ; inutile tant qu'on reste en bedrock).
	@REGION=$$($(TF) output -raw aws_region 2>/dev/null); REGION=$${REGION:-eu-west-3} ./scripts/aws_gpu_quota.sh

.PHONY: free-credits
free-credits: ## Plan gratuit AWS : fait les 5 activites "Earn AWS credits" (Budgets, EC2, Bedrock, Lambda, RDS) puis nettoie. BUDGET_EMAIL=... pour l'alerte
	@REGION=$$($(TF) output -raw aws_region 2>/dev/null); REGION=$${REGION:-eu-west-3} ./scripts/aws_free_credits.sh

# --- Phases -----------------------------------------------------------------

.PHONY: phase-setup
phase-setup: ## Front seul : preparer les challenges, ouvrir les inscriptions
	$(TF) apply -var 'phase=setup'
	@$(MAKE) --no-print-directory wait-front deploy
	@$(TF) output -raw dns_action_required; echo

.PHONY: phase-preselection
phase-preselection: ## 23-25 oct : front + arena (IA via Bedrock, sans noeud), ~300 joueurs
	$(TF) apply -var 'phase=preselection'
	@$(MAKE) --no-print-directory wait-front deploy wait-nodes link
	@$(TF) output -raw dns_action_required; echo

.PHONY: phase-final
phase-final: ## 29-30 oct : front + arena (IA via Bedrock, sans noeud), ~50 joueurs
	$(TF) apply -var 'phase=final'
	@$(MAKE) --no-print-directory wait-front deploy wait-nodes link
	@$(TF) output -raw dns_action_required; echo

.PHONY: season-down
season-down: ## Fin de phase : archive, sauvegarde VERIFIEE, puis detruit l'EC2
	@echo ">> Sauvegarde et archivage avant destruction"
	@$(MAKE) --no-print-directory backup archive
	@echo
	@echo ">> Sauvegarde verifiee. Destruction des instances."
	$(TF) apply -var 'phase=off'
	@echo
	@echo "Toutes les instances sont detruites. Seules les archives S3 subsistent."
	@echo "Archives : $$($(TF) output -raw archive_site_url)"

# --- Attentes ---------------------------------------------------------------

.PHONY: wait-front
wait-front: ## Attend la fin du provisionnement du front
	@echo -n "Attente du front ($(FRONT_IP)) "
	@deadline=$$(( $$(date +%s) + $(WAIT_TIMEOUT) )); \
	 until $(FRONT_SSH) 'test -f /var/lib/cloud/ctfd-front-provisioned' 2>/dev/null; do \
	   if [ $$(date +%s) -gt $$deadline ]; then \
	     echo " ECHEC"; \
	     echo "Le front n'est pas provisionne apres $(WAIT_TIMEOUT)s."; \
	     echo "Diagnostiquer : make ssh-front puis 'sudo cat /var/log/cloud-init-output.log'"; \
	     exit 1; \
	   fi; \
	   printf '.'; sleep 10; \
	 done; echo " pret."

.PHONY: wait-nodes
wait-nodes: ## Attend l'arena (et, en repli ollama, le noeud IA) avec delai maximal
	@echo -n "Attente de l'arena ($(ARENA_IP)) "
	@deadline=$$(( $$(date +%s) + $(WAIT_TIMEOUT) )); \
	 until $(ARENA_SSH) 'test -f /var/lib/cloud/ctfd-arena-provisioned' 2>/dev/null; do \
	   if [ $$(date +%s) -gt $$deadline ]; then \
	     echo " ECHEC"; echo "Diagnostiquer : make ssh-arena puis 'sudo cat /var/log/cloud-init-output.log'"; exit 1; \
	   fi; \
	   printf '.'; sleep 10; \
	 done; echo " pret."
	@$(ARENA_SSH) 'cat /var/log/challenge-images.log' || true
	@if [ -z "$(AI_IP)" ]; then \
	   echo "Noeud IA : aucun (ai_backend = $(AI_BACKEND)) ; la passerelle du front interroge Bedrock."; \
	   exit 0; \
	 fi; \
	 echo -n "Attente du noeud IA ($(AI_IP)), telechargement du modele "; \
	 deadline=$$(( $$(date +%s) + $(WAIT_TIMEOUT) )); \
	 until $(AI_SSH) 'test -f /var/lib/cloud/ctfd-ai-provisioned' 2>/dev/null; do \
	   if [ $$(date +%s) -gt $$deadline ]; then \
	     echo " ECHEC"; \
	     echo "Le noeud IA n'a pas valide ses controles (GPU, bind reseau, modele)."; \
	     echo "Diagnostiquer : make ssh-ai puis 'sudo cat /var/log/cloud-init-output.log'"; \
	     exit 1; \
	   fi; \
	   printf '.'; sleep 15; \
	 done; echo " pret."; \
	 $(AI_SSH) 'nvidia-smi --query-gpu=name,memory.used,memory.total --format=csv'

.PHONY: arena-build-images
arena-build-images: ## Construit des images de challenge SUR l'arena (rsync des sources) : ONLY="web/x pwn/y" ou MISSING=1 ; PUSH=1 = aussi vers S3
	@ARENA_IP=$(ARENA_IP) BUCKET=$(BUCKET) SSH_OPTS="$(SSH_OPTS)" PUSH=$(PUSH) \
	  scripts/arena-build-images.sh $(if $(MISSING),--missing) $(ONLY)

.PHONY: arena-koth
arena-koth: ## King of the Hill sur AWS : collines sur l'arena + tunnel frps (ports 28490-28493) + plugin CTFd. STATUS=1 / DOWN=1
	@FRONT_IP=$(FRONT_IP) FRONT_PRIV=$(FRONT_PRIV) ARENA_IP=$(ARENA_IP) BUCKET=$(BUCKET) SSH_OPTS="$(SSH_OPTS)" \
	  scripts/arena-koth.sh $(if $(STATUS),--status)$(if $(DOWN),--down)

.PHONY: refresh-fronts
refresh-fronts: ## Rebuild+relance des fronts web (11 servis + colline reseau-fortune :28493) apres MAJ du depot. SERVED=1/KOTH=1 pour cibler ; RECREATE=1 recree les instances servies en cours ; STATUS=1 ; PUSH=1 = aussi vers S3
	@ARENA_IP=$(ARENA_IP) BUCKET=$(BUCKET) SSH_OPTS="$(SSH_OPTS)" PUSH=$(PUSH) \
	  scripts/refresh-fronts.sh $(if $(SERVED),--served-only)$(if $(KOTH), --koth-only)$(if $(RECREATE), --recreate-served)$(if $(STATUS), --status)

.PHONY: check-arena
check-arena: ## Liste les images de challenge reellement presentes sur l'arena
	@$(ARENA_SSH) 'docker image ls --format "{{.Repository}}:{{.Tag}}" | sort'
	@echo
	@n=$$($(ARENA_SSH) 'docker image ls --format "{{.Repository}}" | grep -c "^ctf-" || true'); \
	 if [ "$$n" -lt 1 ]; then \
	   echo "AUCUNE image de challenge (ctf-*) sur l'arena. L'instancier ne pourra rien lancer."; \
	   echo "Poussez-les avec 'make push-images' puis relancez la phase."; \
	   exit 1; \
	 fi

# --- Deploiement ------------------------------------------------------------

.PHONY: deploy
deploy: ## Deploie/met a jour CTFd sur le front (envoie front/.env au premier deploiement)
	@test -f front/.env || { echo "ERREUR : creez deploy/front/.env (voir .env.example)"; exit 1; }
	$(FRONT_SSH) 'set -euo pipefail; \
	  if [ ! -d /opt/ctfd/CTFd ]; then \
	    git clone --branch $(REPO_BRANCH) $(REPO_URL) /opt/ctfd/CTFd; \
	  else \
	    cd /opt/ctfd/CTFd && git fetch origin $(REPO_BRANCH) && git checkout $(REPO_BRANCH) && git pull origin $(REPO_BRANCH); \
	  fi'
	@if ! $(FRONT_SSH) 'test -f /opt/ctfd/CTFd/deploy/front/.env'; then \
	   echo ">> Premier deploiement : envoi de front/.env sur le front (les prochains 'make link' le completent sur place)"; \
	   scp $(SSH_OPTS) front/.env ubuntu@$(FRONT_IP):/opt/ctfd/CTFd/deploy/front/.env; \
	 fi
	$(FRONT_SSH) 'cd /opt/ctfd/CTFd && BACKUP_BUCKET=$(BUCKET) deploy/scripts/front-update.sh $(REPO_BRANCH)'

.PHONY: tls-init
tls-init: ## Emet le certificat Let's Encrypt et bascule nginx en HTTPS
	@echo ">> Verification que le domaine pointe bien sur ce front"
	@$(FRONT_SSH) 'set -euo pipefail; cd /opt/ctfd/CTFd; \
	  set -a; . deploy/front/.env; set +a; \
	  test -n "$$CTF_DOMAIN" || { echo "ERREUR : CTF_DOMAIN vide dans .env"; exit 1; }; \
	  test -n "$$CERTBOT_EMAIL" || { echo "ERREUR : CERTBOT_EMAIL vide dans .env"; exit 1; }; \
	  resolved=$$(getent hosts "$$CTF_DOMAIN" | awk "{print \$$1}" | head -1); \
	  echo "  $$CTF_DOMAIN -> $$resolved (attendu : $(FRONT_IP))"; \
	  test "$$resolved" = "$(FRONT_IP)" || { \
	    echo "ERREUR : le domaine ne pointe pas sur ce front. Let'"'"'s Encrypt echouerait"; \
	    echo "et brulerait un essai sur le quota horaire. Corrigez le DNS d'"'"'abord."; exit 1; }'
	@echo ">> Emission du certificat"
	@$(FRONT_SSH) 'set -euo pipefail; cd /opt/ctfd/CTFd; \
	  set -a; . deploy/front/.env; set +a; \
	  $(COMPOSE) run --rm --entrypoint certbot certbot certonly \
	    --webroot -w /var/www/certbot \
	    -d "$$CTF_DOMAIN" --email "$$CERTBOT_EMAIL" \
	    --agree-tos --no-eff-email --non-interactive'
	@echo ">> Bascule de nginx en HTTPS"
	@$(FRONT_SSH) 'set -euo pipefail; cd /opt/ctfd/CTFd; \
	  set -a; . deploy/front/.env; set +a; \
	  sed "s|__CTF_DOMAIN__|$$CTF_DOMAIN|g" deploy/front/nginx/tls.conf.template \
	    > deploy/front/nginx/active.conf; \
	  $(COMPOSE) exec -T nginx nginx -t || { \
	    echo "ERREUR : configuration nginx invalide, retour au HTTP"; \
	    cp deploy/front/nginx/bootstrap.conf deploy/front/nginx/active.conf; \
	    $(COMPOSE) restart nginx; exit 1; }; \
	  $(COMPOSE) restart nginx'
	@echo ">> Verification depuis l'exterieur"
	@curl -fsS -o /dev/null -w "  HTTPS %{http_code}, redirection HTTP -> %{redirect_url}\n" \
	  "https://$$($(FRONT_SSH) 'cd /opt/ctfd/CTFd && . deploy/front/.env && echo $$CTF_DOMAIN')/" \
	  && echo "TLS actif."

.PHONY: tls-cloudflare
tls-cloudflare: ## TLS derriere le proxy Cloudflare (certificat d'origine + Full strict). CF_API_TOKEN=... requis. Remplace tls-init quand le domaine est proxifie
	@test -n "$$CF_API_TOKEN" || { echo "CF_API_TOKEN manquant (jeton API Cloudflare, jamais dans git)"; exit 2; }
	@set -a; . ./front/.env; set +a; FRONT_IP=$(FRONT_IP) ./scripts/cloudflare-origin-tls.sh

.PHONY: link
link: ## Relie le front a l'arena (et au noeud IA en repli ollama), ecrit AI_BACKEND/AI_BEDROCK_* et verifie la passerelle IA
	@echo ">> Cle de service deposee sur l'arena"
	@PUBKEY=$$($(FRONT_SSH) 'cat ~/.ssh/id_ed25519_arena.pub'); \
	 test -n "$$PUBKEY" || { echo "ERREUR : cle publique introuvable sur le front"; exit 1; }; \
	 $(ARENA_SSH) "grep -qF \"$$PUBKEY\" ~/.ssh/authorized_keys || echo \"$$PUBKEY\" >> ~/.ssh/authorized_keys"
	@echo ">> Cle privee et empreinte d'hote installees pour le tunnel Docker"
	@$(FRONT_SSH) 'set -euo pipefail; cd /opt/ctfd/CTFd; \
	  install -d -m 700 deploy/front/ssh; \
	  install -m 600 ~/.ssh/id_ed25519_arena deploy/front/ssh/id_ed25519; \
	  ssh-keyscan -H $(ARENA_PRIV) > deploy/front/ssh/known_hosts 2>/dev/null; \
	  test -s deploy/front/ssh/known_hosts || { echo "ERREUR : ssh-keyscan n'"'"'a rien renvoye"; exit 1; }'
	@echo ">> Jeton frp injecte sur l'arena et instancier configure sur le front"
	@TOKEN=$$($(FRONT_SSH) 'sudo cat /etc/frp/token'); \
	 test -n "$$TOKEN" || { echo "ERREUR : jeton frp vide cote front"; exit 1; }; \
	 FRPADMIN=$$(openssl rand -hex 16); \
	 $(ARENA_SSH) "sudo sed -i -e \"s|^auth.token = .*|auth.token = \\\"$$TOKEN\\\"|\" -e \"s|^webServer.password = .*|webServer.password = \\\"$$FRPADMIN\\\"|\" /etc/frp/frpc.toml && sudo systemctl restart frpc"; \
	 sleep 2; \
	 $(ARENA_SSH) 'systemctl is-active --quiet frpc' \
	   || { echo "ERREUR : frpc n'a pas demarre. 'make ssh-arena' puis 'journalctl -u frpc'"; exit 1; }; \
	 case "$(PHASE)" in \
	   preselection) W=4; POOL=1G ;; \
	   *)            W=2; POOL=256M ;; \
	 esac; \
	 $(FRONT_SSH) "cd /opt/ctfd/CTFd && \
	   set -e; \
	   upsert() { grep -q \"^\$$1=\" deploy/front/.env && sed -i \"s|^\$$1=.*|\$$1=\$$2|\" deploy/front/.env || echo \"\$$1=\$$2\" >> deploy/front/.env; }; \
	   upsert AI_BACKEND $(AI_BACKEND); \
	   upsert OLLAMA_URL '$(if $(AI_PRIV),http://$(AI_PRIV):11434,)'; \
	   upsert AI_BEDROCK_MODELS '$(BEDROCK_MODELS)'; \
	   upsert AI_BEDROCK_CHAT_MODELS '$(BEDROCK_CHAT)'; \
	   upsert AWS_REGION $(REGION); \
	   upsert AI_PROXY_URL http://$(FRONT_PRIV):8600; \
	   upsert ARENA_HOST $(ARENA_PRIV); \
	   upsert DOCKER_HOST tcp://dockerproxy:2375; \
	   upsert WORKERS $$W; \
	   upsert INNODB_POOL $$POOL; \
	   upsert FRONT_PUBLIC_IP $(FRONT_IP); \
	   upsert FRPC_ADMIN_ADDR dockerproxy:7400; \
	   upsert FRPC_ADMIN_PASSWORD $$FRPADMIN; \
	   upsert WHALE_PORT_RANGE_START $(WHALE_PORT_START); \
	   upsert WHALE_PORT_RANGE_END $(WHALE_PORT_END); \
	   $(COMPOSE) --profile arena up -d --build"
	@echo ">> Verification du canal Docker vers l'arena"
	@$(FRONT_SSH) 'cd /opt/ctfd/CTFd && $(COMPOSE) exec -T ctfd python -c "\
import os, urllib.request, json; \
u = os.environ[\"DOCKER_HOST\"].replace(\"tcp://\", \"http://\") + \"/version\"; \
print(\"  Docker arena :\", json.load(urllib.request.urlopen(u, timeout=10))[\"Version\"])"' \
	  || { echo "ECHEC : CTFd ne joint pas le Docker de l'arena. L'instancier ne marchera pas."; exit 1; }
	@echo ">> Verification du canal IA (passerelle front:8600 -> $(AI_BACKEND))"
	@$(FRONT_SSH) 'sleep 3; python3 -c "\
import urllib.request, json; \
r = json.load(urllib.request.urlopen(\"http://127.0.0.1:8600/api/tags\", timeout=20)); \
print(\"  Backend :\", r.get(\"backend\"), \"| modeles :\", [m[\"name\"] for m in r[\"models\"]])"' \
	  || { echo "ECHEC : la passerelle IA ne repond pas ($(AI_BACKEND)). Les challenges IA ne marcheront pas."; \
	       echo "Diagnostiquer : make logs (service ai-gateway) ; backend bedrock : make check-bedrock."; exit 1; }
	@echo
	@$(TF) output -raw cost_note; echo

# --- Exploitation -----------------------------------------------------------

.PHONY: backup
backup: ## Sauvegarde la base, VERIFIE le dump, puis l'envoie dans S3
	@mkdir -p backups
	@STAMP=$$(date +%Y%m%d-%H%M%S); \
	 OUT=backups/ctfd-$(PHASE)-$$STAMP.sql.gz; \
	 TMP=$$OUT.partial; \
	 echo ">> Dump de la base"; \
	 $(FRONT_SSH) 'set -euo pipefail; cd /opt/ctfd/CTFd && $(COMPOSE) exec -T db sh -c \
	   "mariadb-dump -uroot -p\$$MARIADB_ROOT_PASSWORD --single-transaction --routines ctfd" | gzip' \
	   > $$TMP; \
	 echo ">> Verification de l'archive"; \
	 gzip -t $$TMP || { echo "ECHEC : archive corrompue"; rm -f $$TMP; exit 1; }; \
	 SIZE=$$(stat -c%s $$TMP); \
	 test "$$SIZE" -gt 10000 \
	   || { echo "ECHEC : dump de $$SIZE octets, manifestement vide ou tronque"; rm -f $$TMP; exit 1; }; \
	 zcat $$TMP | grep -c 'CREATE TABLE `users`' >/dev/null \
	   || { echo "ECHEC : la table users est absente du dump"; rm -f $$TMP; exit 1; }; \
	 ROWS=$$(zcat $$TMP | grep -c 'INSERT INTO' || true); \
	 mv $$TMP $$OUT; \
	 echo "  $$OUT : $$SIZE octets, $$ROWS instructions INSERT"; \
	 echo ">> Envoi dans S3"; \
	 aws s3 cp $$OUT s3://$(BUCKET)/backups/ --only-show-errors \
	   || { echo "ECHEC : envoi S3 impossible. La sauvegarde locale est dans $$OUT."; exit 1; }; \
	 echo "  s3://$(BUCKET)/backups/$$(basename $$OUT)"
	@echo ">> Export du journal de la passerelle IA (si present)"
	@$(FRONT_SSH) 'cd /opt/ctfd/CTFd && $(COMPOSE) exec -T ai-gateway sh -c "cat /var/log/ai-gateway/attempts.jsonl 2>/dev/null" | gzip' \
	  > backups/ai-attempts-$(PHASE)-$$(date +%Y%m%d-%H%M%S).jsonl.gz 2>/dev/null; \
	 f=$$(ls -t backups/ai-attempts-*.jsonl.gz 2>/dev/null | head -1); \
	 if [ -n "$$f" ] && [ $$(stat -c%s "$$f") -gt 30 ]; then \
	   aws s3 cp "$$f" s3://$(BUCKET)/backups/ --only-show-errors && echo "  journal IA -> S3"; \
	 else echo "  (pas de journal IA a exporter)"; rm -f "$$f" 2>/dev/null; fi

.PHONY: backup-status
backup-status: ## Etat de la sauvegarde automatique du front (timer, dernier dump, S3)
	@$(FRONT_SSH) 'systemctl list-timers ctfd-backup.timer --no-pager | head -2; echo; \
	  test -f /opt/ctfd/backups/status.json && python3 -c "import json,time; d=json.load(open(\"/opt/ctfd/backups/status.json\")); \
	  age=lambda t: (\"il y a %d min\" % ((time.time()-t)//60)) if t else \"jamais\"; \
	  print(\"dernier passage :\", age(d.get(\"last_run\")), \"OK\" if d.get(\"ok\") else \"ECHEC: \"+str(d.get(\"error\"))); \
	  print(\"dernier dump OK :\", age(d.get(\"last_ok\")), d.get(\"file\",\"\"), d.get(\"size\",0), \"octets, s3=%s\" % d.get(\"s3\")); \
	  print(\"derniers extras  :\", age(d.get(\"last_extra\")))" || echo "aucun status.json : le timer n a jamais tourne"; \
	  echo; ls -1t /opt/ctfd/backups/ 2>/dev/null | head -8'

.PHONY: backup-now
backup-now: ## Force un passage de la sauvegarde automatique sur le front (dump + extras)
	$(FRONT_SSH) 'sudo -u ubuntu CTFD_REPO=/opt/ctfd/CTFd /opt/ctfd/CTFd/deploy/scripts/backup.sh --force --extras'

.PHONY: restore
restore: ## Restaure une sauvegarde sur le front (FILE=backups/...sql.gz)
	@test -n "$(FILE)" || { echo "Usage : make restore FILE=backups/ctfd-....sql.gz"; \
	  echo; echo "Sauvegardes disponibles dans S3 (manuelles, puis auto/ toutes les 15 min, daily/ une par jour) :"; \
	  aws s3 ls s3://$(BUCKET)/backups/ || true; aws s3 ls s3://$(BUCKET)/backups/auto/ | tail -5 || true; exit 1; }
	@test -f "$(FILE)" || { echo "Fichier introuvable : $(FILE)"; exit 1; }
	@gzip -t "$(FILE)" || { echo "Archive corrompue"; exit 1; }
	@echo "Cette commande ECRASE la base actuelle du front."
	@read -p "Taper 'restaurer' pour confirmer : " ans; [ "$$ans" = "restaurer" ] || exit 1
	@gzip -dc "$(FILE)" | $(FRONT_SSH) 'set -euo pipefail; cd /opt/ctfd/CTFd && \
	  $(COMPOSE) exec -T db sh -c "mariadb -uroot -p\$$MARIADB_ROOT_PASSWORD ctfd"'
	@$(FRONT_SSH) 'cd /opt/ctfd/CTFd && $(COMPOSE) restart ctfd'
	@echo "Restauration terminee."

.PHONY: archive
archive: ## Fige le scoreboard de la phase dans S3, en page autonome
	@echo ">> Recuperation des donnees du scoreboard"
	@PREFIX=$(PHASE)-$$(date +%Y%m%d); \
	 mkdir -p /tmp/ctf-archive; \
	 $(FRONT_SSH) 'curl -sf http://localhost/api/v1/scoreboard' > /tmp/ctf-archive/scoreboard.json \
	   || { echo "ECHEC : l'API scoreboard ne repond pas"; exit 1; }; \
	 test -s /tmp/ctf-archive/scoreboard.json \
	   || { echo "ECHEC : scoreboard vide"; exit 1; }; \
	 $(FRONT_SSH) 'curl -sf http://localhost/api/v1/challenges' > /tmp/ctf-archive/challenges.json || true; \
	 if [ "$${WRITEUPS:-1}" = "1" ]; then \
	   $(LOCAL_PY) scripts/publish_writeups.py --static /tmp/ctf-archive/writeups \
	     || { echo "ECHEC du rendu des writeups (WRITEUPS=0 pour archiver sans)"; exit 1; }; \
	 fi; \
	 python3 scripts/render_archive.py /tmp/ctf-archive "$$PREFIX" \
	   || { echo "ECHEC du rendu de l'archive"; exit 1; }; \
	 echo ">> Publication"; \
	 aws s3 sync /tmp/ctf-archive s3://$(BUCKET)/site/$$PREFIX/ --only-show-errors \
	   || { echo "ECHEC : publication S3 impossible"; exit 1; }; \
	 python3 scripts/render_index.py $(BUCKET) \
	   && aws s3 cp /tmp/ctf-site-index.html s3://$(BUCKET)/site/index.html --only-show-errors; \
	 echo "  $$($(TF) output -raw archive_site_url)/$$PREFIX/"

TOKEN ?= $(CTFD_TOKEN)

.PHONY: reglement-publish
reglement-publish: ## Publie deploy/reglement.md dans la page /tos de la plateforme : URL=https://... CTFD_TOKEN=...
	@test -n "$(URL)" -a -n "$$CTFD_TOKEN" || { echo "URL et CTFD_TOKEN (jeton API admin) requis"; exit 2; }
	@python3 -c 'import json,sys; print(json.dumps({"tos_text": open("reglement.md", encoding="utf-8").read()}))' \
	  | curl -sf -H "Authorization: Token $$CTFD_TOKEN" -H "Content-Type: application/json" \
	      -X PATCH "$(URL)/api/v1/configs" -d @- >/dev/null \
	  && echo "Reglement publie : $(URL)/tos" || { echo "ECHEC de la publication"; exit 1; }

.PHONY: anticheat-report
anticheat-report: ## Exporte les deux rapports anti-triche (incidents team_hmac + validations synchrones) : URL=... CTFD_TOKEN=... [WINDOW=300 MIN=3]
	@test -n "$(URL)" -a -n "$$CTFD_TOKEN" || { echo "URL et CTFD_TOKEN (jeton API admin) requis"; exit 2; }
	@D=reports/$$(date -u +%Y%m%dT%H%MZ); mkdir -p $$D; \
	 H="Authorization: Token $$CTFD_TOKEN"; J="Content-Type: application/json"; \
	 curl -sf -H "$$H" -H "$$J" "$(URL)/plugins/anticheat/api/incidents?format=csv" -o $$D/incidents.csv \
	   || { echo "ECHEC : incidents"; exit 1; }; \
	 curl -sf -H "$$H" -H "$$J" "$(URL)/plugins/anticheat/api/sync?format=csv&window=$${WINDOW:-300}&min=$${MIN:-3}" -o $$D/sync.csv \
	   || { echo "ECHEC : validations synchrones"; exit 1; }; \
	 curl -sf -H "$$H" -H "$$J" "$(URL)/plugins/anticheat/api/sync?window=$${WINDOW:-300}&min=$${MIN:-3}" -o $$D/sync.json; \
	 sha256sum $$D/*.csv $$D/*.json > $$D/SHA256SUMS; \
	 echo "Rapports dans $$D ($$(($$(wc -l < $$D/incidents.csv)-1)) incidents, $$(($$(wc -l < $$D/sync.csv)-1)) paires) ; empreintes dans SHA256SUMS -- a archiver avec le dump de cloture"

.PHONY: writeups-prepare
writeups-prepare: ## Cree/met a jour les pages writeups en BROUILLON (404 joueurs) : URL=https://... TOKEN=<jeton admin>
	@test -n "$(URL)" -a -n "$(TOKEN)" || { echo "URL et TOKEN (jeton API admin) requis"; exit 2; }
	$(LOCAL_PY) scripts/publish_writeups.py --url $(URL) --token $(TOKEN) --prepare $(WRITEUPS_ARGS)

.PHONY: writeups-publish
writeups-publish: ## Publie /writeups a la cloture (refuse tant que `end` n'est pas passe ; FORCE=1 pour passer outre)
	@test -n "$(URL)" -a -n "$(TOKEN)" || { echo "URL et TOKEN (jeton API admin) requis"; exit 2; }
	$(LOCAL_PY) scripts/publish_writeups.py --url $(URL) --token $(TOKEN) --publish $(if $(FORCE),--force) $(WRITEUPS_ARGS)

.PHONY: writeups-unpublish
writeups-unpublish: ## Remet les writeups en brouillon
	@test -n "$(URL)" -a -n "$(TOKEN)" || { echo "URL et TOKEN (jeton API admin) requis"; exit 2; }
	$(LOCAL_PY) scripts/publish_writeups.py --url $(URL) --token $(TOKEN) --unpublish $(WRITEUPS_ARGS)

# Sur le DISQUE, pas /tmp : /tmp est souvent un tmpfs en RAM (9,8 Go ici) et
# une centaine de tars d'images (~10 Go) le remplit -> "no space left on device".
IMAGES_DIR ?= /var/tmp/ctf-images

.PHONY: push-images
push-images: ## Envoie les images de challenge dans S3 (lues depuis l'arena au prochain demarrage) ; IMAGES_DIR=/var/tmp/ctf-images
	@test -d ../challenges || { echo "Aucun dossier challenges/ a la racine du depot"; exit 1; }
	@mkdir -p $(IMAGES_DIR)
	@for img in $$(docker image ls --format '{{.Repository}}:{{.Tag}}' | grep '^ctf-' || true); do \
	   name=$$(echo "$$img" | tr '/:' '__'); \
	   echo "  $$img -> $$name.tar"; \
	   docker save "$$img" -o $(IMAGES_DIR)/$$name.tar; \
	 done
	@ls $(IMAGES_DIR)/*.tar >/dev/null 2>&1 \
	  || { echo "Aucune image nommee ctf-* trouvee localement"; exit 1; }
	@AWS_MAX_ATTEMPTS=10 AWS_RETRY_MODE=adaptive aws s3 sync $(IMAGES_DIR) s3://$(BUCKET)/images/ --only-show-errors
	@echo "Images publiees. Elles seront chargees au prochain demarrage de l'arena."

.PHONY: logs
.PHONY: preflight
preflight: ## Check-list de prod sur le front : PHASE=preselection|finale, CTFD_TOKEN=<jeton admin>. Doit etre vert avant make phase-*
	@test -n "$$CTFD_TOKEN" || { echo "CTFD_TOKEN manquant (jeton API admin : Settings > Access Tokens)"; exit 2; }
	@URL="$${URL:-https://$$($(FRONT_SSH) 'cd /opt/ctfd/CTFd && . deploy/front/.env && echo $$CTF_DOMAIN')}"; \
	 $(FRONT_SSH) 'cd /opt/ctfd/CTFd && $(COMPOSE) exec -T ctfd printenv' | \
	 CTFD_URL="$$URL" $(LOCAL_PY) scripts/preflight.py $(PREFLIGHT_ARGS)

.PHONY: mail-test
mail-test: ## [front] Prouve l'envoi SMTP AVANT verify_emails=ON. TO=destinataire@exemple.com
	@test -n "$(TO)" || { echo "TO manquant : make mail-test TO=toi@exemple.com"; exit 2; }
	@echo ">> Envoi d'un e-mail de test via le SMTP du conteneur ctfd (MAIL_* de front/.env)"
	$(FRONT_SSH) 'cd /opt/ctfd/CTFd && $(COMPOSE) exec -T ctfd python3 - "$(TO)"' < scripts/mail-test.py

ai-audit: ## Audit resistance au solve IA des challenges : defaut heuristique (hors-ligne) ; MODEL=https://.../v1 ou OLLAMA=http://.. + MODEL_NAME=<fort> pour la verite terrain. OUT=audit.csv
	$(LOCAL_PY) scripts/ai_resistance_audit.py \
	  $(if $(MODEL),--model $(MODEL)) $(if $(OLLAMA),--ollama $(OLLAMA)) \
	  $(if $(MODEL_NAME),--model-name $(MODEL_NAME)) \
	  $(if $(OUT),--out $(OUT))

scaffold-backlog: ## Stampe les squelettes SERVIS du backlog (deploy/served-backlog.yml) — STUBS caches, a implementer
	$(LOCAL_PY) scripts/scaffold_served.py --manifest served-backlog.yml

writeups-sync: ## (Re)genere writeups/<cat>/<slug>.md depuis les solution/README.md (lu par le plugin writeups) ; PRUNE=1 pour retirer les orphelins
	$(LOCAL_PY) scripts/sync_writeups.py $(if $(PRUNE),--prune)
	@command -v prettier >/dev/null 2>&1 && prettier --write '../writeups/**/*.md' >/dev/null 2>&1 || true
	@echo "writeups/ synchronise. Plugin: /plugins/writeups/ (toggle admin: /plugins/writeups/admin)"

logs: ## Suit les logs du front
	$(FRONT_SSH) 'cd /opt/ctfd/CTFd && $(COMPOSE) logs -f --tail=100'

.PHONY: gpu
gpu: ## Etat du GPU et des requetes Ollama en cours (backend bedrock : compteurs du pool)
	@if [ -z "$(AI_IP)" ]; then \
	   echo "Pas de noeud GPU (ai_backend = $(AI_BACKEND)). Compteurs de la passerelle :"; \
	   $(FRONT_SSH) 'curl -s http://127.0.0.1:8600/metrics'; echo; \
	 else \
	   $(AI_SSH) 'nvidia-smi; echo; curl -s http://127.0.0.1:11434/api/ps'; \
	 fi

.PHONY: check-bedrock
check-bedrock: ## Backend IA par defaut : verifie depuis le poste que chaque modele du pool Bedrock repond (chat + appel d'outil)
	@REGION=$${REGION:-$(REGION)}; REGION=$${REGION:-eu-west-3}; \
	 MODELS="$${MODELS:-$(BEDROCK_MODELS)}"; \
	 test -n "$$MODELS" || MODELS="eu.amazon.nova-lite-v1:0=20,eu.amazon.nova-micro-v1:0=20,eu.amazon.nova-pro-v1:0=25,eu.amazon.nova-2-lite-v1:0=20"; \
	 TOOLS='{"tools":[{"toolSpec":{"name":"read_ticket","description":"Read a ticket","inputSchema":{"json":{"type":"object","properties":{"id":{"type":"string"}},"required":["id"]}}}}]}'; \
	 fail=0; \
	 for entry in $${MODELS//,/ }; do m=$${entry%%=*}; \
	   printf '%-45s ' "$$m"; \
	   out=$$(aws bedrock-runtime converse --region $$REGION --model-id $$m \
	     --system '[{"text":"You are HELM. Use tools when asked."}]' \
	     --messages '[{"role":"user","content":[{"text":"Read ticket TCK-1002 with your tool."}]}]' \
	     --tool-config "$$TOOLS" --inference-config '{"maxTokens":120}' \
	     --query 'stopReason' --output text 2>&1 | tail -1); \
	   case "$$out" in tool_use) echo "OK (appel d'outil)";; *) echo "ECHEC : $$out"; fail=1;; esac; \
	 done; \
	 echo; echo "Quotas Bedrock (req/min) dans $$REGION :"; \
	 aws service-quotas list-service-quotas --service-code bedrock --region $$REGION \
	   --query 'Quotas[?contains(QuotaName, `requests per minute`) && (contains(QuotaName, `Nova`) || contains(QuotaName, `Haiku 4.5`) || contains(QuotaName, `Mistral 7B`))].[Value,Adjustable,QuotaName]' \
	   --output text | sort -rn | sed 's/^/  /'; \
	 test $$fail -eq 0 || { echo "Un modele du pool ne repond pas : le retirer de bedrock_models (terraform.tfvars)."; exit 1; }

.PHONY: cost
cost: ## Rappelle ce qui est facture en ce moment
	@$(TF) output -raw cost_note; echo

.PHONY: ssh-front
ssh-front: ## Shell sur le front
	$(FRONT_SSH)

.PHONY: ssh-arena
ssh-arena: ## Shell sur l'arena
	$(ARENA_SSH)

.PHONY: ssh-ai
ssh-ai: ## Shell sur le noeud IA (repli ollama uniquement)
	$(AI_SSH)

.PHONY: destroy-all
destroy-all: ## Detruit l'EC2 et le reseau. Le bucket d'archives SURVIT.
	@echo "Detruit toutes les instances et le VPC."
	@echo "Le bucket d'archives est protege par prevent_destroy et n'est PAS detruit :"
	@echo "pour le supprimer, il faut retirer ce garde-fou dans archive.tf, a la main."
	@read -p "Taper 'detruire' pour confirmer : " ans; [ "$$ans" = "detruire" ] || exit 1
	$(TF) apply -var 'phase=off'

# --- Validation locale, avant AWS (voir local/README.md) --------------------
# Toute la plateforme sur cette machine : memes images, meme code, memes
# plugins. Aucune ressource AWS touchee.

LOCAL_COMPOSE = docker compose -f local/docker-compose.local.yml
# `make local-venv` cree local/.venv (ctfcli + requests) ; les cibles l'utilisent
# des qu'il existe. Sinon python3 du systeme (il faut alors ctfcli + requests).
LOCAL_PY     ?= $(if $(wildcard local/.venv/bin/python),local/.venv/bin/python,python3)

.PHONY: local-venv
local-venv: ## [local] Cree local/.venv avec ctfcli + requests (Kali/Debian : pip systeme verrouille)
	python3 -m venv local/.venv
	local/.venv/bin/pip install -q --upgrade pip ctfcli requests pyyaml cmarkgfm
	@echo "OK : les cibles local-* utilisent desormais local/.venv automatiquement"

# Les images sont construites avec `docker build` (pas `compose build`) : ce
# dernier exige le plugin buildx, absent de certains Docker (Kali, Debian).
.PHONY: local-up
local-up: ## [local] CTFd + MariaDB + Redis sur http://localhost:8000 (CTFD_PORT=8080 si occupe)
	docker build -t ctfd-local:latest -f ../Dockerfile ..
	$(LOCAL_COMPOSE) up -d ctfd db cache
	@echo; echo "CTFd : http://localhost:$${CTFD_PORT:-8000}   ->   make local-seed"

.PHONY: local-up-ai
local-up-ai: ## [local] Idem + Ollama (CPU) + passerelle IA ; OLLAMA_MODEL=... pour un modele leger
	docker build -t ctfd-local:latest -f ../Dockerfile ..
	docker build -t ctfd-ai-gateway:latest ai-gateway
	$(LOCAL_COMPOSE) --profile ai up -d
	@echo; echo "Le modele se telecharge en arriere-plan : make local-logs"

.PHONY: local-koth
local-koth: ## [local] Active le King of the Hill : construit la colline, la lance et branche le plugin sur CTFd
	@KOTH_SCORER_SECRET="$${KOTH_SCORER_SECRET:-local-dev-koth-scorer}"; \
	 export KOTH_SCORER_SECRET; \
	 export KOTH_HILLS='[{"id":"koth-throne","name":"The Throne","url":"http://koth-throne:8080","player_url":"http://localhost:28900","points":5},{"id":"koth-citadel","name":"The Citadel","url":"http://koth-citadel:8081","player_url":"ssh://player@localhost:28901","points":5},{"id":"koth-armory","name":"The Armory","url":"http://koth-armory:8082","player_url":"ssh://player@localhost:28902","points":5},{"id":"koth-reseau-fortune","name":"Reseau Fortune","url":"http://koth-reseau-fortune:8080","player_url":"http://localhost:28903","points":3}]'; \
	 docker build -t ctf-koth-throne:latest ../challenges/koth/throne; \
	 docker build -t ctf-koth-citadel:latest ../challenges/koth/citadel; \
	 docker build -t ctf-koth-boot2root-base:latest ../challenges/koth/boot2root/base; \
	 docker build -t ctf-koth-boot2root-armory:latest ../challenges/koth/boot2root/armory; \
	 docker build -t ctf-koth-reseau-fortune:latest ../challenges/koth/reseau-fortune; \
	 $(LOCAL_COMPOSE) --profile koth up -d koth-throne koth-citadel koth-armory koth-reseau-fortune; \
	 $(LOCAL_COMPOSE) up -d ctfd; \
	 echo; \
	 echo "King of the Hill actif (tick=$${KOTH_TICK:-15}s) - quatre collines :"; \
	 echo "  - The Throne (HTTP)     : http://localhost:28900"; \
	 echo "  - The Citadel (SSH)     : ssh player@localhost -p 28901   (mot de passe : player)"; \
	 echo "  - The Armory (boot2root): ssh player@localhost -p 28902   (mot de passe : player)"; \
	 echo "  - Reseau Fortune (MLM)  : http://localhost:28903   (POST /api/join {token})"; \
	 echo "  - CTFd (menu 'King of the Hill') : http://localhost:$${CTFD_PORT:-8000}"; \
	 echo "  - Recupere ton jeton d'equipe sur la page KotH, puis tiens une colline :"; \
	 echo "      challenges/koth/throne/solution/solve.sh  http://localhost:28900 <jeton>"; \
	 echo "      challenges/koth/citadel/solution/solve.sh localhost 28901 <jeton>"; \
	 echo "      challenges/koth/boot2root/armory/solution/solve.sh localhost 28902 <jeton>  # root=pleins, sinon /home/player/king.txt=moitie"; \
	 echo "      python3 challenges/koth/reseau-fortune/solution/solve.py http://localhost:28903 <jeton>"

.PHONY: local-fix-heapnote
local-fix-heapnote: ## [local] Recompile le binaire heap-note sur glibc 2.31 (Ubuntu 20.04) puis construit son image
	../challenges/pwn/heap-note/rebuild-binary.sh
	./local/build-images.sh heap-note

.PHONY: local-build-images
local-build-images: ## [local] Construit les images ctf-* des challenges servis (ONLY=nom pour un seul)
	./local/build-images.sh $(ONLY)

.PHONY: lot5
lot5: ## [local] Repetition Lot-5 : build image -> rejoue le solveur -> flip visible (FLIP=1 ; ONLY="cat/slug ..." ; ALL=1)
	scripts/lot5.sh $(if $(FLIP),--flip) $(if $(ALL),--all) $(if $(ONLY),--only $(ONLY))

.PHONY: authors-map
authors-map: ## Regenere la carte nom->auteur lue par la vue "par auteur" du board hibris
	python3 scripts/gen_authors_map.py

.PHONY: local-seed
local-seed: ## [local] Setup NCTF25 + theme hibris + accueil + 36 challenges + equipe de test
	$(LOCAL_PY) local/seed.py

.PHONY: local-smoke
local-smoke: ## [local] Verifie pages, theme, assets, API, chaine IA
	$(LOCAL_PY) local/smoke.py

# Check-list de mise en prod (lecture seule). PHASE=preselection|finale ;
# EXPECT/CATS = set VISIBLE attendu (preflight compte les visibles, pas le total).
# 2026-09-27 apres sync depot : 238 visibles (177 dynamic + 61 servis state:visible) / 21 categories.
# 155 servis pre-dedup restent `hidden` (orphelins sans source) -> hors compte.
PHASE  ?= none
EXPECT ?= 238
CATS   ?= 21
PREFLIGHT_ARGS = --env-stdin --phase $(PHASE) --expect-challenges $(EXPECT) --expect-categories $(CATS) $(PREFLIGHT_EXTRA)

.PHONY: local-preflight
local-preflight: ## [local] Check-list de prod sur la stack locale (attendu : FAIL sur les secrets de dev)
	$(LOCAL_COMPOSE) exec -T ctfd printenv | \
	  CTFD_URL=http://localhost:$${CTFD_PORT:-8000} $(LOCAL_PY) scripts/preflight.py $(PREFLIGHT_ARGS)

# --- Test de charge (k6) : voir loadtest/README.md --------------------------
# Un seul binaire : k6 (K6=/chemin/k6 si hors du PATH). Comptes de charge
# lt-0001.. crees par loadtest/seed.py, JAMAIS sur la base de l'epreuve (le
# seed refuse une plateforme qui porte deja des equipes reelles).
K6       ?= k6
VUS      ?= 300
LT_DIR    = loadtest
LT_ARGS   = -e ACCOUNTS=$(LT_DIR)/out/accounts.json -e OUT=$(LT_DIR)/out --summary-trend-stats="avg,p(95),max,count"

.PHONY: loadtest
loadtest: ## Test de charge sur le front de repetition : URL=https://... CTFD_TOKEN=<jeton admin> VUS=300 (5 + 15 min)
	@test -n "$(URL)" || { echo "URL manquante (ex: URL=https://ctf.exemple.tg)"; exit 2; }
	@test -n "$$CTFD_TOKEN" || { echo "CTFD_TOKEN manquant (jeton API admin : Settings > Access Tokens)"; exit 2; }
	@command -v $(K6) >/dev/null || { echo "k6 introuvable : https://grafana.com/docs/k6/latest/set-up/install/ (ou K6=/chemin/k6)"; exit 2; }
	$(LOCAL_PY) $(LT_DIR)/seed.py --url $(URL) --teams $$(( $(VUS) + 3 )) --allow-remote
	$(K6) run $(LT_ARGS) -e URL=$(URL) -e VUS=$(VUS) $(LT_DIR)/scenarios.js
	@echo "Rapport : $(LT_DIR)/out/scenarios-summary.html  ->  noter le run dans infra-audit.md, puis make loadtest-purge + restore"

.PHONY: loadtest-instancer
loadtest-instancer: ## Instancier sous charge sur le front de repetition : URL=... CTFD_TOKEN=... (50 equipes, 10 min)
	@test -n "$(URL)" || { echo "URL manquante"; exit 2; }
	@test -n "$$CTFD_TOKEN" || { echo "CTFD_TOKEN manquant"; exit 2; }
	@test -f $(LT_DIR)/out/accounts.json || $(LOCAL_PY) $(LT_DIR)/seed.py --url $(URL) --teams $$(( $(VUS) + 3 )) --allow-remote
	$(K6) run $(LT_ARGS) -e URL=$(URL) -e VUS=$${IVUS:-50} $(LT_DIR)/instancer.js

.PHONY: loadtest-purge
loadtest-purge: ## Supprime les equipes de charge lt-* (URL=... CTFD_TOKEN=...) et recalcule les valeurs dynamiques ; puis make restore
	@test -n "$(URL)" || { echo "URL manquante"; exit 2; }
	@test -n "$$CTFD_TOKEN" || { echo "CTFD_TOKEN manquant"; exit 2; }
	$(LOCAL_PY) $(LT_DIR)/seed.py --url $(URL) --purge --allow-remote
	@echo "Restaurer maintenant le dump pris AVANT le test : make restore FILE=backups/..."

.PHONY: local-loadtest
local-loadtest: ## [local] Smoke du test de charge sur la stack locale : 100 VU, 20 s + 40 s + 10 s
	@command -v $(K6) >/dev/null || { echo "k6 introuvable : https://grafana.com/docs/k6/latest/set-up/install/ (ou K6=/chemin/k6)"; exit 2; }
	$(LOCAL_PY) $(LT_DIR)/seed.py --url http://localhost:$${CTFD_PORT:-8000} --teams $$(( $${VUS:-100} + 3 ))
	$(K6) run $(LT_ARGS) -e URL=http://localhost:$${CTFD_PORT:-8000} -e SMOKE=1 -e VUS=$${VUS:-100} $(LT_DIR)/scenarios.js
	-$(K6) run $(LT_ARGS) -e URL=http://localhost:$${CTFD_PORT:-8000} -e SMOKE=1 -e VUS=3 $(LT_DIR)/instancer.js
	@echo "Rapports : $(LT_DIR)/out/*-summary.html   (purge : $(LOCAL_PY) $(LT_DIR)/seed.py --purge)"

.PHONY: local-writeups
local-writeups: ## [local] Pages writeups sur la stack locale : brouillon, puis PUBLISH=1 (FORCE=1 si `end` n'est pas passe)
	@TOKEN=$$($(LOCAL_PY) -c "import sys; sys.path.insert(0,'local'); from seed import admin_session, api_token; u='http://localhost:$${CTFD_PORT:-8000}'; print(api_token(admin_session(u), u))"); \
	 $(LOCAL_PY) scripts/publish_writeups.py --url http://localhost:$${CTFD_PORT:-8000} --token $$TOKEN \
	   $(if $(PUBLISH),--publish $(if $(FORCE),--force),--prepare) $(WRITEUPS_ARGS)

.PHONY: local-playtest
local-playtest: ## [local] Spawn -> solveur -> soumission, pour chaque challenge (ARGS="--only web/jwt-cousin")
	docker build -q -t ctf-playtest -f local/Dockerfile.playtest local >/dev/null
	$(LOCAL_PY) local/playtest.py $(ARGS)

.PHONY: local-race-demo
local-race-demo: ## [local] Peuple le scoreboard de fausses ecuries pour voir la course (ARGS="--live")
	$(LOCAL_PY) local/seed_race_demo.py $(ARGS)

.PHONY: local-race-clear
local-race-clear: ## [local] Retire les ecuries de demo du scoreboard
	$(LOCAL_PY) local/seed_race_demo.py --clear

.PHONY: local-logs
local-logs: ## [local] Logs de la stack locale
	$(LOCAL_COMPOSE) --profile ai --profile koth logs -f --tail=100

.PHONY: local-down
local-down: ## [local] Arrete la stack (base et uploads conserves)
	$(LOCAL_COMPOSE) --profile ai --profile koth down

.PHONY: local-reset
local-reset: ## [local] Arrete ET efface tout : base, uploads, modele Ollama, instances
	$(LOCAL_COMPOSE) --profile ai --profile koth down -v
	-docker ps -aq --filter label=ctfd.instancer=1 | xargs -r docker rm -f
