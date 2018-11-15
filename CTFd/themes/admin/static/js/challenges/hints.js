$(document).ready(function () {
    $('#hint-add-button').click(function (e) {
        $('#hint-edit-modal form').find("input, textarea").val("");
        $('#hint-edit-modal').modal();
    });

    $('.delete-hint').click(function(e){
        e.preventDefault();
        var hint_id = $(this).attr('hint-id');
        var row = $(this).parent().parent();
        ezq({
            title: "Delete Hint",
            body: "Are you sure you want to delete this hint?",
            success: function () {
                var route = script_root + '/api/v1/hints/' + hint_id;
                $.delete(route, {}, function (data) {
                    if (data.success) {
                        row.remove();
                    }
                });
            }
        });
    });

    $('.edit-hint').click(function (e) {
        e.preventDefault();
        var hint_id = $(this).attr('hint-id');

        fetch(script_root + '/api/v1/hints/' + hint_id, {
            method: 'GET',
            credentials: 'same-origin',
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            }
        }).then(function (response) {
            return response.json()
        }).then(function (response) {
            if (response.success) {
                $('#hint-edit-form input[name=content],textarea[name=content]').val(response.data.content);
                $('#hint-edit-form input[name=cost]').val(response.data.cost);
                $('#hint-edit-form input[name=id]').val(response.data.id);

                $('#hint-edit-modal').modal();
            }
        });
    });

    $('#hint-edit-form').submit(function (e) {
        e.preventDefault();
        var params = $(this).serializeJSON(true);
        params['challenge'] = CHALLENGE_ID;

        var method = 'POST';
        var url = '/api/v1/hints';
        if (params.id){
            method = 'PATCH';
            url = '/api/v1/hints/' + params.id;
        }
        fetch(script_root + url, {
            method: method,
            credentials: 'same-origin',
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(params)
        }).then(function (response) {
            return response.json()
        }).then(function(response) {
            if (response.success){
                // TODO: Refresh hints on submit.
                window.location.reload();
            }
        });
    });
});