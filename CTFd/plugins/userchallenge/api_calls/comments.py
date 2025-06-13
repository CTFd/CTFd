


from flask import request
from CTFd.api.v1.comments import get_comment_model
from CTFd.api.v1.helpers.request import validate_args
from CTFd.constants import RawEnum
from CTFd.constants.sessions import Session
from CTFd.plugins.userchallenge.utils import userChallenge_allowed
from CTFd.schemas.comments import CommentSchema
from CTFd.utils.helpers.models import build_model_filters
from CTFd.models import Comments, db
from CTFd.utils.user import get_current_user, is_admin


def load(app):
    @app.route('/userchallenge/api/comments',methods=['GET'])
    @userChallenge_allowed
    @validate_args(
        {
            "challenge_id": (int, None),
            "user_id": (int, None),
            "team_id": (int, None),
            "page_id": (int, None),
            "q": (str, None),
            "field": (RawEnum("CommentFields", {"content": "content"}), None),
        },
        location="query",
    )
    def getComs(query_args):
        q = query_args.pop("q", None)
        field = str(query_args.pop("field", None))
        CommentModel = get_comment_model(data=query_args)
        filters = build_model_filters(model=CommentModel, query=q, field=field)

        comments = (
            CommentModel.query.filter_by(**query_args)
            .filter(*filters)
            .order_by(CommentModel.id.desc())
            .paginate(max_per_page=100, error_out=False)
        )
        schema = CommentSchema(many=True)
        response = schema.dump(comments.items)

        if response.errors:
            return {"success": False, "errors": response.errors}, 400

        return {
            "meta": {
                "pagination": {
                    "page": comments.page,
                    "next": comments.next_num,
                    "prev": comments.prev_num,
                    "pages": comments.pages,
                    "per_page": comments.per_page,
                    "total": comments.total,
                }
            },
            "success": True,
            "data": response.data,
        }
    @app.route('/userchallenge/api/comments',methods=['POST'])
    @userChallenge_allowed
    @validate_args(
        {
            "challenge_id": (int, None),
            "user_id": (int, None),
            "team_id": (int, None),
            "page_id": (int, None),
            "q": (str, None),
            "field": (RawEnum("CommentFields", {"content": "content"}), None),
        },
        location="query",
    )
    def postCom(query_args):
        req = request.get_json()
        # Always force author IDs to be the actual user
        req["author_id"] = Session["id"]
        CommentModel = get_comment_model(data=req)

        m = CommentModel(**req)
        db.session.add(m)
        db.session.commit()

        schema = CommentSchema()

        response = schema.dump(m)
        db.session.close()

        return {"success": True, "data": response.data}
    @app.route('/userchallenge/api/comments/<comment_id>',methods=['DELETE'])
    @userChallenge_allowed
    def deleteCom(comment_id):
        comment = Comments.query.filter_by(id=comment_id).first_or_404()
        if comment.author_id == get_current_user().id or is_admin():
            db.session.delete(comment)
            db.session.commit()
            db.session.close()        
            return {"success": True}
        else:
            return {"success": False}
    