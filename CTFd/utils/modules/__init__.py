from datetime import datetime

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


def is_module_accessible(module_ids, accessible_ids):
    """True if a challenge with these module ids is visible given accessible_ids."""
    module_ids = set(module_ids or ())
    return not module_ids or bool(module_ids & accessible_ids)


def can_access_challenge(challenge, user):
    """True if the user can access the challenge.

    A challenge is accessible when its scheduled release time (if any) has
    passed AND it either has no modules or is in any module the user can access.
    This does not account for admin status; callers are expected to bypass
    this check for admins where appropriate.
    """
    scheduled_at = getattr(challenge, "scheduled_at", None)
    if scheduled_at is not None and scheduled_at > datetime.utcnow():
        return False
    module_ids = getattr(challenge, "module_ids", None)
    if not module_ids:
        return True
    return is_module_accessible(module_ids, get_accessible_module_ids(user))


def filter_challenges_by_module_access(query, user):
    """Keep challenges with no modules or with any module the user can access."""
    ids = get_accessible_module_ids(user)
    if not ids:
        return query.filter(~Challenges.modules.any())
    return query.filter(
        or_(~Challenges.modules.any(), Challenges.modules.any(Modules.id.in_(ids)))
    )
