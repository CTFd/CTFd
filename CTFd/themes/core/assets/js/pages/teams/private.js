import "../main";
import "../../utils";
import CTFd from "../../CTFd";
import "bootstrap/js/dist/modal";
import $ from "jquery";
import { copyToClipboard } from "../../utils";
import { ezBadge, ezQuery, ezAlert } from "../../ezq";

$(() => {
  if (window.team_captain) {
    $(".edit-team").click(function() {
      $("#team-edit-modal").modal();
    });

    $(".edit-captain").click(function() {
      $("#team-captain-modal").modal();
    });

    $(".invite-members").click(function() {
      CTFd.fetch("/api/v1/teams/me/members", {
        method: "POST",
        credentials: "same-origin",
        headers: {
          Accept: "application/json",
          "Content-Type": "application/json"
        }
      })
        .then(function(response) {
          return response.json();
        })
        .then(function(response) {
          if (response.success) {
            let code = response.data.code;
            let url = `${window.location.origin}${
              CTFd.config.urlRoot
            }/teams/invite?code=${code}`;
            $("#team-invite-modal input[name=link]").val(url);
            $("#team-invite-modal").modal();
          }
        });
    });

    $("#team-invite-link-copy").click(function(event) {
      copyToClipboard(event, "#team-invite-link");
    });

    $(".disband-team").click(function() {
      ezQuery({
        title: "Disband Team",
        body: "Are you sure you want to disband your team?",
        success: function() {
          CTFd.fetch("/api/v1/teams/me", {
            method: "DELETE"
          })
            .then(function(response) {
              return response.json();
            })
            .then(function(response) {
              if (response.success) {
                window.location.reload();
              } else {
                ezAlert({
                  title: "Error",
                  body: response.errors[""].join(" "),
                  button: "Got it!"
                });
              }
            });
        }
      });
    });
  }

  let form = $("#team-info-form");
  form.submit(function(e) {
    e.preventDefault();
    $("#results").empty();
    let params = $(this).serializeJSON();

    params.fields = [];

    for (const property in params) {
      if (property.match(/fields\[\d+\]/)) {
        let field = {};
        let id = parseInt(property.slice(7, -1));
        field["field_id"] = id;
        field["value"] = params[property];
        params.fields.push(field);
        delete params[property];
      }
    }

    let method = "PATCH";
    let url = "/api/v1/teams/me";
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
              let i = form.find("input[name={0}]".format(error));
              let input = $(i);
              input.addClass("input-filled-invalid");
              input.removeClass("input-filled-valid");
              let error_msg = object.errors[error];
              let alert = error_template.format(error_msg);
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
