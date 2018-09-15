from flask import render_template, Blueprint, redirect, url_for, request

from CTFd.utils import config
from CTFd.utils import get_config

from CTFd.utils.scores import get_standings

scoreboard = Blueprint('scoreboard', __name__)


@scoreboard.route('/scoreboard')
def scoreboard_view():
    if get_config('view_scoreboard_if_authed') and not config.authed():
        return redirect(url_for('auth.login', next=request.path))
    if config.hide_scores():
        return render_template('scoreboard.html', errors=['Scores are currently hidden'])
    standings = get_standings()
    return render_template('scoreboard.html', teams=standings, score_frozen=config.is_scoreboard_frozen())
