import os
import time

import requests

SLEEP_INTERVAL = 60  # how long does our script sleep in between iterations. For production use, it should be like 60 seconds or so
INVITATION_TIME_MINUTES = 5  # how many minutes (!) before the event starts should we start inviting the users?
INVITATION_CUTOFF_MINUTES = (
    15  # how many minutes after we started the event should we stop inviting new users?
)
CTFD_HOST = (
    "http://ctfd"  # we default to the container name for our standard deployment
)

if os.getenv("CTFD_HOST") is not None:
    CTFD_HOST = os.getenv("CTFD_HOST")  # but we accept it to be overridden

if os.getenv("CTFD_TOKEN") is None:
    print("FATAL: There is no CTFD Token defined. Giving up!")
    exit(256)
CTFD_TOKEN = os.getenv("CTFD_TOKEN")

print(
    "DatadogInviter is starting up. CTFD Token: "
    + CTFD_TOKEN
    + " at host: "
    + CTFD_HOST
)
print("Will sleep now for 120s to give CTFd the time to start up")
time.sleep(20)

ROLE_NAME = "CustomRoleForMyColleagues"
if os.getenv("DD_ROLE") is not None:
    ROLE_NAME = os.getenv("DD_ROLE")

do_invite = False
sent_invitations = []


# this method checks if the CTF is starting
def check_start_time():
    global do_invite

    print("Checking start time")
    url = CTFD_HOST + "/api/v1/configs/start"
    headers = {
        "content-type": "application/json",
        "Authorization": "Token " + CTFD_TOKEN,
    }

    r = requests.get(url, headers=headers)
    response = r.json()
    if response is None or response["data"] is None:
        print("Unexpected response: " + response)
    if response["data"]["value"] == "":
        # there is no start time configured. We do not handle invitations in this case.
        print(
            "The CTF has no start time configured. We are not going to manage invitations then."
        )
        do_invite = False
        return do_invite

    start_time = int(response["data"]["value"])
    current_time = time.time()
    delta = start_time - current_time
    if delta > INVITATION_TIME_MINUTES * 60:
        print(
            "CTF starts in more than "
            + str(INVITATION_TIME_MINUTES)
            + " minutes not inviting yet."
        )
    else:
        if delta < INVITATION_CUTOFF_MINUTES * -60:
            print(
                "CTF started more than "
                + str(INVITATION_CUTOFF_MINUTES)
                + " minutes ago. Stopping invitations."
            )
            do_invite = False
        else:
            print(
                "CTF starts in less than "
                + str(INVITATION_TIME_MINUTES)
                + " minutes. Ready to invite."
            )
            do_invite = True

    return do_invite


def get_teams():
    print("Fetching list of teams")
    url = CTFD_HOST + "/api/v1/teams"
    headers = {
        "content-type": "application/json",
        "Authorization": "Token " + CTFD_TOKEN,
    }

    r = requests.get(url, headers=headers)
    response = r.json()

    return response["data"]


def get_team_details(team_id):
    url = CTFD_HOST + "/api/v1/teams/" + str(team_id)
    headers = {
        "content-type": "application/json",
        "Authorization": "Token " + CTFD_TOKEN,
    }

    r = requests.get(url, headers=headers)
    response = r.json()

    ret = {}
    ret["name"] = response["data"]["name"]
    for field in response["data"]["fields"]:
        ret[field["name"]] = field["value"]

    return ret


def get_team_members(team_id):
    url = CTFD_HOST + "/api/v1/teams/" + str(team_id) + "/members"
    headers = {
        "content-type": "application/json",
        "Authorization": "Token " + CTFD_TOKEN,
    }

    r = requests.get(url, headers=headers)
    response = r.json()

    return response["data"]


def get_user_details(user_id):
    url = CTFD_HOST + "/api/v1/users/" + str(user_id)
    headers = {
        "content-type": "application/json",
        "Authorization": "Token " + CTFD_TOKEN,
    }

    r = requests.get(url, headers=headers)
    response = r.json()

    return response["data"]


def get_role_id(dd_api_key, dd_app_key, role_name):
    url = "https://api.datadoghq.com/api/v2/roles"
    headers = {
        "content-type": "application/json",
        "DD-API-KEY": dd_api_key,
        "DD-APPLICATION-KEY": dd_app_key,
    }

    r = requests.get(url, headers=headers)

    response = r.json()
    for role in response["data"]:
        if role["attributes"]["name"] == role_name:
            return role["id"]

    return None


def invite_user(dd_api_key, dd_app_key, email, role_id):
    print("inviting user: " + email)

    url = "https://api.datadoghq.com/api/v2/users"
    headers = {
        "content-type": "application/json",
        "DD-API-KEY": dd_api_key,
        "DD-APPLICATION-KEY": dd_app_key,
    }

    r = requests.post(
        url,
        headers=headers,
        json={
            "data": {
                "type": "users",
                "attributes": {
                    "email": email,
                    "name": email,
                    "access_role": "CustomRoleForMyColleagues",
                },
                "relationships": {
                    "roles": {"data": [{"id": role_id, "type": "roles"}]}
                },
            }
        },
    )

    response = r.json()
    print("user " + email + " created with code: " + str(r.status_code))
    if r.status_code == 200 or r.status_code == 201:
        invitation_request = requests.post(
            "https://api.datadoghq.com/api/v2/user_invitations",
            headers=headers,
            json={
                "data": [
                    {
                        "type": "user_invitations",
                        "relationships": {
                            "user": {
                                "data": {"type": "users", "id": response["data"]["id"]}
                            }
                        },
                    }
                ]
            },
        )
        print(invitation_request.json())

    return r.status_code == 200 or r.status_code == 409


def invite_users():
    global sent_invitations
    # get the list of teams
    teams = get_teams()

    # now, for every team
    for team in teams:
        print(
            "Checking members for team: " + team["name"] + "(" + str(team["id"]) + ")"
        )
        details = get_team_details(team["id"])
        members = get_team_members(team["id"])
        print(details)
        role_id = get_role_id(details["apikey"], details["appkey"], ROLE_NAME)

        if role_id is None:
            print("ERROR: Could not identify role id for team " + details["name"])
        else:
            print("Role for team " + details["name"] + " is " + role_id)
        for user_id in members:
            user = get_user_details(user_id)
            # ok, we have everything we need, invite the user
            if not user["email"] in sent_invitations:
                if invite_user(
                    details["apikey"], details["appkey"], user["email"], role_id
                ):
                    sent_invitations.append(user["email"])
            else:
                print("User " + user["email"] + " has already been invited")


## main loop

print("Datadog inviter is starting")

while True:  # we run until we're killed
    if check_start_time():
        # now we send invitations
        print("Checking for any users that need to get invited")
        invite_users()
    else:
        print(
            "We are not yet at the CTF Start time minus 5 minutes. Not sending invitations yet"
        )
    time.sleep(SLEEP_INTERVAL)
