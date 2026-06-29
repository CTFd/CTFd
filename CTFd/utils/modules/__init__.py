from flask import g
from sqlalchemy.sql import or_

from CTFd.models import (
    AudienceMembers,
    Audiences,
    Challenges,
    ModuleAudienceAccess,
    Modules,
)
from CTFd.utils import get_config
from CTFd.utils.modes import TEAMS_MODE


def _resolve_account(user):
    """Return (user_id, team_id) for the access query, depending on user_mode."""
    if user is None:
        return None, None
    if get_config("user_mode") == TEAMS_MODE:
        return None, getattr(user, "team_id", None)
    return user.id, None


def get_accessible_module_ids(user):
    """Module IDs accessible to this account, cached per-request on flask.g."""
    if user is None:
        return set()

    cache_key = "_ctfd_accessible_module_ids"
    cached = getattr(g, cache_key, None)
    if cached is not None and cached.get("user_id") == user.id:
        return cached["ids"]

    user_id, team_id = _resolve_account(user)
    if user_id is None and team_id is None:
        ids = set()
    else:
        q = (
            Modules.query.with_entities(Modules.id)
            .join(ModuleAudienceAccess, ModuleAudienceAccess.module_id == Modules.id)
            .join(Audiences, Audiences.id == ModuleAudienceAccess.audience_id)
            .join(AudienceMembers, AudienceMembers.audience_id == Audiences.id)
        )
        if team_id is not None:
            q = q.filter(AudienceMembers.team_id == team_id)
        else:
            q = q.filter(AudienceMembers.user_id == user_id)
        ids = {row[0] for row in q.all()}

    setattr(g, cache_key, {"user_id": user.id, "ids": ids})
    return ids


def can_access_challenge(challenge, user):
    """True if the challenge has no module OR is in a module the user can access."""
    module_id = getattr(challenge, "module_id", None)
    if module_id is None:
        return True
    return module_id in get_accessible_module_ids(user)


def filter_challenges_by_module_access(query, user):
    """Apply (module_id IS NULL OR module_id IN accessible) to a Challenges query."""
    ids = get_accessible_module_ids(user)
    if not ids:
        return query.filter(Challenges.module_id.is_(None))
    return query.filter(
        or_(Challenges.module_id.is_(None), Challenges.module_id.in_(ids))
    )
