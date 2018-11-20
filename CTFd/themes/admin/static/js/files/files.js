function upload_files(form, cb) {
    if (form instanceof jQuery) {
        form = form[0];
    }
    var formData = new FormData(form);
    formData.append('nonce', csrf_nonce);
    $.ajax({
        url: script_root + '/api/v1/files',
        data: formData,
        type: 'POST',
        cache: false,
        contentType: false,
        processData: false,
        success: function (data) {
            if (cb) {
                cb(data);
            }
        }
    });
}
