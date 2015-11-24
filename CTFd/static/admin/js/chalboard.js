//http://stackoverflow.com/a/2648463 - wizardry!
String.prototype.format = String.prototype.f = function() {
    var s = this,
        i = arguments.length;

    while (i--) {
        s = s.replace(new RegExp('\\{' + i + '\\}', 'gm'), arguments[i]);
    }
    return s;
};

//http://stackoverflow.com/a/7616484
String.prototype.hashCode = function() {
    var hash = 0, i, chr, len;
    if (this.length == 0) return hash;
    for (i = 0, len = this.length; i < len; i++) {
        chr   = this.charCodeAt(i);
        hash  = ((hash << 5) - hash) + chr;
        hash |= 0; // Convert to 32bit integer
    }
    return hash;
};

function loadchal(id) {
    // $('#chal *').show()
    // $('#chal > h1').hide()
    obj = $.grep(challenges['game'], function (e) {
        return e.id == id;
    })[0]
    $('a[href=#desc-write]').click() // Switch to Write tab
    $('.chal-title').text(obj.name);
    $('.chal-name').val(obj.name);
    $('.chal-desc').val(obj.description);
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
            var elem = $('<div>');
            elem.append($("<input class='current-key' type='text'>").val(keys[x].key));
            elem.append('<input type="radio" name="key_type['+x+']" value="0">Static');
            elem.append('<input type="radio" name="key_type['+x+']" value="1">Regex');
            elem.append('<a href="#" onclick="$(this).parent().remove()" class="remove-key">Remove</a>');
            
            $('#current-keys').append(elem);
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
    $('#current-keys input[name*="key_type"]:checked').each(function(){
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
                $('#challenges').append($('<tr id="' + challenges['game'][i].category.replace(/ /g,"-").hashCode() + '"><td class="large-2"><h3>' + challenges['game'][i].category + '</h3></td></tr>'))
            }
        };

        for (var i = 0; i <= challenges['game'].length - 1; i++) {
            var chal = challenges['game'][i]
            var chal_button = $('<button class="chal-button" value="{0}"><p>{1}</p><span>{2}</span></button>'.format(chal.id, chal.name, chal.value))
            $('#' + challenges['game'][i].category.replace(/ /g,"-").hashCode()).append(chal_button);
        };

        $('#challenges button').click(function (e) {
            loadchal(this.value);
            loadkeys(this.value);
            loadtags(this.value);
            loadfiles(this.value);
        });

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
    updatekeys()
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



// Markdown Preview
$('#desc-edit').on('toggled', function (event, tab) {
    if (tab[0].id == 'desc-preview'){
        $(tab[0]).html(marked($('#desc-editor').val(), {'gfm':true, 'breaks':true}))
    }
});
$('#new-desc-edit').on('toggled', function (event, tab) {
    if (tab[0].id == 'new-desc-preview'){
        $(tab[0]).html(marked($('#new-desc-editor').val(), {'gfm':true, 'breaks':true}))
    }
});

// Open New Challenge modal when New Challenge button is clicked
$('.create-challenge').click(function (e) {
    $('#create-challenge').foundation('reveal', 'open');
});


$('#create-key').click(function(e){
    var amt = $('#current-keys input[type=text]').length
    // $('#current-keys').append("<input class='current-key' type='text' placeholder='Blank Key'>");
    // $('#current-keys').append('<input type="radio" name="key_type[{0}]" value="0">Static'.format(amt));
    // $('#current-keys').append('<input type="radio" name="key_type[{0}]" value="1">Regex'.format(amt));
    
    var elem = $('<div>');
    elem.append("<input class='current-key' type='text' placeholder='Blank Key'>");
    elem.append('<input type="radio" name="key_type[{0}]" value="0" checked="checked">Static'.format(amt));
    elem.append('<input type="radio" name="key_type[{0}]" value="1">Regex'.format(amt));
    elem.append('<a href="#" onclick="$(this).parent().remove()" class="remove-key">Remove</a>');
    $('#current-keys').append(elem);
});

$(function(){
    loadchals();
})
