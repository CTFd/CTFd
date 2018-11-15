$(document).ready(function () {
    $('#notifications_form').submit(function(e){
        e.preventDefault();
        var form = $('#notifications_form');
        var params = form.serializeJSON();

        fetch(script_root + '/api/v1/notifications', {
            method: 'POST',
            credentials: 'same-origin',
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(params)
        }).then(function (response) {
            return response.json();
        });
    });
});