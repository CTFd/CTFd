#!/usr/bin/env python3
"""Initialise un CTFd vierge comme il le sera le jour J, puis importe les
challenges. Idempotent : relancable sans casser ce qui existe.

  python3 deploy/local/seed.py [--url http://localhost:8000] [--only web/jwt-cousin ...]

Etapes :
  1. attend que CTFd reponde ;
  2. /setup  : nom, mode EQUIPES, admin, theme hibris ;
  3. accueil : remplace le contenu CMS par defaut (qui trahit CTFd) par
     deploy/theme-home-hero.html ;
  4. jeton API admin -> ctfcli -> `ctf challenge install` sur chaque dossier,
     dans un ordre qui respecte les prerequis (ai0 -> ai1 -> ai2 -> ai3) ;
  5. une equipe de test (playtest / playtest) pour le playtest et les essais
     manuels.

Pre-requis sur la machine : pip install ctfcli requests
Identifiants crees : admin / admin (compte admin), playtest / playtest (joueur).

Hors stack locale (bascule de fenetre sur la prod : `make presel-window APPLY=1
URL=https://...`), s'authentifier par CTFD_TOKEN (jeton API admin) ou par
CTFD_ADMIN_USER / CTFD_ADMIN_PASS -- jamais en argument de ligne de commande.
"""
import argparse
import glob
import os
import re
import subprocess
import sys
import tempfile
import time
from pathlib import Path

try:
    import requests
except ImportError:
    sys.exit("pip install requests ctfcli")

ROOT = Path(__file__).resolve().parents[2]
# ctfcli installe dans le meme environnement que l'interpreteur courant (venv), sinon PATH.
CTF_BIN = (
    str(Path(sys.executable).parent / "ctf")
    if (Path(sys.executable).parent / "ctf").exists()
    else "ctf"
)
CHALLENGES = ROOT / "challenges"
HERO = ROOT / "deploy" / "theme-home-hero.html"
REGLEMENT = ROOT / "deploy" / "reglement.md"

ADMIN = {"name": "admin", "email": "admin@nctf.local", "password": "admin"}
PLAYER = {"name": "playtest", "email": "playtest@nctf.local", "password": "playtest"}
TEAM = {"name": "playtest", "password": "playtest"}

# Les prerequis sont resolus PAR NOM par ctfcli : la cible doit deja exister.
INSTALL_LAST = [
    "ai/ai0-leaked-transcript",
    "ai/ai1-naive-guard",
    "ai/ai2-output-filter",
    "ai/ai3-tool-abuse",
]


def log(msg):
    print(msg, flush=True)


def nonce_of(html):
    m = re.search(r"'csrfNonce':\s*\"([0-9a-f]+)\"", html) or re.search(
        r'name="nonce" value="([0-9a-f]+)"', html
    )
    if not m:
        raise SystemExit("nonce CSRF introuvable dans la page")
    return m.group(1)


def wait_for(url, timeout=180):
    log(f">> attente de {url}")
    t0 = time.time()
    while time.time() - t0 < timeout:
        try:
            r = requests.get(url + "/healthcheck", timeout=5)
            if r.status_code == 200:
                return
        except requests.RequestException:
            pass
        time.sleep(2)
    raise SystemExit("CTFd ne repond pas (make local-logs ?)")


def is_prod():
    """Un jeton API = plateforme de prod (le local se connecte en admin/admin).
    Garde-fou : jamais de /setup admin/admin ni de compte playtest en prod."""
    return bool(os.environ.get("CTFD_TOKEN"))


def do_setup(url):
    s = requests.Session()
    r = s.get(url + "/setup", allow_redirects=False)
    if r.status_code != 200:
        log("   setup deja fait, on passe")
        return
    if is_prod():
        raise SystemExit(
            "REFUS : /setup n'est pas fait et CTFD_TOKEN est pose : faire le /setup "
            "a la main avec un mot de passe fort (deploy/PROD-SETUP.md §2)."
        )
    data = {
        "ctf_name": "NCTF26",
        "ctf_description": "NCTF26 — CTF national de cybersécurité du Togo, organisé par le CERT.tg. Présélection en ligne du vendredi 23 octobre 19:00 au lundi 26 octobre 00:00 (53 h, non-stop), finale à Lomé 29–30 octobre.",
        "user_mode": "teams",
        "name": ADMIN["name"],
        "email": ADMIN["email"],
        "password": ADMIN["password"],
        "ctf_theme": "hibris",
        "theme_color": "",
        "verify_emails": "false",
        "challenge_visibility": "private",
        "account_visibility": "public",
        "score_visibility": "public",
        "registration_visibility": "public",
        # La fenêtre (start / end / freeze) est appliquée par set_configs() via
        # CTF_START / CTF_END / CTF_FREEZE : idempotent, ça marche aussi sur une
        # instance déjà installée (bascule présélection -> finale sans reset).
        # Voir deploy/event-windows.env.example. Vide ici => local reste ouvert.
        "start": "",
        "end": "",
        "team_size": os.environ.get("CTF_TEAM_SIZE", ""),
        "nonce": nonce_of(r.text),
    }
    r = s.post(url + "/setup", data=data, allow_redirects=False)
    if r.status_code not in (302, 200):
        raise SystemExit(f"setup: HTTP {r.status_code}\n{r.text[:500]}")
    log("   setup OK : NCTF26, mode equipes, theme hibris, admin/admin")


def admin_session(url):
    s = requests.Session()
    token = os.environ.get("CTFD_TOKEN")
    if token:
        # Prod : CTFd n'honore le jeton qu'avec Content-Type: application/json.
        s.headers["Authorization"] = "Token " + token
        s.headers["Content-Type"] = "application/json"
        r = s.get(url + "/api/v1/configs")
        if r.status_code != 200:
            raise SystemExit("CTFD_TOKEN refuse (jeton non admin ?)")
        return s
    r = s.get(url + "/login")
    r = s.post(
        url + "/login",
        data={
            "name": os.environ.get("CTFD_ADMIN_USER", ADMIN["name"]),
            "password": os.environ.get("CTFD_ADMIN_PASS", ADMIN["password"]),
            "nonce": nonce_of(r.text),
        },
        allow_redirects=False,
    )
    if r.status_code != 302:
        raise SystemExit("login admin impossible")
    s.headers["CSRF-Token"] = nonce_of(s.get(url + "/").text)
    return s


def api_token(s, url):
    if os.environ.get("CTFD_TOKEN"):
        return os.environ["CTFD_TOKEN"]
    r = s.post(url + "/api/v1/tokens", json={"description": "seed local"})
    r.raise_for_status()
    return r.json()["data"]["value"]


def set_home(s, url):
    if not HERO.exists():
        log(f"   {HERO} absent, accueil laisse tel quel")
        return
    pages = s.get(url + "/api/v1/pages").json()["data"]
    home = next((p for p in pages if p["route"] in ("index", "")), None)
    if not home:
        log("   page d'accueil introuvable")
        return
    content = HERO.read_text(encoding="utf-8")
    r = s.patch(
        url + f"/api/v1/pages/{home['id']}", json={"content": content, "format": "html"}
    )
    r.raise_for_status()
    log("   accueil remplace par deploy/theme-home-hero.html")


def set_configs(s, url):
    cfg = {"ctf_theme": "hibris", "user_mode": "teams"}
    # Fenêtre de compétition + gel du scoreboard depuis l'environnement (epoch
    # secondes, GMT/Lomé). Absents => inchangés (le local reste ouvert). Valeurs
    # présélection / finale : voir deploy/event-windows.env.example.
    for key, env in (
        ("start", "CTF_START"),
        ("end", "CTF_END"),
        ("freeze", "CTF_FREEZE"),
    ):
        v = os.environ.get(env)
        if v:
            cfg[key] = v
    if REGLEMENT.exists():
        # Reglement -> page /tos (Markdown), referencee par l'inscription.
        cfg["tos_text"] = REGLEMENT.read_text(encoding="utf-8")
    r = s.patch(url + "/api/v1/configs", json=cfg)
    r.raise_for_status()
    applied = [k for k in ("start", "end", "freeze") if k in cfg]
    if applied:
        log("   config: " + ", ".join(f"{k}={cfg[k]}" for k in applied))


def installed_names(s, url):
    return {
        c["name"] for c in s.get(url + "/api/v1/challenges?view=admin").json()["data"]
    }


def patch_dynamic_scoring(s, url):
    """Certaines versions de ctfcli n'ecrivent pas initial/minimum/decay/function
    des challenges dynamiques/servis a l'install -> ils restent NULL en base et la
    1re resolution fraiche plante (decay.logarithmic: minimum-initial sur None).
    On lit extra: du challenge.yml et on PATCH ce qui manque (idempotent). En prod
    ces champs sont deja poses ; ici ca aligne le local sur la prod."""
    import yaml  # PyYAML est une dep de ctfcli, donc dispo dans le venv

    by_name = {}
    for y in glob.glob(str(CHALLENGES / "*/*/challenge.yml")):
        try:
            doc = yaml.safe_load(Path(y).read_text())
        except Exception:
            continue
        if not isinstance(doc, dict):
            continue
        by_name[doc.get("name")] = doc
    fixed = 0
    for c in s.get(url + "/api/v1/challenges?view=admin").json()["data"]:
        if c.get("type") not in ("team_instance", "dynamic"):
            continue
        detail = s.get(url + f"/api/v1/challenges/{c['id']}").json().get("data", {})
        if detail.get("initial") not in (None, ""):
            continue  # deja renseigne
        doc = by_name.get(c["name"]) or {}
        extra = doc.get("extra") or {}
        value = doc.get("value") or detail.get("value") or 500
        initial = extra.get("initial", value)
        minimum = extra.get("minimum", max(1, int(initial) // 5))
        decay = extra.get("decay", 30)
        function = extra.get("function", "logarithmic")
        body = {
            "value": initial,
            "initial": initial,
            "minimum": minimum,
            "decay": decay,
            "function": function,
        }
        r = s.patch(url + f"/api/v1/challenges/{c['id']}", json=body)
        if r.ok:
            fixed += 1
        else:
            log(f"   scoring KO {c['name']}: {r.status_code} {r.text[:100]}")
    if fixed:
        log(f">> scoring dynamique corrige sur {fixed} challenge(s)")


def install_challenges(url, token, only, already):
    dirs = sorted(
        str(Path(p).parent.relative_to(CHALLENGES))
        for p in glob.glob(str(CHALLENGES / "*/*/challenge.yml"))
    )
    if only:
        dirs = [d for d in dirs if d in only]
    ordered = [d for d in dirs if d not in INSTALL_LAST] + [
        d for d in INSTALL_LAST if d in dirs
    ]
    with tempfile.TemporaryDirectory() as tmp:
        (Path(tmp) / ".ctf").mkdir()
        (Path(tmp) / ".ctf" / "config").write_text(
            f"[config]\nurl = {url}\naccess_token = {token}\n\n[challenges]\n"
        )
        ok, ko, skip = [], [], []
        for d in ordered:
            name = (
                re.search(
                    r"^name:\s*(.+)$",
                    (CHALLENGES / d / "challenge.yml").read_text(),
                    re.M,
                )
                .group(1)
                .strip()
                .strip('"')
            )
            if name in already:
                skip.append(d)
                continue
            log(f">> ctf challenge install {d}")
            p = subprocess.run(
                [CTF_BIN, "challenge", "install", str(CHALLENGES / d)],
                cwd=tmp,
                capture_output=True,
                text=True,
            )
            if p.returncode == 0:
                ok.append(d)
            else:
                ko.append(d)
                log(
                    "   ECHEC\n"
                    + "\n".join(
                        "   | " + l
                        for l in (p.stdout + p.stderr).strip().splitlines()[-12:]
                    )
                )
    return ok, ko, skip


def ensure_university_field(s, url):
    """Champ user 'Université' (requis) affiché à l'inscription. Le thème hibris
    le rend en liste déroulante (components/universites_options.html). Idempotent."""
    fields = s.get(url + "/api/v1/configs/fields?type=user").json().get("data", [])
    if any("universit" in (f.get("name") or "").lower() for f in fields):
        log("   champ 'Université' déjà présent")
        return
    r = s.post(
        url + "/api/v1/configs/fields",
        json={
            "type": "user",
            "field_type": "text",
            "name": "Université",
            "description": "Votre établissement d'enseignement supérieur (ou « Autre / N/A »).",
            "required": True,
            "public": True,
            "editable": True,
        },
    )
    r.raise_for_status()
    log("   champ 'Université' créé (requis, liste déroulante à l'inscription)")


def ensure_player(s, url):
    users = {
        u["name"]: u for u in s.get(url + "/api/v1/users?view=admin").json()["data"]
    }
    if PLAYER["name"] not in users:
        r = s.post(
            url + "/api/v1/users", json={**PLAYER, "type": "user", "verified": True}
        )
        r.raise_for_status()
        users[PLAYER["name"]] = r.json()["data"]
    teams = {
        t["name"]: t for t in s.get(url + "/api/v1/teams?view=admin").json()["data"]
    }
    if TEAM["name"] not in teams:
        r = s.post(url + "/api/v1/teams", json=TEAM)
        r.raise_for_status()
        teams[TEAM["name"]] = r.json()["data"]
    team = teams[TEAM["name"]]
    members = s.get(url + f"/api/v1/teams/{team['id']}/members").json()["data"]
    if users[PLAYER["name"]]["id"] not in members:
        s.post(
            url + f"/api/v1/teams/{team['id']}/members",
            json={"user_id": users[PLAYER["name"]]["id"]},
        ).raise_for_status()
    log(
        f"   joueur {PLAYER['name']}/{PLAYER['password']} dans l'equipe {TEAM['name']} (id {team['id']})"
    )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--url",
        default=os.environ.get(
            "CTFD_URL", "http://localhost:" + os.environ.get("CTFD_PORT", "8000")
        ),
    )
    ap.add_argument(
        "--only", nargs="*", default=[], help="ex: web/jwt-cousin misc/proto-fuzz"
    )
    ap.add_argument("--no-challenges", action="store_true")
    ap.add_argument(
        "--no-player",
        action="store_true",
        help="ne cree pas le compte/equipe playtest (implicite avec CTFD_TOKEN)",
    )
    a = ap.parse_args()
    url = a.url.rstrip("/")

    wait_for(url)
    log(">> setup")
    do_setup(url)
    s = admin_session(url)
    log(">> config")
    set_configs(s, url)
    set_home(s, url)
    log(">> champ inscription")
    ensure_university_field(s, url)
    log(">> equipe de test")
    if a.no_player or is_prod():
        log("   prod (jeton API) ou --no-player : aucun compte playtest")
    else:
        ensure_player(s, url)
    if a.no_challenges:
        return
    log(">> challenges")
    ok, ko, skip = install_challenges(
        url, api_token(s, url), set(a.only), installed_names(s, url)
    )
    patch_dynamic_scoring(s, url)
    total = len(installed_names(s, url))
    log(
        f"\ninstalles : {len(ok)}   deja presents : {len(skip)}   en echec : {len(ko)}   -> {total} challenges sur la plateforme"
    )
    if ko:
        log("EN ECHEC : " + ", ".join(ko))
        sys.exit(1)


if __name__ == "__main__":
    main()
