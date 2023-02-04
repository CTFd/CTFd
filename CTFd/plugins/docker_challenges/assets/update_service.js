CTFd.plugin.run((_CTFd) => {
    const $ = _CTFd.lib.$
    const md = _CTFd.lib.markdown()
    $(document).ready(function() {
        $.getJSON("/api/v1/docker", function(result) {
            $.each(result['data'], function(i, item) {
                $("#dockerimage_select").append($("<option />").val(item.name).text(item.name));
            });
            $("#dockerimage_select").val(DOCKER_IMAGE).change();
        });
        $.getJSON("/api/v1/secret", function(result){
            $.each(result['data'], function(i, item){
                $("#dockersecrets_select").append($("<option />").val(item.id).text(item.name));
            });
            $.each($("#dockersecrets_select option"), function(i, option) {
                if (SECRETS.includes(option.value)) {
                    $(option).prop("selected", true);
                }
            });
        });
    });
});
