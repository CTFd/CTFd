"""Writeups plugin — an in-app writeups page the admin can show or hide.

Reads Markdown writeups from a directory tree named by category and challenge:

    <WRITEUPS_DIR>/<category>/<slug>.md

`WRITEUPS_DIR` defaults to `writeups/` at the repository root (the tree produced
by `deploy/scripts/sync_writeups.py` from each challenge's solution/README.md);
override with the `WRITEUPS_DIR` env var to point at a mounted volume.

Visibility is a single admin toggle (`writeups_visible` config):

  * OFF (default): the page shows players a "not published yet" notice; admins
    still see everything (a preview). Nothing leaks during the event.
  * ON: everyone sees the writeups. Flip it after the CTF closes.

Every `NCTF{...}` in a writeup is redacted to `NCTF{…}` at render time, so a
writeup file that still carries a real static flag never serves it.

No new tables, no migration: the toggle is a CTFd config value; the content is
files on disk. Path lookups are constrained to `[a-z0-9-]` category/slug under
WRITEUPS_DIR, so a request cannot traverse out of the tree.
"""

import os
import re

from flask import Blueprint, abort, redirect, render_template, request, url_for

from CTFd.utils import get_config, set_config
from CTFd.utils.config.pages import build_markdown
from CTFd.utils.decorators import admins_only
from CTFd.utils.user import is_admin

bp = Blueprint(
    "writeups", __name__, template_folder="templates", static_folder="assets"
)

_SLUG = re.compile(r"[a-z0-9][a-z0-9-]*")
_FLAG = re.compile(r"NCTF\{[^}]*\}")
_TITLE = re.compile(r"^#\s+(.+)$", re.M)
# Machine-readable meta line written by sync_writeups.py (invisible once
# rendered: it is parsed here for the pills, then stripped before Markdown).
_META = re.compile(r"<!--\s*nctf-meta\s+(.*?)-->", re.S)
_META_KV = re.compile(r'(\w+)="([^"]*)"')


def _base_dir() -> str:
    env = os.environ.get("WRITEUPS_DIR")
    if env:
        return os.path.abspath(env)
    # repo root: CTFd/plugins/writeups/__init__.py -> up 3 -> repo root
    root = os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    )
    return os.path.join(root, "writeups")


def visible() -> bool:
    """Whether the writeups are shown to non-admins. Admins always see them."""
    v = get_config("writeups_visible")
    return str(v).lower() in ("1", "true", "yes", "on") if v is not None else False


def _safe_path(category: str, slug: str):
    """Resolve <base>/<category>/<slug>.md, or None if the names are unsafe or
    the file is missing. Constant, allowlisted names + a containment check keep
    a crafted request inside the writeups tree."""
    if not _SLUG.fullmatch(category or "") or not _SLUG.fullmatch(slug or ""):
        return None
    base = _base_dir()
    path = os.path.abspath(os.path.join(base, category, slug + ".md"))
    if os.path.commonpath([path, base]) != base:
        return None
    return path if os.path.isfile(path) else None


def _title_of(md: str, fallback: str) -> str:
    m = _TITLE.search(md or "")
    return m.group(1).strip() if m else fallback


def _meta_of(head: str) -> dict:
    """Parse the `nctf-meta` line into a dict (empty if absent)."""
    m = _META.search(head or "")
    if not m:
        return {}
    return dict(_META_KV.findall(m.group(1)))


def _entry(head: str, slug: str) -> dict:
    """One writeup's card metadata (title + optional difficulty/points/stub)."""
    meta = _meta_of(head)
    pts = (meta.get("points") or "").strip()
    return {
        "slug": slug,
        "title": _title_of(head, slug),
        "difficulty": (meta.get("difficulty") or "").strip().lower() or None,
        "points": pts if pts.isdigit() else None,
        "stub": meta.get("stub") == "1",
    }


def _index():
    """{category: [entry, ...]} for every writeup file on disk (sorted)."""
    base = _base_dir()
    out = {}
    if not os.path.isdir(base):
        return out
    for cat in sorted(os.listdir(base)):
        cat_dir = os.path.join(base, cat)
        if not os.path.isdir(cat_dir) or not _SLUG.fullmatch(cat):
            continue
        entries = []
        for fn in sorted(os.listdir(cat_dir)):
            if not fn.endswith(".md"):
                continue
            slug = fn[:-3]
            if not _SLUG.fullmatch(slug):
                continue
            try:
                head = open(os.path.join(cat_dir, fn), encoding="utf-8").read(400)
            except OSError:
                head = ""
            entries.append(_entry(head, slug))
        if entries:
            out[cat] = entries
    return out


def _render_md(path: str) -> str:
    md = open(path, encoding="utf-8").read()
    md = _META.sub("", md, count=1).lstrip()  # drop the machine meta line
    md = _FLAG.sub("NCTF{…}", md)  # never serve a real flag from a writeup
    return build_markdown(md)


@bp.route("/")
def index():
    admin = is_admin()
    live = visible()
    if not live and not admin:
        return render_template(
            "writeups/index.html",
            published=False,
            tree={},
            total=0,
            admin=False,
            live=False,
        )
    tree = _index()
    total = sum(len(v) for v in tree.values())
    return render_template(
        "writeups/index.html",
        published=True,
        tree=tree,
        total=total,
        admin=admin,
        live=live,
    )


@bp.route("/<category>/<slug>")
def show(category, slug):
    admin = is_admin()
    if not visible() and not admin:
        return redirect(url_for("writeups.index"))
    path = _safe_path(category, slug)
    if not path:
        abort(404)
    content = _render_md(path)
    head = open(path, encoding="utf-8").read(400)
    entry = _entry(head, slug)
    return render_template(
        "writeups/show.html",
        content=content,
        title=entry["title"],
        category=category,
        difficulty=entry["difficulty"],
        points=entry["points"],
        stub=entry["stub"],
    )


@bp.route("/admin")
@admins_only
def admin_page():
    return render_template(
        "writeups/admin.html", enabled=visible(), tree=_index(), base=_base_dir()
    )


@bp.route("/admin/toggle", methods=["POST"])
@admins_only
def admin_toggle():
    want = (request.form.get("visible") or "").lower() in ("1", "true", "yes", "on")
    set_config("writeups_visible", "true" if want else "false")
    return redirect(url_for("writeups.admin_page"))


def load(app):
    from CTFd.plugins import register_admin_plugin_menu_bar, register_user_page_menu_bar

    app.register_blueprint(bp, url_prefix="/plugins/writeups")
    register_user_page_menu_bar("Writeups", "/plugins/writeups/")
    register_admin_plugin_menu_bar("Writeups", "/plugins/writeups/admin")
