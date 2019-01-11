function renderSubmissionResponse(response, cb) {
    var result = response.data;

    var result_message = $('#result-message');
    var result_notification = $('#result-notification');
    var answer_input = $("#submission-input");
    result_notification.removeClass();
    result_message.text(result.message);

    if (result.status === "authentication_required") {
        window.location = script_root + "/login?next=" + script_root + window.location.pathname + window.location.hash;
        return
    }
    else if (result.status === "incorrect") { // Incorrect key
        result_notification.addClass('alert alert-danger alert-dismissable text-center');
        result_notification.slideDown();

        answer_input.removeClass("correct");
        answer_input.addClass("wrong");
        setTimeout(function () {
            answer_input.removeClass("wrong");
        }, 3000);
    }
    else if (result.status === "correct") { // Challenge Solved
        result_notification.addClass('alert alert-success alert-dismissable text-center');
        result_notification.slideDown();

        $('.challenge-solves').text((parseInt($('.challenge-solves').text().split(" ")[0]) + 1 + " Solves"));

        answer_input.val("");
        answer_input.removeClass("wrong");
        answer_input.addClass("correct");
    }
    else if (result.status === "already_solved") { // Challenge already solved
        result_notification.addClass('alert alert-info alert-dismissable text-center');
        result_notification.slideDown();

        answer_input.addClass("correct");
    }
    else if (result.status === "paused") { // CTF is paused
        result_notification.addClass('alert alert-warning alert-dismissable text-center');
        result_notification.slideDown();
    }
    else if (result.status === "ratelimited") { // Keys per minute too high
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
    $('.preview-challenge').click(function (e) {
        window.challenge = new Object();
        $.get(script_root + "/api/v1/challenges/" + CHALLENGE_ID, function (response) {
            var challenge_data = response.data;
            challenge_data['solves'] = null;

            $.getScript(script_root + challenge_data.type_data.scripts.view, function () {
                $.get(script_root + challenge_data.type_data.templates.view, function (template_data) {

                    $('#challenge-window').empty();
                    var template = nunjucks.compile(template_data);
                    window.challenge.data = challenge_data;
                    window.challenge.preRender();

                    challenge_data['description'] = window.challenge.render(challenge_data['description']);
                    challenge_data['script_root'] = script_root;

                    $('#challenge-window').append(template.render(challenge_data));

                    $('.challenge-solves').click(function (e) {
                        getsolves($('#challenge-id').val())
                    });
                    $('.nav-tabs a').click(function (e) {
                        e.preventDefault();
                        $(this).tab('show')
                    });

                    // Handle modal toggling
                    $('#challenge-window').on('hide.bs.modal', function (event) {
                        $("#submission-input").removeClass("wrong");
                        $("#submission-input").removeClass("correct");
                        $("#incorrect-key").slideUp();
                        $("#correct-key").slideUp();
                        $("#already-solved").slideUp();
                        $("#too-fast").slideUp();
                    });

                    $('#submit-key').click(function (e) {
                        e.preventDefault();
                        $('#submit-key').addClass("disabled-button");
                        $('#submit-key').prop('disabled', true);
                        window.challenge.submit(function (data) {
                            renderSubmissionResponse(data)
                        }, true);
                        // Preview passed as true
                    });

                    $("#submission-input").keyup(function (event) {
                        if (event.keyCode == 13) {
                            $("#submit-key").click();
                        }
                    });

                    $(".input-field").bind({
                        focus: function () {
                            $(this).parent().addClass('input--filled');
                            $label = $(this).siblings(".input-label");
                        },
                        blur: function () {
                            if ($(this).val() === '') {
                                $(this).parent().removeClass('input--filled');
                                $label = $(this).siblings(".input-label");
                                $label.removeClass('input--hide');
                            }
                        }
                    });

                    window.challenge.postRender();
                    window.location.replace(window.location.href.split('#')[0] + '#preview');

                    $('#challenge-window').modal();
                });
            });
        });
    });

    $('.delete-challenge').click(function(e){
        ezq({
            title: "Delete Challenge",
            body: "Are you sure you want to delete {0}".format("<strong>" + htmlentities(CHALLENGE_NAME) + "</strong>"),
            success: function () {
                CTFd.fetch('/api/v1/challenges/' + CHALLENGE_ID, {
                    method: 'DELETE',
                }).then(function (response) {
                    return response.json();
                }).then(function (response) {
                    if (response.success) {
                        window.location = script_root + '/admin/challenges';
                    }
                });
            }
        });
    });

    $('#challenge-update-container > form').submit(function(e){
        e.preventDefault();
        var params = $(e.target).serializeJSON(true);
        console.log(params);


        CTFd.fetch('/api/v1/challenges/' + CHALLENGE_ID, {
            method: 'PATCH',
            credentials: 'same-origin',
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(params)
        }).then(function (response) {
            return response.json();
        }).then(function (data) {
            if (data.success) {
                ezal({
                    title: "Success",
                    body: "Your challenge has been updated!",
                    button: "OK"
                });
            }
        });
    });

    if (window.location.hash) {
        let hash = window.location.hash.replace("<>[]'\"", "");
        $('nav a[href="' + hash + '"]').tab('show');
    }

    $('.nav-tabs a').click(function (e) {
        $(this).tab('show');
        window.location.hash = this.hash;
    });
});