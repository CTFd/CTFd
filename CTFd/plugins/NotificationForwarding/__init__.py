from flask import render_template,request,Blueprint, url_for, abort,redirect,session

from CTFd.utils.email import sendmail

from CTFd.cache import cache
from CTFd.models import db

def load(app):


    def get_newest_notification():
        # get newest notif from database
        return
    
    cache.memoize()
    def _get_all_users_checked():
        # get all users who have checked email notifications
        return

    def get_all_users_checked():
        # do like get config
        return

    def send_mail_all_users():
        # send mail through inbuilt api and put all users in reciever
        users = get_all_users_checked()
        if len(users) > 1 :
            addr = ", ".join(users)
        else:
            addr = users[0]
        
        notif = get_newest_notification()

        text = notif.content
        title = notif.title

        sendmail(addr,text,title)
        
        return