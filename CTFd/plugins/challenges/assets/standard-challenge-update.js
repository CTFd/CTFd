$('#submit-key').click(function (e) {
    submitkey($('#chalid').val(), $('#answer').val())
});

$('#submit-keys').click(function (e) {
    e.preventDefault();
    $('#update-keys').modal('hide');
});

$('#limit_max_attempts').change(function() {
    if(this.checked) {
        $('#chal-attempts-group').show();
    } else {
        $('#chal-attempts-group').hide();
        $('#chal-attempts-input').val('');
    }
});

// Markdown Preview
$('#desc-edit').on('shown.bs.tab', function (event) {
    if (event.target.hash == '#desc-preview') {
        var editor_value = $('#desc-editor').val();
        $(event.target.hash).html(
            window.challenge.render(editor_value)
        );
    }
});
$('#new-desc-edit').on('shown.bs.tab', function (event) {
    if (event.target.hash == '#new-desc-preview') {
        var editor_value = $('#new-desc-editor').val();
        $(event.target.hash).html(
            window.challenge.render(editor_value)
        );
    }
});

function updateChallenge(){
    var params = {};
    var form = $("#update-modals-entry-div form");
    var values = form.serializeArray();
    values = values.concat(
        form.find('input[type=checkbox]:checked').map(
        function () {
            return {"name": this.name, "value": true}
        }).get()
    );
    values.map(function (x) {
        params[x.name] = x.value || null;
    });
    var challenge_id = form.find('.chal-id').val();
    console.log(params);
    fetch(script_root + '/api/v1/challenges/' + challenge_id, {
        method: 'PATCH',
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(params)
    }).then(function (response) {
        $('#update-challenge').modal('toggle');
    });
}

function loadchal(id, update) {
    $.get(script_root + '/api/v1/challenges/' + id, function(obj){
        $('#desc-write-link').click(); // Switch to Write tab
        if (typeof update === 'undefined')
            $('#update-challenge').modal();
    });
}

function openchal(id){
    loadchal(id);
}

$(document).ready(function(){
    $('[data-toggle="tooltip"]').tooltip();
    $("#update-modals-entry-div form").submit(function(e){
        e.preventDefault();
        updateChallenge();
    });
});
