import logging
import requests
import json, os
from requests.auth import HTTPBasicAuth
import functools
from CTFd.models import Configs, db
from CTFd.utils.user import get_current_team


logging.basicConfig(level=logging.DEBUG)

class DatadogInvitationController:
    @staticmethod
    def create_user(email, name):
        # in order to invite the user to the correct org, we need to know the users' team

        team = get_current_team()
        
        if team == None: # don't try this if the user is not in a team
            return

        logging.debug("User {} belongs to team {}".format("", team))
        data = {}
        data['account_id'] = team.name # the name of the team
        data['account_name'] = team.name # same, name of the team
        data['user_email'] = email # is this the email address field?
        data['user_id'] = email
        data['partner_program'] = "Sales and Services Partners"
        data['partner_type'] = "Managed Services Partners"
        data['partner_tier'] = "Basic"
        
        # we get our credentials and the url from the env variables
        creds = HTTPBasicAuth(os.getenv('DATADOG_API_USERNAME'), os.getenv('DATADOG_API_PASSWORD'))
        request_url = os.getenv('DATADOG_API_URL')
        
        verify_response = requests.post(request_url, json=data, auth=creds, verify=False)
        logging.debug("Inviting user to org through Datadog API at: {}".format(request_url))
        
        bad_request = False
        if not verify_response.ok:
            bad_request = True
            logging.debug("Got an error from the Datadog provisioning API.")

        if bad_request:
            logging.warn("Unable to contact Datadog provisioning API to invite user to their team's org. Please reach out to one of the player assistants.")
