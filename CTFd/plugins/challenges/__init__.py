from CTFd.plugins import register_plugin_assets_directory
from CTFd.plugins.keys import get_key_class
from CTFd.models import db, Solves, WrongKeys, Keys
from CTFd import utils


class BaseChallenge(object):
    id = None
    name = None
    templates = {}
    scripts = {}


class CTFdStandardChallenge(BaseChallenge):
    id = 0
    name = "standard"
    templates = {
        'create': '/plugins/challenges/assets/standard-challenge-create.hbs',
        'update': '/plugins/challenges/assets/standard-challenge-update.hbs',
        'modal': '/plugins/challenges/assets/standard-challenge-modal.hbs',
    }
    scripts = {
        'create': '/plugins/challenges/assets/standard-challenge-create.js',
        'update': '/plugins/challenges/assets/standard-challenge-update.js',
        'modal': '/plugins/challenges/assets/standard-challenge-modal.js',
    }

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
            if get_key_class(chal_key.key_type).compare(chal_key.flag, provided_key):
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


def get_chal_class(class_id):
    cls = CHALLENGE_CLASSES.get(class_id)
    if cls is None:
        raise KeyError
    return cls


CHALLENGE_CLASSES = {
    0: CTFdStandardChallenge
}


def load(app):
    register_plugin_assets_directory(app, base_path='/plugins/challenges/assets/')