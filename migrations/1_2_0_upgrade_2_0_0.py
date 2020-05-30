from __future__ import print_function

import os
import sys

import dataset
from sqlalchemy_utils import drop_database

from CTFd import config, create_app
from CTFd.utils import string_types

# This is important to allow access to the CTFd application factory
sys.path.append(os.getcwd())


def cast_bool(value):
    if value and value.isdigit():
        return int(value)
    elif value and isinstance(value, string_types):
        if value.lower() == "true":
            return True
        elif value.lower() == "false":
            return False
        else:
            return value


if __name__ == "__main__":
    print("/*\\ Migrating your database to 2.0.0 can potentially lose data./*\\")
    print(
        """/*\\ Please be sure to back up all data by:
        * creating a CTFd export
        * creating a dump of your actual database
        * and backing up the CTFd source code directory"""
    )
    print("/*\\ CTFd maintainers are not responsible for any data loss! /*\\")
    if input("Run database migrations (Y/N)").lower().strip() == "y":
        pass
    else:
        print("/*\\ Aborting database migrations... /*\\")
        print("/*\\ Exiting... /*\\")
        exit(1)

    db_url = config.Config.SQLALCHEMY_DATABASE_URI
    old_data = {}

    old_conn = dataset.connect(config.Config.SQLALCHEMY_DATABASE_URI)
    tables = old_conn.tables
    for table in tables:
        old_data[table] = old_conn[table].all()

    if "alembic_version" in old_data:
        old_data.pop("alembic_version")

    print("Current Tables:")
    for table in old_data.keys():
        print("\t", table)

    old_conn.executable.close()

    print("DROPPING DATABASE")
    drop_database(db_url)

    app = create_app()

    new_conn = dataset.connect(config.Config.SQLALCHEMY_DATABASE_URI)

    print("MIGRATING Challenges")
    for challenge in old_data["challenges"]:
        hidden = challenge.pop("hidden")
        challenge["state"] = "hidden" if hidden else "visible"
        new_conn["challenges"].insert(dict(challenge))
    del old_data["challenges"]

    print("MIGRATING Teams")
    for team in old_data["teams"]:
        admin = team.pop("admin")
        team["type"] = "admin" if admin else "user"
        team["hidden"] = bool(team.pop("banned"))
        team["banned"] = False
        team["verified"] = bool(team.pop("verified"))
        new_conn["users"].insert(dict(team))
    del old_data["teams"]

    print("MIGRATING Pages")
    for page in old_data["pages"]:
        page["content"] = page.pop("html")
        new_conn["pages"].insert(dict(page))
    del old_data["pages"]

    print("MIGRATING Keys")
    for key in old_data["keys"]:
        key["challenge_id"] = key.pop("chal")
        key["content"] = key.pop("flag")
        new_conn["flags"].insert(dict(key))
    del old_data["keys"]

    print("MIGRATING Tags")
    for tag in old_data["tags"]:
        tag["challenge_id"] = tag.pop("chal")
        tag["value"] = tag.pop("tag")
        new_conn["tags"].insert(dict(tag))
    del old_data["tags"]

    print("MIGRATING Files")
    for f in old_data["files"]:
        challenge_id = f.pop("chal")
        if challenge_id:
            f["challenge_id"] = challenge_id
            f["type"] = "challenge"
        else:
            f["page_id"] = None
            f["type"] = "page"
        new_conn["files"].insert(dict(f))
    del old_data["files"]

    print("MIGRATING Hints")
    for hint in old_data["hints"]:
        hint["type"] = "standard"
        hint["challenge_id"] = hint.pop("chal")
        hint["content"] = hint.pop("hint")
        new_conn["hints"].insert(dict(hint))
    del old_data["hints"]

    print("MIGRATING Unlocks")
    for unlock in old_data["unlocks"]:
        unlock["user_id"] = unlock.pop(
            "teamid"
        )  # This is intentional as previous CTFds are effectively in user mode
        unlock["target"] = unlock.pop("itemid")
        unlock["type"] = unlock.pop("model")
        new_conn["unlocks"].insert(dict(unlock))
    del old_data["unlocks"]

    print("MIGRATING Awards")
    for award in old_data["awards"]:
        award["user_id"] = award.pop(
            "teamid"
        )  # This is intentional as previous CTFds are effectively in user mode
        new_conn["awards"].insert(dict(award))
    del old_data["awards"]

    submissions = []
    for solve in old_data["solves"]:
        solve.pop("id")  # ID of a solve doesn't really matter
        solve["challenge_id"] = solve.pop("chalid")
        solve["user_id"] = solve.pop("teamid")
        solve["provided"] = solve.pop("flag")
        solve["type"] = "correct"
        solve["model"] = "solve"
        submissions.append(solve)

    for wrong_key in old_data["wrong_keys"]:
        wrong_key.pop("id")  # ID of a fail doesn't really matter.
        wrong_key["challenge_id"] = wrong_key.pop("chalid")
        wrong_key["user_id"] = wrong_key.pop("teamid")
        wrong_key["provided"] = wrong_key.pop("flag")
        wrong_key["type"] = "incorrect"
        wrong_key["model"] = "wrong_key"
        submissions.append(wrong_key)

    submissions = sorted(submissions, key=lambda k: k["date"])
    print("MIGRATING Solves & WrongKeys")
    for submission in submissions:
        model = submission.pop("model")
        if model == "solve":
            new_id = new_conn["submissions"].insert(dict(submission))
            submission["id"] = new_id
            new_conn["solves"].insert(dict(submission))
        elif model == "wrong_key":
            new_conn["submissions"].insert(dict(submission))
    del old_data["solves"]
    del old_data["wrong_keys"]

    print("MIGRATING Tracking")
    for tracking in old_data["tracking"]:
        tracking["user_id"] = tracking.pop("team")
        new_conn["tracking"].insert(dict(tracking))
    del old_data["tracking"]

    print("MIGRATING Config")
    banned = ["ctf_version"]
    workshop_mode = None
    hide_scores = None
    prevent_registration = None
    view_challenges_unregistered = None
    view_scoreboard_if_authed = None

    challenge_visibility = "private"
    registration_visibility = "public"
    score_visibility = "public"
    account_visibility = "public"
    for c in old_data["config"]:
        c.pop("id")

        if c["key"] == "workshop_mode":
            workshop_mode = cast_bool(c["value"])
        elif c["key"] == "hide_scores":
            hide_scores = cast_bool(c["value"])
        elif c["key"] == "prevent_registration":
            prevent_registration = cast_bool(c["value"])
        elif c["key"] == "view_challenges_unregistered":
            view_challenges_unregistered = cast_bool(c["value"])
        elif c["key"] == "view_scoreboard_if_authed":
            view_scoreboard_if_authed = cast_bool(c["value"])

        if c["key"] not in banned:
            new_conn["config"].insert(dict(c))

    if workshop_mode:
        score_visibility = "admins"
        account_visibility = "admins"

    if hide_scores:
        score_visibility = "hidden"

    if prevent_registration:
        registration_visibility = "private"

    if view_challenges_unregistered:
        challenge_visibility = "public"

    if view_scoreboard_if_authed:
        score_visibility = "private"

    new_conn["config"].insert({"key": "user_mode", "value": "users"})
    new_conn["config"].insert(
        {"key": "challenge_visibility", "value": challenge_visibility}
    )
    new_conn["config"].insert(
        {"key": "registration_visibility", "value": registration_visibility}
    )
    new_conn["config"].insert({"key": "score_visibility", "value": score_visibility})
    new_conn["config"].insert(
        {"key": "account_visibility", "value": account_visibility}
    )
    del old_data["config"]

    manual = []
    not_created = []
    print("MIGRATING extra tables")
    for table in old_data.keys():
        print("MIGRATING", table)
        new_conn.create_table(table, primary_id=False)
        data = old_data[table]

        ran = False
        for row in data:
            new_conn[table].insert(dict(row))
            ran = True
        else:  # We finished inserting
            if ran:
                manual.append(table)

        if ran is False:
            not_created.append(table)

    print("Migration completed.")
    print(
        "The following tables require manual setting of primary keys and manual inspection"
    )
    for table in manual:
        print("\t", table)

    print(
        "For example you can use the following commands if you know that the PRIMARY KEY for the table is `id`:"
    )
    for table in manual:
        print("\t", "ALTER TABLE `{table}` ADD PRIMARY KEY(id)".format(table=table))

    print(
        "The following tables were not created because they were empty and must be manually recreated (e.g. app.db.create_all()"
    )
    for table in not_created:
        print("\t", table)
