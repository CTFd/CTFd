$(document).ready(function () {
    $('#user-info-form').submit(function (e) {
        e.preventDefault();
        var params = $('#user-info-form').serializeJSON(true);

        fetch(script_root + '/api/v1/users', {
            method: 'POST',
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(params)
        }).then(function (response) {
            return response.json();
        }).then(function (response) {
            if (response.success) {
                var user_id = response.data.id;
                window.location = script_root + '/admin/users/' + user_id;
            }
        });
    });
});