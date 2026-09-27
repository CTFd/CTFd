#!/usr/bin/env python3
"""Playtest automatique : pour chaque challenge, fait exactement ce qu'une
equipe ferait — demander une instance, lancer le solveur de reference, soumettre
le flag — et verifie que la plateforme repond "correct".

  python3 deploy/local/playtest.py                      # tout ce qui est automatisable
  python3 deploy/local/playtest.py --only web/jwt-cousin pwn/heap-note
  python3 deploy/local/playtest.py --static-only        # sans instance Docker
  python3 deploy/local/playtest.py --ai                 # inclut ai1 (LLM reel, lent)
  python3 deploy/local/playtest.py --unlock-chain       # teste ai2/ai3 sans avoir resolu ai1

Pre-requis : `make local-up local-build-images local-seed` ; l'image ctf-playtest
(construite par `make local-playtest`) sinon --runner host avec pwntools/numpy/
scapy/requests/flask installes.

Verdicts :
  PASS    flag obtenu par le solveur ET accepte par la plateforme
  FAIL    le solveur a echoue, ou la plateforme a refuse le flag
  GATED   prerequis non remplis cote plateforme (chaine IA) -> --unlock-chain
  STUB    ai3/agent-tool-abuse : seul le self-test hors-ligne est automatisable ;
          la resolution live exige de jailbreaker un LLM (playtest humain)
  SKIP    necessite le profil IA (Ollama) -> --ai
"""
import argparse
import json
import os
import re
import shlex
import socket
import subprocess
import sys
import time
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[2]
CH = ROOT / "challenges"
FLAG_RE = re.compile(r"NCTF\{[^}\s]+\}")

# Comment lancer chaque solveur, cwd = dossier du challenge. Placeholders :
# {HOST} {PORT} {URL}. Source : deploy/local/solvers.json (catalogue des 36).
#   mode: static | served | stub | ai
PLAN = {
    "ai/agent-tool-abuse": (
        "stub",
        "MODEL_BACKEND=stub TEAM_SECRET=local-demo-team-secret python3 solution/solve.py",
        60,
    ),
    "ai/ai0-leaked-transcript": (
        "static",
        "python3 solution/solve.py public/transcript.json",
        30,
    ),
    "ai/ai1-naive-guard": ("ai", "python3 solution/solve.py {URL}", 900),
    "ai/ai2-output-filter": ("served", "python3 solution/solve.py {URL}", 120),
    "ai/ai3-tool-abuse": (
        "stub",
        "MODEL_BACKEND=stub TEAM_SECRET=local-demo-team-secret python3 solution/solve.py",
        60,
    ),
    "crypto/commit-bias": (
        "static",
        "python3 solution/solve.py handout/ledger.coinvault",
        60,
    ),
    "crypto/lcg-casino": ("served", "python3 solution/solve.py {HOST} {PORT}", 120),
    "crypto/nonce-sense": ("static", "python3 solution/solve.py capture.json", 1800),
    "crypto/padding-oracle-lite": (
        "served",
        "python3 solution/solve.py {HOST} {PORT}",
        300,
    ),
    "crypto/tlv-vault": ("static", "python3 solution/solve.py", 30),
    "forensics/audio-fsk": (
        "static",
        "python3 solution/solve.py transmission.wav",
        120,
    ),
    "forensics/dns-exfil": ("static", "python3 solution/solve.py capture.pcap", 60),
    "forensics/evasion-timeline": (
        "static",
        "python3 solution/solve.py sysmon.jsonl",
        60,
    ),
    "forensics/sram-retention": (
        "static",
        "python3 solution/solve.py retention.dump",
        30,
    ),
    "forensics/usb-keystrokes": (
        "static",
        "python3 solution/solve.py capture.pcap",
        30,
    ),
    "misc/esolang-jail": ("served", "python3 solution/solve.py {HOST} {PORT}", 120),
    "misc/git-archaeology": (
        "static",
        "bash solution/solve.sh logparse-cli.tar.gz",
        60,
    ),
    "misc/polyglot-onion": ("static", "python3 solution/solve.py keepsake.png", 30),
    "misc/proto-fuzz": ("served", "python3 solution/solve.py {HOST} {PORT}", 120),
    "misc/timing-channel": ("static", "python3 solution/solve.py capture.pcap", 60),
    "ml/adversarial-gate": ("served", "python3 solution/solve.py {URL}", 180),
    "ml/model-inversion": ("served", "python3 solution/solve.py {URL}", 120),
    "ml/pickle-rce": ("served", "python3 solution/solve.py {URL}", 60),
    "pwn/boot2root-linux": ("served", "bash solution/solve.sh {URL}", 120),
    "pwn/format-string-101": ("served", "python3 solution/solve.py {HOST} {PORT}", 120),
    "pwn/heap-note": ("served", "python3 solution/solve.py {HOST} {PORT}", 120),
    "pwn/ret2csu-ish": ("served", "python3 solution/solve.py {HOST} {PORT}", 120),
    "reverse/maze-vm": ("static", "python3 solution/solve.py ./chall", 60),
    "reverse/packed-vm-lite": ("static", "python3 solution/solve.py ./vmcheck", 30),
    "reverse/strings-lie": ("static", "python3 solution/solve.py ./chall", 60),
    "reverse/synthvm": ("static", "python3 solution/solve.py ./synthvm", 60),
    "web/graphql-introspection-maze": (
        "served",
        "python3 solution/solve.py {URL}",
        120,
    ),
    "web/jwt-cousin": ("served", "python3 solution/solve.py {URL}", 60),
    "web/race-the-coupon": ("served", "python3 solution/solve.py {URL}", 120),
    "web/smuggle-gap": ("served", "python3 solution/solve.py {URL}", 60),
    "web/ssrf-metadata-decoy": ("served", "python3 solution/solve.py {URL}", 120),
}
CHAIN = ["ai1-naive-guard", "ai2-output-filter", "ai3-tool-abuse"]


def nonce_of(html):
    m = re.search(r"'csrfNonce':\s*\"([0-9a-f]+)\"", html)
    return m.group(1) if m else ""


class Ctfd:
    def __init__(self, url, name, password):
        self.url = url.rstrip("/")
        self.s = requests.Session()
        r = self.s.get(self.url + "/login")
        r = self.s.post(
            self.url + "/login",
            data={"name": name, "password": password, "nonce": nonce_of(r.text)},
            allow_redirects=False,
        )
        if r.status_code != 302:
            sys.exit(f"login {name} impossible (make local-seed ?)")
        self.s.headers["CSRF-Token"] = nonce_of(self.s.get(self.url + "/").text)

    def challenges_admin(self):
        return self.s.get(self.url + "/api/v1/challenges?view=admin").json()["data"]

    def get(self, cid):
        return self.s.get(self.url + f"/api/v1/challenges/{cid}").json()["data"]

    def patch(self, cid, body):
        return self.s.patch(self.url + f"/api/v1/challenges/{cid}", json=body)

    def spawn(self, cid):
        return self.s.post(
            self.url + "/plugins/team_instancer/spawn", json={"challenge_id": cid}
        )

    def destroy(self, cid):
        r = self.s.post(
            self.url + "/plugins/team_instancer/destroy", json={"challenge_id": cid}
        )
        if r.status_code != 200:
            print(
                f"   !! destroy cid={cid} -> HTTP {r.status_code}: {r.text[:150]}",
                flush=True,
            )
        return r

    def attempt(self, cid, flag):
        r = self.s.post(
            self.url + "/api/v1/challenges/attempt",
            json={"challenge_id": cid, "submission": flag},
        )
        try:
            return r.json()["data"]["status"], r.json()["data"].get("message", "")
        except Exception:
            return f"http {r.status_code}", r.text[:200]


def spawn_resilient(player, url, cid, tries=5):
    """Spawn en gerant les deux 429 possibles : plafond d'instances par equipe
    (-> on purge toutes les instances de l'equipe puis on retente) et rate-limit
    anti-abus 6/60s sur /spawn (-> on attend la fenetre puis on retente). Le
    rate-limit est un controle voulu en prod ; ici on le subit parce qu'un
    playtest sequentiel spawne bien plus vite qu'une equipe reelle."""
    for _ in range(tries):
        r = player.spawn(cid)
        if r.status_code != 429:
            return r
        try:
            msg = r.json().get("error", "")
        except Exception:
            msg = r.text
        if "instances" in msg.lower():  # plafond par equipe
            for oc in player.s.get(url + "/api/v1/challenges").json().get("data", []):
                player.destroy(oc["id"])
        else:  # rate-limit 6/60s : attendre la fenetre
            print("   rate-limit /spawn (6/60s) atteint, attente 62s...", flush=True)
            time.sleep(62)
    return r


def wait_http(url, timeout=120):
    """Attend que CTFd reponde (il vient peut-etre d'etre (re)cree par make local-up :
    gunicorn + flask db upgrade prennent quelques secondes)."""
    t0 = time.time()
    while time.time() - t0 < timeout:
        try:
            if requests.get(url + "/healthcheck", timeout=5).status_code == 200:
                return
        except requests.RequestException:
            pass
        time.sleep(2)
    sys.exit(f"CTFd ne repond pas sur {url} (make local-up ? make local-logs ?)")


def wait_port(host, port, timeout=90):
    t0 = time.time()
    while time.time() - t0 < timeout:
        try:
            with socket.create_connection((host, port), timeout=2):
                return True
        except OSError:
            time.sleep(1)
    return False


def wait_http_ready(host, port, timeout=20):
    """Best-effort : certains services HTTP (ex. ssrf-metadata-decoy) ouvrent le
    port TCP avant d'accepter des requetes -- le proxy Docker fait un RemoteDisconnect
    tant que werkzeug n'ecoute pas. On sonde un GET reel ; tout code HTTP = pret.
    Silencieux et non bloquant pour les challenges TCP bruts (retombe sur le sleep)."""
    t0 = time.time()
    url = f"http://{host}:{port}/"
    while time.time() - t0 < timeout:
        try:
            requests.get(url, timeout=3)
            return True
        except requests.RequestException:
            time.sleep(1)
    return False


def run_solver(runner, chdir, cmd, timeout):
    if runner == "docker":
        # Pas de --network host (absent sur Docker Desktop) : le conteneur joint
        # les instances publiees sur l'hote via host.docker.internal, que
        # --add-host rend disponible sur Linux comme sur Desktop.
        cmd = cmd.replace("127.0.0.1", "host.docker.internal").replace(
            "localhost", "host.docker.internal"
        )
        full = [
            "docker",
            "run",
            "--rm",
            "--add-host",
            "host.docker.internal:host-gateway",
            "-v",
            f"{ROOT}:/work",
            "-w",
            f"/work/challenges/{chdir}",
            "-e",
            "PWNLIB_NOTERM=1",
            "ctf-playtest",
            "bash",
            "-lc",
            cmd,
        ]
        cwd = None
    else:
        full = ["bash", "-lc", cmd]
        cwd = CH / chdir
    try:
        p = subprocess.run(
            full, cwd=cwd, capture_output=True, text=True, timeout=timeout
        )
        return p.returncode, (p.stdout or "") + "\n" + (p.stderr or "")
    except subprocess.TimeoutExpired as e:
        return 124, f"TIMEOUT apres {timeout}s\n" + (
            (e.stdout or b"").decode(errors="replace")
            if isinstance(e.stdout, bytes)
            else (e.stdout or "")
        )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--url",
        default=os.environ.get(
            "CTFD_URL", "http://localhost:" + os.environ.get("CTFD_PORT", "8000")
        ),
    )
    ap.add_argument("--only", nargs="*", default=[])
    ap.add_argument("--static-only", action="store_true")
    ap.add_argument("--served-only", action="store_true")
    ap.add_argument(
        "--ai", action="store_true", help="inclut ai1 (LLM reel via Ollama, profil ai)"
    )
    ap.add_argument(
        "--unlock-chain",
        action="store_true",
        help="retire temporairement les prerequis ai1->ai2->ai3",
    )
    ap.add_argument(
        "--runner",
        choices=["docker", "host"],
        default="docker",
        help="docker (image ctf-playtest, marche sur Linux et Docker Desktop) ou host (pwntools/numpy/scapy/requests/flask installes localement)",
    )
    ap.add_argument(
        "--keep", action="store_true", help="ne detruit pas les instances apres le test"
    )
    a = ap.parse_args()
    url = a.url.rstrip("/")

    if (
        a.runner == "docker"
        and subprocess.run(
            ["docker", "image", "inspect", "ctf-playtest"], capture_output=True
        ).returncode
        != 0
    ):
        sys.exit("image ctf-playtest absente : make local-playtest (ou --runner host)")
    if a.runner == "docker" and "127.0.0.1" not in url and "localhost" not in url:
        print(
            "!! --runner docker suppose un CTFd sur localhost ; sinon --runner host",
            file=sys.stderr,
        )

    wait_http(url)
    admin = Ctfd(url, "admin", "admin")
    player = Ctfd(url, "playtest", "playtest")
    byname = {c["name"]: c for c in admin.challenges_admin()}

    saved_reqs = {}
    if a.unlock_chain:
        for n in CHAIN:
            if n in byname:
                saved_reqs[n] = admin.get(byname[n]["id"]).get("requirements")
                admin.patch(byname[n]["id"], {"requirements": {"prerequisites": []}})
        print(
            f">> chaine IA deverrouillee ({', '.join(saved_reqs)}) — restauree a la fin"
        )

    # Le nom CTFd d'un challenge vient de son challenge.yml (ex. "Audio FSK"),
    # pas du nom de dossier.
    def yml_name(d):
        m = re.search(r"^name:\s*(.+)$", (CH / d / "challenge.yml").read_text(), re.M)
        return m.group(1).strip().strip('"') if m else d.split("/")[1]

    todo = [d for d in PLAN if not a.only or d in a.only]
    results = []
    try:
        for d in todo:
            mode, cmd, timeout = PLAN[d]
            name = yml_name(d)
            if (
                a.static_only
                and mode != "static"
                or a.served_only
                and mode not in ("served", "ai")
            ):
                continue
            c = byname.get(name)
            if c is None:
                results.append(
                    (d, "FAIL", "challenge absent de la plateforme (make local-seed)")
                )
                continue
            cid = c["id"]
            if mode == "ai" and not a.ai:
                results.append(
                    (d, "SKIP", "LLM reel requis : make local-up-ai puis --ai")
                )
                continue
            print(f"\n>> {d}  [{mode}]", flush=True)

            host = port = None
            if mode in ("served", "ai"):
                player.destroy(cid)  # nettoie une instance restee d'un run precedent
                r = spawn_resilient(player, url, cid)
                try:
                    j = r.json()
                except Exception:
                    j = {"success": False, "error": f"http {r.status_code}"}
                if not j.get("success"):
                    err = (
                        j.get("error", "")
                        or j.get("message", "")
                        or f"http {r.status_code}: {r.text[:200]}"
                    )
                    verdict = (
                        "GATED"
                        if r.status_code == 403 and "requis" in err.lower()
                        else "FAIL"
                    )
                    results.append((d, verdict, f"spawn: {err}"))
                    continue
                host, port = j["connection"]["host"], j["connection"]["port"]
                print(f"   instance {host}:{port} ({j.get('status')})", flush=True)
                if not wait_port(host, port):
                    results.append(
                        (
                            d,
                            "FAIL",
                            f"port {host}:{port} jamais ouvert (docker logs ti-*-{cid})",
                        )
                    )
                    if not a.keep:
                        player.destroy(cid)
                    continue
                wait_http_ready(
                    host, port
                )  # HTTP: attend une vraie reponse ; TCP brut: retombe apres 20s
                time.sleep(1)

            cmdf = cmd.format(
                HOST=host or "",
                PORT=port or "",
                URL=f"http://{host}:{port}" if host else "",
            )
            t0 = time.time()
            rc, out = run_solver(a.runner, d, cmdf, timeout)
            dt = time.time() - t0
            tail = "\n".join("   | " + l for l in out.strip().splitlines()[-6:])

            if mode == "stub":
                ok = rc == 0 and "ALL CHECKS PASSED" in out
                results.append(
                    (
                        d,
                        "STUB" if ok else "FAIL",
                        f"self-test hors-ligne {'OK' if ok else 'KO'} ({dt:.0f}s); live = playtest humain",
                    )
                )
                if not ok:
                    print(tail)
            else:
                flags = FLAG_RE.findall(out)
                if not flags:
                    results.append(
                        (d, "FAIL", f"solveur rc={rc}, aucun flag ({dt:.0f}s)")
                    )
                    print(tail)
                else:
                    # Beaucoup de solveurs impriment le flag puis sortent rc!=0 sur
                    # une etape de verification optionnelle : la vraie question est
                    # "la plateforme accepte-t-elle le flag ?". On soumet donc des
                    # qu'un flag valide est imprime, en notant le rc.
                    flag = flags[-1]
                    status, msg = player.attempt(cid, flag)
                    ok = status in ("correct", "already_solved")
                    note = f"{flag} -> {status} ({dt:.0f}s)" + (
                        f" [solveur rc={rc}]" if rc != 0 else ""
                    )
                    results.append(
                        (d, "PASS" if ok else "FAIL", note + ("" if ok else f" {msg}"))
                    )
                    if not ok:
                        print(tail)
            if host and not a.keep:
                player.destroy(cid)
    finally:
        for n, req in saved_reqs.items():
            admin.patch(byname[n]["id"], {"requirements": req})

    print("\n" + "=" * 78)
    counts = {}
    for d, v, info in results:
        counts[v] = counts.get(v, 0) + 1
        print(f"{v:5} {d:32} {info}")
    print("=" * 78)
    print("  ".join(f"{k}={v}" for k, v in sorted(counts.items())))
    sys.exit(1 if counts.get("FAIL") else 0)


if __name__ == "__main__":
    main()
