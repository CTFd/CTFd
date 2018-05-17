$.ajaxSetup({ cache: false });

window.challenge = new Object();

function load_chal_template(challenge){
    $.getScript(script_root + challenge.scripts.modal, function () {
        console.log('loaded renderer');
        $.get(script_root + challenge.templates.create, function (template_data) {
            var template = nunjucks.compile(template_data);
            $("#create-chal-entry-div").html(template.render({'nonce': nonce, 'script_root': script_root}));
            $.getScript(script_root + challenge.scripts.create, function () {
                console.log('loaded');
            });
        });
    });
}

$.get(script_root + '/admin/chal_types', function(data){
    $("#create-chals-select").empty();
    var chal_type_amt = Object.keys(data).length;
    if (chal_type_amt > 1){
        var option = "<option> -- </option>";
        $("#create-chals-select").append(option);
        for (var key in data){
            var challenge = data[key];
            var option = $("<option/>");
            option.attr('value', challenge.type);
            option.text(challenge.name);
            option.data('meta', challenge);
            $("#create-chals-select").append(option);
        }
        $("#create-chals-select-div").show();
    } else if (chal_type_amt == 1) {
        var key = Object.keys(data)[0];
        $("#create-chals-select").empty();
        load_chal_template(data[key]);
    }
});
$('#create-chals-select').change(function(){
    var challenge = $(this).find("option:selected").data('meta');
    load_chal_template(challenge);
});
