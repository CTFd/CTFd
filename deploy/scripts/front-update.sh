#!/usr/bin/env bash
# Met a jour CTFd sur le front, depuis le depot deja clone dans /opt/ctfd/CTFd.
# Idempotent. Lance :
#   - par `make deploy` (SSH admin), avec la branche en argument ;
#   - par le CD GitHub Actions (SSM Run Command), avec le SHA pousse.
#
#   deploy/scripts/front-update.sh [<branche>|<sha>]     (defaut : branche courante)
#
# Env : BACKUP_BUCKET=<bucket> pour (re)poser la destination des sauvegardes
#       dans deploy/front/.env. Le fichier .env lui-meme n'est jamais cree ici.
set -euo pipefail

REPO=${CTFD_REPO:-/opt/ctfd/CTFd}
cd "$REPO"

REF=${1:-$(git rev-parse --abbrev-ref HEAD)}
COMPOSE="docker compose -f deploy/front/docker-compose.prod.yml --env-file deploy/front/.env"

echo ">> git : $REF"
git fetch --prune origin
if git show-ref --verify --quiet "refs/remotes/origin/$REF"; then
  git checkout -q "$REF"
  git reset -q --hard "origin/$REF"
else
  git checkout -q --detach "$REF"
fi
git log -1 --oneline

test -f deploy/front/.env || { echo "ERREUR : deploy/front/.env absent (make deploy l'envoie au premier deploiement)"; exit 1; }
test -f deploy/front/nginx/active.conf || cp deploy/front/nginx/bootstrap.conf deploy/front/nginx/active.conf

if [ -n "${BACKUP_BUCKET:-}" ]; then
  if grep -q '^BACKUP_BUCKET=' deploy/front/.env; then
    sed -i "s|^BACKUP_BUCKET=.*|BACKUP_BUCKET=$BACKUP_BUCKET|" deploy/front/.env
  else
    echo "BACKUP_BUCKET=$BACKUP_BUCKET" >> deploy/front/.env
  fi
fi

echo ">> sauvegarde automatique"
sudo CTFD_REPO="$REPO" deploy/scripts/install-backup-timer.sh

echo ">> conteneurs"
$COMPOSE up -d --build ctfd db cache nginx certbot

echo ">> sante"
# Depuis tls.conf, nginx ferme (444) toute requete dont le Host n'est pas le
# domaine : on sonde donc avec le vrai nom (SNI + Host) resolu sur 127.0.0.1.
# CTFd est servi sur arena.<domaine> (l'apex sert la vitrine statique, ou
# /healthcheck repond 404) ; l'apex reste sonde pour un active.conf plus ancien.
# Les sondes sans nom restent pour bootstrap.conf (avant le certificat).
DOMAIN=$(grep -E '^CTF_DOMAIN=' deploy/front/.env | cut -d= -f2- | tr -d '[:space:]' || true)
ok=0
for _ in $(seq 1 60); do
  if [ -n "$DOMAIN" ]; then
    for host in "arena.$DOMAIN" "$DOMAIN"; do
      code=$(curl -sk -o /dev/null -w '%{http_code}' --max-time 10 \
        --resolve "$host:443:127.0.0.1" "https://$host/healthcheck" || true)
      [ "$code" = 200 ] && { ok=1; break; }
    done
    [ "$ok" -eq 1 ] && break
  fi
  code=$(curl -s -o /dev/null -w '%{http_code}' --max-time 10 http://127.0.0.1/healthcheck || true)
  [ "$code" = 200 ] && { ok=1; break; }
  # nginx en HTTPS : le port 80 redirige, on interroge alors le 443 en local.
  code=$(curl -sk -o /dev/null -w '%{http_code}' --max-time 10 https://127.0.0.1/healthcheck || true)
  [ "$code" = 200 ] && { ok=1; break; }
  sleep 5
done
$COMPOSE ps --format 'table {{.Name}}\t{{.Status}}'
if [ "$ok" -ne 1 ]; then
  echo "ERREUR : /healthcheck ne repond pas 200 apres 5 min"
  $COMPOSE logs --tail=40 ctfd nginx
  exit 1
fi
echo "OK : CTFd a jour ($(git rev-parse --short HEAD))"
