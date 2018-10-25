$(document).ready(function () {
    $('#announcements_form').submit(function(e){
        e.preventDefault();
        var form = $('#announcements_form');
        var params = form.serializeJSON();

        fetch(script_root + '/api/v1/announcements', {
            method: 'POST',
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