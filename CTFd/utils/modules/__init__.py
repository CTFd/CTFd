from sqlalchemy.sql import or_

from CTFd.cache import cache
from CTFd.models import (
    AudienceMembers,
    Audiences,
    Challenges,
    ModuleAudienceAccess,
    Modules,
)


@cache.memoize(timeout=60)
def get_accessible_module_ids_for_account_id(account_id):
    if account_id is None:
        return set()
    q = (
        Modules.query.with_entities(Modules.id)
        .join(ModuleAudienceAccess, ModuleAudienceAccess.module_id == Modules.id)
        .join(Audiences, Audiences.id == ModuleAudienceAccess.audience_id)
        .join(AudienceMembers, AudienceMembers.audience_id == Audiences.id)
        .filter(AudienceMembers.account_id == account_id)
    )
    return {row.id for row in q.all()}


def get_accessible_module_ids(user):
    if user is None:
        return set()
    return get_accessible_module_ids_for_account_id(user.account_id)


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
