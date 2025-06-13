from CTFd.api.v1.helpers.request import validate_args
from CTFd.models import ChallengeTopics as ChallengeTopicsModel, Topics
from CTFd.models import ChallengeTopics,db
from CTFd.plugins.userchallenge.utils import userChallenge_allowed
from CTFd.schemas.topics import ChallengeTopicSchema, TopicSchema
from flask import request

def load(app):
    @app.route('/userchallenge/api/challenges/<challenge_id>/topics', methods=['GET'])
    def getTopics(challenge_id):
        response = []

        topics = ChallengeTopicsModel.query.filter_by(challenge_id=challenge_id).all()

        for t in topics:
            response.append(
                {
                    "id": t.id,
                    "challenge_id": t.challenge_id,
                    "topic_id": t.topic_id,
                    "value": t.topic.value,
                }
            )
        return {"success": True, "data": response}
    
    @app.route('/userchallenge/api/topics',methods=['POST'])
    @userChallenge_allowed
    def createTopic():
        req = request.get_json()
        value = req.get("value")

        if value:
            topic = Topics.query.filter_by(value=value).first()
            if topic is None:
                schema = TopicSchema()
                response = schema.load(req, session=db.session)

                if response.errors:
                    return {"success": False, "errors": response.errors}, 400

                topic = response.data
                db.session.add(topic)
                db.session.commit()
        else:
            topic_id = req.get("topic_id")
            topic = Topics.query.filter_by(id=topic_id).first_or_404()

        req["topic_id"] = topic.id
        topic_type = req.get("type")
        if topic_type == "challenge":
            schema = ChallengeTopicSchema()
            response = schema.load(req, session=db.session)
        else:
            return {"success": False}, 400

        db.session.add(response.data)
        db.session.commit()

        response = schema.dump(response.data)
        db.session.close()

        return {"success": True, "data": response.data}

    @app.route('/userchallenge/api/topics',methods=['DELETE'])
    @validate_args(
        {"type": (str, None), "target_id": (int, 0)},
        location="query",
    )
    def deleteTop(query_args):
        topic_type = query_args.get("type")
        target_id = int(query_args.get("target_id", 0))

        if topic_type == "challenge":
            Model = ChallengeTopics
        else:
            return {"success": False}, 400

        topic = Model.query.filter_by(id=target_id).first_or_404()
        db.session.delete(topic)
        db.session.commit()
        db.session.close()

        return {"success": True}
    @app.route('/userchallenge/api/topics/<topic_id>',methods=['GET'])
    def getTopic(topic_id):
        topic = Topics.query.filter_by(id=topic_id).first_or_404()
        response = TopicSchema().dump(topic)

        if response.errors:
            return {"success": False, "errors": response.errors}, 400

        return {"success": True, "data": response.data}
    @app.route('/userchallenge/api/topic/<topic_id>',methods=['DELETE'])
    @userChallenge_allowed
    def deleteTopic(topic_id):
        topic = Topics.query.filter_by(id=topic_id).first_or_404()
        db.session.delete(topic)
        db.session.commit()
        db.session.close()

        return {"success": True}
    