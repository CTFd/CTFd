from flask import session


class _SessionWrapper:
    @property
    def id(self):
        return session.get("id", 0)

    @property
    def nonce(self):
        return session.get("nonce")

    @property
    def hash(self):
        return session.get("hash")


Session = _SessionWrapper()
