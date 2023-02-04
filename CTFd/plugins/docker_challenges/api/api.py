import json
from datetime import datetime

from flask import abort, request
from flask_restx import Namespace, Resource

from CTFd.models import db
from CTFd.utils.config import is_teams_mode
from CTFd.utils.dates import unix_time
from CTFd.utils.decorators import admins_only, authed_only
from CTFd.utils.user import get_current_team, get_current_user

from ..functions.containers import create_container, delete_container
from ..functions.general import (get_repositories, get_secrets,
                                 get_unavailable_ports)
from ..functions.services import create_service, delete_service
from ..models.models import (DockerChallenge, DockerChallengeTracker,
                             DockerConfig, DockerServiceChallenge)

active_docker_namespace = Namespace("docker_status", description='Endpoint to retrieve User Docker Image Status')
container_namespace = Namespace("container", description='Endpoint to interact with containers')
docker_namespace = Namespace("docker", description='Endpoint to retrieve dockerstuff')
secret_namespace = Namespace("secret", description='Endpoint to retrieve dockerstuff')
kill_container = Namespace("nuke", description='Endpoint to nuke containers')

def delete_docker(docker, type, id):
    if type == "docker_service":
        assert(delete_service(docker, id))

    else:
        assert(delete_container(docker, id))
    DockerChallengeTracker.query.filter_by(instance_id=id).delete()
    db.session.commit()


@kill_container.route("", methods=['POST', 'GET'])
class KillContainerAPI(Resource):
    @admins_only
    def get(self):
        container = request.args.get('container')
        full = request.args.get('all')
        docker_config = DockerConfig.query.filter_by(id=1).first_or_404()
        docker_tracker = DockerChallengeTracker.query.all()
        challenges = {c.id: c for c in DockerChallenge.query.all()}
        challenges.update({c.id: c for c in DockerServiceChallenge.query.all()})

        if full == "true":
            for c in docker_tracker:
                challenge_id = c.challenge_id
                challenge = challenges.get(challenge_id)
                if challenge:
                    challenge_type = challenge.type
                    print(f"type:{challenge_type}")
                    print(f"instance_id:{c.instance_id}")
                    delete_docker(docker=docker_config, type=challenge_type, id=c.instance_id)

        elif container != 'null' and container in [c.instance_id for c in docker_tracker]:
            c = next((c for c in docker_tracker if c.instance_id == container), None)
            if c:
                challenge = challenges.get(c.challenge_id)
                if challenge:
                    delete_docker(docker=docker_config, type=challenge.type, id=c.instance_id)
                else:
                    return "Challenge not found", 404
            else:
                return "Container not found", 404

        else:
            return "Invalid request", 400

        return "Success", 200


@container_namespace.route("", methods=['POST', 'GET'])
class ContainerAPI(Resource):
    @authed_only
    # I wish this was Post... Issues with API/CSRF and whatnot. Open to a Issue solving this.
    def get(self):
        challenge_id = request.args.get('id')
        if not challenge_id:
            return abort(403)
        docker = DockerConfig.query.filter_by(id=1).first()
        containers = DockerChallengeTracker.query.all()
        challenge = DockerChallenge.query.filter_by(id=challenge_id).first()
        if not challenge:
            challenge = DockerServiceChallenge.query.filter_by(id=challenge_id).first()
        if not challenge:
            return abort(403)
        if is_teams_mode():
            session = get_current_team()
        else:
            session = get_current_user()
        for i in containers:
            if int(session.id) == int(i.team_id if is_teams_mode() else i.user_id) and (unix_time(datetime.utcnow()) - int(i.timestamp)) >= 7200:
                delete_docker(docker, challenge.type, i.instance_id)
                DockerChallengeTracker.query.filter_by(instance_id=i.instance_id).delete()
                db.session.commit()
        if is_teams_mode():
            check = DockerChallengeTracker.query.filter_by(team_id=session.id).filter_by(docker_image=challenge.docker_image).filter_by(challenge_id=challenge.id).first()
        else:
            check = DockerChallengeTracker.query.filter_by(user_id=session.id).filter_by(docker_image=challenge.docker_image).filter_by(challenge_id=challenge.id).first()
        # If this container is already created, we don't need another one.
        if check != None and not (unix_time(datetime.utcnow()) - int(check.timestamp)) >= 300:
            return abort(403)
        # The exception would be if we are reverting a box. So we'll delete it if it exists and has been around for more than 5 minutes.
        elif check != None:
            delete_docker(docker, challenge.type, check.instance_id)
            if is_teams_mode():
                DockerChallengeTracker.query.filter_by(team_id=session.id).filter_by(docker_image=challenge.docker_image).filter_by(challenge_id=challenge.id).delete()
            else:
                DockerChallengeTracker.query.filter_by(user_id=session.id).filter_by(docker_image=challenge.docker_image).filter_by(challenge_id=challenge.id).delete()
            db.session.commit()
        portsbl = get_unavailable_ports(docker)
        if challenge.docker_type == 'service':
            instance_id, data = create_service(docker, challenge_id=challenge.id, image=challenge.docker_image, team=session.name, portbl=portsbl)
            ports_json = json.loads(data)['EndpointSpec']['Ports']
            ports = [f"{p['PublishedPort']}/{p['Protocol']}" for p in ports_json]
        else:
            instance_id, data = create_container(docker, challenge.docker_image, session.name, portsbl)
            ports_json = json.loads(data)['HostConfig']['PortBindings'].values()
            ports = [ f"{i['HostPort']}" for p in ports_json for i in p ]
        entry = DockerChallengeTracker(
            team_id=session.id if is_teams_mode() else None,
            user_id=session.id if not is_teams_mode() else None,
            challenge_id=challenge_id,
            docker_image=challenge.docker_image,
            timestamp=unix_time(datetime.utcnow()),
            revert_time=unix_time(datetime.utcnow()) + 300,
            instance_id=instance_id,
            ports=','.join(ports),
            host=str(docker.hostname).split(':')[0]
        )
        db.session.add(entry)
        db.session.commit()
        return


@active_docker_namespace.route("", methods=['POST', 'GET'])
class DockerStatus(Resource):
    """
	The Purpose of this API is to retrieve a public JSON string of all docker containers
	in use by the current team/user.
	"""

    @authed_only
    def get(self):
        docker = DockerConfig.query.filter_by(id=1).first()
        if is_teams_mode():
            session = get_current_team()
            tracker = DockerChallengeTracker.query.filter_by(team_id=session.id)
        else:
            session = get_current_user()
            tracker = DockerChallengeTracker.query.filter_by(user_id=session.id)
        data = list()
        for i in tracker:
            data.append({
                'id': i.id,
                'team_id': i.team_id,
                'user_id': i.user_id,
                'challenge_id': i.challenge_id,
                'docker_image': i.docker_image,
                'timestamp': i.timestamp,
                'revert_time': i.revert_time,
                'instance_id': i.instance_id,
                'ports': i.ports.split(','),
                'host': str(docker.hostname).split(':')[0]
            })
        return {
            'success': True,
            'data': data
        }


@docker_namespace.route("", methods=['POST', 'GET'])
class DockerAPI(Resource):
    """
	This is for creating Docker Challenges. The purpose of this API is to populate the Docker Image Select form
	object in the Challenge Creation Screen.
	"""

    @admins_only
    def get(self):
        docker = DockerConfig.query.filter_by(id=1).first()
        images = get_repositories(docker, tags=True, repos=docker.repositories)
        if images:
            data = list()
            for i in images:
                data.append({'name': i})
            return {
                'success': True,
                'data': data
            }
        else:
            return {
                       'success': False,
                       'data': [
                           {
                               'name': 'Error in Docker Config!'
                           }
                       ]
                   }, 400

@secret_namespace.route("", methods=['POST', 'GET'])
class SecretAPI(Resource):
    """
	This is for creating Docker Challenges. The purpose of this API is to populate the Docker Secret Select form
	object in the Challenge Creation Screen.
	"""

    @admins_only
    def get(self):
        docker = DockerConfig.query.filter_by(id=1).first()
        secrets = get_secrets(docker)
        if secrets:
            data = list()
            for i in secrets:
                data.append({'name': i['Name'],'id': i['ID']})
            return {
                'success': True,
                'data': data
            }
        else:
            return {
                       'success': False,
                       'data': [
                           {
                               'name': 'Error in Docker Config!'
                           }
                       ]
                   }, 400