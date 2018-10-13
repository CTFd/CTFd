from __future__ import division # Use floating point for math calculations
from CTFd.plugins.challenges import BaseChallenge, CHALLENGE_CLASSES
from CTFd.plugins import register_plugin_assets_directory
from CTFd.plugins.keys import get_key_class
from CTFd.models import db, Solves, WrongKeys, Keys, Challenges, Files, Tags, Teams, Hints
from CTFd import utils
import math


class DynamicValueChallenge(BaseChallenge):
    id = "dynamic"  # Unique identifier used to register challenges
    name = "dynamic"  # Name of a challenge type
    templates = {  # Handlebars templates used for each aspect of challenge editing & viewing
        'create': '/plugins/DynamicValueChallenge/assets/dynamic-challenge-create.njk',
        'update': '/plugins/DynamicValueChallenge/assets/dynamic-challenge-update.njk',
        'modal': '/plugins/DynamicValueChallenge/assets/dynamic-challenge-modal.njk',
    }
    scripts = {  # Scripts that are loaded when a template is loaded
        'create': '/plugins/DynamicValueChallenge/assets/dynamic-challenge-create.js',
        'update': '/plugins/DynamicValueChallenge/assets/dynamic-challenge-update.js',
        'modal': '/plugins/DynamicValueChallenge/assets/dynamic-challenge-modal.js',
    }

    @staticmethod
    def create(request):
        """
        This method is used to process the challenge creation request.

        :param request:
        :return:
        """
        files = request.files.getlist('files[]')

        # Create challenge
        chal = DynamicChallenge(
            name=request.form['name'],
            description=request.form['description'],
            value=request.form['value'],
            category=request.form['category'],
            type=request.form['chaltype'],
            minimum=request.form['minimum'],
            decay=request.form['decay']
        )

        if 'hidden' in request.form:
            chal.hidden = True
        else:
            chal.hidden = False

        max_attempts = request.form.get('max_attempts')
        if max_attempts and max_attempts.isdigit():
            chal.max_attempts = int(max_attempts)

        db.session.add(chal)
        db.session.commit()

        flag = Keys(chal.id, request.form['key'], request.form['key_type[0]'])
        if request.form.get('keydata'):
            flag.data = request.form.get('keydata')
        db.session.add(flag)

        db.session.commit()

        for f in files:
            utils.upload_file(file=f, chalid=chal.id)

        db.session.commit()

    @staticmethod
    def read(challenge):
        """
        This method is in used to access the data of a challenge in a format processable by the front end.

        :param challenge:
        :return: Challenge object, data dictionary to be returned to the user
        """
        challenge = DynamicChallenge.query.filter_by(id=challenge.id).first()
        data = {
            'id': challenge.id,
            'name': challenge.name,
            'value': challenge.value,
            'initial': challenge.initial,
            'decay': challenge.decay,
            'minimum': challenge.minimum,
            'description': challenge.description,
            'category': challenge.category,
            'hidden': challenge.hidden,
            'max_attempts': challenge.max_attempts,
            'type': challenge.type,
            'type_data': {
                'id': DynamicValueChallenge.id,
                'name': DynamicValueChallenge.name,
                'templates': DynamicValueChallenge.templates,
                'scripts': DynamicValueChallenge.scripts,
            }
        }
        return challenge, data

    @staticmethod
    def update(challenge, request):
        """
        This method is used to update the information associated with a challenge. This should be kept strictly to the
        Challenges table and any child tables.

        :param challenge:
        :param request:
        :return:
        """
        challenge = DynamicChallenge.query.filter_by(id=challenge.id).first()

        challenge.name = request.form['name']
        challenge.description = request.form['description']
        challenge.value = int(request.form.get('value', 0)) if request.form.get('value', 0) else 0
        challenge.max_attempts = int(request.form.get('max_attempts', 0)) if request.form.get('max_attempts', 0) else 0
        challenge.category = request.form['category']
        challenge.hidden = 'hidden' in request.form

        challenge.initial = request.form['initial']
        challenge.minimum = request.form['minimum']
        challenge.decay = request.form['decay']

        db.session.commit()
        db.session.close()

    @staticmethod
    def delete(challenge):
        """
        This method is used to delete the resources used by a challenge.

        :param challenge:
        :return:
        """
        WrongKeys.query.filter_by(chalid=challenge.id).delete()
        Solves.query.filter_by(chalid=challenge.id).delete()
        Keys.query.filter_by(chal=challenge.id).delete()
        files = Files.query.filter_by(chal=challenge.id).all()
        for f in files:
            utils.delete_file(f.id)
        Files.query.filter_by(chal=challenge.id).delete()
        Tags.query.filter_by(chal=challenge.id).delete()
        Hints.query.filter_by(chal=challenge.id).delete()
        DynamicChallenge.query.filter_by(id=challenge.id).delete()
        Challenges.query.filter_by(id=challenge.id).delete()
        db.session.commit()

    @staticmethod
    def attempt(chal, request):
        """
        This method is used to check whether a given input is right or wrong. It does not make any changes and should
        return a boolean for correctness and a string to be shown to the user. It is also in charge of parsing the
        user's input from the request itself.

        :param chal: The Challenge object from the database
        :param request: The request the user submitted
        :return: (boolean, string)
        """
        provided_key = request.form['key'].strip()
        chal_keys = Keys.query.filter_by(chal=chal.id).all()
        for chal_key in chal_keys:
            if get_key_class(chal_key.type).compare(chal_key, provided_key):
                return True, 'Correct'
        return False, 'Incorrect'

    @staticmethod
    def solve(team, chal, request):
        """
        This method is used to insert Solves into the database in order to mark a challenge as solved.

        :param team: The Team object from the database
        :param chal: The Challenge object from the database
        :param request: The request the user submitted
        :return:
        """
        chal = DynamicChallenge.query.filter_by(id=chal.id).first()

        solve_count = Solves.query.join(Teams, Solves.teamid == Teams.id).filter(Solves.chalid==chal.id, Teams.banned==False).count()

        # It is important that this calculation takes into account floats.
        # Hence this file uses from __future__ import division
        value = (
                    (
                        (chal.minimum - chal.initial)/(chal.decay**2)
                    ) * (solve_count**2)
                ) + chal.initial

        value = math.ceil(value)

        if value < chal.minimum:
            value = chal.minimum

        chal.value = value

        provided_key = request.form['key'].strip()
        solve = Solves(teamid=team.id, chalid=chal.id, ip=utils.get_ip(req=request), flag=provided_key)
        db.session.add(solve)

        db.session.commit()
        db.session.close()

    @staticmethod
    def fail(team, chal, request):
        """
        This method is used to insert WrongKeys into the database in order to mark an answer incorrect.

        :param team: The Team object from the database
        :param chal: The Challenge object from the database
        :param request: The request the user submitted
        :return:
        """
        provided_key = request.form['key'].strip()
        wrong = WrongKeys(teamid=team.id, chalid=chal.id, ip=utils.get_ip(request), flag=provided_key)
        db.session.add(wrong)
        db.session.commit()
        db.session.close()


class DynamicChallenge(Challenges):
    __mapper_args__ = {'polymorphic_identity': 'dynamic'}
    id = db.Column(None, db.ForeignKey('challenges.id'), primary_key=True)
    initial = db.Column(db.Integer)
    minimum = db.Column(db.Integer)
    decay = db.Column(db.Integer)

    def __init__(self, name, description, value, category, type='dynamic', minimum=1, decay=50):
        self.name = name
        self.description = description
        self.value = value
        self.initial = value
        self.category = category
        self.type = type
        self.minimum = minimum
        self.decay = decay


def load(app):
    app.db.create_all()
    CHALLENGE_CLASSES['dynamic'] = DynamicValueChallenge
    register_plugin_assets_directory(app, base_path='/plugins/DynamicValueChallenge/assets/')