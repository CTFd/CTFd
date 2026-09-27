"""CMS Uploadssrf — an upload filter bypass that feeds a server-side renderer.

Design (served challenge, per-team flag):

  * ``/upload`` accepts a "document" and only allows ``.png`` — but it checks the
    extension on the *declared* filename, so ``report.png.svg`` (or any name
    ending ``.png`` with SVG content) slips through.
  * The uploaded document is rendered server-side. The renderer fetches any URL
    referenced by ``render:<url>`` in the content — an SSRF. The internal
    metadata host returns a role credential and, at ``/latest/meta-data/flag``,
    the instance secret.

Intended path: upload a doc that bypasses the extension check and contains
``render:http://169.254.169.254/latest/meta-data/flag``.

The flag at ``/flag.txt`` is exposed only through the internal metadata host the
renderer's SSRF reaches.
"""
import os
import re

from flask import Flask, jsonify, request

app = Flask(__name__)


def _flag():
    try:
        with open("/flag.txt", encoding="utf-8") as fh:
            return fh.read().strip()
    except OSError:
        return "NCTF{flag-unavailable-in-dev}"


# Internal metadata service (reachable only server-side).
def _metadata(url):
    table = {
        "http://169.254.169.254/latest/meta-data/role": "backup-restore",
        "http://169.254.169.254/latest/meta-data/flag": _flag(),
    }
    return table.get(url)


def _allowed(filename):
    # BUG: only checks that the name ends with .png, ignoring real content type
    # and double extensions.
    return filename.endswith(".png")


INDEX_HTML = """<!doctype html>
<html lang="fr"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>NovaCMS &middot; médiathèque</title>
<style>
  :root{--bg:#0f1420;--card:#171f30;--line:#26304a;--ink:#e7ecf6;--mut:#8a97b2;
        --acc:#22b8a6;--bad:#ff6b6b;--mono:ui-monospace,SFMono-Regular,Menlo,monospace}
  *{box-sizing:border-box}
  body{margin:0;font:15px/1.5 system-ui,Segoe UI,Roboto,sans-serif;background:var(--bg);color:var(--ink)}
  header{background:linear-gradient(90deg,#0e2a28,#0f1420);border-bottom:1px solid var(--line);
         padding:14px 20px;display:flex;align-items:center;gap:12px}
  .logo{font-weight:700}.logo b{color:var(--acc)}
  header .tag{color:var(--mut);font-size:13px}
  main{max-width:880px;margin:0 auto;padding:22px 16px;display:grid;gap:18px}
  .card{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:18px}
  .card h2{margin:0 0 4px;font-size:16px}.card p.h{margin:0 0 14px;color:var(--mut);font-size:13px}
  label{display:block;font-size:12px;color:var(--mut);margin:10px 0 4px}
  input,textarea{width:100%;background:#0c1120;border:1px solid var(--line);color:var(--ink);
        border-radius:8px;padding:9px 11px;font-family:var(--mono);font-size:13px}
  textarea{min-height:90px;resize:vertical}
  button{margin-top:12px;background:var(--acc);color:#052b28;border:0;border-radius:8px;
        padding:9px 16px;font-weight:700;cursor:pointer}
  pre{background:#0a0e18;border:1px solid var(--line);border-radius:8px;padding:12px;
      overflow:auto;font-size:12.5px;color:#cfe0ff;margin:12px 0 0;white-space:pre-wrap}
  code{font-family:var(--mono);color:#ffd479}.muted{color:var(--mut);font-size:12px}
  .badge{display:inline-block;background:#0c1120;border:1px solid var(--line);border-radius:20px;
        padding:2px 10px;font-size:12px;color:var(--mut)}
</style></head><body>
<header><div class="logo"><b>Nova</b>CMS</div>
  <div class="tag">médiathèque &middot; téléversement de documents</div></header>
<main>
  <div class="card">
    <h2>Téléverser un document</h2>
    <p class="h">Seules les images <span class="badge">.png</span> sont acceptées.
       Le document est rendu côté serveur&nbsp;; une directive
       <code>render:&lt;url&gt;</code> dans le contenu déclenche un aperçu distant.</p>
    <label>Nom du fichier</label>
    <input id="fn" value="rapport.png">
    <label>Contenu</label>
    <textarea id="ct">Rapport trimestriel — brouillon.</textarea>
    <button onclick="up()">Téléverser</button>
    <pre id="out" class="muted">&mdash;</pre>
  </div>
</main>
<script>
async function up(){
  const filename=document.getElementById('fn').value;
  const content=document.getElementById('ct').value;
  const r=await fetch('/upload',{method:'POST',
      headers:{'Content-Type':'application/json'},
      body:JSON.stringify({filename,content})});
  const j=await r.json();
  document.getElementById('out').textContent=JSON.stringify(j,null,2);}
</script>
</body></html>"""


@app.route("/")
def index():
    return INDEX_HTML


@app.route("/upload", methods=["POST"])
def upload():
    body = request.get_json(silent=True) or {}
    filename = body.get("filename", "")
    content = body.get("content", "")
    if not _allowed(filename):
        return jsonify({"error": "only .png allowed"}), 400
    # Server-side render: follow any render:<url> directive (SSRF).
    m = re.search(r"render:(\S+)", content)
    rendered = None
    if m:
        rendered = _metadata(m.group(1))
        if rendered is None:
            rendered = f"<fetched {m.group(1)}>"
    return jsonify({"stored": filename, "rendered": rendered})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "8080")))
