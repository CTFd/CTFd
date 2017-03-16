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

function load_edit_key_modal(key_id, key_type_name) {
    $.get(script_root + '/static/admin/js/templates/keys/'+key_type_name+'/edit-'+key_type_name+'-modal.hbs', function(template_data){
        $.get(script_root + '/admin/keys/' + key_id, function(key_data){
            $('#edit-keys').empty();
            var template = Handlebars.compile(template_data);
            key_data['script_root'] = script_root;
            $('#edit-keys').append(template(key_data));
            $('#key-id').val(key_id);
            $('#submit-keys').click(function (e) {
                e.preventDefault();
                updatekey()
            });
            $('#edit-keys').modal();
        });
    });
}

function loadchal(id, update) {
    // $('#chal *').show()
    // $('#chal > h1').hide()
    obj = $.grep(challenges['game'], function (e) {
        return e.id == id;
    })[0]
    $('#desc-write-link').click() // Switch to Write tab
    $('.chal-title').text(obj.name);
    $('.chal-name').val(obj.name);
    $('.chal-desc').val(obj.description);
    $('.chal-value').val(obj.value);
    if (parseInt(obj.max_attempts) > 0){
        $('.chal-attempts').val(obj.max_attempts);
        $('#limit_max_attempts').prop('checked', true);
        $('#chal-attempts-group').show();
    }
    $('.chal-category').val(obj.category);
    $('.chal-id').val(obj.id);
    $('.chal-hidden').prop('checked', false);
    if (obj.hidden) {
        $('.chal-hidden').prop('checked', true);
    }
    //$('#update-challenge .chal-delete').attr({
    //    'href': '/admin/chal/close/' + (id + 1)
    //})
    if (typeof update === 'undefined')
        $('#update-challenge').modal();
}

function submitkey(chal, key) {
    $.post(script_root + "/admin/chal/" + chal, {
        key: key,
        nonce: $('#nonce').val()
    }, function (data) {
        alert(data)
    })
}

function create_key(chal, key, key_type) {
    $.post(script_root + "/admin/keys", {
        chal: chal,
        key: key,
        key_type: key_type,
        nonce: $('#nonce').val()
    }, function (data) {
        if (data == "1"){
            loadkeys(chal);
            $("#create-keys").modal('toggle');
        }
    });
}

function loadkeys(chal){
    $.get(script_root + '/admin/chal/' + chal + '/keys', function(data){
        $('#keys-chal').val(chal);
        keys = $.parseJSON(JSON.stringify(data));
        keys = keys['keys'];
        $('#current-keys').empty();
        $.get(script_root + "/static/admin/js/templates/admin-keys-table.hbs", function(data){
            var template = Handlebars.compile(data);
            var wrapper  = {keys: keys, script_root: script_root};
            $('#current-keys').append(template(wrapper));
        });
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
    $.post(script_root + '/admin/keys/'+chal, {'keys':keys, 'vals':vals, 'nonce': $('#nonce').val()})
    loadchal(chal, true)
    $('#update-keys').modal('hide');
}


function deletekey(key_id){
    $.post(script_root + '/admin/keys/'+key_id+'/delete', {'nonce': $('#nonce').val()}, function(data){
        if (data == "1") {
            $('tr[name={0}]'.format(key_id)).remove();
        }
    });
}

function updatekey(){
    var key_id = $('#key-id').val();
    var chal = $('#keys-chal').val();
    var key_data = $('#key-data').val();
    var key_type = $('#key-type').val();
    var nonce = $('#nonce').val();
    $.post(script_root + '/admin/keys/'+key_id, {
        'chal':chal,
        'key':key_data,
        'key_type': key_type,
        'nonce': nonce
    }, function(data){
        if (data == "1") {
            loadkeys(chal);
            $('#edit-keys').modal('toggle');
        }
    })
}

function loadtags(chal){
    $('#tags-chal').val(chal)
    $('#current-tags').empty()
    $('#chal-tags').empty()
    $.get(script_root + '/admin/tags/'+chal, function(data){
        tags = $.parseJSON(JSON.stringify(data))
        tags = tags['tags']
        for (var i = 0; i < tags.length; i++) {
            tag = "<span class='label label-primary chal-tag'><span>"+tags[i].tag+"</span><a name='"+tags[i].id+"'' class='delete-tag'>&#215;</a></span>"
            $('#current-tags').append(tag)
        };
        $('.delete-tag').click(function(e){
            deletetag(e.target.name)
            $(e.target).parent().remove()
        });
    });
}

function deletetag(tagid){
    $.post(script_root + '/admin/tags/'+tagid+'/delete', {'nonce': $('#nonce').val()});
}

function deletechal(chalid){
    $.post(script_root + '/admin/chal/delete', {'nonce':$('#nonce').val(), 'id':chalid});
}

function updatetags(){
    tags = [];
    chal = $('#tags-chal').val()
    $('#chal-tags > span > span').each(function(i, e){
        tags.push($(e).text())
    });
    $.post(script_root + '/admin/tags/'+chal, {'tags':tags, 'nonce': $('#nonce').val()})
    loadchal(chal)
}

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
            $('#update-files').modal('hide');
        }
    });
}

function loadfiles(chal){
    $('#update-files form').attr('action', script_root+'/admin/files/'+chal)
    $.get(script_root + '/admin/files/' + chal, function(data){
        $('#files-chal').val(chal)
        files = $.parseJSON(JSON.stringify(data));
        files = files['files']
        $('#current-files').empty()
        for(x=0; x<files.length; x++){
            filename = files[x].file.split('/')
            filename = filename[filename.length - 1]
            $('#current-files').append('<div class="row" style="margin:5px 0px;">'+'<a style="position:relative;top:10px;" href='+script_root+'/files/'+files[x].file+'>'+filename+'</a><a href="#" class="btn btn-danger" onclick="deletefile('+chal+','+files[x].id+', $(this))" value="'+files[x].id+'" style="float:right;">Delete</a></div>')
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
            elem.parent().remove()
        }
    });
}


function loadchals(){
    $('#challenges').empty();
    $.post(script_root + "/admin/chals", {
        'nonce': $('#nonce').val()
    }, function (data) {
        categories = [];
        challenges = $.parseJSON(JSON.stringify(data));


        for (var i = challenges['game'].length - 1; i >= 0; i--) {
            if ($.inArray(challenges['game'][i].category, categories) == -1) {
                categories.push(challenges['game'][i].category)
                $('#challenges').append($('<tr id="' + challenges['game'][i].category.replace(/ /g,"-").hashCode() + '"><td class="col-md-1"><h3>' + challenges['game'][i].category + '</h3></td></tr>'))
            }
        };

        for (var i = 0; i <= challenges['game'].length - 1; i++) {
            var chal = challenges['game'][i]
            var chal_button = $('<button class="chal-button col-md-2 theme-background" value="{0}"><h5>{1}</h5><p class="chal-points">{2}</p><span class="chal-percent">{3}% solved</span></button>'.format(chal.id, chal.name, chal.value, Math.round(chal.percentage_solved * 100)));
            $('#' + challenges['game'][i].category.replace(/ /g,"-").hashCode()).append(chal_button);
        };

        $('#challenges button').click(function (e) {
            loadchal(this.value);
            loadkeys(this.value);
            loadtags(this.value);
            loadfiles(this.value);
        });

        // $('.create-challenge').click(function (e) {
        //     $('#new-chal-category').val($($(this).siblings()[0]).text().trim());
        //     $('#new-chal-title').text($($(this).siblings()[0]).text().trim());
        //     $('#new-challenge').modal();
        // });

    });
}

$('#submit-key').click(function (e) {
    submitkey($('#chalid').val(), $('#answer').val())
});

$('#submit-keys').click(function (e) {
    e.preventDefault();
    $('#update-keys').modal('hide');
});

$('#submit-tags').click(function (e) {
    e.preventDefault();
    updatetags()
});

$('#submit-files').click(function (e) {
    e.preventDefault();
    updatefiles()
});

$('#delete-chal form').submit(function(e){
    e.preventDefault();
    $.post(script_root + '/admin/chal/delete', $(this).serialize(), function(data){
        console.log(data)
        if (data){
            loadchals();
        }
        else {
            alert('There was an error');
        }
    })
    $("#delete-chal").modal("hide");
    $("#update-challenge").modal("hide");
});

$(".tag-insert").keyup(function (e) {
    if (e.keyCode == 13) {
        tag = $('.tag-insert').val()
        tag = tag.replace(/'/g, '');
        if (tag.length > 0){
            tag = "<span class='label label-primary chal-tag'><span>"+tag+"</span><a class='delete-tag' onclick='$(this).parent().remove()'>&#215;</a></span>"
            $('#chal-tags').append(tag)
        }
        $('.tag-insert').val("")
    }
});

$('#limit_max_attempts').change(function() {
    if(this.checked) {
        $('#chal-attempts-group').show();
    } else {
        $('#chal-attempts-group').hide();
        $('#chal-attempts-input').val('');
    }
});

// Markdown Preview
$('#desc-edit').on('shown.bs.tab', function (event) {
    if (event.target.hash == '#desc-preview'){
        $(event.target.hash).html(marked($('#desc-editor').val(), {'gfm':true, 'breaks':true}))
    }
});
$('#new-desc-edit').on('shown.bs.tab', function (event) {
    if (event.target.hash == '#new-desc-preview'){
        $(event.target.hash).html(marked($('#new-desc-editor').val(), {'gfm':true, 'breaks':true}))
    }
});

// Open New Challenge modal when New Challenge button is clicked
// $('.create-challenge').click(function (e) {
//     $('#create-challenge').modal();
// });


$('#create-key').click(function(e){
    $.get(script_root + '/admin/key_types', function(data){
        $("#create-keys-select").empty();
        var option = "<option> -- </option>";
        $("#create-keys-select").append(option);
        for (var key in data){
            var option = "<option value='{0}'>{1}</option>".format(key, data[key]);
            $("#create-keys-select").append(option);
        }
        $("#create-keys").modal();
    });
});

$('#create-keys-select').change(function(){
    var key_type_name = $(this).find("option:selected").text();

    $.get(script_root + '/static/admin/js/templates/keys/'+key_type_name +'/'+key_type_name+'.hbs', function(template_data){
        var template = Handlebars.compile(template_data);
        $("#create-keys-entry-div").html(template());
        $("#create-keys-button-div").show();
    });
});


$('#create-keys-submit').click(function (e) {
    e.preventDefault();
    var chalid = $('#create-keys').find('.chal-id').val();
    var key_data = $('#create-keys').find('input[name=key]').val();
    var key_type = $('#create-keys-select').val();
    create_key(chalid, key_data, key_type);
});

$(function(){
    loadchals();
})
