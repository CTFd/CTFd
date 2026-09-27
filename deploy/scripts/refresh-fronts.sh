#!/usr/bin/env bash
# Rebuild + relance des fronts web apres une mise a jour du depot.
#
# Cible :
#   * 11 challenges SERVIS (team_instance, geres par whale) dont on a refait
#     l'interface web (route « / ») -- commit « vraie interface web ».
#   * la colline KotH « reseau-fortune » (conteneur PARTAGE du compose /opt/koth,
#     exposee aux joueurs sur le port fixe 28493) -- meme refonte de front.
#
# Ce que fait le script, sur l'ARENA, a partir des sources du depot :
#   1. reconstruit chaque image concernee (delegue a arena-build-images.sh :
#      rsync du dossier + docker build la-bas ; PUSH=1 archive aussi en S3) ;
#   2. recree immediatement la colline reseau-fortune depuis sa nouvelle image
#      (docker compose up -d --force-recreate) -- le port 28493 est rafraichi ;
#   3. pour les servis : les NOUVEAUX lancements repartent de l'image a jour
#      automatiquement (whale relance un conteneur par equipe a chaque launch).
#      Une instance DEJA lancee garde l'ancienne image tant qu'elle n'est pas
#      recreee : --recreate-served arrete+supprime les conteneurs en cours de ces
#      11 images pour forcer un redemarrage propre au prochain lancement.
#
# Usage :
#   ARENA_IP=... [SSH_OPTS=...] [PUSH=1 BUCKET=...] deploy/scripts/refresh-fronts.sh [options]
#   make refresh-fronts ...  (memes variables que arena-build-images / arena-koth)
#
# Options :
#   --served-only        ne traiter que les 11 challenges servis
#   --koth-only          ne traiter que la colline reseau-fortune (port 28493)
#   --recreate-served    arreter+supprimer les conteneurs servis en cours pour
#                        les 11 images (voir la note whale plus bas)
#   --status             affiche l'etat (images + conteneurs), ne build rien
#
# Note whale : --recreate-served retire les conteneurs au niveau Docker ; la
#   fiche d'instance de CTFd (whale) peut alors pointer un conteneur disparu.
#   Avant l'evenement (aucune equipe branchee) c'est sans risque. En course,
#   preferer « detruire » les instances depuis l'admin whale (retire conteneur +
#   fiche), puis laisser les equipes relancer : le rebuild d'image suffit a ce
#   que ce relancement reparte a jour.
set -euo pipefail

: "${ARENA_IP:?ARENA_IP requis - adresse IP de l arene}"
SSH_OPTS="${SSH_OPTS:--o StrictHostKeyChecking=accept-new -o ConnectTimeout=10}"
PUSH="${PUSH:-0}"
BUCKET="${BUCKET:-}"
ROOT=$(cd "$(dirname "$0")/../.." && pwd)
BUILD="$ROOT/deploy/scripts/arena-build-images.sh"
FORTUNE_SVC=koth-reseau-fortune
FORTUNE_IMG=ctf-koth-reseau-fortune
FORTUNE_PORT=28493

# shellcheck disable=SC2086
arena() { ssh $SSH_OPTS "ubuntu@$ARENA_IP" "$@"; }

# image_of : meme convention que arena-build-images.sh.
image_of() {
  case "$1" in
    koth/*) echo "ctf-koth-$(basename "$1")" ;;
    *) grep -E "^\s*docker_image:" "$ROOT/challenges/$1/challenge.yml" | awk '{print $2}' | sed 's/:latest$//' ;;
  esac
}

# Les 11 fronts servis (team_instance).
SERVED=(
  web/cms-authbypass
  web/cms-jwtconf
  web/cms-smuggle
  web/cms-uploadssrf
  web/forum-protopoll
  web/forum-sqli2
  web/forum-xxe
  web/graph-climb
  web/graphql-introspection-maze
  web/jwt-cousin
  web/webhook-relay
)

# Noms d'image des servis, resolus une fois (iteres cites -> pas de re-split).
SERVED_IMAGES=()
for _d in "${SERVED[@]}"; do SERVED_IMAGES+=("$(image_of "$_d")"); done

DO_SERVED=1; DO_KOTH=1; RECREATE=0; STATUS_ONLY=0
for a in "$@"; do
  case "$a" in
    --served-only) DO_KOTH=0 ;;
    --koth-only) DO_SERVED=0 ;;
    --recreate-served) RECREATE=1 ;;
    --status) STATUS_ONLY=1 ;;
    *) echo "option inconnue : $a" >&2; exit 2 ;;
  esac
done

status() {
  echo ">> Images sur l'arene (date de construction)"
  local imgs=()
  [ "$DO_SERVED" -eq 1 ] && imgs+=("${SERVED_IMAGES[@]}")
  [ "$DO_KOTH" -eq 1 ] && imgs+=("$FORTUNE_IMG")
  local img
  for img in "${imgs[@]}"; do
    printf '  %-42s ' "$img"
    arena 'docker image inspect '"$img"':latest --format "{{.Created}}" 2>/dev/null || echo ABSENTE'
  done
  if [ "$DO_SERVED" -eq 1 ]; then
    echo ">> Conteneurs servis EN COURS (image -> nb)"
    for img in "${SERVED_IMAGES[@]}"; do
      n=$(arena 'docker ps -q --filter ancestor='"$img"':latest | wc -l' 2>/dev/null || echo 0)
      [ "${n:-0}" != "0" ] && printf '  %-42s %s\n' "$img" "$n"
    done
    echo "  (aucun affiche = aucune instance en cours a recreer)"
  fi
  if [ "$DO_KOTH" -eq 1 ]; then
    echo ">> Colline reseau-fortune (port $FORTUNE_PORT)"
    arena 'docker ps --filter name='"$FORTUNE_SVC"' --format "  {{.Names}}  {{.Status}}  {{.Image}}" || true'
  fi
}

if [ "$STATUS_ONLY" -eq 1 ]; then status; exit 0; fi
[ -x "$BUILD" ] || { echo "introuvable/non executable : $BUILD" >&2; exit 1; }

# --- 1. rebuild des images sur l'arene ---------------------------------------
targets=()
[ "$DO_SERVED" -eq 1 ] && targets+=("${SERVED[@]}")
[ "$DO_KOTH" -eq 1 ] && targets+=("koth/reseau-fortune")
echo ">> Reconstruction de ${#targets[@]} image(s) sur l'arene (PUSH=$PUSH)"
ARENA_IP="$ARENA_IP" SSH_OPTS="$SSH_OPTS" PUSH="$PUSH" BUCKET="$BUCKET" \
  "$BUILD" "${targets[@]}"

# --- 2. relance immediate de la colline reseau-fortune (conteneur partage) ----
if [ "$DO_KOTH" -eq 1 ]; then
  echo ">> Recreation de la colline $FORTUNE_SVC depuis la nouvelle image"
  if arena 'test -f /opt/koth/docker-compose.yml'; then
    arena 'cd /opt/koth && sudo docker compose up -d --force-recreate '"$FORTUNE_SVC"' && sleep 2 && docker ps --filter name='"$FORTUNE_SVC"' --format "  {{.Names}} {{.Status}}"'
    echo "   port $FORTUNE_PORT rafraichi (frps -> arene 127.0.0.1:$FORTUNE_PORT)."
  else
    echo "   /opt/koth absent : lancer d'abord « make arena-koth », puis relancer ce script --koth-only."
  fi
fi

# --- 3. servis : recreation optionnelle des instances en cours ---------------
if [ "$DO_SERVED" -eq 1 ]; then
  if [ "$RECREATE" -eq 1 ]; then
    echo ">> Recreation des conteneurs servis en cours (--recreate-served)"
    for img in "${SERVED_IMAGES[@]}"; do
      arena 'ids=$(docker ps -q --filter ancestor='"$img"':latest); if [ -n "$ids" ]; then echo "  '"$img"': $(echo $ids | wc -w) conteneur(s) supprime(s)"; docker rm -f $ids >/dev/null; fi'
    done
    echo "   (whale relancera un conteneur a jour au prochain lancement de chaque equipe ;"
    echo "    penser a purger les fiches d'instance cote admin whale si des equipes etaient deja branchees.)"
  else
    echo ">> Servis : images a jour. Les nouveaux lancements repartent propres."
    echo "   Pour forcer les instances DEJA lancees : relancer avec --recreate-served."
  fi
fi

echo ">> Termine."
