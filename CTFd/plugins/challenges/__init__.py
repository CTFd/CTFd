from CTFd.plugins import register_plugin_assets_directory
from CTFd.plugins.keys import get_key_class
from CTFd.models import db, Solves, WrongKeys, Keys, Challenges, Files, Tags
from CTFd import utils

from pymitter import EventEmitter
class NameSpace(object):
    """
    A way to create references to local variables, such that they may be modified
    in event functions.
    """
    def __init__(self, **kwargs):
        for k,v in kwargs.iteritems():
            self.__setattr__(k, v)

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
        ns = NameSpace(**locals())
        cls.ee.emit("challenge.onPreCreate", ns)

        ns.files = ns.request.files.getlist('files[]')

        # Create challenge
        _, chal_db_cls = CHALLENGE_CLASSES.get(cls.id, (None, None))
        # Dynamically get the form elements, and convert them to the correct
        # type, before passing it to the given challenge database object
        # initialisation.
        data = {}
        for col in chal_db_cls.__mapper__.columns:
            if col.name in ns.request.form:
                data[col.name] = ns.request.form.get(
                        col.name, default=col.default.arg if col.default else None,
                        type=col.type.python_type # if col.type.python_type in
                )
            # Checkboxes will not be included in `request.form` (as per the W3C
            # HTML4 recommendation).  A trick to get them to be part of the
            # `request.form` is to add a hidden input box below, with the value
            # that gets interpreted as false (see
            # https://stackoverflow.com/a/11424091).
            elif col.name in ['hidden']:
                data[col.name] = False

        ns.chal = chal_db_cls(**data)
        cls.ee.emit("challenge.onCreate", ns)

        db.session.add(ns.chal)
        db.session.commit()

        ns.flag = Keys(ns.chal.id, ns.request.form['key'], ns.request.form['key_type[0]'])
        if ns.request.form.get('keydata'):
            ns.flag.data = ns.request.form.get('keydata')

        cls.ee.emit("challenge.onPostCreate", ns)

        db.session.add(ns.flag)
        db.session.commit()

        for f in ns.files:
            utils.upload_file(file=f, chalid=ns.chal.id)

        db.session.commit()

    @classmethod
    def read(cls, challenge):
        """
        This method is in used to access the data of a challenge in a format
        processable by the front end.

        :param challenge: The Challenge object from the database
        :return: Challenge object, data dictionary to be returned to the user
        """
        ns = NameSpace(**locals())
        cls.ee.emit("challenge.onPreRead", ns)

        ns.data = {
            'type_data': {
                'id': cls.id,
                'name': cls.name,
                'templates': cls.templates,
                'scripts': cls.scripts,
            }
        }
        for col in ns.challenge.__mapper__.columns:
            ns.data[col.name] = ns.challenge.__getattribute__(col.name)

        cls.ee.emit("challenge.onPostRead", ns)

        return ns.challenge, ns.data

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
        ns = NameSpace(**locals())
        cls.ee.emit("challenge.onPreUpdate", ns)

        for col in ns.challenge.__mapper__.columns:
            if col.name in ns.request.form:
                ns.challenge.__setattr__(
                    col.name, ns.request.form.get(
                        col.name, default=col.default.arg if col.default else None,
                        type=col.type.python_type
                    )
                )
            # Specially handle checkboxes, as they won't be part of the
            # `request.form` if they are unchecked.  Thus explicitly set them to
            # False.  See `create()` above for the same challenges.
            elif col.name in ['hidden']:
                ns.challenge.__setattr__(col.name, False)

        cls.ee.emit("challenge.onPostUpdate", ns)

        db.session.commit()
        db.session.close()

    @classmethod
    def delete(cls, challenge):
        """
        This method is used to delete the resources used by a challenge.

        :param challenge: The Challenge object from the database
        :return:
        """
        ns = NameSpace(**locals())
        cls.ee.emit("challenge.onPreDelete", ns)

        WrongKeys.query.filter_by(chalid=ns.challenge.id).delete()
        Solves.query.filter_by(chalid=ns.challenge.id).delete()
        Keys.query.filter_by(chal=ns.challenge.id).delete()
        ns.files = Files.query.filter_by(chal=ns.challenge.id).all()
        for f in ns.files:
            utils.delete_file(f.id)
        Files.query.filter_by(chal=ns.challenge.id).delete()
        Tags.query.filter_by(chal=ns.challenge.id).delete()
        # Having subclasses define `ondelete="CASCADE"` will make sure their
        # referencing rows are also deleted, when this one is.
        Challenges.query.filter_by(id=ns.challenge.id).delete()

        cls.ee.emit("challenge.onPostDelete", ns)

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
        ns = NameSpace(**locals())
        cls.ee.emit("challenge.onPreAttempt", ns)

        ns.provided_key = ns.request.form['key'].strip()
        ns.chal_keys = Keys.query.filter_by(chal=ns.chal.id).all()
        for ns.chal_key in ns.chal_keys:
            if get_key_class(ns.chal_key.key_type).compare(ns.chal_key.flag, ns.provided_key):

                cls.ee.emit("challenge.onPostAttempt", ns, status=True)

                return True, 'Correct'

        cls.ee.emit("challenge.onPostAttempt", ns, status=False)

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
        ns = NameSpace(**locals())
        cls.ee.emit("challenge.onPreSolve", ns)

        ns.provided_key = ns.request.form['key'].strip()
        ns.solve = Solves(teamid=ns.team.id, chalid=ns.chal.id,
                       ip=utils.get_ip(req=ns.request), flag=ns.provided_key)

        cls.ee.emit("challenge.onPostSolve", ns)

        db.session.add(ns.solve)
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
        ns = NameSpace(**locals())
        cls.ee.emit("challenge.onPreFail", ns)

        ns.provided_key = ns.request.form['key'].strip()
        ns.wrong = WrongKeys(teamid=ns.team.id, chalid=ns.chal.id,
                          ip=utils.get_ip(req=ns.request), flag=ns.provided_key)

        cls.ee.emit("challenge.onPostFail", ns)

        db.session.add(ns.wrong)
        db.session.commit()
        db.session.close()


def get_chal_class(class_id):
    """
    Utility function used to get the corresponding class from a class ID.

    :param class_id: String representing the class ID
    :return: Challenge class
    """
    chal_cls, chal_db_cls = CHALLENGE_CLASSES[class_id]
    return chal_cls, chal_db_cls


"""
Global dictionary used to hold all the Challenge Type classes used by
CTFd. Insert into this dictionary to register your Challenge Type.
"""
CHALLENGE_CLASSES = {
    "standard": (CTFdStandardChallenge, Challenges)
}


def load(app):
    register_plugin_assets_directory(app, base_path='/plugins/challenges/assets/')
