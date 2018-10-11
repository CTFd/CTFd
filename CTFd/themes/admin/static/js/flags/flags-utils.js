function load_edit_key_modal(flag_id) {
    $.get(script_root + '/api/v1/flags/' + flag_id, function (flag_data) {
        $.get(script_root + flag_data.templates.update, function (template_data) {
            $('#edit-flags').empty();
            var template = nunjucks.compile(template_data);
            flag_data['script_root'] = script_root;
            flag_data['nonce'] = $('#nonce').val();
            $('#edit-flags').append(template.render(flag_data));
            $('#key-id').val(flag_id);
            $('#submit-keys').click(function (e) {
                e.preventDefault();
                updatekey()
            });
            $('#edit-flags').modal();
        });
    });
}


function create_key(challenge_id, chal_data) {
    fetch(script_root + '/api/v1/flags', {
        method: 'POST',
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(chal_data)
    }).then(function(response){
        loadkeys(challenge_id);
        $("#create-keys").modal('toggle');
    });
}

function loadkeys(challenge_id, cb){
    $.get(script_root + '/api/v1/challenges/' + challenge_id + '/flags', function(flags){
        $('#keys-chal').val(challenge_id);
        $('#current-keys').empty();
        $.get(script_root + "/themes/admin/static/js/templates/admin-flags-table.njk", function(data){
            var template = nunjucks.compile(data);
            var wrapper  = {
                flags: flags,
                script_root: script_root
            };
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
    var chal = $('#keys-chal').val();
    $('.current-key').each(function(){
        keys.push($(this).val());
    });
    $('#current-keys input[name*="key_type"]:checked').each(function(){
        vals.push($(this).val());
    });
    $.post(script_root + '/admin/keys/'+chal, {'keys':keys, 'vals':vals, 'nonce': $('#nonce').val()})
    loadchal(chal, true);
    $('#update-keys').modal('hide');
}


function deletekey(flag_id){
    $.delete(script_root + '/api/v1/flags/'+flag_id, function(data){
        if (data.success) {
            $('tr[name={0}]'.format(flag_id)).remove();
        }
    });
}

function updatekey(){
    var edit_key_modal = $('#edit-flags form').serializeArray();

    var flag_id = $('#key-id').val();
    var challenge_id = $("#update-keys").attr('chal-id');

    $.post(script_root + '/api/v1/flags/'+flag_id, edit_key_modal, function(data){
        if (data.success) {
            loadkeys(challenge_id);
            $('#edit-flags').modal('toggle');
        }
    });
}


$(document).ready(function () {
    $('.edit-flags').click(function (e) {
        var chal_id = $(this).attr('chal-id');
        loadkeys(chal_id, function () {
            $("#update-keys").attr('chal-id', chal_id);
            $('#update-keys').modal();
        });
    });


    $('#create-key').click(function (e) {
        $.get(script_root + '/api/v1/flags/types', function (data) {
            $("#create-keys-select").empty();
            var option = "<option> -- </option>";
            $("#create-keys-select").append(option);
            for (var key in data) {
                if (data.hasOwnProperty(key)){
                    var option = "<option value='{0}'>{1}</option>".format(key, data[key].name);
                    $("#create-keys-select").append(option);
                }
            }
            $("#create-keys-entry-div").empty();
            $("#create-keys-button-div").hide();
            $("#create-keys").modal();
        });
    });

    $('#create-keys-select').change(function () {
        var flag_type_name = $(this).find("option:selected").text();

        $.get(script_root + '/api/v1/flags/types/' + flag_type_name, function (key_data) {
            $.get(script_root + key_data.templates.create, function (template_data) {
                var template = nunjucks.compile(template_data);
                $("#create-keys-entry-div").html(template.render());
                $("#create-keys-button-div").show();
            });
        })
    });


    $('#create-keys-submit').click(function (e) {
        e.preventDefault();
        var challenge_data = {}
        $('#create-keys-entry-div :input').serializeArray()
            .map(function (x) {
                challenge_data[x.name] = x.value;
            });

        var challenge_id = $("#update-keys").attr('chal-id');
        challenge_data['challenge'] = challenge_id;

        var flag_type = $('#create-keys-select').val();
        challenge_data['type'] = flag_type;
        create_key(challenge_id, challenge_data);
    });
});