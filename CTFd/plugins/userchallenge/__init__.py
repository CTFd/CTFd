from CTFd.plugins.userchallenge.api_calls import challenges, comments, attempts, files, flags, hints, tags, topics
from flask import render_template,request,Blueprint, url_for, abort
from sqlalchemy.sql import and_
from CTFd.plugins.challenges import CHALLENGE_CLASSES, get_chal_class
from CTFd.models import Challenges, Solves, Flags, db, Configs,Flags
from CTFd.utils.decorators import admins_only
from CTFd.plugins.userchallenge.utils import *

userChallenge = Blueprint('userchallenge',__name__,template_folder='templates',static_folder ='staticAssets')

def load(app):

    app.db.create_all()

    app.register_blueprint(userChallenge,url_prefix='/userchallenge')

    # add config value false for allowing user challenges if not existent on startup
    if not Configs.query.filter_by(key="allowUserChallenges").first():
        conf = Configs(key="allowUserChallenges",value="false")
        db.session.add(conf)
        db.session.commit()

    registerTemplate('users/private.html','newUserPage.html')
    registerTemplate('admin/challenges/challenge.html','adminChallenge.html')
    

    @app.route('/admin/userChallenge')
    @admins_only
    def view_config():        
        key = Configs.query.filter(Configs.key == "allowUserChallenges").first().value
        db.session.commit()
        if key:
            if key == "true":
                enabled = "enabled"
            else :
                enabled = "disabled"
        else:
            enabled = "non-existant"
                
        return render_template('userConfig.html',enabled = enabled)
    
    @admins_only
    def challenges_listing():
        q = request.args.get("q")
        field = request.args.get("field")
        filters = []

        if q:
            # The field exists as an exposed column
            if Challenges.__mapper__.has_property(field):
                filters.append(getattr(Challenges, field).like("%{}%".format(q)))

        query = Challenges.query.filter(*filters).order_by(Challenges.id.asc())
        challenges_pre = query.all()
        total = query.count()

        challenges = []
        for n in challenges_pre:
            author = getUserForChallenge(n.id)
            date = getCreationDate(n.id)
            lchange = getLastChanged(n.id)
            challenges.append(UserChallenge(n.id,n.name,n.category,author,n.value,n.type,n.state,date,lchange=lchange))
            

        return render_template(
            "adminChallenges.html",
            challenges=challenges,
            total=total,
            q=q,
            field=field,)

    app.view_functions['admin.challenges_listing'] = challenges_listing

    @app.route('/userchallenge/api/config',methods=['GET','POST'])
    @admins_only
    def getConfig():
        newstate = update_allow_challenges()
        data = "disabled"
        if newstate:
            data = "enabled"
        return {"success":True,"data":data}

    @app.route('/userchallenge/challenges',methods=['GET','POST'])
    @userChallenge_allowed
    def view_challenges():
        #TODO: add custom html extension of admin/challenges/challenges
        #      change methods to check for rights and only display challenges by user
        #      add custom html to change challenge editing to be available to users
        #
        #      add other plugin to modify challenge creation?                    

        q = request.args.get("q")
        field = request.args.get("field") 
        challenges = getAllUserChallenges(q, field)
        total = len(challenges)    

        #return render_template('userChallenges.html',challenges=challenges,total=total,q=q,field=field)
        return render_template('userChallenges.html',challenges=challenges,total = total,q=q,field=field)    
     
    @app.route('/userchallenge/challenges/new',methods=['GET'])
    @userChallenge_allowed
    def view_newChallenge():
        types = CHALLENGE_CLASSES.keys()
        return render_template('createUserChallenge.html',types=types)
    
    @app.route('/userchallenge/challenges/<int:challenge_id>',methods=['GET'])
    @owned_by_user
    @userChallenge_allowed
    @owned_by_user
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
            challenge_class.templates["update"].lstrip("/admin/challenges/"), challenge=challenge
        )

        update_script = url_for(
            "views.static_html", route=challenge_class.scripts["update"].lstrip("/admin/challenges/")
        )
        return render_template(
            "editUserChallenge.html",
            update_template=update_j2,
            update_script=update_script,
            challenge=challenge,
            challenges=challenges,
            solves=solves,
            flags=flags,
        )
    
    # api rerouting
    ## challenges
    challenges.load(app)
    ## FLAGS
    flags.load(app)
    #FILES
    files.load(app)
    #TOPICS
    topics.load(app)
    # TAGS
    tags.load(app)
    # Hints
    hints.load(app)
    # Requirements
    @app.route('/userchallenge/api/challenges/<challenge_id>/requirements',methods=['GET'])
    def getReqs(challenge_id):
        challenge = Challenges.query.filter_by(id=challenge_id).first_or_404()
        return {"success": True, "data": challenge.requirements}
    # Comments
    comments.load(app)
    # attempts
    attempts.load(app)
    