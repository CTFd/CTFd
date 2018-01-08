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


function get_challenge(id){
    var obj = $.grep(challenges['game'], function (e) {
        return e.id == id;
    })[0];
    return obj;
}


function load_challenge_preview(id){
    loadchal(id, function(){
        var chal = get_challenge(id);
        var modal_template = chal.type_data.templates.modal;
        var modal_script = chal.type_data.scripts.modal;

        render_challenge_preview(chal, modal_template, modal_script);
    });
}

function render_challenge_preview(chal, modal_template, modal_script){
    var preview_window = $('#challenge-preview');
    $.get(script_root + modal_template, function (template_data) {
        preview_window.empty();
        var template = nunjucks.compile(template_data);
        var data = {
            id: chal.id,
            name: chal.name,
            value: chal.value,
            tags: chal.tags,
            desc: chal.description,
            files: chal.files,
            hints: chal.hints,
            script_root: script_root
        };

        var challenge = template.render(data);

        preview_window.append(challenge);

        $.getScript(script_root + modal_script, function () {
            preview_window.modal();
        });
    });
}


function loadchal(chalid, cb){
    $.get(script_root + "/admin/chal/"+chalid, {
    }, function (data) {
        var categories = [];
        var challenge = $.parseJSON(JSON.stringify(data));

        for (var i = challenges['game'].length - 1; i >= 0; i--) {
            if (challenges['game'][i]['id'] == challenge.id) {
                challenges['game'][i] = challenge
            }
        }

        if (cb) {
            cb();
        }
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

loadchals(function(){
    $('.edit-challenge').click(function (e) {
        var id = $(this).attr('chal-id');
        load_chal_template(id, function () {
            openchal(id);
        });
    });
});

function loadhint(hintid) {
    ezq({
        title: "Unlock Hint?",
        body: "Are you sure you want to open this hint?",
        success: function () {
            $.post(script_root + "/hints/" + hintid, {'nonce': $('#nonce').val()}, function (data) {
                if (data.errors) {
                    ezal({
                        title: "Error!",
                        body: data.errors,
                        button: "Okay"
                    });
                } else {
                    ezal({
                        title: "Hint",
                        body: marked(data.hint, {'gfm': true, 'breaks': true}),
                        button: "Got it!"
                    });
                }
            });
        }
    });
}

function submitkey(chal, key, nonce){
    $.post(script_root + "/admin/chal/" + chal, {
        key: key,
        nonce: nonce
    }, function (data) {
        console.log(data);
        var result = $.parseJSON(JSON.stringify(data));

        var result_message = $('#result-message');
        var result_notification = $('#result-notification');
        var answer_input = $("#answer-input");
        result_notification.removeClass();
        result_message.text(result.message);

        if (result.status == -1) {
            window.location = script_root + "/login?next=" + script_root + window.location.pathname + window.location.hash
            return
        }
        else if (result.status == 0) { // Incorrect key
            result_notification.addClass('alert alert-danger alert-dismissable text-center');
            result_notification.slideDown();

            answer_input.removeClass("correct");
            answer_input.addClass("wrong");
            setTimeout(function () {
                answer_input.removeClass("wrong");
            }, 3000);
        }
        else if (result.status == 1) { // Challenge Solved
            result_notification.addClass('alert alert-success alert-dismissable text-center');
            result_notification.slideDown();

            answer_input.val("");
            answer_input.removeClass("wrong");
            answer_input.addClass("correct");
        }
        else if (result.status == 2) { // Challenge already solved
            result_notification.addClass('alert alert-info alert-dismissable text-center');
            result_notification.slideDown();

            answer_input.addClass("correct");
        }
        else if (result.status == 3) { // Keys per minute too high
            result_notification.addClass('alert alert-warning alert-dismissable text-center');
            result_notification.slideDown();

            answer_input.addClass("too-fast");
            setTimeout(function () {
                answer_input.removeClass("too-fast");
            }, 3000);
        }

        setTimeout(function () {
            $('.alert').slideUp();
            $('#submit-key').removeClass("disabled-button");
            $('#submit-key').prop('disabled', false);
        }, 3000);
    });
}

$(document).ready(function () {
    $('.delete-challenge').click(function (e) {
        var chal_id = $(this).attr('chal-id');
        var td_row = $(this).parent().parent();

        ezq({
            title: "Delete Challenge",
            body: "Are you sure you want to delete this challenge?",
            success: function () {
                $.post(script_root + '/admin/chal/delete', {
                    'id': chal_id,
                    'nonce': $('#nonce').val()
                }, function (data) {
                    if (data == 1) {
                        td_row.remove();
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

    $('.preview-challenge').click(function (e) {
        var chal_id = $(this).attr('chal-id');

        load_challenge_preview(chal_id);
    });
});