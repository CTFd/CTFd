function upload_file(form, cb) {
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

function upload_logo(form) {
    upload_file(form, function(data){
        var upload = data[0];
        if (upload.location) {
            var params = {
                'value': upload.location
            };
            fetch(script_root + '/api/v1/configs/ctf_logo', {
                method: 'PATCH',
                headers: {
                    'Accept': 'application/json',
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(params)
            }).then(function (response) {
                return response.json();
            }).then(function (data) {
                if (data.id){
                    window.location.reload()
                } else {
                    ezal({
                        title: "Error!",
                        body: "Logo uploading failed!",
                        button: "Okay"
                    });
                }
            });
        }
    })
}