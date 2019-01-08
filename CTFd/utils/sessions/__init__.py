from flask.sessions import SessionInterface, SessionMixin
from flask.json.tag import TaggedJSONSerializer
from werkzeug.datastructures import CallbackDict
from CTFd.cache import cache
from CTFd.utils import text_type
from uuid import uuid4
from itsdangerous import Signer, BadSignature, want_bytes
import six


def total_seconds(td):
    return td.days * 60 * 60 * 24 + td.seconds


class CachedSession(CallbackDict, SessionMixin):
    """
    This code is mostly based off of the ServerSideSession from Flask-Session.

    https://github.com/fengsp/flask-session/blob/master/flask_session/sessions.py#L37
    """

    def __init__(self, initial=None, sid=None, permanent=None):
        def on_update(self):
            self.modified = True

        CallbackDict.__init__(self, initial, on_update)
        self.sid = sid
        if permanent:
            self.permanent = permanent
        self.modified = False

    def regenerate(self):
        cache.delete(self.sid)

        # Empty current sid and mark modified so the interface will give it a new one.
        self.sid = None
        self.modified = True


class CachingSessionInterface(SessionInterface):
    """
    This code is partially based off of the RedisSessionInterface from Flask-Session with updates to properly
    interoperate with Flask-Caching and be more inline with modern Flask (i.e. doesn't use pickle).

    https://github.com/fengsp/flask-session/blob/master/flask_session/sessions.py#L90
    """

    serializer = TaggedJSONSerializer()
    session_class = CachedSession

    def _generate_sid(self):
        return str(uuid4())

    def __init__(self, key_prefix, use_signer=False, permanent=False):
        self.key_prefix = key_prefix
        self.use_signer = use_signer
        self.permanent = permanent

    def open_session(self, app, request):
        sid = request.cookies.get(app.session_cookie_name)
        if not sid:
            sid = self._generate_sid()
            return self.session_class(sid=sid, permanent=self.permanent)

        if not six.PY2 and not isinstance(sid, text_type):
            sid = sid.decode('utf-8', 'strict')
        val = cache.get(self.key_prefix + sid)
        if val is not None:
            try:
                data = self.serializer.loads(val)
                return self.session_class(data, sid=sid)
            except Exception as e:
                return self.session_class(sid=sid, permanent=self.permanent)
        return self.session_class(sid=sid, permanent=self.permanent)

    def save_session(self, app, session, response):
        domain = self.get_cookie_domain(app)
        path = self.get_cookie_path(app)

        if not session:
            if session.modified:
                cache.delete(self.key_prefix + session.sid)
                response.delete_cookie(app.session_cookie_name,
                                       domain=domain, path=path)
            return

        if session.modified:
            httponly = self.get_cookie_httponly(app)
            secure = self.get_cookie_secure(app)
            expires = self.get_expiration_time(app, session)
            samesite = self.get_cookie_samesite(app)
            val = self.serializer.dumps(dict(session))

            if session.sid is None:
                session.sid = self._generate_sid()

            cache.set(key=self.key_prefix + session.sid, value=val, timeout=total_seconds(app.permanent_session_lifetime))
            session_id = session.sid
            response.set_cookie(
                app.session_cookie_name,
                session_id,
                expires=expires,
                httponly=httponly,
                domain=domain,
                path=path,
                secure=secure,
                samesite=samesite
            )
