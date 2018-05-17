function load_edit_key_modal(key_id, key_type_name) {
    $.get(script_root + '/admin/keys/' + key_id, function (key_data) {
        $.get(script_root + key_data.templates.update, function (template_data) {
            $('#edit-keys').empty();
            var template = nunjucks.compile(template_data);
            key_data['script_root'] = script_root;
            key_data['nonce'] = $('#nonce').val();
            $('#edit-keys').append(template.render(key_data));
            $('#key-id').val(key_id);
            $('#submit-keys').click(function (e) {
                e.preventDefault();
                updatekey()
            });
            $('#edit-keys').modal();
        });
    });
}


function create_key(chal, chal_data) {
    chal_data.push({name: 'nonce', value: $('#nonce').val()});
    $.post(script_root + "/admin/keys", chal_data, function (data) {
        if (data == "1"){
            loadkeys(chal);
            $("#create-keys").modal('toggle');
        }
    });
}

function loadkeys(chal, cb){
    $.get(script_root + '/admin/chal/' + chal + '/keys', function(data){
        $('#keys-chal').val(chal);
        var keys = $.parseJSON(JSON.stringify(data));
        keys = keys['keys'];
        $('#current-keys').empty();
        $.get(script_root + "/themes/admin/static/js/templates/admin-keys-table.njk", function(data){
            var template = nunjucks.compile(data);
            var wrapper  = {keys: keys, script_root: script_root};
            $('#current-keys').append(template.render(wrapper));
            if (cb) {
                cb();
            }
        });
    });
}

function updatekeys(){
    var keys = [];
    var vals = [];
    var chal = $('#keys-chal').val()
    $('.current-key').each(function(){
        keys.push($(this).val());
    });
    $('#current-keys input[name*="key_type"]:checked').each(function(){
        vals.push($(this).val());
    })
    $.post(script_root + '/admin/keys/'+chal, {'keys':keys, 'vals':vals, 'nonce': $('#nonce').val()})
    loadchal(chal, true)
    $('#update-keys').modal('hide');
}


function deletekey(key_id){
    $.post(script_root + '/admin/keys/'+key_id+'/delete', {'nonce': $('#nonce').val()}, function(data){
        if (data == "1") {
            $('tr[name={0}]'.format(key_id)).remove();
        }
    });
}

function updatekey(){
    var edit_key_modal = $('#edit-keys form').serializeArray();

    var key_id = $('#key-id').val();
    var chal = $("#update-keys").attr('chal-id');

    $.post(script_root + '/admin/keys/'+key_id, edit_key_modal, function(data){
        if (data == "1") {
            loadkeys(chal);
            $('#edit-keys').modal('toggle');
        }
    });
}


$(document).ready(function () {
    $('.edit-keys').click(function (e) {
        var chal_id = $(this).attr('chal-id');
        loadkeys(chal_id, function () {
            $("#update-keys").attr('chal-id', chal_id);
            $('#update-keys').modal();
        });
    });


    $('#create-key').click(function (e) {
        $.get(script_root + '/admin/key_types', function (data) {
            $("#create-keys-select").empty();
            var option = "<option> -- </option>";
            $("#create-keys-select").append(option);
            for (var key in data) {
                var option = "<option value='{0}'>{1}</option>".format(key, data[key]);
                $("#create-keys-select").append(option);
            }
            $("#create-keys-entry-div").empty();
            $("#create-keys-button-div").hide();
            $("#create-keys").modal();
        });
    });

    $('#create-keys-select').change(function () {
        var key_type_name = $(this).find("option:selected").text();

        $.get(script_root + '/admin/key_types/' + key_type_name, function (key_data) {
            $.get(script_root + key_data.templates.create, function (template_data) {
                var template = nunjucks.compile(template_data);
                $("#create-keys-entry-div").html(template.render());
                $("#create-keys-button-div").show();
            });
        })
    });


    $('#create-keys-submit').click(function (e) {
        e.preventDefault();
        var chal_data = $('#create-keys-entry-div :input').serializeArray();

        var chalid = $("#update-keys").attr('chal-id');
        chal_data.push({name: 'chal', value: chalid});

        var key_type = $('#create-keys-select').val();
        chal_data.push({name: 'key_type', value: key_type});
        create_key(chalid, chal_data);
    });
});