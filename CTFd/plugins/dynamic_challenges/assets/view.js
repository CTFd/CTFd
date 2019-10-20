CTFd._internal.challenge.data = undefined

CTFd._internal.challenge.renderer = new CTFd.lib.MarkdownIt({
    html: true,
    linkify: true,
})

CTFd._internal.challenge.renderer.renderer.rules.link_open = function (tokens, idx, options, env, self) {
    tokens[idx].attrPush(['target', '_blank']);
    return self.renderToken(tokens, idx, options);
};

CTFd._internal.challenge.preRender = function () { }

CTFd._internal.challenge.render = function (markdown) {
    return CTFd._internal.challenge.renderer.render(markdown)
}


CTFd._internal.challenge.postRender = function () { }


CTFd._internal.challenge.submit = function (preview) {
    var challenge_id = parseInt(CTFd.lib.$('#challenge-id').val())
    var submission = CTFd.lib.$('#submission-input').val()

    var params = {
        'challenge_id': challenge_id,
        'submission': submission,
    }
    if (preview) {
        params['preview'] = true
    }

    return CTFd.api.post_challenge_attempt(params).then(function (response) {
        if (response.status === 429) {
            // User was ratelimited but process response
            return response
        }
        if (response.status === 403) {
            // User is not logged in or CTF is paused.
            return response
        }
        return response
    })
};
