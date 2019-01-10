$(document).ready(function () {
    $('.delete-page').click(function () {
        var elem = $(this);
        var name = elem.attr("page-route");
        var page_id = elem.attr("page-id");
        ezq({
            title: 'Delete ' + name,
            body: "Are you sure you want to delete {0}?".format(
                "<strong>" + htmlentities(name) + "</strong>"
            ),
            success: function () {
                CTFd.fetch('/api/v1/pages/' + page_id, {
                    method: 'DELETE',
                }).then(function (response) {
                    return response.json();
                }).then(function (response) {
                    if (response.success) {
                        elem.parent().parent().remove();
                    }
                });
            }
        });
    });
});