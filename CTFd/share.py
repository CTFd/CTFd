from flask import Blueprint, abort, request

from CTFd.utils import get_config
from CTFd.utils.social import get_social_share

social = Blueprint("social", __name__)


@social.route("/share/<type>/assets/<path>")
def assets(type, path):
    if bool(get_config("social_shares")) is False:
        abort(403)
    SocialShare = get_social_share(type)
    if SocialShare is None:
        abort(404)

    s = SocialShare()
    if path != s.mac + ".png":
        abort(404)

    return s.asset(path)


@social.route("/share/<type>")
def share(type):
    if bool(get_config("social_shares")) is False:
        abort(403)
    SocialShare = get_social_share(type)
    if SocialShare is None:
        abort(404)

    s = SocialShare()
    if request.args.get("mac") != s.mac:
        abort(404)

    return s.content
