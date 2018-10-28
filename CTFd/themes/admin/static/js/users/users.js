// TODO: this likely doesn't work
function load_update_modal(id, name, email, website, affiliation, country, admin, verified, hidden, banned) {
    var modal_form = $('#update-user-modal form');

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
    modal_form.find('input[name=banned]').prop('checked', banned);

    if (id == 'new') {
        $('#update-user-modal .modal-action').text('Create User');
    } else {
        $('#update-user-modal .modal-action').text('Edit User');
    }

    $('#results').empty();
    $('#update-user-modal').modal("show");
}


function load_email_modal(id) {
    var modal = $('#email-user');
    modal.find('textarea').val("");
    modal.find('input[name=id]').val(id);
    $('#email-user-errors').empty();
    $('#email-user form').attr('action', '{{ request.script_root }}/admin/team/' + id + '/mail');
    $('#email-user').modal();
}


$(document).ready(function () {
    $('#update-user').click(function (e) {
        e.preventDefault();
        var params = $("#update-user-modal form").serializeJSON(true);

        var target = '/api/v1/users';
        var method = 'POST';
        if (params.id) {
            target += '/' + params.id;
            method = 'PATCH';
        }
        fetch(script_root + target, {
            method: method,
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(params)
        }).then(function(response) {
            return response.json();
        }).then(function(data){
            if (data.success) {
                // TODO: Update row in place
                window.location.reload();
            }
        });
    });

    // TODO: This likely doesn't work
    $('#send-user-email').click(function (e) {
        e.preventDefault();
        var id = $('#email-user input[name="id"]').val();
        var email_data = $('#email-user form').serializeArray();
        $.post($('#email-user form').attr('action'), $('#email-user form').serialize(), function (data) {
            if (data.result) {
                var error = $('<div class="alert alert-success alert-dismissable">\n' +
                    '  <a href="#" class="close" data-dismiss="alert" aria-label="close">&times;</a>\n' +
                    '  {0}\n'.format(data.message) +
                    '</div>');
                $('#email-user-errors').append(error);
            }
            else {
                var error = $('<div class="alert alert-danger alert-dismissable">\n' +
                    '  <a href="#" class="close" data-dismiss="alert" aria-label="close">&times;</a>\n' +
                    '  {0}\n'.format(data.message) +
                    '</div>');
                $('#email-user-errors').append(error);
            }
        });
    });

    // TODO: This likely doesn't work
    $('.edit-team').click(function () {
        var elem = $(this).parent().parent().parent();
        var id = elem.find('.team-id').attr('value') || '';
        var name = elem.find('.team-name').attr('value') || '';
        var email = elem.find('.team-email').attr('value') || '';
        var website = elem.find('.team-website > a').attr('href') || '';
        var affiliation = elem.find('.team-affiliation').attr('value') || '';
        var country = elem.find('.team-country').attr('value') || '';

        var admin = elem.find('.team-admin').attr('value') == 'True' || false;
        var verified = elem.find('.team-verified').attr('value') == 'True' || false;
        var hidden = elem.find('.team-hidden').attr('value') == 'True' || false;
        var banned = elem.find('.team-banned').attr('value') == 'True' || false;

        load_update_modal(id, name, email, website, affiliation, country, admin, verified, hidden);
    });

    $('.create-team').click(function () {
        load_update_modal('new', '', '', '', '', '', false, false, false);
    });

    $('.delete-team').click(function () {
        var elem = $(this).parent().parent().parent();
        var user_id = elem.find('.team-id').text().trim();
        var name = htmlentities(elem.find('.team-name').text().trim());

        var td_row = $(this).parent().parent().parent();

        ezq({
            title: "Delete User",
            body: "Are you sure you want to delete {0}".format("<strong>" + name + "</strong>"),
            success: function () {
                var route = script_root + '/api/v1/users/' + user_id;
                $.delete(route, {}, function (data) {
                    if (data.success) {
                        td_row.remove();
                    }
                });
            }
        });
    });


    $('.email-team').click(function () {
        var elem = $(this).parent().parent().parent();
        var id = elem.find('.team-id').text().trim();
        load_email_modal(id);
    });

});