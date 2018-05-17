function loadtags(chal, cb){
    $('#tags-chal').val(chal)
    $('#current-tags').empty()
    $('#chal-tags').empty()
    $.get(script_root + '/admin/tags/'+chal, function(data){
        tags = $.parseJSON(JSON.stringify(data))
        tags = tags['tags']
        for (var i = 0; i < tags.length; i++) {
            tag = "<span class='badge badge-primary mx-1 chal-tag'><span>"+tags[i].tag+"</span><a name='"+tags[i].id+"'' class='btn-fa delete-tag'> &#215;</a></span>"
            $('#current-tags').append(tag)
        };
        $('.delete-tag').click(function(e){
            deletetag(e.target.name)
            $(e.target).parent().remove()
        });

        if (cb) {
            cb();
        }
    });
}

function deletetag(tagid){
    $.post(script_root + '/admin/tags/'+tagid+'/delete', {'nonce': $('#nonce').val()});
}


function updatetags(){
    tags = [];
    chal = $('#tags-chal').val();
    $('#chal-tags > span > span').each(function(i, e){
        tags.push($(e).text());
    });
    $.post(script_root + '/admin/tags/'+chal, {'tags':tags, 'nonce': $('#nonce').val()});
    $('#update-tags').modal('toggle');
}

$(document).ready(function () {
    $('.edit-tags').click(function (e) {
        var chal_id = $(this).attr('chal-id');
        loadtags(chal_id, function () {
            $('#update-tags').modal();
        });
    });


    $(".tag-insert").keyup(function (e) {
        if (e.keyCode == 13) {
            var tag = $('.tag-insert').val()
            tag = tag.replace(/'/g, '');
            if (tag.length > 0) {
                tag = "<span class='badge badge-primary mx-1 chal-tag'><span>" + tag + "</span><a class='btn-fa delete-tag' onclick='$(this).parent().remove()'> &times;</a></span>"
                $('#chal-tags').append(tag);
            }
            $('.tag-insert').val("");
        }
    });

    $('#submit-tags').click(function (e) {
        e.preventDefault();
        updatetags()
    });
});