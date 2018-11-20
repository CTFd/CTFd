from flask import render_template, Blueprint, redirect, url_for, request

from CTFd.utils import config
from CTFd.utils import get_config
from CTFd.utils.decorators.visibility import check_score_visibility

from CTFd.utils.scores import get_standings

scoreboard = Blueprint('scoreboard', __name__)


@scoreboard.route('/scoreboard')
@check_score_visibility
def listing():
    standings = get_standings()
    return render_template(
        'scoreboard.html',
        standings=standings,
        score_frozen=config.is_scoreboard_frozen()
    )
