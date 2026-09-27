#!/usr/bin/env bash
# King of the Hill sur AWS : déploie les collines partagées sur l'ARENA, les
# expose aux joueurs via frps (front) sur des ports FIXES, et branche le plugin
# koth de CTFd (front).
#
#   deploy/scripts/arena-koth.sh            # déploie / met à jour
#   deploy/scripts/arena-koth.sh --status   # état (conteneurs, /king, plugin)
#   deploy/scripts/arena-koth.sh --down     # retire les collines et le tunnel
#
# Appelé par `make arena-koth` qui fournit FRONT_IP, FRONT_PRIV, ARENA_IP,
# SSH_OPTS. Prérequis : `make link` passé (jeton frp injecté sur l'arena), images
# ctf-koth-* dans s3://<bucket>/images/ (make push-images) ou déjà chargées.
#
# Topologie :
#   joueur -> FRONT_IP:2849x (frps) -> tunnel -> arena 127.0.0.1:2849x (colline)
#   CTFd (front) -> FRONT_PRIV:2849x/king (X-Scorer-Token) pour le scoring
# Les ports 28490-28495 sont dans allowPorts de frps (28000-28500) : le script
# borne l'instancier à WHALE_PORT_RANGE_END=28480 pour éviter toute collision.
set -euo pipefail

: "${FRONT_IP:?}" "${FRONT_PRIV:?}" "${ARENA_IP:?}"
SSH_OPTS="${SSH_OPTS:--o StrictHostKeyChecking=accept-new -o ConnectTimeout=10}"
BUCKET="${BUCKET:-}"
KOTH_TICK="${KOTH_TICK:-30}"
# shellcheck disable=SC2086
front() { ssh $SSH_OPTS "ubuntu@$FRONT_IP" "$@"; }
# shellcheck disable=SC2086
arena() { ssh $SSH_OPTS "ubuntu@$ARENA_IP" "$@"; }

P_THRONE=28490; P_CITADEL=28491; P_ARMORY=28492; P_FORTUNE=28493
# scorers des collines SSH (doivent rester dans allowPorts de frps : 28000-28500)
S_CITADEL=28494; S_ARMORY=28495
ENV_FILE=/opt/ctfd/CTFd/deploy/front/.env
COMPOSE='docker compose -f deploy/front/docker-compose.prod.yml --env-file deploy/front/.env'

status() {
  echo ">> Collines sur l'arena"
  arena 'docker ps --filter name=koth- --format "  {{.Names}}\t{{.Status}}\t{{.Ports}}"; systemctl is-active frpc-koth 2>/dev/null | sed "s/^/  frpc-koth: /"'
  echo ">> /king via frps (depuis le front, avec le secret scorer)"
  front "S=\$(grep '^KOTH_SCORER_SECRET=' $ENV_FILE | cut -d= -f2); for p in $P_THRONE $S_CITADEL $S_ARMORY $P_FORTUNE; do printf '  :%s  ' \$p; curl -s -m 5 -H \"X-Scorer-Token: \$S\" http://$FRONT_PRIV:\$p/king | head -c 120; echo; done"
  echo ">> Plugin koth (CTFd)"
  front "cd /opt/ctfd/CTFd && $COMPOSE exec -T ctfd sh -c 'echo \"  KOTH_TICK=\$KOTH_TICK hills=\$(echo \$KOTH_HILLS | tr -cd , | wc -c)+1\"'; curl -s -m 5 -o /dev/null -w '  /plugins/koth/ -> %{http_code}\n' http://127.0.0.1/plugins/koth/ -H 'Host: ctf.tg'"
}

down() {
  arena 'sudo systemctl disable --now frpc-koth 2>/dev/null; sudo rm -f /etc/frp/frpc-koth.toml /etc/systemd/system/frpc-koth.service; cd /opt/koth 2>/dev/null && sudo docker compose down 2>/dev/null; true'
  front "sed -i -e '/^KOTH_HILLS=/d' -e '/^KOTH_SCORER_SECRET=/d' -e '/^KOTH_TICK=/d' $ENV_FILE && cd /opt/ctfd/CTFd && $COMPOSE up -d ctfd >/dev/null 2>&1"
  echo "KotH retiré (collines, tunnel, variables CTFd)."
}

case "${1:-}" in --status) status; exit 0 ;; --down) down; exit 0 ;; esac

# --- 1. secret scorer (stable : réutilise celui du front s'il existe) --------
SCORER=$(front "grep '^KOTH_SCORER_SECRET=' $ENV_FILE 2>/dev/null | cut -d= -f2" || true)
[ -n "$SCORER" ] || SCORER=$(openssl rand -hex 32)

# --- 2. jeton frp + port frps (lus dans le frpc.toml injecté par make link) ---
FRP_TOKEN=$(arena "sudo grep '^auth.token' /etc/frp/frpc.toml | cut -d'\"' -f2")
FRP_PORT=$(arena "sudo grep '^serverPort' /etc/frp/frpc.toml | awk '{print \$3}'")
[ -n "$FRP_TOKEN" ] && [ "$FRP_TOKEN" != "REMPLACE_TOKEN" ] || { echo "ERREUR : jeton frp absent sur l'arena — lancer make link d'abord"; exit 1; }

# --- 3. images des collines sur l'arena --------------------------------------
echo ">> Images ctf-koth-* sur l'arena"
arena "set -e
  need='ctf-koth-throne ctf-koth-citadel ctf-koth-boot2root-armory ctf-koth-reseau-fortune'
  if [ -n '$BUCKET' ]; then sudo aws s3 sync s3://$BUCKET/images/ /opt/challenge-images/ --exclude '*' --include 'ctf-koth-*' --only-show-errors || true; fi
  for n in \$need; do
    docker image inspect \$n:latest >/dev/null 2>&1 && { echo \"  \$n: présente\"; continue; }
    t=/opt/challenge-images/\${n}_latest.tar
    [ -f \$t ] && sudo docker load -q -i \$t && echo \"  \$n: chargée\" || { echo \"  \$n: MANQUANTE (make push-images après make local-koth)\"; exit 1; }
  done"

# --- 4. compose des collines (ports sur la boucle locale de l'arena) ---------
echo ">> Collines (docker compose sur l'arena)"
arena "sudo mkdir -p /opt/koth && sudo tee /opt/koth/docker-compose.yml >/dev/null <<EOF
services:
  koth-throne:
    image: ctf-koth-throne:latest
    restart: unless-stopped
    environment: [SCORER_SECRET=$SCORER, SKEW=45]
    ports: ['127.0.0.1:$P_THRONE:8080']
  koth-citadel:
    image: ctf-koth-citadel:latest
    restart: unless-stopped
    environment: [SCORER_SECRET=$SCORER, SCORER_PORT=8081]
    ports: ['127.0.0.1:$P_CITADEL:22', '127.0.0.1:$S_CITADEL:8081']
  koth-armory:
    image: ctf-koth-boot2root-armory:latest
    restart: unless-stopped
    environment: [SCORER_SECRET=$SCORER, SCORER_PORT=8082]
    ports: ['127.0.0.1:$P_ARMORY:22', '127.0.0.1:$S_ARMORY:8082']
  koth-reseau-fortune:
    image: ctf-koth-reseau-fortune:latest
    restart: unless-stopped
    environment: [SCORER_SECRET=$SCORER]
    ports: ['127.0.0.1:$P_FORTUNE:8080']
EOF
cd /opt/koth && sudo docker compose up -d --remove-orphans 2>&1 | tail -4"

# --- 5. second client frp : proxies fixes (frpc principal est réécrit par whale)
echo ">> Tunnel frps pour les collines (frpc-koth)"
arena "sudo tee /etc/frp/frpc-koth.toml >/dev/null <<EOF
serverAddr = \"$FRONT_PRIV\"
serverPort = $FRP_PORT
auth.method = \"token\"
auth.token = \"$FRP_TOKEN\"
log.to = \"/var/log/frpc-koth.log\"

[[proxies]]
name = \"koth-throne\"
type = \"tcp\"
localIP = \"127.0.0.1\"
localPort = $P_THRONE
remotePort = $P_THRONE

[[proxies]]
name = \"koth-citadel-ssh\"
type = \"tcp\"
localIP = \"127.0.0.1\"
localPort = $P_CITADEL
remotePort = $P_CITADEL

[[proxies]]
name = \"koth-citadel-scorer\"
type = \"tcp\"
localIP = \"127.0.0.1\"
localPort = $S_CITADEL
remotePort = $S_CITADEL

[[proxies]]
name = \"koth-armory-ssh\"
type = \"tcp\"
localIP = \"127.0.0.1\"
localPort = $P_ARMORY
remotePort = $P_ARMORY

[[proxies]]
name = \"koth-armory-scorer\"
type = \"tcp\"
localIP = \"127.0.0.1\"
localPort = $S_ARMORY
remotePort = $S_ARMORY

[[proxies]]
name = \"koth-reseau-fortune\"
type = \"tcp\"
localIP = \"127.0.0.1\"
localPort = $P_FORTUNE
remotePort = $P_FORTUNE
EOF
sudo chmod 600 /etc/frp/frpc-koth.toml
sudo tee /etc/systemd/system/frpc-koth.service >/dev/null <<'EOF'
[Unit]
Description=frp client (collines KotH, proxies fixes)
After=network.target docker.service
[Service]
ExecStart=/usr/local/bin/frpc -c /etc/frp/frpc-koth.toml
Restart=always
RestartSec=5
[Install]
WantedBy=multi-user.target
EOF
sudo systemctl daemon-reload && sudo systemctl enable --now frpc-koth && sudo systemctl restart frpc-koth && sleep 2 && systemctl is-active frpc-koth"

# --- 6. plugin koth sur le front ---------------------------------------------
echo ">> Plugin koth (front/.env + recréation de ctfd)"
HILLS=$(printf '[{"id":"koth-throne","name":"The Throne","url":"http://%s:%s","player_url":"http://%s:%s","points":5},{"id":"koth-citadel","name":"The Citadel","url":"http://%s:%s","player_url":"ssh://player@%s:%s","points":5},{"id":"koth-armory","name":"The Armory","url":"http://%s:%s","player_url":"ssh://player@%s:%s","points":5},{"id":"koth-reseau-fortune","name":"Reseau Fortune","url":"http://%s:%s","player_url":"http://%s:%s","points":3}]' \
  "$FRONT_PRIV" "$P_THRONE" "$FRONT_IP" "$P_THRONE" \
  "$FRONT_PRIV" "$S_CITADEL" "$FRONT_IP" "$P_CITADEL" \
  "$FRONT_PRIV" "$S_ARMORY" "$FRONT_IP" "$P_ARMORY" \
  "$FRONT_PRIV" "$P_FORTUNE" "$FRONT_IP" "$P_FORTUNE")
front "cd /opt/ctfd/CTFd && set -e
  upsert() { grep -q \"^\$1=\" $ENV_FILE && sed -i \"s|^\$1=.*|\$1=\$2|\" $ENV_FILE || echo \"\$1=\$2\" >> $ENV_FILE; }
  upsert KOTH_SCORER_SECRET '$SCORER'
  upsert KOTH_TICK '$KOTH_TICK'
  upsert WHALE_PORT_RANGE_END 28480
  upsert KOTH_HILLS '$HILLS'
  $COMPOSE up -d ctfd 2>&1 | tail -1"
sleep 8
status
echo
echo "Joueurs : Throne http://$FRONT_IP:$P_THRONE | Citadel ssh player@$FRONT_IP -p $P_CITADEL | Armory ssh player@$FRONT_IP -p $P_ARMORY | Reseau Fortune http://$FRONT_IP:$P_FORTUNE"
echo "Jeton d'équipe : menu « King of the Hill » de CTFd. Retirer : make arena-koth DOWN=1"
