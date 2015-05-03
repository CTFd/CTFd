function loadchal(id) {
    // $('#chal *').show()
    // $('#chal > h1').hide()
    obj = $.grep(challenges['game'], function (e) {
        return e.id == id;
    })[0]
    $('.chal-name').val(obj.name);
    $('.chal-desc').html(obj.description);
    $('.chal-value').val(obj.value);
    $('.chal-category').val(obj.category);
    $('.chal-id').val(obj.id);
    //$('#update-challenge .chal-delete').attr({
    //    'href': '/admin/chal/close/' + (id + 1)
    //})
    $('#update-challenge').foundation('reveal', 'open');

}

function submitkey(chal, key) {
    $.post("/admin/chal/" + chal, {
        key: key,
        nonce: $('#nonce').val()
    }, function (data) {
        alert(data)
    })
}

function loadkeys(chal){
    $.get('/admin/keys/' + chal, function(data){
        $('#keys-chal').val(chal);
        keys = $.parseJSON(JSON.stringify(data));
        keys = keys['keys'];
        $('#current-keys').empty();
        for(x=0; x<keys.length; x++){
            $('#current-keys').append($("<input class='current-key' type='text'>").val(keys[x].key));
            $('#current-keys').append('<input type="radio" name="key_type['+x+']" value="0">Static');
            $('#current-keys').append('<input type="radio" name="key_type['+x+']" value="1">Regex');
            $('#current-keys input[name="key_type['+x+']"][value="'+keys[x].type+'"]').prop('checked',true);
        }
    });
}

function updatekeys(){
    keys = [];
    vals = [];
    chal = $('#keys-chal').val()
    $('.current-key').each(function(){
        keys.push($(this).val());
    })
    $('#current-keys > input[name*="key_type"]:checked').each(function(){
        vals.push($(this).val());
    })
    $.post('/admin/keys/'+chal, {'keys':keys, 'vals':vals, 'nonce': $('#nonce').val()})
    loadchal(chal)
}

function loadtags(chal){
    $('#tags-chal').val(chal)
    $('#current-tags').empty()
    $('#chal-tags').empty()
    $.get('/admin/tags/'+chal, function(data){
        tags = $.parseJSON(JSON.stringify(data))
        tags = tags['tags']
        for (var i = 0; i < tags.length; i++) {
            tag = "<span class='secondary label chal-tag'><span>"+tags[i].tag+"</span><a name='"+tags[i].id+"'' class='delete-tag'>&#215;</a></span>"
            $('#current-tags').append(tag)
        };
        $('.delete-tag').click(function(e){
            deletetag(e.target.name)
            $(e.target).parent().remove()
        });
    });
}

function deletetag(tagid){
    $.post('/admin/tags/'+tagid+'/delete', {'nonce': $('#nonce').val()});
}

function deletechal(chalid){
    $.post('/admin/chal/delete', {'nonce':$('#nonce').val(), 'id':chalid});
}

function updatetags(){
    tags = [];
    chal = $('#tags-chal').val()
    $('#chal-tags > span > span').each(function(i, e){
        tags.push($(e).text())
    });
    $.post('/admin/tags/'+chal, {'tags':tags, 'nonce': $('#nonce').val()})
    loadchal(chal)
}

function loadfiles(chal){
    $('#update-files > form').attr('action', '/admin/files/'+chal)
    $.get('/admin/files/' + chal, function(data){
        $('#files-chal').val(chal)
        files = $.parseJSON(JSON.stringify(data));
        files = files['files']
        $('#current-files').empty()
        for(x=0; x<files.length; x++){
            filename = files[x].file.split('/')
            filename = filename[filename.length - 1]
            $('#current-files').append('<div data-alert class="alert-box info radius">'+'<a href=/'+files[x].file+'>'+filename+'</a><a href="#" onclick="deletefile('+chal+','+files[x].id+', $(this))" value="'+files[x].id+'" style="float:right;">Delete</a></div>')
        }
    });
}

function deletefile(chal, file, elem){
    $.post('/admin/files/' + chal,{
        'nonce': $('#nonce').val(),
        'method': 'delete', 
        'file': file
    }, function (data){
        if (data == "1") {
            elem.parent().remove()
        }
    });
}


function loadchals(){
    $('#challenges').empty();
    $.post("/admin/chals", {
        'nonce': $('#nonce').val()
    }, function (data) {
        categories = [];
        challenges = $.parseJSON(JSON.stringify(data));


        for (var i = challenges['game'].length - 1; i >= 0; i--) {
            if ($.inArray(challenges['game'][i].category, categories) == -1) {
                categories.push(challenges['game'][i].category)
                $('#challenges').append($('<tr id="' + challenges['game'][i].category.replace(/ /g,"-") + '"><td class="large-2"><h3>' + challenges['game'][i].category + '</h3></td></tr>'))
            }
        };

        for (var i = categories.length - 1; i >= 0; i--) {
            $('#new-challenge select').append('<option value="' + categories[i] + '">' + categories[i] + '</option>');
            $('#update-challenge select').append('<option value="' + categories[i] + '">' + categories[i] + '</option>');
        };

        for (var i = 0; i <= challenges['game'].length - 1; i++) {
            $('#' + challenges['game'][i].category.replace(/ /g,"-")).append($('<button class="radius" value="' + challenges['game'][i].id + '">' + challenges['game'][i].value + '</button>'));
        };

        $('#challenges button').click(function (e) {
            loadchal(this.value);
            loadkeys(this.value);
            loadtags(this.value);
            loadfiles(this.value);
        });

        $('tr').append('<button class="radius create-challenge"><i class="fa fa-plus"></i></button>');

        $('.create-challenge').click(function (e) {
            $('#new-chal-category').val($($(this).siblings()[0]).text().trim())
            $('#new-chal-title').text($($(this).siblings()[0]).text().trim())
            $('#new-challenge').foundation('reveal', 'open');
        });

    });
}
$('#submit-key').click(function (e) {
    submitkey($('#chalid').val(), $('#answer').val())
});

$('#submit-keys').click(function (e) {
    if (confirm('Updating keys. Are you sure?')){
        updatekeys()
    }
});

$('#submit-tags').click(function (e) {
    updatetags()
});

$('#delete-chal > form').submit(function(e){
    e.preventDefault();
    $.post('/admin/chal/delete', $(this).serialize(), function(data){
        console.log(data)
        if (data){
            loadchals();
            $('#delete-chal').foundation('reveal', 'close');
        }
        else {
            alert('There was an error');
        }
    })
});

$(".tag-insert").keyup(function (e) {
    if (e.keyCode == 13) {
        tag = $('.tag-insert').val()
        tag = tag.replace(/'/g, '');
        if (tag.length > 0){
            tag = "<span class='secondary label chal-tag'><span>"+tag+"</span><a onclick='$(this).parent().remove()'>&#215;</a></span>"
            $('#chal-tags').append(tag)
        }
        $('.tag-insert').val("")
    }
});

$('.create-category').click(function (e) {
    $('#new-category').foundation('reveal', 'open');
});
count = 1;
$('#create-key').click(function (e) {
    $('#current-keys').append("<input class='current-key' type='text' placeholder='Blank Key'>");
    $('#current-keys').append('<input type="radio" name="key_type['+count+']" value="0">Static');
    $('#current-keys').append('<input type="radio" name="key_type['+count+']" value="1">Regex');
    count++;
});

$(function(){
    loadchals();
})
