from pathlib import Path
from sqlalchemy.exc import IntegrityError
from CTFd.utils import email
from CTFd.utils.config import is_teams_mode
from CTFd.utils.decorators.visibility import check_registration_visibility
from CTFd.utils.helpers import get_errors, get_infos, markup
from CTFd.utils.plugins import override_template
from CTFd.utils import set_config,get_config, validators
from CTFd.utils.logging import log
from CTFd.schemas.notifications import NotificationSchema
from CTFd.utils.decorators import admins_only, authed_only, ratelimit
from CTFd.utils.security.auth import login_user
from CTFd.utils.user import get_current_team, get_current_user
from flask import render_template,request,current_app,Blueprint,url_for,redirect,abort
from flask_restx import Namespace
from flask_babel import lazy_gettext as _l

from CTFd.utils.email import sendmail

from CTFd.cache import cache
from CTFd.models import Brackets, UserFieldEntries, UserFields, UserTokens, Users, db
from CTFd.plugins.LuaUtils import _LuaAsset, ConfigPanel, toggle_config
from wtforms import SelectField
from CTFd.utils.validators import ValidationError
from CTFd.utils import user as current_user

class UserNotifs(db.Model):
    __tablename__ = "UserNotifs"
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.Integer,db.ForeignKey('users.id'))
    email = db.Column(db.String(128),db.ForeignKey('users.email'),unique=True)
    data = db.Column(db.Boolean,default=False)

    def __init__(self,user,data):
        self.user = user.id
        self.email = user.email
        self.data = data

notifications_namespace = Namespace(
    "notifications", description="Endpoint to retrieve Notifications"
)

cache.memoize()
def _get_all_users_checked():
    # get all users who have checked email notifications
    users = db.session.execute(
        Users.__table__.select(Users.notifs_mail).where(Users.notifs_mail == 1)
    ).all()

    return users
    
def get_all_users_checked():
    # do like get config
    users = _get_all_users_checked()
    return users

def send_mail_all_users(notif):
    # send mail through inbuilt api and put all users in reciever
    users = get_all_users_checked()
    if len(users) > 1 :
        addr = ", ".join(users)
    elif len(users) > 0:
        addr = users[0]
    else: 
        return 

    text = notif["content"]
    title = notif["title"]

    sendmail(addr,text,title)
    
    return

def registerTemplate(old_path, new_path):
    dir_path = Path(__file__).parent.resolve()
    template_path = dir_path/'templates'/new_path
    override_template(old_path,open(template_path).read())

emailNotifs = Blueprint('emailnotifications',__name__,template_folder='templates',static_folder ='staticAssets')

def load(app):

    app.jinja_env.globals.update(EmailNotifAssets=_LuaAsset("emailnotifications"))

    # put every existing user in table
    users = db.session.query(Users).all()
    checks = []
    for u in users:
        checks.append(UserNotifs(u,False))
    for c in checks:
        try:
            db.session.add(c)
            db.session.commit()
        except IntegrityError as e:
            db.session.rollback()
            checks = []
        
    # TODO: fix error duplicate handling
    # put every new user in table
    @check_registration_visibility
    @ratelimit(method="POST", limit=10, interval=5)
    def register():
        errors = get_errors()
        if current_user.authed():
            return redirect(url_for("challenges.listing"))

        num_users_limit = int(get_config("num_users", default=0))
        num_users = Users.query.filter_by(banned=False, hidden=False).count()
        if num_users_limit and num_users >= num_users_limit:
            abort(
                403,
                description=f"Reached the maximum number of users ({num_users_limit}).",
            )

        if request.method == "POST":
            name = request.form.get("name", "").strip()
            email_address = request.form.get("email", "").strip().lower()
            password = request.form.get("password", "").strip()

            website = request.form.get("website")
            affiliation = request.form.get("affiliation")
            country = request.form.get("country")
            registration_code = str(request.form.get("registration_code", ""))
            bracket_id = request.form.get("bracket_id", None)

            name_len = len(name) == 0
            names = (
                Users.query.add_columns(Users.name, Users.id).filter_by(name=name).first()
            )
            emails = (
                Users.query.add_columns(Users.email, Users.id)
                .filter_by(email=email_address)
                .first()
            )
            pass_short = len(password) == 0
            pass_long = len(password) > 128
            valid_email = validators.validate_email(email_address)
            team_name_email_check = validators.validate_email(name)

            if get_config("registration_code"):
                if (
                    registration_code.lower()
                    != str(get_config("registration_code", default="")).lower()
                ):
                    errors.append("The registration code you entered was incorrect")

            # Process additional user fields
            fields = {}
            for field in UserFields.query.all():
                fields[field.id] = field

            entries = {}
            for field_id, field in fields.items():
                value = request.form.get(f"fields[{field_id}]", "").strip()
                if field.required is True and (value is None or value == ""):
                    errors.append("Please provide all required fields")
                    break

                if field.field_type == "boolean":
                    entries[field_id] = bool(value)
                else:
                    entries[field_id] = value

            if country:
                try:
                    validators.validate_country_code(country)
                    valid_country = True
                except ValidationError:
                    valid_country = False
            else:
                valid_country = True

            if website:
                valid_website = validators.validate_url(website)
            else:
                valid_website = True

            if affiliation:
                valid_affiliation = len(affiliation) < 128
            else:
                valid_affiliation = True

            if bracket_id:
                valid_bracket = bool(
                    Brackets.query.filter_by(id=bracket_id, type="users").first()
                )
            else:
                if Brackets.query.filter_by(type="users").count():
                    valid_bracket = False
                else:
                    valid_bracket = True

            if not valid_email:
                errors.append("Please enter a valid email address")
            if email.check_email_is_whitelisted(email_address) is False:
                errors.append("Your email address is not from an allowed domain")
            if names:
                errors.append("That user name is already taken")
            if team_name_email_check is True:
                errors.append("Your user name cannot be an email address")
            if emails:
                errors.append("That email has already been used")
            if pass_short:
                errors.append("Pick a longer password")
            if pass_long:
                errors.append("Pick a shorter password")
            if name_len:
                errors.append("Pick a longer user name")
            if valid_website is False:
                errors.append("Websites must be a proper URL starting with http or https")
            if valid_country is False:
                errors.append("Invalid country")
            if valid_affiliation is False:
                errors.append("Please provide a shorter affiliation")
            if valid_bracket is False:
                errors.append("Please provide a valid bracket")

            if len(errors) > 0:
                return render_template(
                    "register.html",
                    errors=errors,
                    name=request.form["name"],
                    email=request.form["email"],
                    password=request.form["password"],
                )
            else:
                with app.app_context():
                    user = Users(
                        name=name,
                        email=email_address,
                        password=password,
                        bracket_id=bracket_id,
                    )

                    if website:
                        user.website = website
                    if affiliation:
                        user.affiliation = affiliation
                    if country:
                        user.country = country

                    db.session.add(user)

                    # add user check
                    check = UserNotifs(user,False)
                    db.session.add(check)
                    db.session.commit()
                    db.session.flush()

                    for field_id, value in entries.items():
                        entry = UserFieldEntries(
                            field_id=field_id, value=value, user_id=user.id
                        )
                        db.session.add(entry)
                    db.session.commit()

                    login_user(user)

                    if request.args.get("next") and validators.is_safe_url(
                        request.args.get("next")
                    ):
                        return redirect(request.args.get("next"))

                    if config.can_send_mail() and get_config(
                        "verify_emails"
                    ):  # Confirming users is enabled and we can send email.
                        log(
                            "registrations",
                            format="[{date}] {ip} - {name} registered (UNCONFIRMED) with {email}",
                            name=user.name,
                            email=user.email,
                        )
                        email.verify_email_address(user.email)
                        db.session.close()
                        return redirect(url_for("auth.confirm"))
                    else:  # Don't care about confirming users
                        if (
                            config.can_send_mail()
                        ):  # We want to notify the user that they have registered.
                            email.successful_registration_notification(user.email)

            log(
                "registrations",
                format="[{date}] {ip} - {name} registered with {email}",
                name=user.name,
                email=user.email,
            )
            db.session.close()

            if is_teams_mode():
                return redirect(url_for("teams.private"))

            return redirect(url_for("challenges.listing"))
        else:
            return render_template("register.html", errors=errors)

    app.view_functions['auth.register'] = register

    app.register_blueprint(emailNotifs,url_prefix='/emailnotifications')
    
    @app.route("/admin/emailNotifs/config/<configType>",methods=['GET','POST'])
    @admins_only
    def toggle_notifs(configType):
        key = configType
    
        newstate = toggle_config(key)
        log(
            "registrations",
            format="####################### {name}",
            name=newstate,
        )
        data = "disabled"
        if newstate:
            data = "enabled"
        
        return {"success":True,"data":data,"id":key}
    
    @app.route("/admin/NotificationForwarding")
    @admins_only
    def config():
        notif = get_config('sendEmailNotif')
        check = get_config('allowUserCheckmarkNotif')
        if notif:
            if notif == "true":
                notif = "enabled"
            else :
                notif = "disabled"
        else:
            notif = "disabled"
        if check:
            if check == "true":
                check = "enabled"
            else :
                check = "disabled"
        else:
            check = "disabled"

        
        configs = []
        configs.append(ConfigPanel("Email Notifications",
                                   "Enabeling Email-Notifications sends all Notifications to all users per email. Disableling also removes the checkmark option from User profiles.",
                                   notif,'sendEmailNotif'))
        configs.append(ConfigPanel("Opt out",
                                   "Toggles wether Users can opt out of email Notifications or not.",
                                   check,'allowUserCheckmarkNotif'))
        
        return render_template('notificationConfig.html',configs = configs)

    @admins_only
    def notification_post():
        req = request.get_json()

        schema = NotificationSchema()
        result = schema.load(req)

        if result.errors:
            return {"success": False, "errors": result.errors}, 400

        db.session.add(result.data)
        db.session.commit()

        response = schema.dump(result.data)

        # Grab additional settings
        notif_type = req.get("type", "alert")
        notif_sound = req.get("sound", True)
        response.data["type"] = notif_type
        response.data["sound"] = notif_sound

        current_app.events_manager.publish(data=response.data, type="notification")

        email = get_config("sendEmailNotif")
        if email:
            send_mail_all_users(response.data)
        elif email == None:
            set_config("sendEmailNotif",'false')
        

        return {"success": True, "data": response.data}
    
    app.view_functions['api.notifications_notificantion_list'] = notification_post

    @authed_only
    def settings():
        infos = get_infos()
        errors = get_errors()

        user = get_current_user()

        if is_teams_mode() and get_current_team() is None:
            team_url = url_for("teams.private")
            infos.append(
                markup(
                    f'In order to participate you must either <a href="{team_url}">join or create a team</a>.'
                )
            )

        tokens = UserTokens.query.filter_by(user_id=user.id).all()

        prevent_name_change = get_config("prevent_name_change")

        if get_config("verify_emails") and not user.verified:
            confirm_url = markup(url_for("auth.confirm"))
            infos.append(
                markup(
                    "Your email address isn't confirmed!<br>"
                    "Please check your email to confirm your email address.<br><br>"
                    f'To have the confirmation email resent please <a href="{confirm_url}">click here</a>.'
                )
            )

        notif = SelectField(_l("Email Notifications"),choices=["false","true"])
        notifs_mail = db.session.execute(Users.__table__.select(Users.notifs_mail).where(Users.id == user.id))

        return render_template(
            "settings.html",
            name=user.name,
            email=user.email,
            language=user.language,
            website=user.website,
            affiliation=user.affiliation,
            country=user.country,
            tokens=tokens,
            prevent_name_change=prevent_name_change,
            infos=infos,
            errors=errors,
            checked=notifs_mail,
            notif = notif
        )
    
    app.view_functions['views.settings'] = settings