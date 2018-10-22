$(document).ready(function () {
    $('.delete-item').click(function () {
        var elem = $(this).parent().parent();
        var type = elem.attr('class');
        var chal_name = elem.find('.chal').text().trim();
        var team_name = $("#team-id").text();
        var key_id = elem.find('.flag').attr('id');

        if (type == 'chal-solve') {
            var title = 'Delete Solve';
            var description = "<span>Are you sure you want to delete " +
                "<strong>correct</strong> " +
                "submission from " +
                "<strong id='confirm-team-name'></strong> " +
                "for challenge: " +
                "<strong id='confirm-chal-name'></strong>?</span>"


            var description = $($.parseHTML(description));
            description.find('#confirm-team-name').text(team_name);
            description.find('#confirm-chal-name').text(chal_name);
            description = description.html();

            var action = '{{ request.script_root }}/admin/solves/' + key_id + '/delete';
        } else if (type == 'chal-wrong') {
            var title = 'Delete Wrong Key';
            var description = "<span>Are you sure you want to delete " +
                "<strong>incorrect</strong> " +
                "submission from " +
                "<strong id='confirm-team-name'></strong> " +
                "for <strong id='confirm-chal-name'></strong>?</span>";

            var description = $($.parseHTML(description));
            description.find('#confirm-team-name').text(team_name);
            description.find('#confirm-chal-name').text(chal_name);
            description = description.html();

            var action = '{{ request.script_root }}/admin/wrong_keys/' + key_id + '/delete';
        } else if (type == 'award-row') {
            var title = 'Delete Award';
            var award_id = elem.find('.chal').attr('id');
            var description = "<span>Are you sure you want to delete the " +
                "<strong>{0}</strong> award?</span>".format(chal_name);
            var action = '{{ request.script_root }}/admin/awards/{0}/delete'.format(award_id);
        }

        var msg = {
            title: title,
            description: description,
            action: action,
        };

        var td_row = $(this).parent().parent();

        ezq({
            title: title,
            body: description,
            success: function () {
                var route = action;
                $.post(route, {
                    nonce: csrf_nonce,
                }, function (data) {
                    var data = $.parseJSON(JSON.stringify(data));
                    if (data == "1") {
                        td_row.remove();
                    }
                });
            }
        });
    });

    $('.mark-correct').click(function () {
        var elem = $(this).parent().parent();
        var type = elem.attr('class');
        var chal = elem.find('.chal').attr('id');
        var team = window.location.pathname.split('/').pop();

        var chal_name = htmlentities(elem.find('.chal').text().trim());
        var team_name = htmlentities($("#team-id").text());


        var description = $($.parseHTML(description));
        description.find('#confirm-team-name').text(team_name);
        description.find('#confirm-chal-name').text(chal_name);
        description = description.html();

        var action = '{{request.script_root }}/admin/solves/' + team + '/' + chal + '/solve';

        var title = 'Mark ' + chal_name + ' solved for ' + team_name;
        var description = "<span>Are you sure you want to mark " +
            "<strong>{0}</strong> ".format(team_name) +
            "as solved for team " +
            "<strong>{0}</strong>?</span>".format(chal_name);

        var td_row = $(this).parent().parent();

        ezq({
            title: title,
            body: description,
            success: function () {
                var route = script_root + '/admin/solves/' + team + '/' + chal + '/solve';
                $.post(route, {
                    nonce: csrf_nonce,
                }, function (data) {
                    var data = $.parseJSON(JSON.stringify(data));
                    if (data == "1") {
                        td_row.remove();
                    }
                });
            }
        })
    });

    $('#award-create-form').submit(function (e) {
        $.post($(this).attr('action'), $(this).serialize(), function (res) {
            if (res == '1') {
                var award = $('#award-create-form').serializeObject();
                var award_text = '<td class="text-center">{0}</td>'.format(award.name) +
                    '<td class="text-center">{0}</td>'.format(award.description) +
                    '<td class="text-center solve-time">{0}</td>'.format(moment().local().format('MMMM Do, h:mm:ss A')) +
                    '<td class="text-center">{0}</td>'.format(award.value) +
                    '<td class="text-center">{0}</td>'.format(award.category) +
                    '<td class="text-center">{0}</td>'.format('None') +
                    '<td class="text-center"><i class="fas fa-times"></i></td>'
                $('#awards-body').append(award_text);
                $('#create-award-modal').modal('hide');
            }
        })
        e.preventDefault();
    });
});