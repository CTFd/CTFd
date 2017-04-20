//http://stackoverflow.com/a/2648463 - wizardry!
String.prototype.format = String.prototype.f = function() {
    var s = this,
        i = arguments.length;

    while (i--) {
        s = s.replace(new RegExp('\\{' + i + '\\}', 'gm'), arguments[i]);
    }
    return s;
};

//http://stackoverflow.com/a/7616484
String.prototype.hashCode = function() {
    var hash = 0, i, chr, len;
    if (this.length == 0) return hash;
    for (i = 0, len = this.length; i < len; i++) {
        chr   = this.charCodeAt(i);
        hash  = ((hash << 5) - hash) + chr;
        hash |= 0; // Convert to 32bit integer
    }
    return hash;
};

function load_edit_key_modal(key_id, key_type_name) {
    $.get(script_root + '/static/admin/js/templates/keys/'+key_type_name+'/edit-'+key_type_name+'-modal.hbs', function(template_data){
        $.get(script_root + '/admin/keys/' + key_id, function(key_data){
            $('#edit-keys').empty();
            var template = Handlebars.compile(template_data);
            key_data['script_root'] = script_root;
            key_data['nonce'] = $('#nonce').val();
            $('#edit-keys').append(template(key_data));
            $('#key-id').val(key_id);
            $('#submit-keys').click(function (e) {
                e.preventDefault();
                updatekey()
            });
            $('#edit-keys').modal();
        });
    });
}

function load_chal_template(id, success_cb){
    obj = $.grep(challenges['game'], function (e) {
        return e.id == id;
    })[0]
    $.get(script_root + '/static/admin/js/templates/challenges/'+ obj['type_name'] +'/' + obj['type_name'] + '-challenge-update.hbs', function(template_data){
        var template = Handlebars.compile(template_data);
        $("#update-modals-entry-div").html(template({'nonce':$('#nonce').val(), 'script_root':script_root}));
        $.ajax({
          url: script_root + '/static/admin/js/templates/challenges/'+obj['type_name']+'/'+obj['type_name']+'-challenge-update.js',
          dataType: "script",
          success: success_cb,
          cache: true,
        });
    });
}

function loadchals(){
    $('#challenges').empty();
    $.post(script_root + "/admin/chals", {
        'nonce': $('#nonce').val()
    }, function (data) {
        categories = [];
        challenges = $.parseJSON(JSON.stringify(data));


        for (var i = challenges['game'].length - 1; i >= 0; i--) {
            if ($.inArray(challenges['game'][i].category, categories) == -1) {
                categories.push(challenges['game'][i].category)
                $('#challenges').append($('<tr id="' + challenges['game'][i].category.replace(/ /g,"-").hashCode() + '"><td class="col-md-1"><h3>' + challenges['game'][i].category + '</h3></td></tr>'))
            }
        };

        for (var i = 0; i <= challenges['game'].length - 1; i++) {
            var chal = challenges['game'][i]
            var chal_button = $('<button class="chal-button col-md-2 theme-background" value="{0}"><h5>{1}</h5><p class="chal-points">{2}</p><span class="chal-percent">{3}% solved</span></button>'.format(chal.id, chal.name, chal.value, Math.round(chal.percentage_solved * 100)));
            $('#' + challenges['game'][i].category.replace(/ /g,"-").hashCode()).append(chal_button);
        };

        $('#challenges button').click(function (e) {
            id = this.value
            load_chal_template(id, function(){
                openchal(id);
            });
        });

        // $('.create-challenge').click(function (e) {
        //     $('#new-chal-category').val($($(this).siblings()[0]).text().trim());
        //     $('#new-chal-title').text($($(this).siblings()[0]).text().trim());
        //     $('#new-challenge').modal();
        // });

    });
}

$(function(){
    loadchals();
})
