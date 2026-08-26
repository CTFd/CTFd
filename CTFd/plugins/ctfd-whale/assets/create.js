// Markdown Preview
if ($ === undefined) $ = CTFd.lib.$
$('#desc-edit').on('shown.bs.tab', function(event) {
    if (event.target.hash == '#desc-preview') {
        var editor_value = $('#desc-editor').val();
        $(event.target.hash).html(
            CTFd._internal.challenge.render(editor_value)
        );
    }
});
$('#new-desc-edit').on('shown.bs.tab', function(event) {
    if (event.target.hash == '#new-desc-preview') {
        var editor_value = $('#new-desc-editor').val();
        $(event.target.hash).html(
            CTFd._internal.challenge.render(editor_value)
        );
    }
});
$("#solve-attempts-checkbox").change(function() {
    if (this.checked) {
        $('#solve-attempts-input').show();
    } else {
        $('#solve-attempts-input').hide();
        $('#max_attempts').val('');
    }
});

$(document).ready(function() {
    $('[data-toggle="tooltip"]').tooltip();
});