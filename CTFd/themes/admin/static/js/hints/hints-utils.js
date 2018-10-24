function load_hint_modal(method, hintid){
    $('#hint-modal-hint').val('');
    $('#hint-modal-cost').val('');
    if (method == 'create'){
        $('#hint-modal-title').text('Create Hint');
        $('#hint-id-for-hint').removeAttr('value');
        $("#hint-modal").modal();
    } else if (method == 'update'){
        $.get(script_root + '/api/v1/hints/' + hintid, function(data){
            $('#hint-modal-submit').attr('action', '/admin/hints/' + hintid);
            $('#hint-id-for-hint').val(data.id);
            $('#hint-modal-hint').val(data.content);
            $('#hint-modal-cost').val(data.cost);
            $('#hint-modal-title').text('Update Hint');
            $("#hint-modal-button").text('Update Hint');
            $("#hint-modal").modal();
        });
    }
}

function deletehint(hint_id){
    $.delete(script_root + '/api/v1/hints/' + hint_id, function(response){
        var data = response.data;
        if (data.success){
            var chalid = $("#update-hints").attr('chal-id');
            loadhints(chalid);
        }
    });
}


function loadhints(challenge_id, cb){
    $.get(script_root + '/api/v1/challenges/{0}/hints'.format(challenge_id), function(response){
        var data = response.data;
        var table = $('#hintsboard > tbody');
        table.empty();
        for (var i = 0; i < data.length; i++) {
            var hint = data[i];
            var hint_row = "<tr>" +
            "<td class='hint-entry d-table-cell w-75'><pre>{0}</pre></td>".format(htmlentities(hint.content)) +
            "<td class='hint-cost d-table-cell text-center'>{0}</td>".format(hint.cost) +
            "<td class='hint-settings d-table-cell text-center'><span>" +
                "<i role='button' class='btn-fa fas fa-edit' onclick=javascript:load_hint_modal('update',{0})></i>".format(hint.id)+
                "<i role='button' class='btn-fa fas fa-times' onclick=javascript:deletehint({0})></i>".format(hint.id)+
                "</span></td>" +
            "</tr>";
            table.append(hint_row);
        }
        if (cb) {
            cb();
        }
    });
}

$(document).ready(function () {
    $('.edit-hints').click(function (e) {
        var chal_id = $(this).attr('chal-id');
        loadhints(chal_id, function () {
            $("#chal-id-for-hint").val(chal_id);  // Preload the challenge ID so the form submits properly. Remove in later iterations
            $("#update-hints").attr('chal-id', chal_id);
            $('#update-hints').modal();
        });
    });


    $('#create-hint').click(function (e) {
        e.preventDefault();
        load_hint_modal('create');
    });


    $('#hint-modal-submit').submit(function (e) {
        e.preventDefault();
        var params = $(this).serializeJSON();
        var target = '/api/v1/hints';
        var method = 'POST';
        if (params.id){
            target += '/' + params.id;
            method = 'PATCH';
        }
        fetch(script_root + target, {
            method: method,
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(params)
        }).then(function (response) {
            loadhints(params['challenge']);
            $("#hint-modal").modal('hide');
        });
    });


    $('a[data-toggle="tab"]').on('shown.bs.tab', function (e) {
        var md = window.markdownit({
            html: true,
        });
        var target = $(e.target).attr("href");
        if (target == '#hint-preview') {
            var obj = $('#hint-modal-hint');
            var data = md.render(obj.val());
            $('#hint-preview').html(data);
        }
    });

});