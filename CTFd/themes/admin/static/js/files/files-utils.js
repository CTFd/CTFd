function updatefiles(){
    var chal = $('#files-chal').val();
    var form = $('#update-files form')[0];
    var formData = new FormData(form);
    $.ajax({
        url: script_root + '/admin/files/'+chal,
        data: formData,
        type: 'POST',
        cache: false,
        contentType: false,
        processData: false,
        success: function(data){
            form.reset();
            loadfiles(chal);
        }
    });
}

function loadfiles(chal, cb){
    $('#update-files form').attr('action', script_root+'/admin/files/'+chal)
    $.get(script_root + '/api/v1/challenges/'+chal+'/files', function(data){
        $('#files-chal').val(chal);
        $('#current-files').empty();
        for(var x = 0; x < data.length; x++){
            var filename = data[x].location.split('/');
            var filename = filename[filename.length - 1];

            var curr_file = '<div class="col-md-12"><a href="{2}/files/{3}">{4}</a> <i class="btn-fa fas fa-times float-right" onclick="deletefile({1}, this)" value="{2}" ></i></div>'.format(
                chal,
                data[x].id,
                script_root,
                data[x].file,
                filename
            );

            $('#current-files').append(curr_file);
        }

        if (cb){
            cb();
        }
    });
}

function deletefile(file_id, elem){
    $.delete(script_root + '/api/v1/files/'+file_id, {}, function (data){
        if (data.success) {
            $(elem).parent().remove();
        }
    });
}


$(document).ready(function () {
    $('.edit-files').click(function (e) {
        var chal_id = $(this).attr('chal-id');
        loadfiles(chal_id, function () {
            $('#update-files').modal();
        });
    });


    $('#submit-files').click(function (e) {
        e.preventDefault();
        updatefiles()
    });
});