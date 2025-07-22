import csv
import json
from io import BytesIO, StringIO

from CTFd.models import (
    Flags,
    Hints,
    Tags,
    TeamFields,
    Teams,
    UserFields,
    Users,
    db,
    get_class_by_tablename,
)
from CTFd.plugins.challenges import get_chal_class
from CTFd.schemas.challenges import ChallengeSchema
from CTFd.schemas.teams import TeamSchema
from CTFd.schemas.users import UserSchema
from CTFd.utils.config import is_teams_mode, is_users_mode
from CTFd.utils.scores import get_standings


def get_dumpable_tables():
    csv_keys = list(CSV_KEYS.keys())
    db_keys = list(db.metadata.tables.keys())
    tables = csv_keys + db_keys
    table_keys = list(zip(tables, tables))
    return table_keys


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

    # Get all user fields in a specific order
    user_fields = UserFields.query.all()
    user_field_ids = [f.id for f in user_fields]
    user_field_names = [f.name for f in user_fields]

    if is_teams_mode():
        team_fields = TeamFields.query.all()
        team_field_ids = [f.id for f in team_fields]
        team_field_names = [f.name for f in team_fields]

        header = (
            [
                "place",
                "team",
                "team id",
                "score",
                "member name",
                "member id",
                "member email",
                "member score",
                "team bracket id",
                "team bracket name",
                "member bracket id",
                "member bracket name",
            ]
            + user_field_names
            + team_field_names
        )
        writer.writerow(header)

        for i, standing in enumerate(standings):
            team = Teams.query.filter_by(id=standing.account_id).first()

            # Build field entries using the order of the field values
            team_field_entries = {f.field_id: f.value for f in team.field_entries}
            team_field_values = [
                team_field_entries.get(f_id, "") for f_id in team_field_ids
            ]
            user_field_values = len(user_field_names) * [""]
            team_row = (
                [
                    i + 1,
                    team.name,
                    team.id,
                    standing.score,
                    "",
                    "",
                    "",
                    "",
                    team.bracket_id,
                    team.bracket.name if team.bracket else "",
                    "",
                    "",
                ]
                + user_field_values
                + team_field_values
            )

            writer.writerow(team_row)

            for member in team.members:
                user_field_entries = {f.field_id: f.value for f in member.field_entries}
                user_field_values = [
                    user_field_entries.get(f_id, "") for f_id in user_field_ids
                ]
                team_field_values = len(team_field_names) * [""]
                user_row = (
                    [
                        "",
                        "",
                        "",
                        "",
                        member.name,
                        member.id,
                        member.email,
                        member.score,
                        "",
                        "",
                        member.bracket_id,
                        member.bracket.name if member.bracket else "",
                    ]
                    + user_field_values
                    + team_field_values
                )
                writer.writerow(user_row)
    elif is_users_mode():
        header = [
            "place",
            "user name",
            "user id",
            "user email",
            "score",
            "user bracket id",
            "user bracket name",
        ] + user_field_names
        writer.writerow(header)

        for i, standing in enumerate(standings):
            user = Users.query.filter_by(id=standing.account_id).first()

            # Build field entries using the order of the field values
            user_field_entries = {f.field_id: f.value for f in user.field_entries}
            user_field_values = [
                user_field_entries.get(f_id, "") for f_id in user_field_ids
            ]
            user_row = [
                i + 1,
                user.name,
                user.id,
                user.email,
                standing.score,
                user.bracket_id,
                user.bracket.name if user.bracket else "",
            ] + user_field_values
            writer.writerow(user_row)

    # In Python 3 send_file requires bytes
    output = BytesIO()
    output.write(temp.getvalue().encode("utf-8"))
    output.seek(0)
    temp.close()

    return output


def dump_users_with_fields_csv():
    temp = StringIO()
    writer = csv.writer(temp)

    user_fields = UserFields.query.all()
    user_field_ids = [f.id for f in user_fields]
    user_field_names = [f.name for f in user_fields]

    header = [column.name for column in Users.__mapper__.columns] + user_field_names
    writer.writerow(header)

    responses = Users.query.all()

    for curr in responses:
        user_field_entries = {f.field_id: f.value for f in curr.field_entries}
        user_field_values = [
            user_field_entries.get(f_id, "") for f_id in user_field_ids
        ]
        user_row = [
            getattr(curr, column.name) for column in Users.__mapper__.columns
        ] + user_field_values
        writer.writerow(user_row)

    temp.seek(0)

    # In Python 3 send_file requires bytes
    output = BytesIO()
    output.write(temp.getvalue().encode("utf-8"))
    output.seek(0)
    temp.close()

    return output


def dump_teams_with_fields_csv():
    temp = StringIO()
    writer = csv.writer(temp)

    team_fields = TeamFields.query.all()
    team_field_ids = [f.id for f in team_fields]
    team_field_names = [f.name for f in team_fields]

    header = [column.name for column in Teams.__mapper__.columns] + team_field_names
    writer.writerow(header)

    responses = Teams.query.all()

    for curr in responses:
        team_field_entries = {f.field_id: f.value for f in curr.field_entries}
        team_field_values = [
            team_field_entries.get(f_id, "") for f_id in team_field_ids
        ]

        team_row = [
            getattr(curr, column.name) for column in Teams.__mapper__.columns
        ] + team_field_values

        writer.writerow(team_row)

    temp.seek(0)

    # In Python 3 send_file requires bytes
    output = BytesIO()
    output.write(temp.getvalue().encode("utf-8"))
    output.seek(0)
    temp.close()

    return output


def dump_teams_with_members_fields_csv():
    temp = StringIO()
    writer = csv.writer(temp)

    team_fields = TeamFields.query.all()
    team_field_ids = [f.id for f in team_fields]
    team_field_names = [f.name for f in team_fields]

    user_fields = UserFields.query.all()
    user_field_ids = [f.id for f in user_fields]
    user_field_names = [f.name for f in user_fields]

    user_header = [
        f"member_{column.name}" for column in Users.__mapper__.columns
    ] + user_field_names

    header = (
        [column.name for column in Teams.__mapper__.columns]
        + team_field_names
        + user_header
    )
    writer.writerow(header)

    responses = Teams.query.all()

    for curr in responses:
        team_field_entries = {f.field_id: f.value for f in curr.field_entries}
        team_field_values = [
            team_field_entries.get(f_id, "") for f_id in team_field_ids
        ]

        team_row = [
            getattr(curr, column.name) for column in Teams.__mapper__.columns
        ] + team_field_values

        writer.writerow(team_row)

        for member in curr.members:
            padding = [""] * len(team_row)

            user_field_entries = {f.field_id: f.value for f in member.field_entries}
            user_field_values = [
                user_field_entries.get(f_id, "") for f_id in user_field_ids
            ]
            user_row = [
                getattr(member, column.name) for column in Users.__mapper__.columns
            ] + user_field_values
            writer.writerow(padding + user_row)

    temp.seek(0)

    # In Python 3 send_file requires bytes
    output = BytesIO()
    output.write(temp.getvalue().encode("utf-8"))
    output.seek(0)
    temp.close()

    return output


def dump_database_table(tablename):
    # TODO: It might make sense to limit dumpable tables. Config could potentially leak sensitive information.
    model = get_class_by_tablename(tablename)

    if model is None:
        raise KeyError("Unknown database table")

    temp = StringIO()
    writer = csv.writer(temp)

    header = model.__mapper__.column_attrs.keys()
    writer.writerow(header)

    responses = model.query.all()

    for curr in responses:
        writer.writerow([getattr(curr, column) for column in header])

    temp.seek(0)

    # In Python 3 send_file requires bytes
    output = BytesIO()
    output.write(temp.getvalue().encode("utf-8"))
    output.seek(0)
    temp.close()

    return output


def load_users_csv(dict_reader):
    schema = UserSchema()
    errors = []
    for i, line in enumerate(dict_reader):
        response = schema.load(line)
        if response.errors:
            errors.append((i, response.errors))
        else:
            db.session.add(response.data)
            db.session.commit()
    if errors:
        return errors
    return True


def load_teams_csv(dict_reader):
    schema = TeamSchema()
    errors = []
    for i, line in enumerate(dict_reader):
        response = schema.load(line)
        if response.errors:
            errors.append((i, response.errors))
        else:
            db.session.add(response.data)
            db.session.commit()
    if errors:
        return errors
    return True


def load_challenges_csv(dict_reader):
    schema = ChallengeSchema()
    errors = []

    for i, line in enumerate(dict_reader):
        # Throw away fields that we can't trust if provided
        _ = line.pop("id", None)
        _ = line.pop("requirements", None)

        flags = line.pop("flags", None)
        tags = line.pop("tags", None)
        hints = line.pop("hints", None)
        challenge_type = line.pop("type", "standard")

        # Load in custom type_data
        type_data = json.loads(line.pop("type_data", "{}") or "{}")
        line.update(type_data)

        response = schema.load(line)
        if response.errors:
            errors.append((i + 1, response.errors))
            continue

        ChallengeClass = get_chal_class(challenge_type)
        challenge = ChallengeClass.challenge_model(**line)
        db.session.add(challenge)
        db.session.commit()

        if flags:
            try:
                # Allow for column to contain JSON for more flexible data entry
                json_flags = json.loads(flags)
                if isinstance(json_flags, list) and all(
                    isinstance(f, dict) for f in json_flags
                ):
                    for flag in json_flags:
                        type = flag.get("type", "static")
                        content = flag.get("content", "")
                        data = flag.get("data", None)
                        f = Flags(
                            challenge_id=challenge.id,
                            type=type,
                            content=content,
                            data=data,
                        )
                        db.session.add(f)
                        db.session.commit()
                else:
                    raise TypeError("Processing flags as strings instead of JSON")

            except (json.JSONDecodeError, TypeError):
                string_flags = [flag.strip() for flag in flags.split(",")]
                for flag in string_flags:
                    f = Flags(
                        type="static",
                        challenge_id=challenge.id,
                        content=flag,
                    )
                    db.session.add(f)
                    db.session.commit()

        if tags:
            tags = [tag.strip() for tag in tags.split(",")]
            for tag in tags:
                t = Tags(
                    challenge_id=challenge.id,
                    value=tag,
                )
                db.session.add(t)
                db.session.commit()

        if hints:
            try:
                # Allow for column to contain JSON for more flexible data entry
                json_hints = json.loads(hints)
                if isinstance(json_hints, list) and all(
                    isinstance(h, dict) for h in json_hints
                ):
                    for hint in json_hints:
                        content = hint.get("content", "")
                        cost = hint.get("cost", 0)
                        h = Hints(
                            challenge_id=challenge.id,
                            content=content,
                            cost=cost,
                        )
                        db.session.add(h)
                        db.session.commit()
                else:
                    raise TypeError("Processing hints as strings instead of JSON")
            except (json.JSONDecodeError, TypeError):
                string_hints = [hint.strip() for hint in hints.split(",")]
                for hint in string_hints:
                    h = Hints(
                        challenge_id=challenge.id,
                        content=hint,
                    )
                    db.session.add(h)
                    db.session.commit()
    if errors:
        return errors
    return True


CSV_KEYS = {
    "scoreboard": dump_scoreboard_csv,
    "users+fields": dump_users_with_fields_csv,
    "teams+fields": dump_teams_with_fields_csv,
    "teams+members+fields": dump_teams_with_members_fields_csv,
}
