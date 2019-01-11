$(document).ready(function () {
    $('#team-info-form').submit(function (e) {
        e.preventDefault();
        var params = $('#team-info-form').serializeJSON(true);

        CTFd.fetch('/api/v1/teams/' + TEAM_ID, {
            method: 'PATCH',
            credentials: 'same-origin',
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(params)
        }).then(function (response) {
            return response.json();
        }).then(function (response) {
            if (response.success) {
                window.location.reload();
            } else {
                $('#team-info-form > #results').empty();
                Object.keys(response.errors).forEach(function (key, index) {
                    $('#team-info-form > #results').append(
                        ezbadge({
                            type: 'error',
                            body: response.errors[key]
                        })
                    );
                    var i = $('#team-info-form').find('input[name={0}]'.format(key));
                    var input = $(i);
                    input.addClass('input-filled-invalid');
                    input.removeClass('input-filled-valid');
                });
            }
        })
    });
});