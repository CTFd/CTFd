from flask import render_template,request,Blueprint, url_for, abort
from pathlib import Path
from CTFd.utils.plugins import override_template
from CTFd.plugins import register_plugin_asset
from CTFd.plugins.challenges import CHALLENGE_CLASSES, get_chal_class
from CTFd.utils.user import get_current_user
from CTFd.models import Challenges, Solves, Flags, db
from CTFd.utils.decorators import authed_only



def load(app):

    app.db.create_all()

    userChallenge = Blueprint('userChallenge',__name__,template_folder='templates',static_folder ='static')
    app.register_blueprint(userChallenge,url_prefix='/userChallenge')

    #register_plugin_asset(app, base_path ='plugins/UserChallengeManagement/static/js/userChallenge.js')

    registerTemplate('users/private.html','newUserPage.html')


    @app.route('/userChallenge/challenges',methods=['GET'])
    @authed_only
    def view_challenges():
        
        #TODO: add custom html extension of admin/challenges/challenges
        #      change methods to check for rights and only display challenges by user
        #      add custom html to change challenge editing to be available to users
        #
        #      add other plugin to modify challenge creation?        
            

        q = request.args.get("q")
        field = request.args.get("field")    
        
        query = UserChallenges.query.filter(UserChallenges.user == get_current_user().id).order_by(UserChallenges.id.asc())
        challenge_ids = query.all()
        
        challenges = Challenges.query.filter(Challenges.id.in_(challenge_ids)).all()
        
        total = query.count()

    #    return render_template('userChallenges.html',challenges=challenges,total=total,q=q,field=field)
        return render_template('userChallenges.html',challenges=challenges,total = total)
    
    
    @app.route('/userChallenge/challenges/new',methods=['GET'])
    @authed_only
    def view_newChallenge():
        types = CHALLENGE_CLASSES.keys()
        return render_template('createUserChallenge.html',types=types)
        
    @app.route('/userChallenge/challenges/<int:challenge_id>')
    def updateChallenge(challenge_id):
        #TODO: update logic to work with plugin   
        challenges = dict(
        Challenges.query.with_entities(Challenges.id, Challenges.name).all()
        )
        challenge = Challenges.query.filter_by(id=challenge_id).first_or_404()
        solves = (
            Solves.query.filter_by(challenge_id=challenge.id)
            .order_by(Solves.date.asc())
            .all()
        )
        flags = Flags.query.filter_by(challenge_id=challenge.id).all()

        try:
            challenge_class = get_chal_class(challenge.type)
        except KeyError:
            abort(
                500,
                f"The underlying challenge type ({challenge.type}) is not installed. This challenge can not be loaded.",
            )

        update_j2 = render_template(
            challenge_class.templates["update"].lstrip("/"), challenge=challenge
        )

        update_script = url_for(
            "views.static_html", route=challenge_class.scripts["update"].lstrip("/")
        )
        return render_template(
            "editUserChallenge",
            update_template=update_j2,
            update_script=update_script,
            challenge=challenge,
            challenges=challenges,
            solves=solves,
            flags=flags,
        )


def registerTemplate(old_path, new_path):
    dir_path = Path(__file__).parent.resolve()
    template_path = dir_path/'templates'/new_path
    override_template(old_path,open(template_path).read())

def add_User_Link(challenge_id):
    userChallenge  = UserChallenges(get_current_user().id,challenge_id)
    db.session.add(userChallenge)

class UserChallenges(db.Model):
    __tablename__ = "UserChallenges"
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.Integer,db.ForeignKey('users.id'))
    challenge = db.Column(db.Integer,db.ForeignKey('challenges.id'))


    def __init__(self,user,challenge):
        self.user = user
        self.challenge = challenge

