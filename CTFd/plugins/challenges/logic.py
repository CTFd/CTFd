from CTFd.models import Partials
from CTFd.plugins.flags import FlagException, get_flag_class
from CTFd.utils.config import is_teams_mode
from CTFd.utils.user import get_current_team, get_current_user


def challenge_attempt_any(submission, challenge, flags):
    from CTFd.plugins.challenges import ChallengeResponse

    for flag in flags:
        try:
            if get_flag_class(flag.type).compare(flag, submission):
                return ChallengeResponse(
                    status="correct",
                    message="Correct",
                )
        except FlagException as e:
            return ChallengeResponse(
                status="incorrect",
                message=str(e),
            )
    return ChallengeResponse(
        status="incorrect",
        message="Incorrect",
    )


def challenge_attempt_all(submission, challenge, flags):
    from CTFd.plugins.challenges import ChallengeResponse

    user = get_current_user()
    partials = Partials.query.filter_by(
        account_id=user.account_id, challenge_id=challenge.id
    ).all()
    provideds = [partial.provided for partial in partials]
    provideds.append(submission)

    target_flags_ids = {flag.id for flag in flags}
    compared_flag_ids = []

    for flag in flags:
        # Skip flags that we have already evaluated as captured
        if flag.id in compared_flag_ids:
            continue
        flag_class = get_flag_class(flag.type)
        for provided in provideds:
            if flag_class.compare(flag, provided):
                compared_flag_ids.append(flag.id)

    # If we have captured against all flag IDs the challenge is correct
    if target_flags_ids == set(compared_flag_ids):
        return ChallengeResponse(
            status="correct",
            message="Correct",
        )

    # If we didn't capture all flag IDs we must be missing something.
    for flag in flags:
        if get_flag_class(flag.type).compare(flag, submission):
            return ChallengeResponse(
                status="partial",
                message="Correct but more flags are required",
            )

    # Input is just wrong
    return ChallengeResponse(
        status="incorrect",
        message="Incorrect",
    )


def challenge_attempt_team(submission, challenge, flags):
    from CTFd.plugins.challenges import ChallengeResponse

    if is_teams_mode():
        user = get_current_user()
        team = get_current_team()
        partials = Partials.query.filter_by(
            team_id=team.id, challenge_id=challenge.id
        ).all()

        submitter_ids = {partial.user_id for partial in partials}

        # Check if the user's submission is correct
        for flag in flags:
            try:
                if get_flag_class(flag.type).compare(flag, submission):
                    submitter_ids.add(user.id)
                    break
            except FlagException as e:
                return ChallengeResponse(
                    status="incorrect",
                    message=str(e),
                )
        else:
            return ChallengeResponse(
                status="incorrect",
                message="Incorrect",
            )

        # The submission is correct so compare if we have received from all team members
        member_ids = {member.id for member in team.members}
        if member_ids == submitter_ids:
            return ChallengeResponse(
                status="correct",
                message="Correct",
            )
        else:
            # We have not received from all members
            return ChallengeResponse(
                status="partial",
                message="Correct but all team members must submit a flag",
            )
    else:
        for flag in flags:
            try:
                if get_flag_class(flag.type).compare(flag, submission):
                    return ChallengeResponse(
                        status="correct",
                        message="Correct",
                    )
            except FlagException as e:
                return ChallengeResponse(
                    status="incorrect",
                    message=str(e),
                )
        return ChallengeResponse(
            status="incorrect",
            message="Incorrect",
        )
