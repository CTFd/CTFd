from flask import abort, request
from flask_restx import Namespace, Resource

from CTFd.utils import get_config
from CTFd.utils.decorators import authed_only
from CTFd.utils.social import get_social_share
from CTFd.utils.user import get_current_user_attrs

shares_namespace = Namespace("shares", description="Endpoint to create Share links")


@shares_namespace.route("")
class Share(Resource):
    @authed_only
    def post(self):
        if bool(get_config("social_shares")) is False:
            abort(403)
        req = request.get_json()
        share_type = req.get("type")

        SocialShare = get_social_share(type=share_type)
        user = get_current_user_attrs()
        share = SocialShare(user_id=user.id)
        response = {"url": share.url}
        return {"success": True, "data": response}
