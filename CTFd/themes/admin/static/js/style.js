$(".form-control").bind({
    focus: function() {
        $(this).addClass('input-filled-valid' );
    },
    blur: function() {
        if ($(this).val() === '') {
            $(this).removeClass('input-filled-valid' );
        }
    }
});

$('.modal').on('show.bs.modal', function (e) {
    $('.form-control').each(function () {
        if ($(this).val()) {
            $(this).addClass("input-filled-valid");
        }
    });

});

$(function () {
    $('.form-control').each(function () {
        if ($(this).val()) {
            $(this).addClass("input-filled-valid");
        }
    });

    $("tr").click(function () {
        var sel = getSelection().toString();
        if (!sel) {
            var href = $(this).attr('data-href');
            if (href) {
                window.location = href;
            }
        }
        return false;
    });

    $('[data-toggle="tooltip"]').tooltip()
});