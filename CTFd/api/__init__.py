from flask import current_app as app, request, redirect, jsonify, url_for, Blueprint, abort

api = Blueprint('api', __name__)

