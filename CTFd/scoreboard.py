from flask import Blueprint, render_template

from CTFd.cache import cache, make_cache_key
from CTFd.utils import config
from CTFd.utils.decorators.visibility import check_score_visibility
from CTFd.utils.helpers import get_infos
from CTFd.utils.scores import get_standings

scoreboard = Blueprint("scoreboard", __name__)


@scoreboard.route("/scoreboard")
@check_score_visibility
@cache.cached(timeout=60, key_prefix=make_cache_key)
def listing():
    infos = get_infos()

    if config.is_scoreboard_frozen():
        infos.append("Scoreboard has been frozen")

    standings = get_standings()
    return render_template("scoreboard.html", standings=standings, infos=infos)
