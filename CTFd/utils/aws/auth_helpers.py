import hmac
import hashlib
import base64
import boto3
import requests
import time
from jose import jwt
from jose.exceptions import JWTError
from CTFd.utils import get_app_config

cognito = boto3.client('cognito-idp', region_name='il-central-1')

def get_client_vars():
    return get_app_config("OAUTH_CLIENT_ID"), get_app_config("OAUTH_CLIENT_SECRET")

def calculate_secret_hash(client_id, client_secret, username):
    message = username + client_id
    dig = hmac.new(
        client_secret.encode('utf-8'),
        message.encode('utf-8'),
        hashlib.sha256
    ).digest()
    return base64.b64encode(dig).decode()

def cognito_registration(user):
    client_id, client_secret = get_client_vars()
    SecretHash = calculate_secret_hash(client_id, client_secret, user['username'])
    payload = {
        "ClientId": client_id,
        "SecretHash": SecretHash,
        "Username": user['username'],
        "Password": user['password'],
        "UserAttributes": [
            {"Name": "email", "Value": user['email']},
            { "Name": "name", "Value": "Sefi Ovadia" }

        ],
    }
    url = 'https://ctf.auth.il-central-1.amazoncognito.com'
    
    # Make the POST request
    #response = requests.post(url, headers=headers, data=json.dumps(payload))
    try:
        response = cognito.sign_up(**payload)
        print("User registered successfully!")
        print(response)
        return {'success': True, 'message': 'User registered successfully!', 'data': response}
    except cognito.exceptions.ClientError as e:
        print(f"Error during user registration: {e.response['Error']['Message']}")
        return {'success': False, 'message': e.response['Error']['Message']}

def cognito_login(username, password):
    client_id, client_secret = get_client_vars()
    SecretHash = calculate_secret_hash(client_id, client_secret, username)
    payload = {
        "ClientId": client_id,
        "AuthFlow": "USER_PASSWORD_AUTH",
        "AuthParameters": {
            "USERNAME": username,
            "PASSWORD": password,
            "SECRET_HASH": SecretHash
        }
    }
    try:
        response = cognito.initiate_auth(**payload)
        print("User logged in successfully!")
        return {'success': True, 'message': 'User logged in successfully!', 'data': response}
    except cognito.exceptions.UserNotConfirmedException:
        return {'success': False, 'error': 'user_not_confirmed'}
    except cognito.exceptions.ClientError as e:
        print(f"Error during user login: {e.response['Error']['Message']}")
        return {'success': False, 'error': e.response['Error']['Message']}

def cognito_confirm_registration(username, confirmation_code):
    client_id, client_secret = get_client_vars()
    SecretHash = calculate_secret_hash(client_id, client_secret, username)
    payload = {
        "ClientId": client_id,
        "ConfirmationCode": confirmation_code,
        "Username": username,
        "SecretHash": SecretHash
    }
    try:
        response = cognito.confirm_sign_up(**payload)
        print("User confirmed successfully!")
        print(response)
        return {'success': True, 'message': 'User confirmed successfully!', 'data': response}
    except cognito.exceptions.ClientError as e:
        print(f"Error during user confirmation: {e.response['Error']['Message']}")
        return {'success': False, 'message': e.response['Error']['Message']}

def get_cognito_public_keys(cognito_region, user_pool_id):
    COGNITO_KEYS_URL = f"https://cognito-idp.{cognito_region}.amazonaws.com/{user_pool_id}/.well-known/jwks.json"
    response = requests.get(COGNITO_KEYS_URL)
    response.raise_for_status()
    return response.json()

def validate_cognito_token(token):
    client_id = get_app_config("OAUTH_CLIENT_ID")
    cognito_region = get_app_config("COGNITO_REGION")
    user_pool_id = get_app_config("COGNITO_USER_POOL_ID")
    try:
        # Fetch Cognito public keys
        keys = get_cognito_public_keys(cognito_region, user_pool_id)

        # Decode the token header to get the kid
        headers = jwt.get_unverified_header(token)
        kid = headers['kid']

        # Match the kid with the corresponding key in JWKS
        key = next((key for key in keys['keys'] if key['kid'] == kid), None)
        if not key:
            raise ValueError("Public key not found for given kid")

        # Verify and decode the token
        decoded_token = jwt.decode(
            token,
            key,
            algorithms=["RS256"],
            audience=client_id,  # Optional: validate audience if using
            issuer=f"https://cognito-idp.{cognito_region}.amazonaws.com/{user_pool_id}"
        )
        current_time = int(time.time())
        if decoded_token["exp"] < current_time:
            raise ValueError("Token has expired")
        return {'success': True, 'message':'Token validation succeeded', 'data': decoded_token}
    except (JWTError, ValueError) as e:
        print(f"Token validation failed: {e}")
        return {'success': False, 'message': f"Token validation failed: {e}"}


def uuid_to_number(uuid_str):
    hash_object = hashlib.sha256(uuid_str.encode())
    large_int = int(hash_object.hexdigest(), 16)
    # Truncate to fit within SQLite INTEGER range (signed 64-bit integer)
    return large_int % (2**63)

#exmaple seccusfull registration
# {
#     "CodeDeliveryDetails": {
#         "AttributeName": "email",
#         "DeliveryMedium": "EMAIL",
#         "Destination": "s***@e***"
#     },
#     "UserConfirmed": false,
#     "UserSub": "6a3372ec-0041-70cd-82e3-40f0b075af87"
# }
