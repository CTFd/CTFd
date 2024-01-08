import logging
import requests
import json, os
from requests.auth import HTTPBasicAuth
import functools
from CTFd.models import Configs, db
from CTFd.utils.user import get_current_team
from pprint import pprint


logging.basicConfig(level=logging.DEBUG)

class DatadogInvitationController:
    @staticmethod
    def create_user(email, name):
        # in order to invite the user to the correct org, we need to know the users' team

        team = get_current_team()
        
        if team == None: # don't try this if the user is not in a team
            return

        logging.debug("User {} belongs to team {}".format("", team))
        logging.debug("Determining the 'ctfplayer' role")

        pprint(team)

        
        creds = HTTPBasicAuth(team.fields['dd_api_key'], team.fields['dd_app_key'])
        roles_response = requests.get("https://api.datadoghq.com/api/v2/roles", auth=creds, verify=False)
        roles = roles_response.json()
        
        role_id = ""
        for role in roles['data']:
            rolename = role['attributes']['name']
            if rolename == 'ctfplayer' or rolename == 'Dash2023PartnerTechChallenge':
                role_id = role['id']



        jsondata = {}
        data = {}
        data['type'] = 'users'
        data['attributes'] = {}
        data['attributes']['name'] = email
        data['attributes']['email'] = email
        data['relationships']['roles'] = {}
        data['relationships']['roles']['data'] = []
        data['relationships']['roles']['data'][0] = {}
        data['relationships']['roles']['data'][0]['id'] = role_id
        data['relationships']['roles']['data'][0]['type'] = 'roles'
        jsondata['data'] = data

        invitation_request = requests.post("https://api.datadoghq.com/api/v2/users", json=jsondata, auth=creds, verify=False)
        logging.debug("Invitation response: {}".format(invitation_request.json))
        
        bad_request = False
        if not verify_response.ok:
            bad_request = True
            logging.debug("Got an error from the Datadog provisioning API.")

        if bad_request:
            logging.warn("Unable to contact Datadog provisioning API to invite user to their team's org. Please reach out to one of the player assistants.")
