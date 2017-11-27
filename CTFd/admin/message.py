from flask import render_template, Blueprint, request

from CTFd.models import Teams
from CTFd.utils import admins_only
from CTFd import utils
admin_message = Blueprint('admin_message', __name__)


@admin_message.route('/admin/message', methods=['GET', 'POST'])
@admins_only
def admin_email_message_view():
    if request.method == "POST":
        message = request.form['message']
        # Send Email to everyone
        try:
            if utils.can_send_mail() is False:
                return render_template('admin/email_message.html', status={'css': 'alert-danger',
                                                                           'message': 'Email could not be sent due to server misconfiguration'})
            else:
                if message == '':
                    return render_template('admin/email_message.html', status={'css': 'alert-danger',
                                                                               'message': 'Message is blank'})
                else:
                    teams = [team for team in Teams.query.all()]
                    for team in teams:
                        result = utils.sendmail(team.email, message)
                    return render_template('admin/email_message.html', status={ 'css': 'alert-success',
                                                                                'message': 'Message send successfully!'})
        except:
            return render_template('admin/email_message.html', status={'css': 'alert-danger',
                                                                   'message': 'Message send failed!'})
    else:
        return render_template('admin/email_message.html')
