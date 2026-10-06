#!/bin/sh
# Passerelle vers le demon Docker de l'arena.
#
# Deux processus :
#   1. un tunnel ssh qui expose le socket Docker distant en LOCAL seulement
#      (127.0.0.1:2381) -- jamais sur le reseau du compose ;
#   2. broker.py, qui ecoute sur 0.0.0.0:2375 (joint par ctfd via `internal`)
#      et ne laisse passer que les operations de l'instancier, apres validation.
#
# Ainsi aucun conteneur ne parle plus au socket Docker brut : y acceder ne vaut
# plus root sur l'arena. (C2 du pentest.)
set -eu

: "${ARENA_HOST:?ARENA_HOST doit etre defini (IP privee de l'arena)}"
ARENA_USER="${ARENA_USER:-ubuntu}"

if [ ! -r /keys/id_ed25519 ]; then
  echo "ERREUR: cle privee absente ou illisible dans /keys/id_ed25519" >&2
  exit 1
fi

# La cle doit etre en 600 : ssh refuse une cle trop permissive. Le montage est
# en lecture seule, on recopie donc avec les bons droits.
install -m 700 -d /root/.ssh
install -m 600 /keys/id_ed25519 /root/.ssh/id_ed25519

if [ -r /keys/known_hosts ]; then
  install -m 644 /keys/known_hosts /root/.ssh/known_hosts
  STRICT=yes
else
  # Sans empreinte connue on accepte a la premiere connexion, mais on le dit :
  # sur ce canal, un homme du milieu obtiendrait root sur l'arena.
  echo "AVERTISSEMENT: pas de known_hosts, verification d'hote desactivee" >&2
  STRICT=accept-new
fi

echo "Tunnel Docker (prive, loopback) vers ${ARENA_USER}@${ARENA_HOST}"

# -L 127.0.0.1:2381 : le socket distant n'est expose qu'en local, pour le broker.
# -L 0.0.0.0:7400  : admin frpc de l'arena (inchange).
ssh -N \
  -o StrictHostKeyChecking="$STRICT" \
  -o ServerAliveInterval=15 \
  -o ServerAliveCountMax=3 \
  -o ExitOnForwardFailure=yes \
  -i /root/.ssh/id_ed25519 \
  -L "127.0.0.1:2381:/var/run/docker.sock" \
  -L "0.0.0.0:7400:127.0.0.1:7400" \
  "${ARENA_USER}@${ARENA_HOST}" &
SSH_PID=$!

python3 /broker.py &
BRK_PID=$!

# Si l'un des deux meurt, on quitte : `restart: always` relancera le conteneur.
trap 'kill "$SSH_PID" "$BRK_PID" 2>/dev/null || true' INT TERM
while kill -0 "$SSH_PID" 2>/dev/null && kill -0 "$BRK_PID" 2>/dev/null; do
  sleep 3
done
echo "ERREUR: tunnel ssh ou broker arrete, sortie." >&2
kill "$SSH_PID" "$BRK_PID" 2>/dev/null || true
exit 1
