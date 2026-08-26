CTFd._internal.challenge.data = undefined

CTFd._internal.challenge.renderer = null;

CTFd._internal.challenge.preRender = function () {
}

CTFd._internal.challenge.render = null;

CTFd._internal.challenge.postRender = function () {
    loadInfo();
}

if (window.$ === undefined) window.$ = CTFd.lib.$;

function loadInfo() {
    var challenge_id = CTFd._internal.challenge.data.id;
    var url = "/api/v1/plugins/ctfd-whale/container?challenge_id=" + challenge_id;

    CTFd.fetch(url, {
        method: 'GET',
        credentials: 'same-origin',
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
    }).then(function (response) {
        if (response.status === 429) {
            // User was ratelimited but process response
            return response.json();
        }
        if (response.status === 403) {
            // User is not logged in or CTF is paused.
            return response.json();
        }
        return response.json();
    }).then(function (response) {
        if (window.t !== undefined) {
            clearInterval(window.t);
            window.t = undefined;
        }
        if (response.success) response = response.data;
        else CTFd._functions.events.eventAlert({
            title: "Fail",
            html: response.message,
            button: "OK"
        });
        if (response.remaining_time != undefined) {
            $('#whale-challenge-user-access').html(response.user_access);
            $('#whale-challenge-lan-domain').html(response.lan_domain);
            $('#whale-challenge-count-down').text(response.remaining_time);
            $('#whale-panel-stopped').hide();
            $('#whale-panel-started').show();

            window.t = setInterval(() => {
                const c = $('#whale-challenge-count-down').text();
                if (!c) return;
                let second = parseInt(c) - 1;
                if (second <= 0) {
                    loadInfo();
                }
                $('#whale-challenge-count-down').text(second);
            }, 1000);
        } else {
            $('#whale-panel-started').hide();
            $('#whale-panel-stopped').show();
        }
    });
};

CTFd._internal.challenge.destroy = function () {
    var challenge_id = CTFd._internal.challenge.data.id;
    var url = "/api/v1/plugins/ctfd-whale/container?challenge_id=" + challenge_id;

    $('#whale-button-destroy').text("Waiting...");
    $('#whale-button-destroy').prop('disabled', true);

    var params = {};

    CTFd.fetch(url, {
        method: 'DELETE',
        credentials: 'same-origin',
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(params)
    }).then(function (response) {
        if (response.status === 429) {
            // User was ratelimited but process response
            return response.json();
        }
        if (response.status === 403) {
            // User is not logged in or CTF is paused.
            return response.json();
        }
        return response.json();
    }).then(function (response) {
        if (response.success) {
            loadInfo();
            CTFd._functions.events.eventAlert({
                title: "Success",
                html: "Your instance has been destroyed!",
                button: "OK"
            });
        } else {
            CTFd._functions.events.eventAlert({
                title: "Fail",
                html: response.message,
                button: "OK"
            });
        }
    }).finally(() => {
        $('#whale-button-destroy').text("Destroy this instance");
        $('#whale-button-destroy').prop('disabled', false);
    });
};

CTFd._internal.challenge.renew = function () {
    var challenge_id = CTFd._internal.challenge.data.id;
    var url = "/api/v1/plugins/ctfd-whale/container?challenge_id=" + challenge_id;

    $('#whale-button-renew').text("Waiting...");
    $('#whale-button-renew').prop('disabled', true);

    var params = {};

    CTFd.fetch(url, {
        method: 'PATCH',
        credentials: 'same-origin',
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(params)
    }).then(function (response) {
        if (response.status === 429) {
            // User was ratelimited but process response
            return response.json();
        }
        if (response.status === 403) {
            // User is not logged in or CTF is paused.
            return response.json();
        }
        return response.json();
    }).then(function (response) {
        if (response.success) {
            loadInfo();
            CTFd._functions.events.eventAlert({
                title: "Success",
                html: "Your instance has been renewed!",
                button: "OK"
            });
        } else {
            CTFd._functions.events.eventAlert({
                title: "Fail",
                html: response.message,
                button: "OK"
            });
        }
    }).finally(() => {
        $('#whale-button-renew').text("Renew this instance");
        $('#whale-button-renew').prop('disabled', false);
    });
};

CTFd._internal.challenge.boot = function () {
    var challenge_id = CTFd._internal.challenge.data.id;
    var url = "/api/v1/plugins/ctfd-whale/container?challenge_id=" + challenge_id;

    $('#whale-button-boot').text("Waiting...");
    $('#whale-button-boot').prop('disabled', true);

    var params = {};

    CTFd.fetch(url, {
        method: 'POST',
        credentials: 'same-origin',
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(params)
    }).then(function (response) {
        if (response.status === 429) {
            // User was ratelimited but process response
            return response.json();
        }
        if (response.status === 403) {
            // User is not logged in or CTF is paused.
            return response.json();
        }
        return response.json();
    }).then(function (response) {
        if (response.success) {
            loadInfo();
            CTFd._functions.events.eventAlert({
                title: "Success",
                html: "Your instance has been deployed!",
                button: "OK"
            });
        } else {
            CTFd._functions.events.eventAlert({
                title: "Fail",
                html: response.message,
                button: "OK"
            });
        }
    }).finally(() => {
        $('#whale-button-boot').text("Launch an instance");
        $('#whale-button-boot').prop('disabled', false);
    });
};


CTFd._internal.challenge.submit = function (preview) {
    var challenge_id = CTFd._internal.challenge.data.id;
    var submission = $('#challenge-input').val()

    var body = {
        'challenge_id': challenge_id,
        'submission': submission,
    }
    var params = {}
    if (preview)
        params['preview'] = true

    return CTFd.api.post_challenge_attempt(params, body).then(function (response) {
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
