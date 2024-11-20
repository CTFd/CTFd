import datetime
import os
from flask import session
from CTFd.cache import clear_user_session
from CTFd.exceptions import UserNotFoundException, UserTokenExpiredException
from CTFd.models import UserTokens, db
from CTFd.utils.encoding import hexencode
from CTFd.utils.security.csrf import generate_nonce
from CTFd.utils.security.signing import hmac
from CTFd.utils.aws.auth_helpers import cognito_login, validate_cognito_token, uuid_to_number

from flask import redirect

def login_user_new(username, password, registration_data = None):
    #before logging, check if the user is confirmed
    authenticationResult = cognito_login(username, password)
    if(not authenticationResult['success']):
        if(authenticationResult['error'] == 'user_not_confirmed'):
            #handle user not confirmed
            return
        else:
            #handle other errors
            return
    if authenticationResult['success']:
        print(authenticationResult['data'])
        session['tokens']  = authenticationResult['data']
    return redirect(url_for("auth.login"))

def validate_user_token(token):
    # this is wrapper function for the oauth token validation
    validation = validate_cognito_token(token)
    return validation['success']

def get_user_token_data(token):
        return validate_cognito_token(token)['data']

def save_token(token):
    print("Saving token...")
    # Save the token in the database
    session['tokens']  = token
    return {'success': True, 'message': 'Token saved' }

def login_user(tokens):
    token_data = get_user_token_data(tokens['IdToken'])
    session['tomer'] = 'tomer'
    # clear_user_session(user_id=token_data['sub'])
    session['id'] = uuid_to_number(token_data['sub']) #the conversion is necessary (temporarily) because the user id is stored as a string in the token
    session['tokens']  = tokens
    session["nonce"] = generate_nonce()
    session.modified = True
    session.permanent = True
    # Clear out any currently cached user attributes


def update_user(user):
    session["id"] = user.id
    session["hash"] = hmac(user.password)
    
    session.permanent = True

    # Clear out any currently cached user attributes
    clear_user_session(user_id=user.id)


def logout_user():
    session.clear()


def generate_user_token(user, expiration=None, description=None):
    temp_token = True
    while temp_token is not None:
        value = "ctfd_" + hexencode(os.urandom(32))
        temp_token = UserTokens.query.filter_by(value=value).first()

    token = UserTokens(
        user_id=user.id, expiration=expiration, description=description, value=value
    )
    db.session.add(token)
    db.session.commit()
    return token


def lookup_user_token(token):
    token = UserTokens.query.filter_by(value=token).first()
    if token:
        if datetime.datetime.utcnow() >= token.expiration:
            raise UserTokenExpiredException
        return token.user
    else:
        raise UserNotFoundException
    return None
