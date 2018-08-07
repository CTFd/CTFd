from flask import current_app as app, request, redirect, jsonify, url_for, Blueprint, abort
from flask_restful import Api, Resource, url_for
from CTFd.api.challenges import Challenges

api = Blueprint('api', __name__, url_prefix='/api')
CTFd_API = Api(api)

CTFd_API.add_resource(Challenges, '/challenges')
