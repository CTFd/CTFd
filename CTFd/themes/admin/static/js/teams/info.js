$(document).ready(function () {
    $('#team-info-form').submit(function (e) {
        e.preventDefault();
        var params = $('#team-info-form').serializeJSON(true);

        fetch(script_root + '/api/v1/teams/' + TEAM_ID, {
            method: 'PATCH',
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
            }
        })
    });
});