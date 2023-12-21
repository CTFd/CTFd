from flask import Blueprint, abort, request

from CTFd.utils.social import get_social_share

social = Blueprint("social", __name__)


@social.route("/share/<type>/assets/<path>")
def assets(type, path):
    SocialShare = get_social_share(type)
    if SocialShare is None:
        abort(404)

    s = SocialShare()
    return s.asset(path)


@social.route("/share/<type>")
def share(type):
    SocialShare = get_social_share(type)
    if SocialShare is None:
        abort(404)

    s = SocialShare()
    if request.args.get("mac") != s.mac:
        abort(403)

    return s.content
