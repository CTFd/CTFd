function updatefiles(){
    chal = $('#files-chal').val();
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
    $.get(script_root + '/admin/files/' + chal, function(data){
        $('#files-chal').val(chal);
        files = $.parseJSON(JSON.stringify(data));
        files = files['files'];
        $('#current-files').empty();
        for(x=0; x<files.length; x++){
            filename = files[x].file.split('/');
            filename = filename[filename.length - 1];

            var curr_file = '<div class="col-md-12"><a href="{2}/files/{3}">{4}</a> <i class="fa fa-times float-right" onclick="deletefile({0}, {1}, $(this))" value="{2}" ></i></div>'.format(
                chal,
                files[x].id,
                script_root,
                files[x].file,
                filename
            );

            $('#current-files').append(curr_file);
        }

        if (cb){
            cb();
        }
    });
}

function deletefile(chal, file, elem){
    $.post(script_root + '/admin/files/' + chal,{
        'nonce': $('#nonce').val(),
        'method': 'delete',
        'file': file
    }, function (data){
        if (data == "1") {
            elem.parent().remove();
        }
    });
}


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