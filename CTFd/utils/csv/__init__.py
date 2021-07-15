import json

from CTFd.models import Flags, Hints, Tags, Teams, Users, db
from CTFd.plugins.challenges import get_chal_class


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
