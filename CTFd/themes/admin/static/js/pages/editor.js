var editor = CodeMirror.fromTextArea(
    document.getElementById("admin-pages-editor"), {
        lineNumbers: true,
        lineWrapping: true,
        mode: "xml",
        htmlMode: true,
    }
);


function uploadfiles() {
    var form = $('#media-library-upload')[0];
    var formData = new FormData(form);
    console.log(formData);
    $.ajax({
        url: script_root + '/admin/media',
        data: formData,
        type: 'POST',
        cache: false,
        contentType: false,
        processData: false,
        success: function (data) {
            refreshfiles(data);
            form.reset();
        }
    });
}

function refreshfiles(data) {
    var data = data.results;
    var list = $('#media-library-list');
    var mapping = {
        // Image Files
        'png': 'fa-file-image',
        'jpg': 'fa-file-image',
        'jpeg': 'fa-file-image',
        'gif': 'fa-file-image',
        'bmp': 'fa-file-image',
        'svg': 'fa-file-image',

        // Text Files
        'txt': 'fa-file-alt',

        // Video Files
        'mov': 'fa-file-video',
        'mp4': 'fa-file-video',
        'wmv': 'fa-file-video',
        'flv': 'fa-file-video',
        'mkv': 'fa-file-video',
        'avi': 'fa-file-video',

        // PDF Files
        'pdf': 'fa-file-pdf',

        // Audio Files
        'mp3': 'fa-file-sound',
        'wav': 'fa-file-sound',
        'aac': 'fa-file-sound',

        // Archive Files
        'zip': 'fa-file-archive',
        'gz': 'fa-file-archive',
        'tar': 'fa-file-archive',
        '7z': 'fa-file-archive',
        'rar': 'fa-file-archive',

        // Code Files
        'py': 'fa-file-code',
        'c': 'fa-file-code',
        'cpp': 'fa-file-code',
        'html': 'fa-file-code',
        'js': 'fa-file-code',
        'rb': 'fa-file-code',
        'go': 'fa-file-code',
    };
    for (var i = 0; i < data.length; i++) {
        var f = data[i];
        var ext = f.location.split('.').pop();
        var fname = f.location.split('/')[1];

        var wrapper = $('<div>').attr('class', 'media-item-wrapper');

        var link = $('<a>');
        link.attr('href', '##');

        if (mapping[ext] == undefined)
            link.append('<i class="far fa-file" aria-hidden="true"></i> '.format(mapping[ext]));
        else
            link.append('<i class="far {0}" aria-hidden="true"></i> '.format(mapping[ext]));

        link.append($('<small>').attr('class', 'media-item-title').text(fname));

        link.click(function (e) {
            var media_div = $(this).parent();
            var icon = $(this).find('.svg-inline--fa')[0];
            var f_loc = media_div.attr('data-location');
            var fname = media_div.attr('data-filename');
            $('#media-link').val(f_loc);
            $('#media-filename').html(
                $('<a>').attr('href', f_loc).attr('target', '_blank').text(fname)
            );

            $('#media-icon').empty();
            if ($(icon).hasClass('fa-file-image')) {
                $('#media-icon').append($('<img>').attr('src', f_loc).css({
                    'max-width': '100%',
                    'max-height': '100%',
                    'object-fit': 'contain'
                }));
            } else {
                // icon is empty so we need to pull outerHTML
                var copy_icon = $(icon).clone();
                $(copy_icon).addClass('fa-4x');
                $('#media-icon').append(copy_icon);
            }
            $('#media-item').show();
        });
        wrapper.append(link);
        wrapper.attr('data-location', script_root + '/files/' + f.location);
        wrapper.attr('data-id', f.id);
        wrapper.attr('data-filename', fname);
        list.append(wrapper);
    }
}

function insert_at_cursor(editor, text) {
    var doc = editor.getDoc();
    var cursor = doc.getCursor();
    doc.replaceRange(text, cursor);
}

function submit_form() {
    editor.save(); // Save the CodeMirror data to the Textarea
    var params = $("#page-edit").serializeJSON();
    var target = '/api/v1/pages';
    var method = 'POST';

    if (params.id){
        target += '/' + params.id;
        method = 'PATCH';
    }

    fetch(script_root + target, {
        method: method,
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(params)
    }).then(function (response) {
        return response.json();
    }).then(function(data){
        if (method === 'PATCH') {
            ezal({
                title: 'Saved',
                body: 'Your changes have been saved',
                button: 'Okay'
            });
        } else {
            console.log(data);
            window.location = script_root + '/admin/pages/' + data.id;
        }
    });
}

function preview_page() {
    editor.save(); // Save the CodeMirror data to the Textarea
    $('#page-edit').attr('action', '{{ request.script_root }}/admin/pages?operation=preview');
    $('#page-edit').attr('target', '_blank');
    $('#page-edit').submit();
}

$(document).ready(function () {
    $('#media-insert').click(function (e) {
        var tag = '';
        try {
            tag = $('#media-icon').children()[0].nodeName.toLowerCase();
        } catch (err) {
            tag = '';
        }
        var link = $('#media-link').val();
        var fname = $('#media-filename').text();
        var entry = null;
        if (tag === 'img') {
            entry = '![{0}]({1})'.format(fname, link);
        } else {
            entry = '[{0}]({1})'.format(fname, link);
        }
        insert_at_cursor(editor, entry);
    });


    $('#publish-page').click(function (e) {
        e.preventDefault();
        submit_form();
    });

    $('#save-page').click(function (e) {
        e.preventDefault();
        submit_form();
    });

    $('#media-button').click(function () {
        $.get(script_root + '/admin/media', function (data) {
            $('#media-library-list').empty();
            refreshfiles(data);
            $('#media-modal').modal();
        });
    });
});