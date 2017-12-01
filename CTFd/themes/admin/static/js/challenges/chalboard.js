var challenges = {};


function load_chal_template(id, success_cb){
    var obj = $.grep(challenges['game'], function (e) {
        return e.id == id;
    })[0];
    $.get(script_root + obj.type_data.templates.update, function(template_data){
        var template = nunjucks.compile(template_data);
        $("#update-modals-entry-div").html(template.render({'nonce':$('#nonce').val(), 'script_root':script_root}));
        $.ajax({
          url: script_root + obj.type_data.scripts.update,
          dataType: "script",
          success: success_cb,
          cache: false,
        });
    });
}

function loadchals(cb){
    $.post(script_root + "/admin/chals", {
        'nonce': $('#nonce').val()
    }, function (data) {
        var categories = [];
        challenges = $.parseJSON(JSON.stringify(data));


        for (var i = challenges['game'].length - 1; i >= 0; i--) {
            if ($.inArray(challenges['game'][i].category, categories) == -1) {
                categories.push(challenges['game'][i].category)
            }
        }

        if (cb) {
            cb();
        }
    });
}


$('.delete-challenge').click(function (e) {
    var chal_id = $(this).attr('chal-id');

    ezq({
        title: "Delete Challenge",
        body: "Are you sure you want to delete this challenge?",
        success: function(){
            $.post(script_root + '/admin/chal/delete', {'id': chal_id, 'nonce': $('#nonce').val()}, function (data) {
                if (data == 1) {
                    location.reload();
                }
                else {
                    ezal({
                        title: "Error",
                        body: "There was an error"
                    });
                }
            });
        }
    });
});


loadchals(function(){
    $('.edit-challenge').click(function (e) {
        var id = $(this).attr('chal-id');
        load_chal_template(id, function () {
            openchal(id);
        });
    });
});

