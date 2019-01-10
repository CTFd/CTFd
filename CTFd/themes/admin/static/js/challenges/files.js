$(document).ready(function () {
    $('#file-add-form').submit(function (e) {
        e.preventDefault();
        var formData = new FormData(e.target);
        formData.append('nonce', csrf_nonce);
        formData.append('challenge', CHALLENGE_ID);
        formData.append('type', 'challenge');
        $.ajax({
            url: script_root + '/api/v1/files',
            data: formData,
            type: 'POST',
            cache: false,
            contentType: false,
            processData: false,
            success: function (data) {
                // TODO: Refresh files on submit
                e.target.reset();
                window.location.reload();
            }
        });
    });

    $('.delete-file').click(function(e){
        var file_id = $(this).attr('file-id');
        var row = $(this).parent().parent();
        ezq({
            title: "Delete Files",
            body: "Are you sure you want to delete this file?",
            success: function () {
                CTFd.fetch('/api/v1/files/' + file_id, {
                    method: 'DELETE',
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