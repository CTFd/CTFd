#!/usr/bin/env python3
"""Check-list de mise en production NCTF26 -- refuse de valider tant qu'un point
est faux. Lecture seule : aucune ecriture sur CTFd.

    # stack locale (env du conteneur lu sur stdin, jamais affiche)
    docker compose exec -T ctfd printenv | python3 preflight.py --env-stdin \
        --url http://localhost:8000 --phase preselection --expect-challenges 203

    # prod : `make preflight PHASE=preselection` (voir deploy/Makefile)

Authentification (jamais en argument de ligne de commande, jamais affichee) :
    CTFD_TOKEN         jeton API admin (Authorization: Token ...)  -- prod
    CTFD_ADMIN_USER / CTFD_ADMIN_PASS   sinon, connexion par formulaire
                                        (defaut admin/admin : stack locale)

Sortie : une ligne [OK]/[WARN]/[FAIL]/[MANUAL] par verification, puis un bilan.
Code retour : 0 = aucun FAIL (les WARN sont tolerees), 1 = au moins un FAIL,
2 = impossible de joindre / de s'authentifier sur CTFd.
"""
import argparse
import os
import re
import sys
import time
from collections import Counter

OK, WARN, FAIL, MANUAL = "OK", "WARN", "FAIL", "MANUAL"

H = 3600
PHASES = {
    # duree attendue de la competition (tolerance +-1 h) ; freeze = derniere heure
    "preselection": {"duration": 53 * H, "registration": "public"},
    "finale": {"duration": 24 * H, "registration": "private"},
}
PLACEHOLDER_SECRETS = {
    "",
    "test-secret",
    "local-dev-koth-scorer",
    "ctfd",
    "changeme",
    "change-me",
    "secret",
    "password",
    "root",
}
BAD_FLAG_WORDS = ("test", "example", "changeme", "todo", "fixme", "xxx")
EXPECTED_NAME = "NCTF26"
EXPECTED_THEME = "hibris"
_ENV_LINE = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*)=(.*)$")


class Result:
    __slots__ = ("status", "section", "name", "detail")

    def __init__(self, status, section, name, detail=""):
        self.status, self.section, self.name, self.detail = (
            status,
            section,
            name,
            detail,
        )

    def __repr__(self):  # pragma: no cover - debugging aid
        return "<%s %s/%s %s>" % (self.status, self.section, self.name, self.detail)


def parse_env(text):
    """`printenv` -> dict. Lines that are not KEY=VALUE (multi-line values,
    banners) are ignored."""
    env = {}
    for line in text.splitlines():
        m = _ENV_LINE.match(line.rstrip("\r"))
        if m:
            env[m.group(1)] = m.group(2)
    return env


def _truthy(v):
    return str(v or "").strip().lower() in ("1", "true", "yes", "on")


def _int(v):
    try:
        return int(str(v).strip())
    except (TypeError, ValueError):
        return None


# ---------------------------------------------------------------------------
# Evaluateurs purs (testables sans reseau). Ils ne renvoient JAMAIS la valeur
# d'un secret dans `detail` : seulement son etat.
# ---------------------------------------------------------------------------
def check_secrets(env):
    S = "secrets"
    out = []
    if env is None:
        out.append(Result(WARN, S, "env", "env du conteneur non fournie (--env-stdin)"))
        return out

    def secret(name, required=True, min_len=32, hexpected=True):
        v = env.get(name)
        if v is None or v == "":
            out.append(Result(FAIL if required else WARN, S, name, "absent ou vide"))
            return
        if v.strip().lower() in PLACEHOLDER_SECRETS:
            out.append(Result(FAIL, S, name, "valeur de developpement / placeholder"))
            return
        if len(v) < min_len:
            out.append(Result(FAIL, S, name, "trop court (< %d caracteres)" % min_len))
            return
        if hexpected and not re.fullmatch(r"[0-9a-fA-F]+", v):
            out.append(
                Result(WARN, S, name, "pas un hex `openssl rand -hex 32` (tolere)")
            )
            return
        out.append(Result(OK, S, name, "pose, %d caracteres" % len(v)))

    secret("CTF_TEAM_FLAG_SECRET")
    secret("SECRET_KEY", hexpected=False)
    if env.get("KOTH_HILLS", "").strip():
        secret("KOTH_SCORER_SECRET", min_len=16)
        if env.get("KOTH_GLOBAL_SECRET"):
            secret("KOTH_GLOBAL_SECRET", min_len=16)
        else:
            out.append(
                Result(OK, S, "KOTH_GLOBAL_SECRET", "absent -> CTF_TEAM_FLAG_SECRET")
            )
    else:
        out.append(Result(OK, S, "KOTH_*", "KotH non configure (KOTH_HILLS vide)"))

    db_pw = [
        k
        for k in (
            "MARIADB_PASSWORD",
            "MARIADB_ROOT_PASSWORD",
            "DB_PASSWORD",
            "DB_ROOT_PASSWORD",
        )
        if k in env
    ]
    for k in db_pw:
        if env[k].strip().lower() in PLACEHOLDER_SECRETS:
            out.append(Result(FAIL, S, k, "mot de passe par defaut"))
        else:
            out.append(Result(OK, S, k, "pose"))
    url = env.get("DATABASE_URL", "")
    m = re.match(r"^[a-z+]+://([^:/@]+):([^@]*)@", url)
    if m:
        if m.group(2).lower() in PLACEHOLDER_SECRETS:
            out.append(Result(FAIL, S, "DATABASE_URL", "mot de passe DB par defaut"))
        else:
            out.append(Result(OK, S, "DATABASE_URL", "mot de passe DB non trivial"))
    elif url:
        out.append(Result(WARN, S, "DATABASE_URL", "forme inattendue, non verifiee"))
    else:
        out.append(Result(FAIL, S, "DATABASE_URL", "absente (SQLite ?)"))

    redis = env.get("REDIS_URL", "")
    if not redis:
        out.append(Result(FAIL, S, "REDIS_URL", "absente (cache/ratelimit en memoire)"))
    elif re.match(r"^rediss?://[^@/]+@", redis):
        out.append(Result(OK, S, "REDIS_URL", "protegee par mot de passe"))
    else:
        out.append(
            Result(
                WARN,
                S,
                "REDIS_URL",
                "sans mot de passe : acceptable seulement sur le reseau compose interne",
            )
        )
    return out


def check_windows(configs, phase, now=None, allow_running=False):
    S = "fenetres"
    out = []
    now = time.time() if now is None else now
    start, freeze, end = (_int(configs.get(k)) for k in ("start", "freeze", "end"))
    if _truthy(configs.get("paused")):
        out.append(Result(FAIL, S, "paused", "le CTF est en pause"))
    missing = [
        k for k, v in (("start", start), ("freeze", freeze), ("end", end)) if not v
    ]
    if missing:
        out.append(
            Result(FAIL, S, "start/freeze/end", "non poses : " + ", ".join(missing))
        )
        return out
    if not (start < freeze < end):
        out.append(Result(FAIL, S, "ordre", "il faut start < freeze < end"))
        return out
    out.append(
        Result(
            OK,
            S,
            "ordre",
            "%s -> gel %s -> %s (UTC)" % (_fmt(start), _fmt(freeze), _fmt(end)),
        )
    )
    if end <= now:
        out.append(Result(FAIL, S, "end", "deja dans le passe"))
    if start < now - H and not allow_running:
        out.append(
            Result(
                FAIL,
                S,
                "start",
                "dans le passe depuis plus d'1 h (--allow-running si voulu)",
            )
        )
    elif start < now:
        out.append(Result(WARN, S, "start", "deja passe : competition en cours"))
    else:
        out.append(Result(OK, S, "start", "dans %s" % _dur(start - now)))
    if phase in PHASES:
        want = PHASES[phase]["duration"]
        got = end - start
        if abs(got - want) <= H:
            out.append(Result(OK, S, "duree", "%s (%s attendu)" % (_dur(got), phase)))
        else:
            out.append(
                Result(
                    FAIL,
                    S,
                    "duree",
                    "%s au lieu de %s pour la %s" % (_dur(got), _dur(want), phase),
                )
            )
    if abs((end - freeze) - H) <= 300:
        out.append(Result(OK, S, "freeze", "derniere heure gelee"))
    else:
        out.append(
            Result(
                WARN,
                S,
                "freeze",
                "gel %s avant la fin (convention : la derniere heure)"
                % _dur(end - freeze),
            )
        )
    return out


def check_identity(configs, phase, team_size=None):
    S = "identite"
    out = []

    def eq(key, want, level=FAIL, label=None):
        got = str(configs.get(key, "") or "")
        if got == want:
            out.append(Result(OK, S, key, got))
        else:
            out.append(Result(level, S, key, "%r au lieu de %r" % (got, want)))

    eq("ctf_name", EXPECTED_NAME)
    eq("ctf_theme", EXPECTED_THEME)
    eq("user_mode", "teams")
    ts = _int(configs.get("team_size"))
    if team_size is not None:
        if ts == team_size:
            out.append(Result(OK, S, "team_size", str(ts)))
        else:
            out.append(
                Result(FAIL, S, "team_size", "%r au lieu de %d" % (ts, team_size))
            )
    elif not ts:
        out.append(Result(WARN, S, "team_size", "illimite (aucune borne)"))
    else:
        out.append(Result(OK, S, "team_size", str(ts)))
    if phase in PHASES:
        eq("registration_visibility", PHASES[phase]["registration"])
    else:
        out.append(
            Result(
                OK,
                S,
                "registration_visibility",
                str(configs.get("registration_visibility")),
            )
        )
    eq("score_visibility", "public", level=WARN)
    eq("account_visibility", "public", level=WARN)
    eq("challenge_visibility", "private", level=WARN)
    ve = _truthy(configs.get("verify_emails"))
    if phase == "preselection" and not ve:
        out.append(
            Result(WARN, S, "verify_emails", "desactivee (inscriptions ouvertes)")
        )
    else:
        out.append(Result(OK, S, "verify_emails", "activee" if ve else "desactivee"))
    return out


def check_email(configs, env, phase):
    """Quand `verify_emails` est ON, l'inscription DEPEND de l'envoi SMTP : un
    SMTP absent ou cassé bloque tout nouveau joueur (lockout massif le soir J).

    On vérifie au moins que le SMTP est *configuré* — via la config CTFd (Admin
    → Email) OU la variable d'env `MAIL_SERVER` (notre cas : le compose injecte
    les MAIL_* ; ils ne remontent alors PAS dans /api/v1/configs). Configuré ne
    veut pas dire qui-marche : on rappelle de PROUVER l'envoi avec `make
    mail-test` avant d'ouvrir. Silencieux si la vérification est OFF.
    """
    S = "email"
    out = []
    if not _truthy(configs.get("verify_emails")):
        return out
    server = str(configs.get("mail_server") or "").strip()
    if not server and env:
        server = str(env.get("MAIL_SERVER") or "").strip()
    if not server:
        out.append(
            Result(
                FAIL,
                S,
                "smtp",
                "verify_emails ON mais aucun SMTP (ni config CTFd ni MAIL_SERVER) "
                "-> lockout a l'inscription ; configurer le SMTP (PROD-SETUP "
                "§2bis) ou verify_emails=OFF",
            )
        )
        return out
    out.append(Result(OK, S, "smtp", "configure (%s)" % server))
    out.append(
        Result(
            MANUAL,
            S,
            "envoi",
            "verify_emails ON : PROUVER l'envoi avant d'ouvrir -> "
            "`make mail-test TO=<toi>` (config != envoi qui marche : mot de "
            "passe, DKIM, port).",
        )
    )
    return out


def check_registration(configs, user_fields, phase):
    """Ce que l'inscription exige : le reglement derriere /tos (case « j'accepte »
    obligatoire du theme) et le champ user « Universite » requis (liste deroulante)."""
    S = "inscription"
    out = []
    level = FAIL if phase == "preselection" else WARN
    if configs.get("tos_url") or (configs.get("tos_text") or "").strip():
        out.append(Result(OK, S, "reglement", "/tos sert le reglement"))
    else:
        out.append(
            Result(level, S, "reglement", "tos_text vide : make reglement-publish")
        )
    uni = [
        f for f in (user_fields or []) if "universit" in (f.get("name") or "").lower()
    ]
    if not uni:
        out.append(
            Result(level, S, "universite", "champ user absent (make local-seed)")
        )
    elif not uni[0].get("required"):
        out.append(Result(level, S, "universite", "champ present mais facultatif"))
    else:
        out.append(Result(OK, S, "universite", "champ requis"))
    return out


def check_content(challenges, flags, expect_challenges=None, expect_categories=None):
    S = "contenu"
    out = []
    # On verifie le set VISIBLE (ce que voient les joueurs) : les challenges
    # laisses `hidden` (ex. doublons pre-dedup archives) ne doivent pas fausser
    # le compte. Le detail des caches est signale plus bas.
    visible = [c for c in challenges if c.get("state") == "visible"]
    n = len(visible)
    if expect_challenges is not None and n != expect_challenges:
        out.append(
            Result(
                FAIL,
                S,
                "challenges",
                "%d visibles au lieu de %d (%d au total dont %d caches)"
                % (n, expect_challenges, len(challenges), len(challenges) - n),
            )
        )
    elif n == 0:
        out.append(Result(FAIL, S, "challenges", "aucun challenge visible"))
    else:
        out.append(
            Result(
                OK, S, "challenges", "%d visibles (%d au total)" % (n, len(challenges))
            )
        )
    cats = Counter(c.get("category") for c in visible)
    if expect_categories is not None and len(cats) != expect_categories:
        out.append(
            Result(
                FAIL,
                S,
                "categories",
                "%d au lieu de %d" % (len(cats), expect_categories),
            )
        )
    else:
        out.append(Result(OK, S, "categories", "%d" % len(cats)))
    hidden = [c["name"] for c in challenges if c.get("state") != "visible"]
    if hidden:
        out.append(
            Result(
                WARN,
                S,
                "hidden",
                "%d non visibles : %s%s"
                % (
                    len(hidden),
                    ", ".join(hidden[:5]),
                    "..." if len(hidden) > 5 else "",
                ),
            )
        )
    else:
        out.append(Result(OK, S, "hidden", "tous visibles"))
    by_chal = {}
    for f in flags:
        by_chal.setdefault(f.get("challenge_id"), []).append(f)
    no_flag = [c["name"] for c in challenges if not by_chal.get(c["id"])]
    if no_flag:
        out.append(
            Result(
                FAIL,
                S,
                "flags",
                "%d challenge(s) sans flag : %s%s"
                % (
                    len(no_flag),
                    ", ".join(no_flag[:5]),
                    "..." if len(no_flag) > 5 else "",
                ),
            )
        )
    else:
        out.append(Result(OK, S, "flags", "chaque challenge a au moins un flag"))
    names = {c["id"]: c["name"] for c in challenges}
    suspicious, empty, hmac = [], [], 0
    for f in flags:
        content = (f.get("content") or "").strip()
        if not content:
            empty.append(names.get(f.get("challenge_id"), "?"))
            continue
        if f.get("type") == "team_hmac":
            hmac += 1
            continue
        low = content.lower()
        if any(w in low for w in BAD_FLAG_WORDS):
            suspicious.append(names.get(f.get("challenge_id"), "?"))
    if empty:
        out.append(Result(FAIL, S, "flags vides", ", ".join(empty[:5])))
    if suspicious:
        out.append(
            Result(
                FAIL,
                S,
                "flags de test",
                "%d flag(s) contiennent test/example/changeme : %s%s"
                % (
                    len(suspicious),
                    ", ".join(suspicious[:5]),
                    "..." if len(suspicious) > 5 else "",
                ),
            )
        )
    else:
        out.append(Result(OK, S, "flags de test", "aucun"))
    out.append(Result(OK, S, "team_hmac", "%d flag(s) par equipe" % hmac))
    return out


def check_koth(state, env):
    S = "koth"
    out = []
    configured = bool((env or {}).get("KOTH_HILLS", "").strip())
    if state is None:
        if configured:
            out.append(
                Result(
                    FAIL,
                    S,
                    "plugin",
                    "KOTH_HILLS pose mais /plugins/koth/api/admin injoignable",
                )
            )
        else:
            out.append(Result(OK, S, "plugin", "inactif (aucune colline configuree)"))
        return out
    if not state.get("active"):
        if configured:
            out.append(
                Result(
                    FAIL,
                    S,
                    "plugin",
                    "KOTH_HILLS pose mais plugin inactif (secret manquant ?)",
                )
            )
        else:
            out.append(Result(OK, S, "plugin", "inactif (aucune colline configuree)"))
        return out
    hills = state.get("hills") or []
    if not hills:
        out.append(Result(FAIL, S, "collines", "plugin actif sans colline"))
    for h in hills:
        king = h.get("king") or {}
        if king.get("online"):
            out.append(
                Result(
                    OK,
                    S,
                    h.get("id", "?"),
                    "%s en ligne, %s pts/tick" % (h.get("name"), h.get("points")),
                )
            )
        else:
            out.append(
                Result(
                    FAIL,
                    S,
                    h.get("id", "?"),
                    "hors ligne%s" % (" (%s)" % h["error"] if h.get("error") else ""),
                )
            )
    return out


def check_theme(home_html, env):
    S = "theme"
    out = []
    if home_html is None:
        out.append(Result(FAIL, S, "accueil", "page / injoignable"))
    elif "nctf-intro" in home_html:
        out.append(Result(OK, S, "accueil", "intro cinematique presente"))
    else:
        out.append(
            Result(
                WARN,
                S,
                "accueil",
                "pas de bloc `nctf-intro` (seed non passe ou HTML assaini)",
            )
        )
    if env is not None and _truthy(env.get("HTML_SANITIZATION")):
        out.append(
            Result(
                WARN,
                S,
                "HTML_SANITIZATION",
                "activee : l'intro et le <style> de l'accueil seront supprimes",
            )
        )
    else:
        out.append(Result(OK, S, "HTML_SANITIZATION", "desactivee"))
    return out


def manual_checks():
    S = "manuel"
    return [
        Result(
            MANUAL, S, "instancier", "spawn/kill d'une instance temoin (RUNBOOK §2)"
        ),
        Result(
            MANUAL, S, "passerelle IA", "un prompt de test sur la piste IA (RUNBOOK §2)"
        ),
        Result(
            MANUAL,
            S,
            "images arena",
            "`make check-arena` : les 26 images ctf-* presentes",
        ),
    ]


def exit_code(results):
    return 1 if any(r.status == FAIL for r in results) else 0


# ---------------------------------------------------------------------------
# Affichage
# ---------------------------------------------------------------------------
def _fmt(ts):
    return time.strftime("%Y-%m-%d %H:%M", time.gmtime(ts))


def _dur(s):
    s = int(s)
    d, s = divmod(s, 86400)
    h, s = divmod(s, 3600)
    m = s // 60
    parts = []
    if d:
        parts.append("%dj" % d)
    if h or d:
        parts.append("%dh" % h)
    parts.append("%02dm" % m)
    return " ".join(parts)


def report(results, out=None):
    out = out or sys.stdout
    section = None
    for r in results:
        if r.section != section:
            section = r.section
            print("== %s ==" % section, file=out)
        print("  [%-6s] %-24s %s" % (r.status, r.name, r.detail), file=out)
    c = Counter(r.status for r in results)
    print(file=out)
    print(
        "Bilan : %d OK, %d WARN, %d FAIL, %d a verifier a la main"
        % (c[OK], c[WARN], c[FAIL], c[MANUAL]),
        file=out,
    )
    print(
        "=> "
        + ("PRET" if c[FAIL] == 0 else "REFUSE : corriger les FAIL puis relancer"),
        file=out,
    )


# ---------------------------------------------------------------------------
# Collecte (reseau)
# ---------------------------------------------------------------------------
def _session(url):
    import requests

    s = requests.Session()
    s.headers["Accept"] = "application/json"
    token = os.environ.get("CTFD_TOKEN")
    if token:
        s.headers["Authorization"] = "Token " + token
        # CTFd n'honore le jeton qu'avec un Content-Type JSON (sinon 302 /login).
        s.headers["Content-Type"] = "application/json"
        return s
    user = os.environ.get("CTFD_ADMIN_USER", "admin")
    pw = os.environ.get("CTFD_ADMIN_PASS", "admin")
    r = s.get(url + "/login", headers={"Accept": "text/html"})
    m = re.search(r"'csrfNonce':\s*\"([0-9a-f]+)\"", r.text)
    r = s.post(
        url + "/login",
        data={"name": user, "password": pw, "nonce": m.group(1) if m else ""},
        headers={"Accept": "text/html"},
        allow_redirects=False,
    )
    if r.status_code != 302:
        raise SystemExit("connexion admin refusee (CTFD_TOKEN ou CTFD_ADMIN_USER/PASS)")
    return s


def _get(s, url, path, ok=(200,), required=False):
    r = s.get(url + path, timeout=20)
    if r.status_code not in ok:
        if required:
            raise SystemExit("%s -> HTTP %d" % (path, r.status_code))
        return None
    return r


def collect(url):
    """Renvoie (configs, user_fields, challenges, flags, koth_state, home_html)."""
    import requests

    try:
        s = _session(url)
        r = s.get(url + "/api/v1/configs", timeout=20)
    except requests.RequestException as e:
        raise SystemExit("CTFd injoignable : %s" % e.__class__.__name__)
    if r.status_code in (401, 403):
        raise SystemExit("acces admin refuse sur /api/v1/configs (jeton non admin ?)")
    if r.status_code != 200:
        raise SystemExit("/api/v1/configs -> HTTP %d" % r.status_code)
    configs = {c["key"]: c["value"] for c in r.json()["data"]}
    r = _get(s, url, "/api/v1/configs/fields?type=user")
    user_fields = r.json()["data"] if r is not None else []
    challenges = _get(s, url, "/api/v1/challenges?view=admin", required=True).json()[
        "data"
    ]
    # the list omits `state`: mark everything not in the visible subset
    visible = {
        c["id"]
        for c in _get(
            s, url, "/api/v1/challenges?view=admin&state=visible", required=True
        ).json()["data"]
    }
    for c in challenges:
        c["state"] = "visible" if c["id"] in visible else "hidden"
    flags = _get(s, url, "/api/v1/flags", required=True).json()["data"]
    r = _get(s, url, "/plugins/koth/api/admin")
    koth = r.json() if r is not None else None
    r = requests.get(url + "/", timeout=20)
    home = r.text if r.status_code == 200 else None
    return configs, user_fields, challenges, flags, koth, home


def main(argv=None):
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument(
        "--url", default=os.environ.get("CTFD_URL", "http://localhost:8000")
    )
    ap.add_argument("--phase", choices=sorted(PHASES) + ["none"], default="none")
    ap.add_argument(
        "--env-stdin",
        action="store_true",
        help="lire `printenv` du conteneur CTFd sur stdin",
    )
    ap.add_argument("--expect-challenges", type=int, default=None)
    ap.add_argument("--expect-categories", type=int, default=None)
    ap.add_argument("--team-size", type=int, default=None)
    ap.add_argument(
        "--allow-running", action="store_true", help="tolerer un start deja passe"
    )
    a = ap.parse_args(argv)
    url = a.url.rstrip("/")

    env = parse_env(sys.stdin.read()) if a.env_stdin else None
    try:
        configs, user_fields, challenges, flags, koth, home = collect(url)
    except SystemExit as e:
        print("[FAIL] %s" % e, file=sys.stderr)
        return 2

    results = []
    results += check_secrets(env)
    results += check_windows(configs, a.phase, allow_running=a.allow_running)
    results += check_identity(configs, a.phase, a.team_size)
    results += check_email(configs, env, a.phase)
    results += check_registration(configs, user_fields, a.phase)
    results += check_content(
        challenges, flags, a.expect_challenges, a.expect_categories
    )
    results += check_koth(koth, env)
    results += check_theme(home, env)
    results += manual_checks()
    report(results)
    return exit_code(results)


if __name__ == "__main__":
    sys.exit(main())
