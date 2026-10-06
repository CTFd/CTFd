#!/usr/bin/env bash
# TLS du front DERRIERE LE PROXY CLOUDFLARE (mode "Full (strict)").
#
# Remplace `make tls-init` (HTTP-01 Let's Encrypt) quand le domaine est
# proxifie par Cloudflare : le nom resout vers Cloudflare, pas vers le front,
# et c'est Cloudflare qui presente le certificat public. Le front n'a besoin
# que d'un certificat reconnu par Cloudflare : un certificat "Origin CA"
# (15 ans, pas de renouvellement), demande a l'API avec le jeton Cloudflare.
#
# Lance depuis deploy/ (make tls-cloudflare) : a besoin de CF_API_TOKEN dans
# l'environnement (jamais dans git), de deploy/front/.env (CTF_DOMAIN) et d'un
# acces SSH au front. Idempotent : reutilise le certificat s'il existe deja
# dans ~/.config/nctf26/origin-cert/.
#
# Etapes : certificat d'origine -> depose dans le volume certbot_conf du front
#          -> nginx tls.conf (+ vraies IP via CF-Connecting-IP) -> Cloudflare
#          en Full (strict), TLS >= 1.2 -> verification via https://<domaine>/.
set -euo pipefail

FRONT_IP=${FRONT_IP:?FRONT_IP requis}
DOMAIN=${CTF_DOMAIN:?CTF_DOMAIN requis (deploy/front/.env)}
: "${CF_API_TOKEN:?CF_API_TOKEN requis (jeton API Cloudflare)}"
SSH="ssh -o StrictHostKeyChecking=accept-new -o ConnectTimeout=10 ubuntu@$FRONT_IP"
CERTDIR=${CERTDIR:-$HOME/.config/nctf26/origin-cert}
API=https://api.cloudflare.com/client/v4
auth=(-H "Authorization: Bearer $CF_API_TOKEN" -H 'Content-Type: application/json')

cf() { curl -fsS "${auth[@]}" "$@"; }

echo ">> zone Cloudflare de $DOMAIN"
ZONE=$(cf "$API/zones?name=$DOMAIN" | python3 -c 'import sys,json; r=json.load(sys.stdin)["result"]; print(r[0]["id"] if r else "")')
test -n "$ZONE" || { echo "ERREUR : zone $DOMAIN introuvable avec ce jeton"; exit 1; }
cf "$API/zones/$ZONE/dns_records?type=A&name=$DOMAIN" \
  | python3 -c 'import sys,json; [print("   A", r["name"], "->", r["content"], "proxied" if r["proxied"] else "DNS ONLY (le mode Full strict n a de sens que proxifie)") for r in json.load(sys.stdin)["result"]]'

echo ">> certificat d'origine (Origin CA, $DOMAIN + *.$DOMAIN)"
umask 077; mkdir -p "$CERTDIR"
if [ ! -s "$CERTDIR/fullchain.pem" ] || [ ! -s "$CERTDIR/privkey.pem" ]; then
  openssl req -new -newkey rsa:2048 -nodes -keyout "$CERTDIR/privkey.pem" -out "$CERTDIR/$DOMAIN.csr" \
    -subj "/CN=$DOMAIN" -addext "subjectAltName=DNS:$DOMAIN,DNS:*.$DOMAIN" 2>/dev/null
  python3 - "$CERTDIR" "$DOMAIN" <<'PY'
import json, os, sys, urllib.request
d, dom = sys.argv[1], sys.argv[2]
body = json.dumps({"hostnames": [dom, "*." + dom], "requested_validity": 5475,
                   "request_type": "origin-rsa", "csr": open(f"{d}/{dom}.csr").read()}).encode()
req = urllib.request.Request("https://api.cloudflare.com/client/v4/certificates", data=body,
        headers={"Authorization": "Bearer " + os.environ["CF_API_TOKEN"], "Content-Type": "application/json"})
r = json.load(urllib.request.urlopen(req))["result"]
open(f"{d}/fullchain.pem", "w").write(r["certificate"])
print("   emis, expire le", r["expires_on"])
PY
else
  echo "   deja present dans $CERTDIR ($(openssl x509 -in "$CERTDIR/fullchain.pem" -noout -enddate))"
fi

echo ">> depot du certificat sur le front (volume certbot_conf, live/$DOMAIN/)"
$SSH 'rm -rf /tmp/oc && mkdir -m 700 /tmp/oc'
scp -q "$CERTDIR/fullchain.pem" "$CERTDIR/privkey.pem" "ubuntu@$FRONT_IP:/tmp/oc/"
$SSH "V=\$(docker volume ls -q | grep certbot_conf | head -1); docker run --rm -v \$V:/le -v /tmp/oc:/src:ro alpine \
  sh -c 'mkdir -p /le/live/$DOMAIN && cp /src/fullchain.pem /src/privkey.pem /le/live/$DOMAIN/ && chmod 600 /le/live/$DOMAIN/privkey.pem'; rm -rf /tmp/oc"

echo ">> nginx : tls.conf + vraies IP clients (CF-Connecting-IP)"
# active.conf est un bind-mount de FICHIER dans le conteneur nginx : on ecrit
# EN PLACE (meme inode), jamais mv/rename, sinon le conteneur garde l'ancien
# inode. Et on recree le conteneur (pas un simple restart) pour qu'il reprenne
# le fichier meme si un montage precedent etait deja perime.
$SSH "set -euo pipefail; cd /opt/ctfd/CTFd; \
  C='docker compose -f deploy/front/docker-compose.prod.yml --env-file deploy/front/.env'; \
  cp deploy/front/nginx/active.conf /tmp/active.conf.bak 2>/dev/null || true; \
  sed 's|__CTF_DOMAIN__|$DOMAIN|g' deploy/front/nginx/tls.conf.template > deploy/front/nginx/active.conf; \
  rollback() { echo 'ERREUR nginx : retour a la config precedente'; \
     cat /tmp/active.conf.bak > deploy/front/nginx/active.conf; \$C up -d --force-recreate nginx >/dev/null; exit 1; }; \
  \$C up -d --force-recreate nginx >/dev/null; sleep 2; \
  \$C exec -T nginx nginx -t 2>&1 | grep -v proxy_headers_hash || rollback; \
  code=\$(curl -sk -o /dev/null -w '%{http_code}' --resolve arena.$DOMAIN:443:127.0.0.1 https://arena.$DOMAIN/healthcheck || true); \
  echo \"   origine https://arena.$DOMAIN/healthcheck -> \$code\"; test \"\$code\" = 200 || rollback"

echo ">> Cloudflare : SSL Full (strict), TLS minimum 1.2, HTTPS force, niveau de securite medium"
# security_level=high defie (JS challenge) les IP a mauvaise reputation : les
# joueurs derriere le CGNAT des FAI togolais et leurs scripts en feraient les frais.
for kv in ssl:strict min_tls_version:1.2 always_use_https:on security_level:medium; do
  k=${kv%%:*}; v=${kv#*:}
  cf -X PATCH "$API/zones/$ZONE/settings/$k" --data "{\"value\":\"$v\"}" >/dev/null && echo "   $k = $v"
done
# Bot Fight Mode bloque tout client non-navigateur (curl, python-requests,
# ctfcli) et n'admet aucune exception sur le plan Free : incompatible avec un CTF.
cf -X PUT "$API/zones/$ZONE/bot_management" --data '{"fight_mode":false}' >/dev/null && echo "   bot_fight_mode = off"
echo "   regles WAF personnalisees de la zone (a verifier a la main, voir PROD-SETUP.md) :"
cf "$API/zones/$ZONE/rulesets/phases/http_request_firewall_custom/entrypoint" \
  | python3 -c 'import sys,json; [print("     ", "ON " if r["enabled"] else "off", r["action"], "|", r["description"][:60], "|", r["expression"]) for r in json.load(sys.stdin)["result"].get("rules",[])]' || true

echo ">> verification a travers Cloudflare"
sleep 3
curl -fsS -o /dev/null -w "   https://$DOMAIN/ (vitrine) -> %{http_code} (%{ssl_verify_result})\n" "https://$DOMAIN/"
curl -fsS -o /dev/null -w "   https://arena.$DOMAIN/ (CTFd) -> %{http_code} (%{ssl_verify_result})\n" "https://arena.$DOMAIN/"
curl -sS -o /dev/null -w "   http://$DOMAIN/ -> %{http_code} vers %{redirect_url}\n" "http://$DOMAIN/"
echo "TLS actif derriere Cloudflare. Pensez a reserver 80/443 aux plages Cloudflare : web_cidrs (terraform.tfvars) + terraform apply."
