from pathlib import Path
from CTFd.utils.plugins import override_template
from flask import render_template,request,Blueprint, url_for, abort,redirect,session



def registerTemplate(old_path, new_path):
    dir_path = Path(__file__).parent.resolve()
    template_path = dir_path/'templates'/new_path
    override_template(old_path,open(template_path).read())
    
def load(app):
    #registerTemplate('base.html','MathBase.html')
    #registerTemplate('challenge.html','MathChallenge.html')
    return