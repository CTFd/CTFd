import json
import os
from functools import wraps
from urllib.parse import urlparse

import requests
from flask import Flask, request

from CTFd.models import Challenges, Hints, Solves, Unlocks
from CTFd.utils import config as ctfd_config
from CTFd.utils.dates import ctftime
from CTFd.utils.logging import log
from CTFd.utils.user import get_current_team, get_current_user


def load(app: Flask):
    print("Datadog log plugin loaded")
    set_default_plugin_config(app)

    def hint_trade_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            result = f(*args, **kwargs)

            if not ctftime() or not is_plugin_configured(app):
                return result

            if result.json['success'] == False:
                return result

            # too little points:
            # pts-ctfd-ctfd-1   | {'success': False, 'errors': {'score': 'You do not have enough points to unlock this hint'}}

            # successful unlock
            # {'success': True, 'data': {'team_id': 3, 'target': 1, 'type': 'hints', 'date': '2024-01-09T16:36:10.899814+00:00', 'user_id': 1, 'id': 3}}

            user = get_current_user()
            team = get_current_team()
            hint = get_hint_by_id(result.json['data']['target'])
            challenge = get_challenge_by_id(hint.challenge_id)

            message = "source=ctfd, event=" + ctfd_config.ctf_name() + ",type=hint,success="+str(result.json['success'])+",challenge="+challenge.name+",category='"+challenge.category+"',team="+team.name+",user="+user.name+",points="+str(hint.cost*-1)+",msg=Player " + user.name + " just traded " + str(hint.cost) + " points for a hint on challenge " + challenge.name
            log("submissions", message)

            return result

        return wrapper

    def challenge_attempt_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            result = f(*args, **kwargs)

            if not ctftime() or not is_plugin_configured(app):
                return result

            challenge = get_challenge_for_request()
            user = get_current_user()
            team = get_current_team()

            #print(result.json)

            if result is None or result.json is None or result.json['data'] is None:
                return result # nothing we can do

            if result.json['data']['status'] == "incorrect":
                message = "source=ctfd, event=" + ctfd_config.ctf_name() + ",type=challenge,status=incorrect,challenge='"+challenge.name+"',category="+challenge.category+",team="+team.name+",user="+user.name+",points=0,msg='Team " + team.name + " provided an incorrect answer for challenge " + challenge.name + "'"
                log("submissions", message)

            elif result.json['data']['status'] == "correct": # there is also already_solve so we need to be precise
                num_solves = get_solvers_count_for_challenge(challenge)

                message = "source=ctfd, event=" + ctfd_config.ctf_name() + ",type=challenge,status=correct,challenge='"+challenge.name+"',category="+challenge.category+",team="+team.name+",user="+user.name+",points="+str(challenge.value)+",msg='Team " + team.name + " is the " + str(num_solves) + " to solve challenge " + challenge.name + "'"
                log("submissions", message)

            return result

        return wrapper

    app.view_functions[
        "api.challenges_challenge_attempt"
    ] = challenge_attempt_decorator(
        app.view_functions["api.challenges_challenge_attempt"]
    )
    #  /api/v1/unlocks
    app.view_functions[
        "api.unlocks_unlock_list"
    ] = hint_trade_decorator(
        app.view_functions["api.unlocks_unlock_list"]
    )


def set_default_plugin_config(app: Flask):
    app.config["DD_API_KEY"] = os.environ.get("DD_API_KEY", "")


def is_plugin_configured(app: Flask) -> bool:
    return True

def validate_url(url: str) -> bool:
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc, result.path])
    except Exception:
        return False


def check_submission_for_valid_flag(data: json) -> bool:
    return (
        isinstance(data, dict)
        and data.get("success")
        and isinstance(data.get("data"), dict)
        and data.get("data").get("status") == "correct"
    )

def get_challenge_by_id(challenge_id: int) -> Challenges:
    challenge = Challenges.query.filter_by(id=challenge_id).first_or_404()

    return challenge

def get_hint_by_id(hint_id: int) -> Hints:
    hint = Hints.query.filter_by(id=hint_id).first_or_404()

    return hint

def get_unlock_by_id(unlock_id: int) -> Unlocks:
    unlock = Unlocks.query.filter_by(id=unlock_id).first_or_404()

    return unlock


def get_challenge_for_request() -> Challenges:
    if request.content_type != "application/json":
        request_data = request.form
    else:
        request_data = request.get_json()

    challenge_id = request_data.get("challenge_id")
    challenge = Challenges.query.filter_by(id=challenge_id).first_or_404()

    return challenge


def get_solvers_count_for_challenge(challenge: Challenges) -> int:
    solvers = get_solvers_for_challenge(challenge)

    return solvers.count()


def get_solvers_for_challenge(challenge: Challenges) -> Solves:
    team_mode = ctfd_config.is_teams_mode()

    solvers = Solves.query.filter_by(challenge_id=challenge.id)
    if team_mode:
        solvers = solvers.filter(Solves.team.has(hidden=False))
    else:
        solvers = solvers.filter(Solves.user.has(hidden=False))

    return solvers


def log_to_dd(data: dict, apikey: str) -> None:
    return # disable posting for now
    try:
        url = 'https://api.datadoghq.com/api/v2/logs'
        headers = {
            'content-type': 'application/json',
            'DD-API-KEY': apikey,
        }

        r = requests.post(url, headers=headers, json=data)
        print("response from datadog: " + str(r.status_code))
    except Exception:
        print("Failed to post payload")
