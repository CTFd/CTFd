$('#submit-key').click(function (e) {
    submitkey($('#chalid').val(), $('#answer').val())
});

$('#submit-keys').click(function (e) {
    e.preventDefault();
    $('#update-keys').modal('hide');
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

function loadchal(id, update) {
    $.get(script_root + '/admin/chal/' + id, function(obj){
        $('#desc-write-link').click(); // Switch to Write tab
        $('.chal-title').text(obj.name);
        $('.chal-name').val(obj.name);
        $('.chal-desc-editor').val(obj.description);
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
    });
}

function openchal(id){
    loadchal(id);
}

$(document).ready(function(){
    $('[data-toggle="tooltip"]').tooltip();
});
