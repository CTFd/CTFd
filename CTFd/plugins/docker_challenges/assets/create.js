CTFd.plugin.run((_CTFd) => {
    const $ = _CTFd.lib.$
    const md = _CTFd.lib.markdown()
    $('a[href="#new-desc-preview"]').on('shown.bs.tab', function (event) {
        if (event.target.hash == '#new-desc-preview') {
            var editor_value = $('#new-desc-editor').val();
            $(event.target.hash).html(
                md.render(editor_value)
            );
        }
    });
    $(document).ready(function(){
    $('[data-toggle="tooltip"]').tooltip();
    $.getJSON("/api/v1/docker", function(result){
        $.each(result['data'], function(i, item){
            if (item.name == 'Error in Docker Config!') { 
                document.docker_form.dockerimage_select.disabled = true;
                $("label[for='DockerImage']").text('Docker Image ' + item.name)
            }
            else {
                $("#dockerimage_select").append($("<option />").val(item.name).text(item.name));
            }
        });
    });
});
});