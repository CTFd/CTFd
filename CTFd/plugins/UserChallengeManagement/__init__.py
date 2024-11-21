from flask import render_template
from pathlib import Path
from CTFd.utils.plugins import override_template

def load(app):

    @app.route('/faq', methods=['GET'])
    def view_faq():
        return render_template('page.html', content="<h1>FAQ Page</h1>")

    @app.route('/user/challenges',methods=['GET'])
    
    def view_challenges():
        return render_template('admin/challenges/challenges.html')
    
    registerTemplate('users/private.html','newUserPage.html')

    #TODO: add custom html extension of admin/challenges/challenges
    #      change methods to check for rights and only display challenges by user
    #      add custom html to change challenge editing to be available to users
    #
    #      add other plugin to modify challenge creation?


def registerTemplate(old_path, new_path):
    dir_path = Path(__file__).parent.resolve()
    
    template_path = dir_path/'templates'/new_path
    override_template(old_path,open(template_path).read())