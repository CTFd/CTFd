var error_template =
  '<div class="alert alert-danger alert-dismissable" role="alert">\n' +
  '  <span class="sr-only">Error:</span>\n' +
  "  {0}\n" +
  '  <button type="button" class="close" data-dismiss="alert" aria-label="Close"><span aria-hidden="true">×</span></button>\n' +
  "</div>";

var success_template =
  '<div class="alert alert-success alert-dismissable submit-row" role="alert">\n' +
  "  <strong>Success!</strong>\n" +
  "   Your profile has been updated\n" +
  '  <button type="button" class="close" data-dismiss="alert" aria-label="Close"><span aria-hidden="true">×</span></button>\n' +
  "</div>";

$(function() {
  var form = $("#user-settings-form");
  form.submit(function(e) {
    e.preventDefault();
    $("#results").empty();
    var params = $("#user-settings-form").serializeJSON();

    CTFd.fetch("/api/v1/users/me", {
      method: "PATCH",
      credentials: "same-origin",
      headers: {
        Accept: "application/json",
        "Content-Type": "application/json"
      },
      body: JSON.stringify(params)
    }).then(function(response) {
      if (response.status === 400) {
        response.json().then(function(object) {
          if (!object.success) {
            Object.keys(object.errors).map(function(error) {
              var i = form.find("input[name={0}]".format(error));
              var input = $(i);
              input.addClass("input-filled-invalid");
              input.removeClass("input-filled-valid");
              var error_msg = object.errors[error];
              var alert = error_template.format(error_msg);
              console.log(error_template);
              $("#results").append(alert);
            });
          }
        });
      } else if (response.status === 200) {
        response.json().then(function(object) {
          if (object.success) {
            $("#results").html(success_template);
          }
        });
      }
    });
  });
});
