function loadtags(chal, cb){
    $('#tags-chal').val(chal);
    $('#current-tags').empty();
    $('#chal-tags').empty();
    $.get(script_root + '/api/v1/challenges/'+chal+'/tags', function(data){
        for (var i = 0; i < data.length; i++) {
            var tag = "<span class='badge badge-primary mx-1 chal-tag'><span>"+data[i].value+"</span><a name='"+data[i].id+"'' class='btn-fa delete-tag'> &#215;</a></span>"
            $('#current-tags').append(tag);
        };
        $('.delete-tag').click(function(e){
            deletetag(e.target.name);
            $(e.target).parent().remove()
        });

        if (cb) {
            cb();
        }
    });
}

function deletetag(tagid){
    $.delete(script_root + '/api/v1/tags/'+tagid);
}


function updatetags(){
    var tags = [];
    var challenge_id = $('#tags-chal').val();
    $('#chal-tags > span > span').each(function(i, e){
        tags.push({
            'value': $(e).text(),
            'challenge': challenge_id,
        });
    });
    console.log(tags);
    fetch(script_root + '/api/v1/tags', {
        method: 'POST',
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(tags)
    });
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