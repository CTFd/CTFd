# todo: split into modules and merge the dicts

def attempts_left(attempts):
    tries_str = "tries"
    if attempts == 1:
        tries_str = "try"
    return "You have {} {} remaining".format(
        attempts, tries_str
    )


api_v1 = {
    "challenges.type.not_installed": lambda type: "The underlying challenge type ({}) is not installed. This challenge can not be loaded.".format(type),
    "challenges.attempt.game_paused": lambda name: "{} is paused".format(name),
    "challenges.attempt.ratelimited": "You're submitting flags too fast. Slow down.",
    "challenges.attempt.attempts_left": attempts_left,
    "challenges.attempt.already_solved": "You already solved this",
}

translations = {

}
translations.update({
    "api.v1." + k: v
    for k, v in api_v1.items()
})
