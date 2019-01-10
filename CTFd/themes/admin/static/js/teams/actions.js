$(document).ready(function () {
    $('.edit-team').click(function (e) {
        $('#team-info-modal').modal('toggle');
    });

    $('.delete-team').click(function (e) {
        ezq({
            title: "Delete Team",
            body: "Are you sure you want to delete {0}".format("<strong>" + htmlentities(TEAM_NAME) + "</strong>"),
            success: function () {
                CTFd.fetch('/api/v1/teams/' + TEAM_ID, {
                    method: 'DELETE',
                }).then(function (response) {
                    return response.json();
                }).then(function (response) {
                    if (response.success) {
                        window.location = script_root + '/admin/teams';
                    }
                });
            }
        });
    });

    $('.delete-submission').click(function (e) {
        e.preventDefault();
        var submission_id = $(this).attr('submission-id');
        var submission_type = $(this).attr('submission-type');
        var submission_challenge = $(this).attr('submission-challenge');

        var body = "<span>Are you sure you want to delete <strong>{0}</strong> submission from <strong>{1}</strong> for <strong>{2}</strong>?</span>".format(
            htmlentities(submission_type),
            htmlentities(TEAM_NAME),
            htmlentities(submission_challenge)
        );

        var row = $(this).parent().parent();

        ezq({
            title: "Delete Submission",
            body: body,
            success: function () {
                CTFd.fetch('/api/v1/submissions/' + submission_id, {
                    method: 'DELETE',
                    credentials: 'same-origin',
                    headers: {
                        'Accept': 'application/json',
                        'Content-Type': 'application/json'
                    }
                }).then(function (response) {
                    return response.json();
                }).then(function (response) {
                    if (response.success) {
                        row.remove();
                    }
                });
            }
        });
    });

    $('.delete-award').click(function (e) {
        e.preventDefault();
        var award_id = $(this).attr('award-id');
        var award_name = $(this).attr('award-name');

        var body = "<span>Are you sure you want to delete the <strong>{0}</strong> award from <strong>{1}</strong>?".format(
            htmlentities(award_name),
            htmlentities(TEAM_NAME)
        );

        var row = $(this).parent().parent();

        ezq({
            title: "Delete Award",
            body: body,
            success: function () {
                CTFd.fetch('/api/v1/awards/' + award_id, {
                    method: 'DELETE',
                    credentials: 'same-origin',
                    headers: {
                        'Accept': 'application/json',
                        'Content-Type': 'application/json'
                    }
                }).then(function (response) {
                    return response.json();
                }).then(function (response) {
                    if (response.success) {
                        row.remove();
                    }
                });
            }
        });
    });
});