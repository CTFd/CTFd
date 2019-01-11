$(document).ready(function () {
    $('#user-info-form').submit(function (e) {
        e.preventDefault();
        var params = $('#user-info-form').serializeJSON(true);

        CTFd.fetch('/api/v1/users', {
            method: 'POST',
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
                var user_id = response.data.id;
                window.location = script_root + '/admin/users/' + user_id;
            } else {
                $('#user-info-form > #results').empty();
                Object.keys(response.errors).forEach(function (key, index) {
                    $('#user-info-form > #results').append(
                        ezbadge({
                            type: 'error',
                            body: response.errors[key]
                        })
                    );
                    var i = $('#user-info-form').find('input[name={0}]'.format(key));
                    var input = $(i);
                    input.addClass('input-filled-invalid');
                    input.removeClass('input-filled-valid');
                });
            }
        });
    });
});