function load_update_modal(id, name, email, website, affiliation, country, admin, verified, hidden) {
    var modal_form = $('#update-team-modal form');

    modal_form.find('input[name=name]').val(name);
    modal_form.find('input[name=id]').val(id);
    modal_form.find('input[name=email]').val(email);
    modal_form.find('input[name=website]').val(website);
    modal_form.find('input[name=affiliation]').val(affiliation);
    modal_form.find('input[name=country]').val(country);
    modal_form.find('input[name=password]').val('');

    modal_form.find('input[name=admin]').prop('checked', admin);
    modal_form.find('input[name=verified]').prop('checked', verified);
    modal_form.find('input[name=hidden]').prop('checked', hidden);

    if (id == 'new') {
        $('#update-team-modal .modal-action').text('Create Team');
    } else {
        $('#update-team-modal .modal-action').text('Edit Team');
    }

    $('#results').empty();
    $('#update-team-modal form').attr('action', '{{ request.script_root }}/admin/team/' + id);
    $('#update-team-modal').modal("show");
}


$(document).ready(function () {
    $('#update-team').click(function (e) {
        e.preventDefault();
        var team_id = $('#update-team-modal input[name="id"]').val();
        var params = $('#update-team-modal form').serializeJSON(true);

        $('#results').empty();

        fetch(script_root + '/api/v1/teams/' + team_id, {
            method: 'PATCH',
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(params)
        }).then(function (response) {
            return response.json();
        }).then(function (data) {
            if (data.id) {
                $('#update-team-modal').modal("toggle");
            } else {
                ezal({
                    title: 'Error!',
                    body: 'Your changes could not be saved!',
                    button: 'Okay'
                });
            }
        });
    });

    $('.edit-team').click(function () {
        var elem = $(this).parent().parent().parent();
        var id = elem.find('.team-id').attr('value') || '';
        var name = elem.find('.team-name').attr('value') || '';
        var email = elem.find('.team-email').attr('value') || '';
        var website = elem.find('.team-website > a').attr('href') || '';
        var affiliation = elem.find('.team-affiliation').attr('value') || '';
        var country = elem.find('.team-country').attr('value') || '';

        var admin = elem.find('.team-admin').attr('value') == 'True' || false;
        var hidden = elem.find('.team-hidden').attr('value') == 'True' || false;

        load_update_modal(id, name, email, website, affiliation, country, admin, hidden);
    });

    $('.create-team').click(function () {
        load_update_modal('new', '', '', '', '', '', false, false, false);
    });

    $('.delete-team').click(function () {
        var elem = $(this).parent().parent().parent();
        var team_id = elem.find('.team-id').text().trim();
        var name = htmlentities(elem.find('.team-name').text().trim());
        var td_row = $(this).parent().parent().parent();

        ezq({
            title: "Delete User",
            body: "Are you sure you want to delete {0}".format("<strong>" + name + "</strong>"),
            success: function () {
                var route = script_root + '/admin/team/' + team_id + '/delete';
                $.delete(script_root + '/api/v1/teams/' + team_id, function(data){
                    if (data.success) {
                        td_row.remove();
                    }
                })
            }
        })
    });
});