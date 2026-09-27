#!/usr/bin/env python3
"""
graphql-introspection-maze -- the "Atlas Ops" GraphQL API.

Design notes (these are NOT hints handed to the player; they document the
server-oracle contract for authors/graders):

  * Introspection is DISABLED. `__schema` / `__type` are rejected by a
    validation rule, so a stock `graphql-cli --introspect` / GraphiQL dump
    returns nothing.

  * Field-suggestion errors are LEFT ON. graphql-core's standard validation
    ("Cannot query field 'x' on type 'Y'. Did you mean '...'?", and
    "argument 'a' of type 'T!' is required") is the ONLY discovery oracle.
    The hidden, unauthenticated mutation `redeemWarrant` is reachable only by
    walking that oracle (a.k.a. "clairvoyance").

  * `NodeRef` is a custom scalar with an INVENTED wire format (see
    encode_noderef / decode_noderef). It is deliberately not Relay's
    base64("Type:id"): little-endian ordinal, an additive checksum with a
    magic constant, and non-obvious "kind" bytes. Readable NodeRefs (your
    principal id, the announcement ids) are the corpus; the WARRANT kind is
    never returned by any field, so a valid warrant NodeRef must be FORGED
    from the inferred format.

  * The flag is a per-team, server-side EFFECT, never a downloadable artifact.
    `redeemWarrant(warrant:)` verifies the forged warrant and, as its effect,
    sets THIS session's clearance to ROOT (a value changes, server-side).
    `controlPlane { flag }` returns the flag ONLY while the caller's session
    clearance is ROOT -- it checks the effect, not the payload that produced
    it.

Run with a SINGLE worker: session clearance lives in an in-process dict.
"""
import base64
import hashlib
import hmac
import os
import secrets
import threading

from flask import Flask, request, jsonify, make_response
from graphql import (
    build_schema,
    parse,
    validate,
    execute,
    GraphQLError,
)
from graphql.error import GraphQLSyntaxError
from graphql.validation import specified_rules, NoSchemaIntrospectionCustomRule

app = Flask(__name__)

# ---------------------------------------------------------------------------
# Per-challenge flag. The platform injects FLAG (and CHALLENGE_SECRET) into the
# container at creation time; TEAM_SECRET is NO LONGER injected. The flag value
# is unchanged: CHALLENGE_SECRET == HMAC(team_secret, CHALLENGE_ID), so
# CHALLENGE_SECRET[:24] is exactly the old flag body. Neither value appears in
# any file the player can download.
# ---------------------------------------------------------------------------
CHALLENGE_ID = "web-graphql-introspection-maze"


def compute_flag() -> str:
    # New per-challenge contract, in order of precedence.
    env_flag = os.environ.get("FLAG")
    if env_flag:
        return env_flag
    challenge_secret = os.environ.get("CHALLENGE_SECRET")
    if challenge_secret:
        return "NCTF{" + challenge_secret[:24] + "}"
    # LOCAL DEV fallback ONLY -- never reached on the arena, where FLAG /
    # CHALLENGE_SECRET are always injected. Reproduces the old per-team value so
    # off-arena runs still work.
    team_secret = os.environ.get("TEAM_SECRET", "local-dev-secret")
    digest = hmac.new(
        team_secret.encode(), CHALLENGE_ID.encode(), hashlib.sha256
    ).hexdigest()
    return "NCTF{" + digest[:24] + "}"


# ---------------------------------------------------------------------------
# NodeRef -- invented opaque reference scalar.
#
#   text  :  "NR1_" + base64url(body)         (no padding)
#   body  :  5 bytes  [ kind, ord_lo, ord_hi, ver, chk ]
#     kind    : 0x21 PRINCIPAL, 0x22 ANNOUNCEMENT, 0x23 NODE, 0x2A WARRANT
#     ord     : uint16, LITTLE-ENDIAN, 1-based
#     ver     : 0x01
#     chk     : (kind + ord_lo + ord_hi + ver + 0x5A) & 0xFF   -- additive,
#               with a magic constant; NOT a CRC.
#
# The WARRANT kind (0x2A) is never emitted by any resolver.
# ---------------------------------------------------------------------------
KIND_PRINCIPAL = 0x21
KIND_ANNOUNCEMENT = 0x22
KIND_NODE = 0x23
KIND_WARRANT = 0x2A
_MAGIC = 0x5A


def _b64u(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode()


def _b64u_dec(s: str) -> bytes:
    return base64.urlsafe_b64decode(s + "=" * (-len(s) % 4))


def encode_noderef(kind: int, ordinal: int) -> str:
    ord_lo = ordinal & 0xFF
    ord_hi = (ordinal >> 8) & 0xFF
    ver = 0x01
    chk = (kind + ord_lo + ord_hi + ver + _MAGIC) & 0xFF
    return "NR1_" + _b64u(bytes([kind, ord_lo, ord_hi, ver, chk]))


def decode_noderef(text) -> dict:
    """Structural decode + checksum verify. Raises GraphQLError on any problem.

    This runs inside the scalar's parse hooks, so a malformed NodeRef fails at
    validation/coercion time for *every* field that takes a NodeRef -- which is
    exactly what forces a correctly-checksummed forgery.
    """
    if not isinstance(text, str) or not text.startswith("NR1_"):
        raise GraphQLError("NodeRef must be a string of the form 'NR1_<data>'")
    try:
        body = _b64u_dec(text[4:])
    except Exception:
        raise GraphQLError("NodeRef payload is not valid base64url")
    if len(body) != 5:
        raise GraphQLError("NodeRef payload has wrong length")
    kind, ord_lo, ord_hi, ver, chk = body
    if ver != 0x01:
        raise GraphQLError("NodeRef version unsupported")
    calc = (kind + ord_lo + ord_hi + ver + _MAGIC) & 0xFF
    if calc != chk:
        raise GraphQLError("NodeRef checksum mismatch")
    return {"kind": kind, "ordinal": ord_lo | (ord_hi << 8), "text": text}


# ---------------------------------------------------------------------------
# Schema (SDL). Nothing here is served to the player -- introspection is off.
# ---------------------------------------------------------------------------
SDL = """
scalar NodeRef

enum ClearanceLevel { OBSERVER OPERATOR ROOT }

type ServiceInfo {
  name: String!
  region: String!
  build: String!
}

type Announcement {
  id: NodeRef!
  title: String!
  body: String!
}

type Principal {
  id: NodeRef!
  displayName: String!
  contactEmail: String!
  clearance: ClearanceLevel!
}

type ControlPlane {
  status: String!
  callerClearance: ClearanceLevel!
  flag: String
}

type Query {
  serviceInfo: ServiceInfo!
  me: Principal!
  announcements: [Announcement!]!
  controlPlane: ControlPlane!
}

type Mutation {
  acknowledgeAnnouncement(ref: NodeRef!): Boolean!
  updateContactEmail(email: String!): Principal!
  requestElevation(reason: String!): String!
  redeemWarrant(warrant: NodeRef!): ControlPlane!
}
"""

schema = build_schema(SDL)

# Attach the custom scalar behaviour.
node_ref = schema.type_map["NodeRef"]
node_ref.serialize = (
    lambda value: value
    if isinstance(value, str)
    else encode_noderef(value["kind"], value["ordinal"])
)
node_ref.parse_value = decode_noderef  # from variables
node_ref.parse_literal = lambda ast, _vars=None: decode_noderef(
    getattr(ast, "value", None)
)  # inline literal

# ---------------------------------------------------------------------------
# Per-session server-side state (the "effect" lives here).
# ---------------------------------------------------------------------------
_LOCK = threading.Lock()
SESSIONS = {}  # sid -> {"clearance": str, "email": str}

# A small, fixed corpus. Ordinals are 1-based and non-contiguous so the
# additive checksum is visible across samples without giving the format away.
ANNOUNCEMENTS = [
    (41, "Scheduled maintenance", "Region ATLAS-3 read-only 02:00-02:30 UTC."),
    (44, "Deprecation notice", "Legacy /v1 refs retire next quarter; ids stay opaque."),
    (
        47,
        "New operator onboarding",
        "Ask your sponsor to reassign your clearance from OBSERVER.",
    ),
    (52, "Incident retro", "ATLAS-3 latency spike root-caused to cache stampede."),
    (58, "Policy update", "Warrant issuance moved to the offline signing HSM."),
    (
        63,
        "Break-glass runbook",
        "To take ROOT, redeem a valid warrant against the ops mutation; expired warrants can no longer be redeemed at the edge.",
    ),
]

YOU_ORDINAL = 1337  # your principal


def _session(context):
    sid = context["sid"]
    with _LOCK:
        st = SESSIONS.get(sid)
        if st is None:
            st = {"clearance": "OBSERVER", "email": "operator@atlas.example"}
            SESSIONS[sid] = st
        return st


# ---------------------------------------------------------------------------
# Resolvers.
# ---------------------------------------------------------------------------
def r_service_info(_root, _info):
    return {"name": "Atlas Ops", "region": "ATLAS-3", "build": "atlas-ops/2.11.4"}


def r_me(_root, info):
    st = _session(info.context)
    return {
        "id": {"kind": KIND_PRINCIPAL, "ordinal": YOU_ORDINAL},
        "displayName": "operator-7",
        "contactEmail": st["email"],
        "clearance": st["clearance"],
    }


def r_announcements(_root, _info):
    return [
        {"id": {"kind": KIND_ANNOUNCEMENT, "ordinal": o}, "title": t, "body": b}
        for (o, t, b) in ANNOUNCEMENTS
    ]


def r_control_plane(_root, info):
    st = _session(info.context)
    is_root = st["clearance"] == "ROOT"
    return {
        "status": "nominal",
        "callerClearance": st["clearance"],
        "flag": compute_flag() if is_root else None,
    }


def r_ack(_root, _info, ref):
    # ref is already decoded by the scalar; a benign no-op that accepts any
    # well-formed reference.
    return True


def r_update_email(_root, info, email):
    st = _session(info.context)
    st["email"] = email
    return {
        "id": {"kind": KIND_PRINCIPAL, "ordinal": YOU_ORDINAL},
        "displayName": "operator-7",
        "contactEmail": st["email"],
        "clearance": st["clearance"],
    }


def r_request_elevation(_root, _info, reason):
    # DECOY: the obvious-looking escalation path. It never changes clearance;
    # it just queues a ticket. Refutable in one round trip (re-query
    # me { clearance } afterwards -- still OBSERVER).
    return "ticket ATLAS-REQ-8821 queued; pending manual approval (no automated grant)"


def r_redeem_warrant(_root, info, warrant):
    # `warrant` has already passed the scalar's structural + checksum decode.
    # The privileged EFFECT: a valid WARRANT reference flips this session to
    # ROOT, server-side. No authentication is required -- the mutation is
    # simply hidden, and hidden != access-controlled.
    if warrant["kind"] != KIND_WARRANT:
        raise GraphQLError("warrant rejected: reference does not name a warrant")
    st = _session(info.context)
    st["clearance"] = "ROOT"
    return {
        "status": "warrant accepted; clearance reassigned",
        "callerClearance": st["clearance"],
        "flag": compute_flag(),  # gate is the effect above; ROOT sessions see it
    }


for _tname, _field, _fn in [
    ("Query", "serviceInfo", r_service_info),
    ("Query", "me", r_me),
    ("Query", "announcements", r_announcements),
    ("Query", "controlPlane", r_control_plane),
    ("Mutation", "acknowledgeAnnouncement", r_ack),
    ("Mutation", "updateContactEmail", r_update_email),
    ("Mutation", "requestElevation", r_request_elevation),
    ("Mutation", "redeemWarrant", r_redeem_warrant),
]:
    schema.type_map[_tname].fields[_field].resolve = _fn


# ---------------------------------------------------------------------------
# HTTP surface.
# ---------------------------------------------------------------------------
VALIDATION_RULES = list(specified_rules) + [NoSchemaIntrospectionCustomRule]

LANDING = """<!doctype html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Atlas Ops &middot; GraphQL</title>
<style>
  :root{--bg:#0f1420;--card:#171f30;--line:#26304a;--ink:#e7ecf6;--mut:#8a97b2;
        --acc:#60a5fa;--mono:ui-monospace,SFMono-Regular,Menlo,monospace}
  *{box-sizing:border-box}
  body{margin:0;font:15px/1.5 system-ui,Segoe UI,Roboto,sans-serif;background:var(--bg);color:var(--ink)}
  header{background:linear-gradient(90deg,#0b2138,#0f1420);border-bottom:1px solid var(--line);
         padding:14px 20px;display:flex;align-items:center;gap:12px}
  .logo{font-weight:700}.logo b{color:var(--acc)}
  header .tag{color:var(--mut);font-size:13px}
  main{max-width:940px;margin:0 auto;padding:22px 16px;display:grid;gap:18px}
  .card{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:18px}
  .card h2{margin:0 0 4px;font-size:16px}.card p.h{margin:0 0 14px;color:var(--mut);font-size:13px}
  label{display:block;font-size:12px;color:var(--mut);margin:10px 0 4px}
  textarea{width:100%;background:#0c1120;border:1px solid var(--line);color:var(--ink);
        border-radius:8px;padding:9px 11px;font-family:var(--mono);font-size:12.5px;min-height:110px;resize:vertical}
  textarea#vars{min-height:56px}
  button{margin-top:12px;background:var(--acc);color:#04223a;border:0;border-radius:8px;
        padding:9px 16px;font-weight:700;cursor:pointer}
  pre{background:#0a0e18;border:1px solid var(--line);border-radius:8px;padding:12px;
      overflow:auto;font-size:12.5px;color:#cfe0ff;margin:12px 0 0;white-space:pre-wrap}
  code{font-family:var(--mono);color:#ffd479}.muted{color:var(--mut);font-size:12px}
</style></head><body>
<header><div class="logo"><b>Atlas</b> Ops</div>
  <div class="tag">GraphQL &middot; single endpoint</div></header>
<main>
  <div class="card">
    <h2>GraphQL console</h2>
    <p class="h">Single endpoint&nbsp;: <code>POST /graphql</code>. Introspection is
       disabled on this deployment&nbsp;: no schema dump, no GraphiQL, no
       <code>__schema</code>. Flag format&nbsp;: <code>NCTF{...}</code>.</p>
    <label>Query</label>
    <textarea id="q">{ serviceInfo { name region build } }</textarea>
    <label>Variables (JSON)</label>
    <textarea id="vars">{}</textarea>
    <button onclick="run()">Run</button>
    <pre id="out" class="muted">&mdash;</pre>
  </div>
</main>
<script>
async function run(){
  let vars={};const vt=document.getElementById('vars').value.trim();
  if(vt){try{vars=JSON.parse(vt)}catch(e){document.getElementById('out').textContent='Invalid variables JSON: '+e;return;}}
  const r=await fetch('/graphql',{method:'POST',
    headers:{'Content-Type':'application/json'},
    body:JSON.stringify({query:document.getElementById('q').value,variables:vars})});
  let b;try{b=await r.json()}catch(e){b=await r.text()}
  document.getElementById('out').textContent='['+r.status+']\\n'+
    (typeof b==='string'?b:JSON.stringify(b,null,2));}
</script>
</body></html>"""


@app.get("/")
def index():
    return LANDING


@app.get("/graphql")
def graphql_get():
    # No GraphiQL. Explicit, so tools don't assume it's just missing.
    return (
        jsonify(
            {"errors": [{"message": "GraphQL over GET is not enabled; POST a query."}]}
        ),
        405,
    )


def _ensure_session():
    sid = request.cookies.get("atlas_session")
    new = False
    if not sid or sid not in SESSIONS:
        if not sid:
            sid = secrets.token_urlsafe(18)
            new = True
        # Touch to create state on first use.
        with _LOCK:
            SESSIONS.setdefault(
                sid, {"clearance": "OBSERVER", "email": "operator@atlas.example"}
            )
    return sid, new


@app.post("/graphql")
def graphql_post():
    sid, new = _ensure_session()
    data = request.get_json(silent=True) or {}
    query = data.get("query")
    variables = data.get("variables") or {}
    operation = data.get("operationName")

    if not query or not isinstance(query, str):
        resp = jsonify({"errors": [{"message": "missing 'query'"}]})
        resp.status_code = 400
        if new:
            resp.set_cookie("atlas_session", sid, httponly=True, samesite="Lax")
        return resp

    # Parse.
    try:
        document = parse(query)
    except GraphQLSyntaxError as exc:
        return _finish({"errors": [_fmt(exc)]}, sid, new)

    # Validate (this is where field-suggestion + no-introspection live).
    errors = validate(schema, document, VALIDATION_RULES)
    if errors:
        return _finish({"errors": [_fmt(e) for e in errors]}, sid, new)

    # Execute.
    result = execute(
        schema,
        document,
        variable_values=variables,
        operation_name=operation,
        context_value={"sid": sid},
    )
    payload = {}
    if result.errors:
        payload["errors"] = [_fmt(e) for e in result.errors]
    if result.data is not None:
        payload["data"] = result.data
    return _finish(payload, sid, new)


def _fmt(err):
    out = {"message": getattr(err, "message", str(err))}
    locs = getattr(err, "locations", None)
    if locs:
        out["locations"] = [{"line": l.line, "column": l.column} for l in locs]
    path = getattr(err, "path", None)
    if path:
        out["path"] = list(path)
    return out


def _finish(payload, sid, new):
    resp = make_response(jsonify(payload))
    if new:
        resp.set_cookie("atlas_session", sid, httponly=True, samesite="Lax")
    return resp


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
