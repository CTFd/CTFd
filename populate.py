#!/usr/bin/python
# -*- coding: utf-8 -*-

import datetime
import hashlib
import random
import argparse

from CTFd import create_app
from CTFd.cache import clear_challenges, clear_config, clear_standings, clear_pages
from CTFd.models import (
    Users,
    Teams,
    Challenges,
    Flags,
    Awards,
    ChallengeFiles,
    Fails,
    Solves,
    Tracking,
)
from faker import Faker

fake = Faker()

parser = argparse.ArgumentParser()

parser.add_argument("--mode", help="Set user mode", default="teams")
parser.add_argument("--users", help="Amount of users to generate", default=50, type=int)
parser.add_argument("--teams", help="Amount of teams to generate", default=10, type=int)
parser.add_argument(
    "--challenges", help="Amount of challenges to generate", default=20, type=int
)
parser.add_argument(
    "--awards", help="Amount of awards to generate", default=5, type=int
)

args = parser.parse_args()

app = create_app()

mode = args.mode
USER_AMOUNT = args.users
TEAM_AMOUNT = args.teams if args.mode == "teams" else 0
CHAL_AMOUNT = args.challenges
AWARDS_AMOUNT = args.awards

categories = [
    "Exploitation",
    "Reversing",
    "Web",
    "Forensics",
    "Scripting",
    "Cryptography",
    "Networking",
]
companies = ["Corp", "Inc.", "Squad", "Team"]
icons = [
    None,
    "shield",
    "bug",
    "crown",
    "crosshairs",
    "ban",
    "lightning",
    "code",
    "cowboy",
    "angry",
]


def gen_sentence():
    return fake.text()


def gen_name():
    return fake.first_name()


def gen_team_name():
    return fake.word().capitalize() + str(random.randint(1, 1000))


def gen_email():
    return fake.email()


def gen_category():
    return random.choice(categories)


def gen_affiliation():
    return (fake.word() + " " + random.choice(companies)).title()


def gen_value():
    return random.choice(range(100, 500, 50))


def gen_word():
    return fake.word()


def gen_icon():
    return random.choice(icons)


def gen_file():
    return fake.file_name()


def gen_ip():
    return fake.ipv4()


def random_date(start, end):
    return start + datetime.timedelta(
        seconds=random.randint(0, int((end - start).total_seconds()))
    )


def random_chance():
    return random.random() > 0.5


if __name__ == "__main__":
    with app.app_context():
        db = app.db

        # Generating Challenges
        print("GENERATING CHALLENGES")
        for x in range(CHAL_AMOUNT):
            word = gen_word()
            chal = Challenges(
                name=word,
                description=gen_sentence(),
                attribution=f"Written by {gen_name()}",
                value=gen_value(),
                category=gen_category(),
            )
            db.session.add(chal)
            db.session.commit()
            f = Flags(challenge_id=x + 1, content=word, type="static")
            db.session.add(f)
            db.session.commit()

        # Generating Files
        print("GENERATING FILES")
        AMT_CHALS_WITH_FILES = int(CHAL_AMOUNT * (3.0 / 4.0))
        for x in range(AMT_CHALS_WITH_FILES):
            chal = random.randint(1, CHAL_AMOUNT)
            filename = gen_file()
            md5hash = hashlib.md5(filename.encode("utf-8")).hexdigest()
            chal_file = ChallengeFiles(
                challenge_id=chal, location=md5hash + "/" + filename
            )
            db.session.add(chal_file)

        db.session.commit()

        # Generating Teams
        print("GENERATING TEAMS")
        used = []
        used_oauth_ids = []
        count = 0
        while count < TEAM_AMOUNT:
            name = gen_team_name()
            if name not in used:
                used.append(name)
                team = Teams(name=name, password="password")
                if random_chance():
                    team.affiliation = gen_affiliation()
                if random_chance():
                    oauth_id = random.randint(1, 1000)
                    while oauth_id in used_oauth_ids:
                        oauth_id = random.randint(1, 1000)
                    used_oauth_ids.append(oauth_id)
                    team.oauth_id = oauth_id
                db.session.add(team)
                count += 1

        db.session.commit()

        # Generating Users
        print("GENERATING USERS")
        used = []
        used_oauth_ids = []
        count = 0
        while count < USER_AMOUNT:
            name = gen_name()
            if name not in used:
                used.append(name)
                try:
                    user = Users(name=name, email=gen_email(), password="password")
                    user.verified = True
                    if random_chance():
                        user.affiliation = gen_affiliation()
                    if random_chance():
                        oauth_id = random.randint(1, 1000)
                        while oauth_id in used_oauth_ids:
                            oauth_id = random.randint(1, 1000)
                        used_oauth_ids.append(oauth_id)
                        user.oauth_id = oauth_id
                    if mode == "teams":
                        user.team_id = random.randint(1, TEAM_AMOUNT)
                    db.session.add(user)
                    db.session.flush()

                    track = Tracking(ip=gen_ip(), user_id=user.id)
                    db.session.add(track)
                    db.session.flush()
                    count += 1
                except Exception:
                    pass

        db.session.commit()

        if mode == "teams":
            # Assign Team Captains
            print("GENERATING TEAM CAPTAINS")
            teams = Teams.query.all()
            for team in teams:
                captain = (
                    Users.query.filter_by(team_id=team.id)
                    .order_by(Users.id)
                    .limit(1)
                    .first()
                )
                if captain:
                    team.captain_id = captain.id
            db.session.commit()

        # Generating Solves
        print("GENERATING SOLVES")
        if mode == "users":
            for x in range(USER_AMOUNT):
                used = []
                base_time = datetime.datetime.utcnow() + datetime.timedelta(
                    minutes=-10000
                )
                for y in range(random.randint(1, CHAL_AMOUNT)):
                    chalid = random.randint(1, CHAL_AMOUNT)
                    if chalid not in used:
                        used.append(chalid)
                        user = Users.query.filter_by(id=x + 1).first()
                        solve = Solves(
                            user_id=user.id,
                            team_id=user.team_id,
                            challenge_id=chalid,
                            ip="127.0.0.1",
                            provided=gen_word(),
                        )

                        new_base = random_date(
                            base_time,
                            base_time
                            + datetime.timedelta(minutes=random.randint(30, 60)),
                        )
                        solve.date = new_base
                        base_time = new_base

                        db.session.add(solve)
                        db.session.commit()
        elif mode == "teams":
            for x in range(1, TEAM_AMOUNT):
                used_teams = []
                used_users = []
                base_time = datetime.datetime.utcnow() + datetime.timedelta(
                    minutes=-10000
                )
                team = Teams.query.filter_by(id=x).first()
                members_ids = [member.id for member in team.members]
                for y in range(random.randint(1, CHAL_AMOUNT)):
                    chalid = random.randint(1, CHAL_AMOUNT)
                    user_id = random.choice(members_ids)
                    if (chalid, team.id) not in used_teams:
                        if (chalid, user_id) not in used_users:
                            solve = Solves(
                                user_id=user_id,
                                team_id=team.id,
                                challenge_id=chalid,
                                ip="127.0.0.1",
                                provided=gen_word(),
                            )
                            new_base = random_date(
                                base_time,
                                base_time
                                + datetime.timedelta(minutes=random.randint(30, 60)),
                            )
                            solve.date = new_base
                            base_time = new_base
                            db.session.add(solve)
                            db.session.commit()
                            used_teams.append((chalid, team.id))
                            used_users.append((chalid, user_id))

        db.session.commit()

        # Generating Awards
        print("GENERATING AWARDS")
        for x in range(USER_AMOUNT):
            base_time = datetime.datetime.utcnow() + datetime.timedelta(minutes=-10000)
            for _ in range(random.randint(0, AWARDS_AMOUNT)):
                user = Users.query.filter_by(id=x + 1).first()
                award = Awards(
                    user_id=user.id,
                    team_id=user.team_id,
                    name=gen_word(),
                    value=random.randint(-10, 10),
                    icon=gen_icon(),
                )
                new_base = random_date(
                    base_time,
                    base_time + datetime.timedelta(minutes=random.randint(30, 60)),
                )
                award.date = new_base
                base_time = new_base

                db.session.add(award)

        db.session.commit()

        # Generating Wrong Flags
        print("GENERATING WRONG FLAGS")
        for x in range(USER_AMOUNT):
            used = []
            base_time = datetime.datetime.utcnow() + datetime.timedelta(minutes=-10000)
            for y in range(random.randint(1, CHAL_AMOUNT * 20)):
                chalid = random.randint(1, CHAL_AMOUNT)
                if chalid not in used:
                    used.append(chalid)
                    user = Users.query.filter_by(id=x + 1).first()
                    wrong = Fails(
                        user_id=user.id,
                        team_id=user.team_id,
                        challenge_id=chalid,
                        ip="127.0.0.1",
                        provided=gen_word(),
                    )

                    new_base = random_date(
                        base_time,
                        base_time + datetime.timedelta(minutes=random.randint(30, 60)),
                    )
                    wrong.date = new_base
                    base_time = new_base

                    db.session.add(wrong)
                    db.session.commit()

        db.session.commit()
        db.session.close()

        clear_config()
        clear_standings()
        clear_challenges()
        clear_pages()
