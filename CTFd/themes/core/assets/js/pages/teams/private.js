import "../main";
import "../../utils";
import CTFd from "../../CTFd";
import "bootstrap/js/dist/modal";
import $ from "jquery";
import { ezBadge } from "../../ezq";

$(() => {
  if (window.team_captain) {
    $(".edit-team").click(function() {
      $("#team-edit-modal").modal();
    });

    $(".edit-captain").click(function() {
      $("#team-captain-modal").modal();
    });
  }

  var form = $("#team-info-form");
  form.submit(function(e) {
    e.preventDefault();
    $("#results").empty();
    var params = $(this).serializeJSON();
    var method = "PATCH";
    var url = "/api/v1/teams/me";
    CTFd.fetch(url, {
      method: method,
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
            const error_template =
              '<div class="alert alert-danger alert-dismissable" role="alert">\n' +
              '  <span class="sr-only">Error:</span>\n' +
              "  {0}\n" +
              '  <button type="button" class="close" data-dismiss="alert" aria-label="Close"><span aria-hidden="true">×</span></button>\n' +
              "</div>";
            Object.keys(object.errors).map(function(error) {
              var i = form.find("input[name={0}]".format(error));
              var input = $(i);
              input.addClass("input-filled-invalid");
              input.removeClass("input-filled-valid");
              var error_msg = object.errors[error];
              var alert = error_template.format(error_msg);
              $("#results").append(alert);
            });
          }
        });
      } else if (response.status === 200) {
        response.json().then(function(object) {
          if (object.success) {
            window.location.reload();
          }
        });
      }
    });
  });

  $("#team-captain-form").submit(function(e) {
    e.preventDefault();
    var params = $("#team-captain-form").serializeJSON(true);

    CTFd.fetch("/api/v1/teams/me", {
      method: "PATCH",
      credentials: "same-origin",
      headers: {
        Accept: "application/json",
        "Content-Type": "application/json"
      },
      body: JSON.stringify(params)
    })
      .then(function(response) {
        return response.json();
      })
      .then(function(response) {
        if (response.success) {
          window.location.reload();
        } else {
          $("#team-captain-form > #results").empty();
          Object.keys(response.errors).forEach(function(key, _index) {
            $("#team-captain-form > #results").append(
              ezBadge({
                type: "error",
                body: response.errors[key]
              })
            );
            var i = $("#team-captain-form").find(
              "select[name={0}]".format(key)
            );
            var input = $(i);
            input.addClass("input-filled-invalid");
            input.removeClass("input-filled-valid");
          });
        }
      });
  });
});
