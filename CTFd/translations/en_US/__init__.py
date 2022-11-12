# todo: split into modules and merge the dicts

def attempts_left(attempts):
    tries_str = "tries"
    if attempts == 1:
        tries_str = "try"
    return "You have {} {} remaining".format(
        attempts, tries_str
    )


api_v1 = {
    "awards.user.not_team_member": "User doesn't have a team to associate award with",
    "challenges.type.not_installed": lambda type: "The underlying challenge type ({}) is not installed. This challenge can not be loaded.".format(type),
    "challenges.attempt.game_paused": lambda name: "{} is paused".format(name),
    "challenges.attempt.ratelimited": "You're submitting flags too fast. Slow down.",
    "challenges.attempt.attempts_left": attempts_left,
    "challenges.attempt.already_solved": "You already solved this",
    "hints.view.unmet_prerequisites": "You must unlock other hints before accessing this hint",
    "teams.edit.not_captain": "Only team captains can edit team information",
    "teams.delete.disabled": "Team disbanding is currently disabled",
    "teams.delete.not_captain": "Only team captains can disband their team",
    "teams.delete.participated": (
        "You cannot disband your team as it has participated in the event. "
        "Please contact an admin to disband your team or remove a member."
    ),
    "teams.member.invite.not_captain": "Only team captains can generate invite codes",
    "teams.member.join.conflict": "User has already joined a team",
    "teams.member.delete.not_member": "User is not part of this team",
    "unlocks.insufficient_points": "You do not have enough points to unlock this hint",
    "unlocks.already_unlocked": "You've already unlocked this this target", # TODO: typo?
    "users.edit.no_self_ban": "You cannot ban yourself",
    "users.delete.no_self_delete": "You cannot delete yourself",
    "users.email.not_configured": "Email settings not configured",
    "users.email.text_empty": "Email text cannot be empty",
}

translations = {
    "challenges.name": "Name",
    "challenges.id": "ID",
    "challenges.category": "Category",
    "challenges.type": "Type",
    "constants.config.invalid_theme_settings": "invalid theme_settings",
    "forms.parameter": "Parameter",
    "forms.search": "Search",
    "forms.submit": "Submit",
    "forms.upload": "Upload",
    "forms.auth.username": "User Name",
    "forms.auth.username_or_email": "User Name or Email",
    "forms.auth.email": "Email",
    "forms.auth.password": "Password",
    "forms.auth.resend_confirm_email": "Resend Confirmation Email",
    "forms.challenge_files.files": "Upload Files",
    "forms.challenge_files.files.desc": "Attach multiple files using Control+Click or Cmd+Click.",
    "forms.awards.icon.none": "None",
    "forms.awards.icon.shield": "Shield",
    "forms.awards.icon.bug": "Bug",
    "forms.awards.icon.crown": "Crown",
    "forms.awards.icon.crosshairs": "Crosshairs",
    "forms.awards.icon.ban": "Ban",
    "forms.awards.icon.lightning": "Lightning",
    "forms.awards.icon.skull": "Skull",
    "forms.awards.icon.brain": "Brain",
    "forms.awards.icon.code": "Code",
    "forms.awards.icon.cowboy": "Cowboy",
    "forms.awards.icon.angry": "Angry",
    "plugins.challenges.correct": "Correct",
    "plugins.challenges.incorrect": "Incorrect",
}
translations.update({
    "api.v1." + k: v
    for k, v in api_v1.items()
})
