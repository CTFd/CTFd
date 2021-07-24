import csv
import json
from io import BytesIO, StringIO

from CTFd.models import Flags, Hints, Tags, Teams, Users, db, get_class_by_tablename, UserFields, TeamFields
from CTFd.plugins.challenges import get_chal_class
from CTFd.utils.scores import get_standings
from CTFd.utils.config import is_users_mode, is_teams_mode

CSV_KEYS = {
    "scoreboard": 1,
    "users+fields": 1,
    "teams+fields": 1,
}


def dump_csv(name):
    dump_func = CSV_KEYS.get(name)
    if dump_func:
        return dump_func()
    elif get_class_by_tablename(name):
        return dump_database_table(tablename=name)
    else:
        raise KeyError


def dump_scoreboard_csv():
    # TODO: Add fields to scoreboard data
    temp = StringIO()
    writer = csv.writer(temp)

    standings = get_standings()
    if is_teams_mode():
        header = ["place", "team", "score", "members", "member score"]
        writer.writerow(header)

        for i, standing in enumerate(standings):
            team = Teams.query.filter_by(id=standing.account_id).first()
            writer.writerow([i + 1, team.name, standing.score, "", ""])
            for member in team.members:
                writer.writerow(["", "", "", member.name, member.score])
    elif is_users_mode():
        header = ["place", "user", "score"]
        writer.writerow(header)

        for i, standing in enumerate(standings):
            user = Users.query.filter_by(id=standing.account_id).first()
            writer.writerow([i + 1, user.name, standing.score])

    # In Python 3 send_file requires bytes
    output = BytesIO()
    output.write(temp.getvalue().encode("utf-8"))
    output.seek(0)
    temp.close()

    return output


def dump_users_with_fields_csv():
    # TODO: Implement
    pass


def dump_teams_with_fields_csv():
    # TODO: Implement
    pass


def dump_database_table(tablename):
    # TODO: It might make sense to limit dumpable tables. Config could potentially leak sensitive information.
    model = get_class_by_tablename(tablename)

    if model is None:
        raise KeyError("Unknown database table")

    temp = StringIO()
    writer = csv.writer(temp)

    header = [column.name for column in model.__mapper__.columns]
    writer.writerow(header)

    responses = model.query.all()

    for curr in responses:
        writer.writerow(
            [getattr(curr, column.name) for column in model.__mapper__.columns]
        )

    temp.seek(0)

    # In Python 3 send_file requires bytes
    output = BytesIO()
    output.write(temp.getvalue().encode("utf-8"))
    output.seek(0)
    temp.close()

    return output


def load_users_csv(dict_reader):
    for line in dict_reader:
        result = Users(**line)
        db.session.add(result)
        db.session.commit()
    return True


def load_teams_csv(dict_reader):
    for line in dict_reader:
        result = Teams(**line)
        db.session.add(result)
        db.session.commit()
    return True


def load_challenges_csv(dict_reader):
    for line in dict_reader:
        flags = line.pop("flags", None)
        tags = line.pop("tags", None)
        hints = line.pop("hints", None)
        challenge_type = line.pop("type", "standard")

        # Load in custome type_data
        type_data = json.loads(line.pop("type_data", "{}"))
        line.update(type_data)

        ChallengeClass = get_chal_class(challenge_type)
        challenge = ChallengeClass.challenge_model(**line)
        db.session.add(challenge)
        db.session.commit()

        if flags:
            flags = [flag.strip() for flag in flags.split(",")]
            for flag in flags:
                f = Flags(type="static", challenge_id=challenge.id, content=flag,)
                db.session.add(f)
                db.session.commit()

        if tags:
            tags = [tag.strip() for tag in tags.split(",")]
            for tag in tags:
                t = Tags(challenge_id=challenge.id, value=tag,)
                db.session.add(t)
                db.session.commit()

        if hints:
            hints = [hint.strip() for hint in hints.split(",")]
            for hint in hints:
                h = Hints(challenge_id=challenge.id, content=hint,)
                db.session.add(h)
                db.session.commit()
    return True
