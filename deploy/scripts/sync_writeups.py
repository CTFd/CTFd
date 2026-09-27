#!/usr/bin/env python3
"""Generate / update the writeups tree the in-app `writeups` plugin reads.

For every challenge, write:

    writeups/<category>/<slug>.md

from that challenge's `solution/README.md` (its author-written writeup), with a
small header (name, category, points, author) prepended and every `NCTF{...}`
redacted to `NCTF{…}`. Idempotent: re-running refreshes the tree in place, so
this is both "écris" and "mets à jour".

    python3 deploy/scripts/sync_writeups.py            # write writeups/ at repo root
    python3 deploy/scripts/sync_writeups.py --out DIR  # elsewhere
    python3 deploy/scripts/sync_writeups.py --prune     # also delete orphans

A challenge whose solution/README.md is a scaffold STUB yields a stub writeup
(marked as such) -- honest: there is no real solution to publish yet.
"""
import argparse
import glob
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CHALLENGES = os.path.join(ROOT, "challenges")
FLAG = re.compile(r"NCTF\{[^}]*\}")

try:
    import yaml
except ImportError:
    sys.exit("pip install pyyaml")


DIFFS = ["warmup", "easy", "medium", "hard", "insane"]


def field(doc, *keys, default=""):
    for k in keys:
        if doc.get(k):
            return doc[k]
    return default


def difficulty_of(doc):
    """First difficulty tag found on the challenge, else "" (no pill)."""
    tags = [str(t).lower() for t in (doc.get("tags") or [])]
    for d in DIFFS:
        if d in tags:
            return d
    return ""


def _strip_leading_h1(body):
    """Drop the body's own top-level title (and a trailing blank), so it does
    not duplicate the canonical `# {name}` header we prepend."""
    lines = body.split("\n")
    if lines and lines[0].lstrip().startswith("# "):
        lines = lines[1:]
        if lines and lines[0].strip() == "":
            lines = lines[1:]
    return "\n".join(lines).strip()


def build(cdir, doc, cat, slug):
    name = field(doc, "name", default=slug)
    pts = doc.get("value") or (doc.get("extra") or {}).get("initial") or "?"
    author = field(doc, "author", default="—")
    diff = difficulty_of(doc)
    readme = os.path.join(cdir, "solution", "README.md")
    if os.path.isfile(readme):
        body = open(readme, encoding="utf-8").read().strip()
    else:
        body = "_Pas encore de writeup pour ce challenge._"
    # "Non finalisé" seulement si le writeup lui-même est un squelette (README STUB).
    # Un servi implémenté+vérifié reste `state: hidden` jusqu'au Lot-5 mais a un
    # vrai writeup — ne pas le marquer provisoire à cause de son état.
    is_stub = "STUB" in body[:400]
    body = _strip_leading_h1(body)
    # Ligne de méta LISIBLE PAR MACHINE (1re ligne, invisible au rendu : le plugin
    # la parse pour les pastilles et la retire avant le rendu Markdown).
    meta = (
        f'<!-- nctf-meta category="{cat}" difficulty="{diff}" '
        f'points="{pts}" author="{author}" stub="{1 if is_stub else 0}" -->'
    )
    header = f"{meta}\n# {name}"
    if is_stub:
        header += "\n\n> ⚠️ Challenge non finalisé — writeup provisoire."
    md = header + "\n\n" + FLAG.sub("NCTF{…}", body) + "\n"
    return md


def main(argv=None):
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("--out", default=os.path.join(ROOT, "writeups"))
    ap.add_argument(
        "--prune", action="store_true", help="delete writeups with no challenge"
    )
    a = ap.parse_args(argv)
    out = os.path.abspath(a.out)

    written = set()
    n = 0
    for y in sorted(glob.glob(os.path.join(CHALLENGES, "*/*/challenge.yml"))):
        cdir = os.path.dirname(y)
        rel = os.path.relpath(cdir, CHALLENGES)
        cat, slug = rel.split("/", 1)
        if "/" in slug:  # only cat/slug depth
            continue
        try:
            doc = yaml.safe_load(open(y, encoding="utf-8")) or {}
        except Exception as e:
            print(f"[skip] {rel}: {e}", file=sys.stderr)
            continue
        dst = os.path.join(out, cat, slug + ".md")
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        with open(dst, "w", encoding="utf-8") as fh:
            fh.write(build(cdir, doc, cat, slug))
        written.add(os.path.abspath(dst))
        n += 1

    pruned = 0
    if a.prune and os.path.isdir(out):
        for md in glob.glob(os.path.join(out, "*", "*.md")):
            if os.path.abspath(md) not in written:
                os.remove(md)
                pruned += 1

    print(f"wrote {n} writeups to {out}" + (f", pruned {pruned}" if a.prune else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
