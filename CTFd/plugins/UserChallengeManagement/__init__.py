from flask import render_template,request,Blueprint
from pathlib import Path
from CTFd.utils.plugins import override_template
from CTFd.plugins import register_plugin_assets_directory
from CTFd.plugins.challenges import CHALLENGE_CLASSES, get_chal_class
from CTFd.utils.user import get_current_user
from CTFd.models import db


def load(app):

    app.db.create_all()


    userChallenge = Blueprint('userChallenge',__name__,template_folder='templates')
    app.register_blueprint(userChallenge,url_prefix='/userChallenge')


    @app.route('/userChallenge/challenges',methods=['GET'])
    def view_challenges():
        
        #TODO: add custom html extension of admin/challenges/challenges
        #      change methods to check for rights and only display challenges by user
        #      add custom html to change challenge editing to be available to users
        #
        #      add other plugin to modify challenge creation?
        
        q = request.args.get("q")
        field = request.args.get("field")    
        filters = [get_current_user().id]
        
        query = UserChallenges.query.order_by(UserChallenges.id.asc())
        challenges = query.all()
        total = query.count()

    #    return render_template('userChallenges.html',challenges=challenges,total=total,q=q,field=field)
        return render_template('userChallenges.html',challenges=challenges,total = total)
    
    @app.route('/userChallenge/challenges/new',methods=['GET'])
    def view_newChallenge():
        types = CHALLENGE_CLASSES.keys()
        return render_template('userChallenge/createUserChallenge.html',types=types)

    
    registerTemplate('users/private.html','newUserPage.html')

    register_plugin_assets_directory(app, base_path ='plugins/UserChallengeManagement/assets/')
    


def registerTemplate(old_path, new_path):
    dir_path = Path(__file__).parent.resolve()
    
    template_path = dir_path/'templates'/new_path
    override_template(old_path,open(template_path).read())



class UserChallenges(db.Model):
    __tablename__ = "UserChallenges"
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.Integer,db.ForeignKey('users.id'))
    challenge = db.Column(db.Integer,db.ForeignKey('challenges.id'))


    def __init__(self,user,challenge):
        self.user = user
        self.challenge = challenge
