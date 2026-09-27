"""Forum XXE — an XML parser that resolves external SYSTEM entities.

Design (served challenge, per-team flag):

  * ``/import`` accepts an XML document (e.g. a bulk post import). The parser
    resolves external entities, including ``SYSTEM "file://..."`` and
    ``SYSTEM "http://..."`` — classic XXE, giving internal file read and SSRF.
  * An entity pointing at ``file:///flag.txt`` expands to the instance secret in
    the parsed output.

Intended path: POST an XML doc declaring
``<!DOCTYPE r [<!ENTITY x SYSTEM "file:///flag.txt">]>`` and referencing ``&x;``.

The flag at ``/flag.txt`` is served by no route; it only reaches the attacker via
the external-entity expansion the parser should have disabled.

This models the XXE resolver explicitly (it recognises SYSTEM entities and
resolves file:// and the internal metadata host) so the behaviour is
deterministic and self-contained, independent of the host XML library's settings.
"""
import os
import re

from flask import Flask, jsonify, request

app = Flask(__name__)

# Internal "metadata" service reachable only from the server (SSRF target).
INTERNAL = {"http://169.254.169.254/latest/meta-data/role": "backup-restore"}


def _resolve_system(uri):
    if uri.startswith("file://"):
        path = uri[len("file://") :]
        try:
            with open(path, encoding="utf-8") as fh:
                return fh.read().strip()
        except OSError:
            return ""
    if uri in INTERNAL:  # SSRF to an internal-only host
        return INTERNAL[uri]
    return ""


def parse_xml(doc):
    # Recognise a single external SYSTEM entity and expand its references.
    entities = {}
    for name, uri in re.findall(r'<!ENTITY\s+(\w+)\s+SYSTEM\s+"([^"]+)"\s*>', doc):
        entities[name] = _resolve_system(uri)
    out = doc
    for name, value in entities.items():
        out = out.replace("&" + name + ";", value)
    # strip the DOCTYPE/entity declarations from the rendered result
    out = re.sub(r"<!DOCTYPE.*?\]>", "", out, flags=re.S)
    return out.strip()


INDEX_HTML = """<!doctype html>
<html lang="fr"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>PostForge &middot; import de sujets</title>
<style>
  :root{--bg:#0f1420;--card:#171f30;--line:#26304a;--ink:#e7ecf6;--mut:#8a97b2;
        --acc:#7c5cff;--bad:#ff6b6b;--mono:ui-monospace,SFMono-Regular,Menlo,monospace}
  *{box-sizing:border-box}
  body{margin:0;font:15px/1.5 system-ui,Segoe UI,Roboto,sans-serif;background:var(--bg);color:var(--ink)}
  header{background:linear-gradient(90deg,#1a1440,#0f1420);border-bottom:1px solid var(--line);
         padding:14px 20px;display:flex;align-items:center;gap:12px}
  header .logo{font-weight:700}.logo b{color:var(--acc)}
  header .tag{color:var(--mut);font-size:13px}
  main{max-width:900px;margin:0 auto;padding:22px 16px;display:grid;gap:18px}
  .card{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:18px}
  .card h2{margin:0 0 4px;font-size:16px}
  .card p.h{margin:0 0 14px;color:var(--mut);font-size:13px}
  label{display:block;font-size:12px;color:var(--mut);margin:10px 0 4px}
  textarea{width:100%;background:#0c1120;border:1px solid var(--line);color:var(--ink);
        border-radius:8px;padding:9px 11px;font-family:var(--mono);font-size:13px;min-height:150px;
        resize:vertical;white-space:pre}
  button{margin-top:12px;background:var(--acc);color:#fff;border:0;border-radius:8px;
        padding:9px 16px;font-weight:600;cursor:pointer}
  pre{background:#0a0e18;border:1px solid var(--line);border-radius:8px;padding:12px;
      overflow:auto;font-size:12.5px;color:#cfe0ff;margin:12px 0 0;white-space:pre-wrap}
  code{font-family:var(--mono);color:#ffd479}
  .muted{color:var(--mut);font-size:12px}
</style></head><body>
<header><div class="logo"><b>Post</b>Forge</div>
  <div class="tag">migration de forum &middot; import XML de sujets</div></header>
<main>
  <div class="card">
    <h2>Importer des sujets (XML)</h2>
    <p class="h">Collez un export XML de votre ancien forum. L'analyseur le lit et
       renvoie le contenu rendu. Format attendu&nbsp;: <code>&lt;r&gt;...&lt;/r&gt;</code>.</p>
    <label>Document XML</label>
    <textarea id="xml">&lt;?xml version="1.0"?&gt;
&lt;r&gt;Bienvenue sur le nouveau forum !&lt;/r&gt;</textarea>
    <button onclick="imp()">Importer</button>
    <pre id="out" class="muted">&mdash;</pre>
  </div>
</main>
<script>
async function imp(){
  const xml=document.getElementById('xml').value;
  const r=await fetch('/import',{method:'POST',
      headers:{'Content-Type':'application/xml'},body:xml});
  const t=await r.text();let j;try{j=JSON.parse(t)}catch(e){j=t}
  document.getElementById('out').textContent=
    typeof j==='string'?j:JSON.stringify(j,null,2);}
</script>
</body></html>"""


@app.route("/")
def index():
    return INDEX_HTML


@app.route("/import", methods=["POST"])
def do_import():
    doc = request.get_data(as_text=True)
    if "<" not in doc:
        return jsonify({"error": "expected XML"}), 400
    return jsonify({"parsed": parse_xml(doc)})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "8080")))
