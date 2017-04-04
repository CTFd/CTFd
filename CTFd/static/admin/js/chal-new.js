function load_chal_template(chal_type_name){
    $.get(script_root + '/static/admin/js/templates/challenges/'+ chal_type_name +'/' + chal_type_name + '-challenge-create.hbs', function(template_data){
        var template = Handlebars.compile(template_data);
        $("#create-chal-entry-div").html(template({'nonce':nonce, 'script_root':script_root}));
        $.getScript(script_root + '/static/admin/js/templates/challenges/'+chal_type_name+'/'+chal_type_name+'-challenge-create.js', function(){
            console.log('loaded');
        });
    });
}


nonce = "{{ nonce }}";
$.get(script_root + '/admin/chal_types', function(data){
    console.log(data);
    $("#create-chals-select").empty();
    var chal_type_amt = Object.keys(data).length;
    if (chal_type_amt > 1){
        var option = "<option> -- </option>";
        $("#create-chals-select").append(option);
        for (var key in data){
            var option = "<option value='{0}'>{1}</option>".format(key, data[key]);
            $("#create-chals-select").append(option);
        }
    } else if (chal_type_amt == 1) {
        var key = Object.keys(data)[0];
        $("#create-chals-select").parent().parent().parent().empty();
        load_chal_template(data[key]);
    }
});
$('#create-chals-select').change(function(){
    var chal_type_name = $(this).find("option:selected").text();
    load_chal_template(chal_type_name);
});
