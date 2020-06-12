import $ from "jquery";
import CTFd from "core/CTFd";
import nunjucks from "nunjucks";
import { ezQuery } from "core/ezq";

export function deleteFlag(event) {
  event.preventDefault();
  const flag_id = $(this).attr("flag-id");
  const row = $(this)
    .parent()
    .parent();

  ezQuery({
    title: "Delete Flag",
    body: "Are you sure you want to delete this flag?",
    success: function() {
      CTFd.fetch("/api/v1/flags/" + flag_id, {
        method: "DELETE"
      })
        .then(function(response) {
          return response.json();
        })
        .then(function(response) {
          if (response.success) {
            row.remove();
          }
        });
    }
  });
}

export function addFlagModal(_event) {
  $.get(CTFd.config.urlRoot + "/api/v1/flags/types", function(response) {
    const data = response.data;
    const flag_type_select = $("#flags-create-select");
    flag_type_select.empty();

    let option = $("<option> -- </option>");
    flag_type_select.append(option);

    for (const key in data) {
      if (data.hasOwnProperty(key)) {
        option = $(
          "<option value='{0}'>{1}</option>".format(key, data[key].name)
        );
        flag_type_select.append(option);
      }
    }
    $("#flag-edit-modal").modal();
  });

  $("#flag-edit-modal form").submit(function(event) {
    event.preventDefault();
    const params = $(this).serializeJSON(true);
    params["challenge"] = window.CHALLENGE_ID;
    CTFd.fetch("/api/v1/flags", {
      method: "POST",
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
      .then(function(_response) {
        window.location.reload();
      });
  });
  $("#flag-edit-modal").modal();
}

export function editFlagModal(event) {
  event.preventDefault();
  const flag_id = $(this).attr("flag-id");
  const row = $(this)
    .parent()
    .parent();

  $.get(CTFd.config.urlRoot + "/api/v1/flags/" + flag_id, function(response) {
    const data = response.data;
    $.get(CTFd.config.urlRoot + data.templates.update, function(template_data) {
      $("#edit-flags form").empty();
      $("#edit-flags form").off();

      const template = nunjucks.compile(template_data);
      $("#edit-flags form").append(template.render(data));

      $("#edit-flags form").submit(function(event) {
        event.preventDefault();
        const params = $("#edit-flags form").serializeJSON();

        CTFd.fetch("/api/v1/flags/" + flag_id, {
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
              $(row)
                .find(".flag-content")
                .text(response.data.content);
              $("#edit-flags").modal("toggle");
            }
          });
      });
      $("#edit-flags").modal();
    });
  });
}

export function flagTypeSelect(event) {
  event.preventDefault();
  const flag_type_name = $(this)
    .find("option:selected")
    .text();

  $.get(CTFd.config.urlRoot + "/api/v1/flags/types/" + flag_type_name, function(
    response
  ) {
    const data = response.data;
    $.get(CTFd.config.urlRoot + data.templates.create, function(template_data) {
      const template = nunjucks.compile(template_data);
      $("#create-keys-entry-div").html(template.render());
      $("#create-keys-button-div").show();
    });
  });
}
