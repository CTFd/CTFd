function delete_tag(elem){
    var elem = $(elem);
    var tag_id = elem.attr('tag-id');

    CTFd.fetch('/api/v1/tags/' + tag_id, {
        method: 'DELETE',
    }).then(function (response) {
        return response.json();
    }).then(function (response) {
        if (response.success) {
            $(elem).parent().remove()
        }
    });
}

$(document).ready(function () {
    $('#tags-add-input').keyup(function (e) {
        if (e.keyCode == 13) {
            var tag = $('#tags-add-input').val();
            var params = {
                value: tag,
                challenge: CHALLENGE_ID
            };

            CTFd.fetch('/api/v1/tags', {
                method: 'POST',
                credentials: 'same-origin',
                headers: {
                    'Accept': 'application/json',
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(params)
            }).then(function (response) {
                return response.json();
            }).then(function (response) {
                if (response.success){
                    var tpl = "<span class='badge badge-primary mx-1 challenge-tag'>" +
                        "<span>{0}</span>" +
                        "<a class='btn-fa delete-tag' tag-id='{1}' onclick='delete_tag(this)'>&times;</a></span>";
                    tag = tpl.format(
                        response.data.value,
                        response.data.id
                    );
                    $('#challenge-tags').append(tag);
                }
            });

            $('#tags-add-input').val("");
        }
    });
});