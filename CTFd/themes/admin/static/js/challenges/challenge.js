$(document).ready(function () {
    $('#challenge-update-container > form').submit(function(e){
        e.preventDefault();
        var params = $(e.target).serializeJSON(true);
        console.log(params);


        fetch(script_root + '/api/v1/challenges/' + CHALLENGE_ID, {
            method: 'PATCH',
            credentials: 'same-origin',
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(params)
        }).then(function (response) {
            return response.json();
        }).then(function (data) {
            if (data.success) {
                ezal({
                    title: "Success",
                    body: "Your challenge has been updated!",
                    button: "OK"
                });
            }
        });
    });

    if (window.location.hash) {
        let hash = window.location.hash.replace("<>[]'\"", "");
        $('nav a[href="' + hash + '"]').tab('show');
    }

    $('.nav-tabs a').click(function (e) {
        $(this).tab('show');
        window.location.hash = this.hash;
    });
});