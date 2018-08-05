from flask import current_app as app, request, redirect, jsonify, url_for, Blueprint, abort
from flask_restful import Api, Resource, url_for
from CTFd.api.challenges import Challenges

api = Blueprint('api', __name__, url_prefix='/api')
CTFdAPI = Api(api)

CTFdAPI.add_resource(Challenges, '/challenges')
