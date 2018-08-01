var challenges = {};
window.challenge = new Object();

function load_chal_template(id, success_cb){
    $.get(script_root + "/admin/chal/" + id, function (obj) {
        $.getScript(script_root + obj.type_data.scripts.modal, function () {
            console.log('loaded renderer');
            $.get(script_root + obj.type_data.templates.update, function (template_data) {
                var template = nunjucks.compile(template_data);

                obj['nonce'] = $('#nonce').val();
                obj['script_root'] = script_root;

                $("#update-modals-entry-div").html(template.render(obj));

                $.ajax({
                    url: script_root + obj.type_data.scripts.update,
                    dataType: "script",
                    success: success_cb,
                    cache: false,
                });
            });
        });
    });
}

function load_challenge_preview(id){
    render_challenge_preview(id);
}

function render_challenge_preview(chal_id){
    var preview_window = $('#challenge-preview');
    $.get(script_root + "/admin/chal/" + chal_id, function(obj){
        $.getScript(script_root + obj.type_data.scripts.modal, function () {
            console.log('loaded renderer');

            $.get(script_root + obj.type_data.templates.modal, function (template_data) {
                var template = nunjucks.compile(template_data);

                window.challenge.data = obj;

                window.challenge.preRender()

                obj['description'] = window.challenge.render(obj['description']);
                obj['script_root'] = script_root;

                var challenge = template.render(obj);

                preview_window.html(challenge);

                $('#submit-key').click(function (e) {
                    e.preventDefault();
                    $('#submit-key').addClass("disabled-button");
                    $('#submit-key').prop('disabled', true);

                    window.challenge.submit(function (data) {
                        renderSubmissionResponse(data)
                    }, preview=true);
                });

                $("#answer-input").keyup(function (event) {
                    if (event.keyCode == 13) {
                        $("#submit-key").click();
                    }
                });

                window.challenge.postRender()

                preview_window.modal();
            });
        });
    });
}


function loadsolves(id) {
    $.get(script_root + '/admin/chal/' + id + '/solves', function (data) {
        var teams = data['teams'];
        var box = $('#challenge-solves-body');
        var modal = $('#challenge-solves-modal')
        box.empty();
        for (var i = 0; i < teams.length; i++) {
            var id = teams[i].id;
            var name = teams[i].name;
            var date = moment(teams[i].date).local().format('MMMM Do, h:mm:ss A');
            box.append('<tr><td><a href="team/{0}">{1}</td><td><small>{2}</small></td></tr>'.format(id, htmlentities(name), date));
        }
        modal.modal();
    });
}


function loadhint(hintid) {
    var md = window.markdownit({
        html: true,
    });
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
                        body: md.render(data.hint),
                        button: "Got it!"
                    });
                }
            });
        }
    });
}

function renderSubmissionResponse(data, cb) {
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

    if (cb) {
        cb(result);
    }
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

    $('.edit-challenge').click(function (e) {
        var id = $(this).attr('chal-id');
        load_chal_template(id, function () {
            openchal(id);
        });
    });

    $('.preview-challenge').click(function (e) {
        var chal_id = $(this).attr('chal-id');

        load_challenge_preview(chal_id);
    });

    $('.stats-challenge').click(function (e) {
        var chal_id = $(this).attr('chal-id');
        var title = $(this).attr('title') || $(this).attr('data-original-title');
        $('#challenge-solves-title').text(title);

        loadsolves(chal_id);
    });
});