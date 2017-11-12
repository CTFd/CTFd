from CTFd.plugins import register_plugin_assets_directory
from CTFd.plugins.keys import get_key_class
from CTFd.models import db, Solves, WrongKeys, Keys, Challenges, Files, Tags
from CTFd import utils

from pymitter import EventEmitter

class BaseChallenge(object):
    id = None
    name = None
    templates = {}
    scripts = {}


class CTFdStandardChallenge(BaseChallenge):
    id = "standard"  # Unique identifier used to register challenges
    name = "standard"  # Name of a challenge type
    templates = {  # Handlebars templates used for each aspect of challenge editing & viewing
        'create': '/plugins/challenges/assets/standard-challenge-create.hbs',
        'update': '/plugins/challenges/assets/standard-challenge-update.hbs',
        'modal': '/plugins/challenges/assets/standard-challenge-modal.hbs',
    }
    scripts = {  # Scripts that are loaded when a template is loaded
        'create': '/plugins/challenges/assets/standard-challenge-create.js',
        'update': '/plugins/challenges/assets/standard-challenge-update.js',
        'modal': '/plugins/challenges/assets/standard-challenge-modal.js',
    }
    ee = EventEmitter(new_listener=False)

    @classmethod
    def create(cls, request):
        """
        This method is used to process the challenge creation request.

        :param request: The request the user submitted
        :return:
        """
        cls.ee.emit("challenge.onPreCreate", **locals())

        files = request.files.getlist('files[]')

        # Create challenge
        chal = Challenges(
            name=request.form['name'],
            description=request.form['desc'],
            value=request.form['value'],
            category=request.form['category'],
            type=request.form['chaltype']
        )

        if 'hidden' in request.form:
            chal.hidden = True
        else:
            chal.hidden = False

        max_attempts = request.form.get('max_attempts')
        if max_attempts and max_attempts.isdigit():
            chal.max_attempts = int(max_attempts)

        cls.ee.emit("challenge.onCreate", **locals())

        db.session.add(chal)
        db.session.commit()

        flag = Keys(chal.id, request.form['key'], request.form['key_type[0]'])
        if request.form.get('keydata'):
            flag.data = request.form.get('keydata')

        cls.ee.emit("challenge.onPostCreate", **locals())

        db.session.add(flag)

        db.session.commit()

        for f in files:
            utils.upload_file(file=f, chalid=chal.id)

        db.session.commit()

    @classmethod
    def read(cls, challenge):
        """
        This method is in used to access the data of a challenge in a format
        processable by the front end.

        :param challenge: The Challenge object from the database
        :return: Challenge object, data dictionary to be returned to the user
        """
        cls.ee.emit("challenge.onPreRead", **locals())

        data = {
            'id': challenge.id,
            'name': challenge.name,
            'value': challenge.value,
            'description': challenge.description,
            'category': challenge.category,
            'hidden': challenge.hidden,
            'max_attempts': challenge.max_attempts,
            'type': challenge.type,
            'type_data': {
                'id': cls.id,
                'name': cls.name,
                'templates': cls.templates,
                'scripts': cls.scripts,
            }
        }

        cls.ee.emit("challenge.onPostRead", **locals())

        return challenge, data

    @classmethod
    def update(cls, challenge, request):
        """
        This method is used to update the information associated with a
        challenge. This should be kept strictly to the Challenges table and any
        child tables.

        :param challenge: The Challenge object from the database
        :param request:  The request the user submitted
        :return:
        """
        cls.ee.emit("challenge.onPreUpdate", **locals())

        challenge.name = request.form['name']
        challenge.description = request.form['desc']
        challenge.value = request.form.get('value', default=0, type=int)
        challenge.max_attempts = request.form.get('max_attempts', default=0, type=int)
        challenge.category = request.form['category']
        challenge.hidden = 'hidden' in request.form

        cls.ee.emit("challenge.onPostUpdate", **locals())

        db.session.commit()
        db.session.close()

    @classmethod
    def delete(cls, challenge):
        """
        This method is used to delete the resources used by a challenge.

        :param challenge: The Challenge object from the database
        :return:
        """
        cls.ee.emit("challenge.onPreDelete", **locals())

        WrongKeys.query.filter_by(chalid=challenge.id).delete()
        Solves.query.filter_by(chalid=challenge.id).delete()
        Keys.query.filter_by(chal=challenge.id).delete()
        files = Files.query.filter_by(chal=challenge.id).all()
        for f in files:
            utils.delete_file(f.id)
        Files.query.filter_by(chal=challenge.id).delete()
        Tags.query.filter_by(chal=challenge.id).delete()
        Challenges.query.filter_by(id=challenge.id).delete()

        cls.ee.emit("challenge.onPostDelete", **locals())

        db.session.commit()

    @classmethod
    def attempt(cls, chal, request):
        """
        This method is used to check whether a given input is right or wrong. It
        does not make any changes and should return a boolean for correctness
        and a string to be shown to the user. It is also in charge of parsing
        the user's input from the request itself.

        :param chal: The Challenge object from the database
        :param request: The request the user submitted
        :return: (boolean, string)
        """
        cls.ee.emit("challenge.onPreAttempt", **locals())

        provided_key = request.form['key'].strip()
        chal_keys = Keys.query.filter_by(chal=chal.id).all()
        for chal_key in chal_keys:
            if get_key_class(chal_key.key_type).compare(chal_key.flag, provided_key):

                cls.ee.emit("challenge.onPostAttempt", status=True, **locals())

                return True, 'Correct'

        cls.ee.emit("challenge.onPostAttempt", status=False, **locals())

        return False, 'Incorrect'

    @classmethod
    def solve(cls, team, chal, request):
        """
        This method is used to insert Solves into the database in order to mark
        a challenge as solved.

        :param team: The Team object from the database
        :param chal: The Challenge object from the database
        :param request: The request the user submitted
        :return:
        """
        cls.ee.emit("challenge.onPreSolve", **locals())

        provided_key = request.form['key'].strip()
        solve = Solves(teamid=team.id, chalid=chal.id,
                       ip=utils.get_ip(req=request), flag=provided_key)

        cls.ee.emit("challenge.onPostSolve", **locals())

        db.session.add(solve)
        db.session.commit()
        db.session.close()

    @classmethod
    def fail(cls, team, chal, request):
        """
        This method is used to insert WrongKeys into the database in order to
        mark an answer incorrect.

        :param team: The Team object from the database
        :param chal: The Challenge object from the database
        :param request: The request the user submitted
        :return:
        """
        cls.ee.emit("challenge.onPreFail", **locals())

        provided_key = request.form['key'].strip()
        wrong = WrongKeys(teamid=team.id, chalid=chal.id,
                          ip=utils.get_ip(request), flag=provided_key)

        cls.ee.emit("challenge.onPostFail", **locals())

        db.session.add(wrong)
        db.session.commit()
        db.session.close()


def get_chal_class(class_id):
    """
    Utility function used to get the corresponding class from a class ID.

    :param class_id: String representing the class ID
    :return: Challenge class
    """
    cls = CHALLENGE_CLASSES.get(class_id)
    if cls is None:
        raise KeyError
    return cls


"""
Global dictionary used to hold all the Challenge Type classes used by
CTFd. Insert into this dictionary to register your Challenge Type.
"""
CHALLENGE_CLASSES = {
    "standard": CTFdStandardChallenge
}


def load(app):
    register_plugin_assets_directory(app, base_path='/plugins/challenges/assets/')
