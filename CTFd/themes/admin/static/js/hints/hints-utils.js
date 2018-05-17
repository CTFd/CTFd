function load_hint_modal(method, hintid){
    $('#hint-modal-hint').val('');
    $('#hint-modal-cost').val('');
    if (method == 'create'){
        $('#hint-modal-submit').attr('action', '/admin/hints');
        $('#hint-modal-title').text('Create Hint');
        $("#hint-modal").modal();
    } else if (method == 'update'){
        $.get(script_root + '/admin/hints/' + hintid, function(data){
            $('#hint-modal-submit').attr('action', '/admin/hints/' + hintid);
            $('#hint-modal-hint').val(data.hint);
            $('#hint-modal-cost').val(data.cost);
            $('#hint-modal-title').text('Update Hint');
            $("#hint-modal-button").text('Update Hint');
            $("#hint-modal").modal();
        });
    }
}

function edithint(hintid){
    $.get(script_root + '/admin/hints/' + hintid, function(data){
        console.log(data);
    })
}


function deletehint(hintid){
    $.delete(script_root + '/admin/hints/' + hintid, function(data, textStatus, jqXHR){
        if (jqXHR.status == 204){
            var chalid = $("#update-hints").attr('chal-id');
            loadhints(chalid);
        }
    });
}


function loadhints(chal, cb){
    $.get(script_root + '/admin/chal/{0}/hints'.format(chal), function(data){
        var table = $('#hintsboard > tbody');
        table.empty();
        for (var i = 0; i < data.hints.length; i++) {
            var hint = data.hints[i]
            var hint_row = "<tr>" +
            "<td class='hint-entry d-table-cell w-75'><pre>{0}</pre></td>".format(htmlentities(hint.hint)) +
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
        var params = {};
        $(this).serializeArray().map(function (x) {
            params[x.name] = x.value;
        });
        $.post(script_root + $(this).attr('action'), params, function (data) {
            loadhints(params['chal']);
        });
        $("#hint-modal").modal('hide');
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