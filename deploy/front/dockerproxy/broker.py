#!/usr/bin/env python3
"""Broker Docker filtrant — ferme C2 du pentest.

L'ancien dockerproxy republiait le socket Docker BRUT de l'arena en TCP : tout
conteneur du reseau `internal` (dont CTFd, expose a Internet) pouvait appeler
n'importe quel verbe de l'API Docker de l'arena => root hote (POST
/containers/create avec Binds:["/:/host"] ou Privileged) et lecture du FLAG de
chaque equipe (GET /containers/{id}/json -> Config.Env).

Ce broker se met en facade : il n'autorise QUE les operations dont l'instancier
(CTFd/plugins/team_instancer/backend.py) a besoin, VALIDE le corps de
`create` (rejet des primitives d'evasion), et EXPURGE `Config.Env` des reponses
d'inspection (le FLAG n'est jamais relu par l'instancier, il l'ecrit).

Facade : 0.0.0.0:2375 (reseau `internal` du compose, joint par ctfd).
Amont   : 127.0.0.1:2381 (tunnel ssh prive vers le socket Docker de l'arena).

Non teste ici (pas de demon Docker dans l'environnement de build) : A VALIDER
EN REPETITION — instancier : create / start / stop / remove / list / reconcile.
"""
import http.client
import json
import re
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

UPSTREAM_HOST = "127.0.0.1"
UPSTREAM_PORT = 2381
LISTEN_PORT = 2375
MAX_BODY = 1 << 20  # 1 MiB : aucune operation legitime n'envoie plus
HOP_BY_HOP = {
    "connection",
    "keep-alive",
    "proxy-authenticate",
    "proxy-authorization",
    "te",
    "trailers",
    "transfer-encoding",
    "upgrade",
}

# Prefixe de version optionnel (/v1.43/...) retire avant d'apparier la route.
_VER = re.compile(r"^/v1\.\d+(?=/)")


def _norm(path):
    """Chemin sans query ni prefixe de version, pour l'appariement de route."""
    p = path.split("?", 1)[0]
    return _VER.sub("", p) or "/"


# (methode, regex sur le chemin normalise) -> operation autorisee.
# Tout le reste (/exec, /build, /commit, swarm, volumes, system, plugins,
# secrets, configs, /attach, /containers/{id}/archive ...) est refuse.
ALLOW = [
    ("GET", re.compile(r"^/_ping$")),
    ("GET", re.compile(r"^/version$")),
    ("HEAD", re.compile(r"^/_ping$")),
    # reseaux par equipe
    ("POST", re.compile(r"^/networks/create$")),
    ("GET", re.compile(r"^/networks/[^/]+$")),
    ("DELETE", re.compile(r"^/networks/[^/]+$")),
    # image locale (inspection seule : pas de pull/build)
    ("GET", re.compile(r"^/images/.+/json$")),
    # conteneurs par equipe
    ("POST", re.compile(r"^/containers/create$")),
    ("POST", re.compile(r"^/containers/[^/]+/start$")),
    ("POST", re.compile(r"^/containers/[^/]+/stop$")),
    ("DELETE", re.compile(r"^/containers/[^/]+$")),
    ("GET", re.compile(r"^/containers/json$")),
    ("GET", re.compile(r"^/containers/[^/]+/json$")),
]

_INSPECT = re.compile(r"^/containers/[^/]+/json$")
_IMG_INSPECT = re.compile(r"^/images/.+/json$")


def _is_allowed(method, npath):
    return any(method == m and rx.match(npath) for m, rx in ALLOW)


def _bad_create(body):
    """Renvoie la raison du refus d'un POST /containers/create, ou None.

    Bloque toute primitive permettant une evasion hote ou l'exposition d'un
    port hors loopback. On refuse en cas de doute (corps illisible)."""
    try:
        spec = json.loads(body or b"{}")
    except Exception:
        return "corps JSON illisible"
    if not isinstance(spec, dict):
        return "corps non-objet"
    hc = spec.get("HostConfig") or {}
    if not isinstance(hc, dict):
        return "HostConfig non-objet"
    if hc.get("Privileged"):
        return "Privileged"
    if hc.get("Binds"):
        return "Binds (montage hote)"
    for m in hc.get("Mounts") or []:
        if isinstance(m, dict) and (m.get("Type") == "bind" or m.get("Source")):
            return "Mounts/bind"
    for key in (
        "CapAdd",
        "Devices",
        "DeviceRequests",
        "Sysctls",
        "CgroupParent",
        "GroupAdd",
    ):
        if hc.get(key):
            return key
    for key in ("PidMode", "IpcMode", "UTSMode", "UsernsMode", "CgroupnsMode"):
        v = hc.get(key)
        if isinstance(v, str) and (v == "host" or v.startswith("container:")):
            return "%s:%s" % (key, v)
    nm = hc.get("NetworkMode")
    if isinstance(nm, str) and (nm == "host" or nm.startswith("container:")):
        return "NetworkMode:%s" % nm
    for so in hc.get("SecurityOpt") or []:
        s = str(so).replace(" ", "").lower()
        if "unconfined" in s or s.startswith("label=disable"):
            return "SecurityOpt:%s" % so
    # Sur l'arena l'instancier publie en loopback (settings.port_binding).
    # On refuse toute publication sur une autre interface.
    for _p, binds in (hc.get("PortBindings") or {}).items():
        for b in binds or []:
            ip = (b or {}).get("HostIp", "")
            if ip not in ("127.0.0.1", "::1"):
                return "PortBindings HostIp=%r (loopback requis)" % ip
    return None


_SCRUB = ["<expurge-par-le-broker>"]


def _redact_env(raw):
    """Expurge Config.Env / ContainerConfig.Env d'une reponse d'inspection."""
    try:
        obj = json.loads(raw)
    except Exception:
        return raw
    if isinstance(obj, dict):
        if "Env" in obj:
            obj["Env"] = list(_SCRUB)
        for k in ("Config", "ContainerConfig"):
            c = obj.get(k)
            if isinstance(c, dict) and "Env" in c:
                c["Env"] = list(_SCRUB)
    return json.dumps(obj).encode()


def _redact_list(raw):
    """Defense en profondeur : retire tout Env d'une liste de conteneurs.
    Le vrai Docker n'en met pas dans /containers/json, mais on ne depend pas
    de ce comportement."""
    try:
        arr = json.loads(raw)
    except Exception:
        return raw
    if isinstance(arr, list):
        for it in arr:
            if isinstance(it, dict) and "Env" in it:
                it["Env"] = list(_SCRUB)
    return json.dumps(arr).encode()


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"
    server_version = "nctf-docker-broker"

    def log_message(self, *a):  # silencieux (stderr pollue les logs compose)
        pass

    def _deny(self, code, reason):
        payload = json.dumps({"message": "broker: %s" % reason}).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def _handle(self, method):
        npath = _norm(self.path)
        if not _is_allowed(method, npath):
            return self._deny(403, "operation non autorisee: %s %s" % (method, npath))

        length = int(self.headers.get("Content-Length") or 0)
        if length > MAX_BODY:
            return self._deny(413, "corps trop volumineux")
        body = self.rfile.read(length) if length else b""

        if method == "POST" and npath == "/containers/create":
            why = _bad_create(body)
            if why:
                return self._deny(403, "create refuse (%s)" % why)

        # Transmission a l'amont (socket Docker de l'arena via le tunnel ssh).
        try:
            up = http.client.HTTPConnection(UPSTREAM_HOST, UPSTREAM_PORT, timeout=35)
            headers = {
                k: v
                for k, v in self.headers.items()
                if k.lower() not in HOP_BY_HOP and k.lower() != "host"
            }
            up.request(method, self.path, body=body or None, headers=headers)
            resp = up.getresponse()
            data = resp.read()
        except Exception as e:
            return self._deny(502, "amont injoignable: %s" % e)

        # Expurge le FLAG des inspections avant de rendre la reponse.
        if method == "GET" and resp.status == 200:
            if _INSPECT.match(npath) or _IMG_INSPECT.match(npath):
                data = _redact_env(data)
            elif npath == "/containers/json":
                data = _redact_list(data)

        self.send_response(resp.status)
        ctype = resp.getheader("Content-Type", "application/json")
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        if method != "HEAD":
            self.wfile.write(data)

    def do_GET(self):
        self._handle("GET")

    def do_POST(self):
        self._handle("POST")

    def do_DELETE(self):
        self._handle("DELETE")

    def do_HEAD(self):
        self._handle("HEAD")

    def do_PUT(self):
        self._deny(403, "PUT non autorise")


def main():
    srv = ThreadingHTTPServer(("0.0.0.0", LISTEN_PORT), Handler)  # nosec B104
    print(
        "broker Docker filtrant: 0.0.0.0:%d -> %s:%d"
        % (LISTEN_PORT, UPSTREAM_HOST, UPSTREAM_PORT),
        file=sys.stderr,
        flush=True,
    )
    srv.serve_forever()


if __name__ == "__main__":
    main()
