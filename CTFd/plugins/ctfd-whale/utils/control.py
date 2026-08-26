import datetime
import traceback

from flask import current_app
from CTFd.utils import get_config
from .cache import CacheProvider
from .db import DBContainer, db
from .docker import DockerUtils
from .routers import Router


class ControlUtil:
    @staticmethod
    def try_add_container(user_id, challenge_id):
        cache = CacheProvider(app=current_app)
        if not cache.acquire_global_lock():
            return False, 'Server busy, please retry.'
        try:
            limit = int(get_config("whale:docker_max_container_count", 1000))
            if int(DBContainer.get_all_alive_container_count()) > limit:
                return False, 'Max container count exceed.'
            container = DBContainer.create_container_record(user_id, challenge_id)
        finally:
            cache.release_global_lock()
        try:
            DockerUtils.add_container(container)
            ok, msg = Router.register(container)
            if ok:
                return True, 'Container created'
        except Exception:
            print(traceback.format_exc())
            msg = 'Container creation failed'
        try:
            DockerUtils.remove_container(container)
        except Exception:
            pass
        DBContainer.remove_container_record(user_id)
        return False, msg

    @staticmethod
    def try_remove_container(user_id):
        container = DBContainer.get_current_containers(user_id=user_id)
        if not container:
            return False, 'No such container'
        for _ in range(3):  # configurable? as "onerror_retry_cnt"
            try:
                ok, msg = Router.unregister(container)
                if not ok:
                    return False, msg
                DockerUtils.remove_container(container)
                DBContainer.remove_container_record(user_id)
                return True, 'Container destroyed'
            except Exception:
                print(traceback.format_exc())
        return False, 'Failed when destroying instance, please contact admin!'

    @staticmethod
    def try_renew_container(user_id):
        container = DBContainer.get_current_containers(user_id)
        if not container:
            return False, 'No such container'
        timeout = int(get_config("whale:docker_timeout", "3600"))
        container.start_time = container.start_time + \
                               datetime.timedelta(seconds=timeout)
        if container.start_time > datetime.datetime.now():
            container.start_time = datetime.datetime.now()
            # race condition? useless maybe?
            # useful when docker_timeout < poll timeout (10 seconds)
            # doesn't make any sense
        else:
            return False, 'Invalid container'
        container.renew_count += 1
        db.session.commit()
        return True, 'Container Renewed'
