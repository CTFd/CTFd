// TODO: Replace this with CTFd JS library
$(document).ready(function () {
    $('.delete-correct-submission').click(function () {
        var elem = $(this).parent().parent();
        var chal = elem.find('.chal').attr('id');
        var chal_name = elem.find('.chal').text().trim();
        var team = elem.find('.team').attr('id');
        var team_name = elem.find('.team').text().trim();
        var key_id = elem.find('.flag').attr('id');

        var td_row = $(this).parent().parent();

        ezq({
            title: 'Delete Submission',
            body: "Are you sure you want to delete correct submission from {0} for challenge {1}".format(
                "<strong>" + htmlentities(team_name) + "</strong>",
                "<strong>" + htmlentities(chal_name) + "</strong>"
            ),
            success: function () {
                CTFd.fetch('/api/v1/submissions/' + key_id, {
                    method: 'DELETE',
                }).then(function (response) {
                    return response.json();
                }).then(function (response) {
                    if (response.success) {
                        td_row.remove();
                    }
                });
            }
        });
    });
});