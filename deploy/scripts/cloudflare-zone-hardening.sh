#!/usr/bin/env bash
# Durcissement de la zone Cloudflare de ctf.tg — plan Free uniquement.
#
# Applique (idempotent, relançable) ce qui a été posé le 2026-09-25 :
#   - réglages de zone : SSL Full (strict), TLS >= 1.2, HTTPS forcé, HSTS (1 an,
#     nosniff), Browser Integrity Check, security_level medium
#   - WAF : déploie le "Cloudflare Managed Free Ruleset" (phase managed)
#   - Rate limiting (1 règle sur Free) : 30 POST / 10 s / IP sur
#     /login /register /reset_password /confirm -> block 10 s
#   - Redirect www -> apex à la bordure (phase dynamic_redirect)
#   - DNSSEC : active la signature côté Cloudflare (le DS reste à poser au
#     registre .tg — affiché en sortie)
#   - DMARC : rapports gérés par Cloudflare (rua @dmarc-reports.cloudflare.net),
#     politique quarantine
#
# NE touche PAS : les règles WAF personnalisées existantes ("IP not from Togo",
# "Known bots blocked", skip /api/), les A/MX/DKIM, le certificat d'origine
# (voir cloudflare-origin-tls.sh) ni web_cidrs (cloudflare-ips.sh).
#
# Usage : set -a; . ~/.config/nctf26/cloudflare.env; set +a
#         deploy/scripts/cloudflare-zone-hardening.sh [--check]
# Variables : CF_API_TOKEN (obligatoire), CF_ZONE_ID (défaut : zone de ctf.tg),
#             CTF_DOMAIN (défaut ctf.tg). --check = lecture seule.
set -euo pipefail

: "${CF_API_TOKEN:?CF_API_TOKEN manquant (jeton API Cloudflare, jamais en argument)}"
CTF_DOMAIN="${CTF_DOMAIN:-ctf.tg}"
CF_ZONE_ID="${CF_ZONE_ID:-b36e2b1982d863f230fb0055f5244c48}"
CHECK=0; [ "${1:-}" = "--check" ] && CHECK=1
API="https://api.cloudflare.com/client/v4"
MANAGED_FREE_RULESET="77454fe2d30c4220b5701f6fdfb893ba" # Cloudflare Managed Free Ruleset (id global)

cf() { # cf METHOD PATH [JSON]
  local m=$1 p=$2 d=${3:-}
  if [ -n "$d" ]; then
    curl -sS -X "$m" "$API$p" -H "Authorization: Bearer $CF_API_TOKEN" -H 'Content-Type: application/json' --data "$d"
  else
    curl -sS -X "$m" "$API$p" -H "Authorization: Bearer $CF_API_TOKEN"
  fi
}
ok()   { python3 -c 'import sys,json; d=json.load(sys.stdin); sys.exit(0 if d.get("success") else 1)'; }
say()  { printf '  %-28s %s\n' "$1" "$2"; }
apply() { # apply LABEL METHOD PATH JSON
  if [ $CHECK = 1 ]; then say "$1" "(check) non appliqué"; return 0; fi
  if cf "$2" "$3" "$4" | ok; then say "$1" "OK"; else say "$1" "ECHEC"; return 1; fi
}

echo ">> Zone $CTF_DOMAIN ($CF_ZONE_ID)"
cf GET "/zones/$CF_ZONE_ID" | python3 -c 'import sys,json; d=json.load(sys.stdin)["result"]; print("  plan :", d["plan"]["name"], "| statut :", d["status"])'

echo ">> Réglages de zone"
for kv in ssl=strict min_tls_version=1.2 always_use_https=on browser_check=on security_level=medium tls_1_3=on 0rtt=off; do
  k=${kv%%=*}; v=${kv#*=}
  apply "$k=$v" PATCH "/zones/$CF_ZONE_ID/settings/$k" "{\"value\":\"$v\"}"
done
apply "HSTS 1 an + nosniff" PATCH "/zones/$CF_ZONE_ID/settings/security_header" \
  '{"value":{"strict_transport_security":{"enabled":true,"max_age":31536000,"include_subdomains":false,"preload":false,"nosniff":true}}}'

# --- Rulesets par phase : créés s'ils manquent, sinon remplacés (PUT) -------
phase_ruleset_id() { # phase_ruleset_id PHASE -> id ou vide
  cf GET "/zones/$CF_ZONE_ID/rulesets" | python3 -c 'import sys,json
d=json.load(sys.stdin); ph=sys.argv[1]
print(next((r["id"] for r in d.get("result",[]) if r.get("phase")==ph and r.get("kind")=="zone"), ""))' "$1"
}
put_phase() { # put_phase LABEL PHASE NAME RULES_JSON
  local id; id=$(phase_ruleset_id "$2")
  if [ -z "$id" ]; then
    apply "$1 (création)" POST "/zones/$CF_ZONE_ID/rulesets" "{\"name\":\"$3\",\"kind\":\"zone\",\"phase\":\"$2\",\"rules\":$4}"
  else
    apply "$1 (mise à jour)" PUT "/zones/$CF_ZONE_ID/rulesets/$id" "{\"rules\":$4}"
  fi
}

echo ">> WAF managé (Free)"
put_phase "Managed Free Ruleset" http_request_firewall_managed "NCTF26 managed WAF" \
  "[{\"action\":\"execute\",\"action_parameters\":{\"id\":\"$MANAGED_FREE_RULESET\"},\"expression\":\"true\",\"description\":\"Cloudflare Free Managed Ruleset\",\"enabled\":true}]"

echo ">> Rate limiting (1 règle Free : block, fenêtre 10 s)"
put_phase "Auth 30 POST/10 s/IP" http_ratelimit "NCTF26 rate limit" \
  '[{"action":"block","expression":"(http.request.method eq \"POST\" and http.request.uri.path in {\"/login\" \"/register\" \"/reset_password\" \"/confirm\"})","description":"Auth endpoints : max 30 POST / 10 s / IP","enabled":true,"ratelimit":{"characteristics":["ip.src","cf.colo.id"],"period":10,"requests_per_period":30,"mitigation_timeout":10}}]'

echo ">> Redirections à la bordure : www -> apex, challenge (ancien nom de la plateforme) -> arena"
# challenge.$CTF_DOMAIN doit exister en DNS et être proxifié (nuage orange) pour
# que la règle s'applique ; sinon les anciens liens tombent en 520/NXDOMAIN.
put_phase "www -> $CTF_DOMAIN, challenge -> arena" http_request_dynamic_redirect "NCTF26 redirects" \
  "[{\"action\":\"redirect\",\"expression\":\"(http.host eq \\\"www.$CTF_DOMAIN\\\")\",\"description\":\"www -> apex\",\"enabled\":true,\"action_parameters\":{\"from_value\":{\"status_code\":301,\"preserve_query_string\":true,\"target_url\":{\"expression\":\"concat(\\\"https://$CTF_DOMAIN\\\", http.request.uri.path)\"}}}},{\"action\":\"redirect\",\"expression\":\"(http.host eq \\\"challenge.$CTF_DOMAIN\\\")\",\"description\":\"challenge -> arena\",\"enabled\":true,\"action_parameters\":{\"from_value\":{\"status_code\":301,\"preserve_query_string\":true,\"target_url\":{\"expression\":\"concat(\\\"https://arena.$CTF_DOMAIN\\\", http.request.uri.path)\"}}}}]"

echo ">> DNSSEC"
if [ $CHECK = 0 ]; then cf PATCH "/zones/$CF_ZONE_ID/dnssec" '{"status":"active"}' >/dev/null; fi
cf GET "/zones/$CF_ZONE_ID/dnssec" | python3 -c 'import sys,json; d=json.load(sys.stdin)["result"]
print("  statut :", d.get("status"))
if d.get("ds"): print("  DS à poser au registre .tg :", d["ds"])'

echo ">> DMARC (rapports gérés par Cloudflare)"
if [ $CHECK = 0 ]; then cf PATCH "/zones/$CF_ZONE_ID/email/auth/dmarc-reports" '{"enabled":true,"skip_wizard":true}' >/dev/null; fi
RUA=$(cf GET "/zones/$CF_ZONE_ID/email/auth/dmarc-reports" | python3 -c 'import sys,json; print(json.load(sys.stdin)["result"]["rua_prefix"])')@dmarc-reports.cloudflare.net
DMARC="\"v=DMARC1; p=quarantine; pct=100; adkim=r; aspf=r; rua=mailto:$RUA\""
DMARC_ID=$(cf GET "/zones/$CF_ZONE_ID/dns_records?type=TXT&name=_dmarc.$CTF_DOMAIN" | python3 -c 'import sys,json; r=json.load(sys.stdin)["result"]; print(r[0]["id"] if r else "")')
if [ -z "$DMARC_ID" ]; then
  apply "_dmarc (création)" POST "/zones/$CF_ZONE_ID/dns_records" "{\"type\":\"TXT\",\"name\":\"_dmarc\",\"content\":$DMARC,\"ttl\":1}"
else
  apply "_dmarc (mise à jour)" PATCH "/zones/$CF_ZONE_ID/dns_records/$DMARC_ID" "{\"content\":$DMARC}"
fi

echo ">> Contrôles (lecture)"
cf GET "/zones/$CF_ZONE_ID/dns_records?per_page=100" | python3 -c 'import sys,json
rs=json.load(sys.stdin)["result"]
bad=[r["name"] for r in rs if r["proxied"] and (r["type"]=="CNAME" and ("mailgun" in r["content"] or "amazonses" in r["content"] or "sendinblue" in r["content"] or "brevo" in r["content"]))]
print("  enregistrements mail proxifiés (doivent être DNS-only) :", bad or "aucun")
spf=[r["content"] for r in rs if r["type"]=="TXT" and r["name"]==sys.argv[1] and "v=spf1" in r["content"]]
print("  SPF apex :", spf[0] if spf else "ABSENT")
dm=[r["content"] for r in rs if r["type"]=="TXT" and r["name"]=="_dmarc."+sys.argv[1]]
print("  DMARC    :", dm[0] if dm else "ABSENT")' "$CTF_DOMAIN"
cf GET "/zones/$CF_ZONE_ID/rulesets/phases/http_request_firewall_custom/entrypoint" | python3 -c 'import sys,json
d=json.load(sys.stdin)
for r in d.get("result",{}).get("rules",[]): print("  WAF perso :", "ON " if r["enabled"] else "off", "|", r["action"], "|", r.get("description",""))'
echo "Terminé. Vérifier : curl -sI https://$CTF_DOMAIN/ | grep -i strict ; et l'API CTFd (PATCH) à travers le WAF."
