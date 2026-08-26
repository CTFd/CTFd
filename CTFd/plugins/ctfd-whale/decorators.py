import functools
import time
from flask import request, current_app, session
from flask_restx import abort
from sqlalchemy.sql import and_

from CTFd.models import Challenges
from CTFd.utils.user import is_admin, get_current_user
from .utils.cache import CacheProvider


def challenge_visible(func):
    @functools.wraps(func)
    def _challenge_visible(*args, **kwargs):
        challenge_id = request.args.get('challenge_id')
        if is_admin():
            if not Challenges.query.filter(
                Challenges.id == challenge_id
            ).first():
                abort(404, 'no such challenge', success=False)
        else:
            if not Challenges.query.filter(
                Challenges.id == challenge_id,
                and_(Challenges.state != "hidden", Challenges.state != "locked"),
            ).first():
                abort(403, 'challenge not visible', success=False)
        return func(*args, **kwargs)

    return _challenge_visible


def frequency_limited(func):
    @functools.wraps(func)
    def _frequency_limited(*args, **kwargs):
        if is_admin():
            return func(*args, **kwargs)
        redis_util = CacheProvider(app=current_app, user_id=get_current_user().id)
        if not redis_util.acquire_lock():
            abort(403, 'Request Too Fast!', success=False)
            # last request was unsuccessful. this is for protection.

        if "limit" not in session:
            session["limit"] = int(time.time())
        else:
            if int(time.time()) - session["limit"] < 60:
                abort(403, 'Frequency limit, You should wait at least 1 min.', success=False)
        session["limit"] = int(time.time())

        result = func(*args, **kwargs)
        redis_util.release_lock()  # if any exception is raised, lock will not be released
        return result

    return _frequency_limited
