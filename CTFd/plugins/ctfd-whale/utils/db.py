import datetime

from CTFd.models import db
from CTFd.utils import get_config
from ..models import WhaleContainer, WhaleRedirectTemplate


class DBContainer:
    @staticmethod
    def create_container_record(user_id, challenge_id):
        container = WhaleContainer(user_id=user_id, challenge_id=challenge_id)
        db.session.add(container)
        db.session.commit()

        return container

    @staticmethod
    def get_current_containers(user_id):
        q = db.session.query(WhaleContainer)
        q = q.filter(WhaleContainer.user_id == user_id)
        return q.first()

    @staticmethod
    def get_container_by_port(port):
        q = db.session.query(WhaleContainer)
        q = q.filter(WhaleContainer.port == port)
        return q.first()

    @staticmethod
    def remove_container_record(user_id):
        q = db.session.query(WhaleContainer)
        q = q.filter(WhaleContainer.user_id == user_id)
        q.delete()
        db.session.commit()

    @staticmethod
    def get_all_expired_container():
        timeout = int(get_config("whale:docker_timeout", "3600"))

        q = db.session.query(WhaleContainer)
        q = q.filter(
            WhaleContainer.start_time <
            datetime.datetime.now() - datetime.timedelta(seconds=timeout)
        )
        return q.all()

    @staticmethod
    def get_all_alive_container():
        timeout = int(get_config("whale:docker_timeout", "3600"))

        q = db.session.query(WhaleContainer)
        q = q.filter(
            WhaleContainer.start_time >=
            datetime.datetime.now() - datetime.timedelta(seconds=timeout)
        )
        return q.all()

    @staticmethod
    def get_all_container():
        q = db.session.query(WhaleContainer)
        return q.all()

    @staticmethod
    def get_all_alive_container_page(page_start, page_end):
        timeout = int(get_config("whale:docker_timeout", "3600"))

        q = db.session.query(WhaleContainer)
        q = q.filter(
            WhaleContainer.start_time >=
            datetime.datetime.now() - datetime.timedelta(seconds=timeout)
        )
        q = q.slice(page_start, page_end)
        return q.all()

    @staticmethod
    def get_all_alive_container_count():
        timeout = int(get_config("whale:docker_timeout", "3600"))

        q = db.session.query(WhaleContainer)
        q = q.filter(
            WhaleContainer.start_time >=
            datetime.datetime.now() - datetime.timedelta(seconds=timeout)
        )
        return q.count()


class DBRedirectTemplate:
    @staticmethod
    def get_all_templates():
        return WhaleRedirectTemplate.query.all()

    @staticmethod
    def create_template(name, access_template, frp_template):
        if WhaleRedirectTemplate.query.filter_by(key=name).first():
            return  # already existed
        db.session.add(WhaleRedirectTemplate(
            name, access_template, frp_template
        ))
        db.session.commit()

    @staticmethod
    def delete_template(name):
        WhaleRedirectTemplate.query.filter_by(key=name).delete()
        db.session.commit()
