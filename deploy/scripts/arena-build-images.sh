#!/usr/bin/env bash
# Construit des images de challenge DIRECTEMENT SUR L'ARENA à partir des sources
# du dépôt (rsync des dossiers, docker build là-bas). Utile quand la liaison
# montante de l'opérateur est lente : pousser 35 tars de 70 Mo depuis le Togo
# prend des heures, construire sur l'arena prend quelques minutes.
#
#   deploy/scripts/arena-build-images.sh web/jwt-cousin pwn/heap-note koth/throne ...
#   deploy/scripts/arena-build-images.sh --missing   # tout servi `visible` absent de l'arena
#
# Nom d'image = extra.docker_image du challenge.yml (servis) ou ctf-koth-<nom>
# pour les collines (koth/boot2root/<x> -> ctf-koth-boot2root-<x>, base d'abord).
# Avec PUSH=1, chaque image est aussi sauvée et copiée dans s3://$BUCKET/images/
# depuis l'arena (réseau AWS), pour survivre à la prochaine recréation de l'arena.
# Fourni par `make arena-build-images ONLY="..."` (ARENA_IP, SSH_OPTS, BUCKET).
set -euo pipefail
: "${ARENA_IP:?}"
SSH_OPTS="${SSH_OPTS:--o StrictHostKeyChecking=accept-new -o ConnectTimeout=10}"
PUSH="${PUSH:-0}"; BUCKET="${BUCKET:-}"
ROOT=$(cd "$(dirname "$0")/../.." && pwd)
# shellcheck disable=SC2086
arena() { ssh $SSH_OPTS "ubuntu@$ARENA_IP" "$@"; }

image_of() { # image_of cat/slug -> nom d'image
  local d="$ROOT/challenges/$1"
  case "$1" in
    koth/boot2root/*) echo "ctf-koth-boot2root-$(basename "$1")" ;;
    koth/*)           echo "ctf-koth-$(basename "$1")" ;;
    *) grep -E "^\s*docker_image:" "$d/challenge.yml" | awk '{print $2}' | sed 's/:latest$//' ;;
  esac
}

if [ "${1:-}" = "--missing" ]; then
  shift; extra=("$@")               # les noms passes en plus de --missing sont conserves
  have=$(arena 'docker image ls --format "{{.Repository}}"')
  set -- "${extra[@]}"
  for y in "$ROOT"/challenges/*/*/challenge.yml; do
    grep -q "type: team_instance" "$y" && grep -q "^state: visible" "$y" || continue
    d=${y#"$ROOT"/challenges/}; d=${d%/challenge.yml}
    img=$(image_of "$d"); [ -n "$img" ] || continue
    echo "$have" | grep -qx "$img" || set -- "$@" "$d"
  done
  echo ">> $# image(s) a construire sur l'arena"
fi
[ $# -gt 0 ] || { echo "rien a construire"; exit 0; }

arena 'sudo mkdir -p /opt/challenge-src && sudo chown ubuntu:ubuntu /opt/challenge-src'
fail=0
for d in "$@"; do
  img=$(image_of "$d"); src="$ROOT/challenges/$d"
  [ -d "$src" ] && [ -n "$img" ] || { echo "  $d : dossier ou docker_image introuvable"; fail=$((fail+1)); continue; }
  case "$d" in koth/boot2root/*) # la base d'abord
    # shellcheck disable=SC2086
    rsync -az --delete -e "ssh $SSH_OPTS" "$ROOT/challenges/koth/boot2root/base/" "ubuntu@$ARENA_IP:/opt/challenge-src/koth-boot2root-base/"
    arena 'docker image inspect ctf-koth-boot2root-base:latest >/dev/null 2>&1 || docker build -q -t ctf-koth-boot2root-base:latest /opt/challenge-src/koth-boot2root-base >/dev/null' ;;
  esac
  dst=$(echo "$d" | tr '/' '-')
  # shellcheck disable=SC2086
  rsync -az --delete --exclude solution --exclude writeup --exclude '__pycache__' -e "ssh $SSH_OPTS" "$src/" "ubuntu@$ARENA_IP:/opt/challenge-src/$dst/"
  printf '  %-40s -> %s ' "$d" "$img"
  if arena "docker build -q -t $img:latest /opt/challenge-src/$dst >/dev/null 2>/tmp/build-$dst.err"; then
    echo "OK"
    if [ "$PUSH" = 1 ] && [ -n "$BUCKET" ]; then
      arena "docker save $img:latest | aws s3 cp - s3://$BUCKET/images/${img}_latest.tar --only-show-errors" && echo "     poussee dans S3"
    fi
  else
    echo "ECHEC"; arena "tail -3 /tmp/build-$dst.err" | sed 's/^/     /'; fail=$((fail+1))
  fi
done
echo; arena 'echo "Images ctf-* sur l arena : $(docker image ls --format "{{.Repository}}" | grep -c "^ctf-")"'
[ $fail = 0 ] || { echo "$fail echec(s)"; exit 1; }
