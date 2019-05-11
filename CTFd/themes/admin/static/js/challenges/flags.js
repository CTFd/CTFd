$(document).ready(function() {
  $("#flag-add-button").click(function(e) {
    $.get(script_root + "/api/v1/flags/types", function(response) {
      var data = response.data;
      var flag_type_select = $("#flags-create-select");
      flag_type_select.empty();

      var option = "<option> -- </option>";
      flag_type_select.append(option);

      for (var key in data) {
        if (data.hasOwnProperty(key)) {
          option = "<option value='{0}'>{1}</option>".format(
            key,
            data[key].name
          );
          flag_type_select.append(option);
        }
      }
      $("#flag-edit-modal").modal();
    });

    $("#flag-edit-modal form").submit(function(e) {
      e.preventDefault();
      var params = $(this).serializeJSON(true);
      params["challenge"] = CHALLENGE_ID;
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
        .then(function(response) {
          window.location.reload();
        });
    });
    $("#flag-edit-modal").modal();
  });

  $("#flags-create-select").change(function(e) {
    e.preventDefault();
    var flag_type_name = $(this)
      .find("option:selected")
      .text();

    $.get(script_root + "/api/v1/flags/types/" + flag_type_name, function(
      response
    ) {
      var data = response.data;
      $.get(script_root + data.templates.create, function(template_data) {
        var template = nunjucks.compile(template_data);
        $("#create-keys-entry-div").html(template.render());
        $("#create-keys-button-div").show();
      });
    });
  });

  $(".edit-flag").click(function(e) {
    e.preventDefault();
    var flag_id = $(this).attr("flag-id");
    var row = $(this)
      .parent()
      .parent();

    $.get(script_root + "/api/v1/flags/" + flag_id, function(response) {
      var data = response.data;
      $.get(script_root + data.templates.update, function(template_data) {
        $("#edit-flags form").empty();

        var template = nunjucks.compile(template_data);
        $("#edit-flags form").append(template.render(data));

        $("#edit-flags form").submit(function(e) {
          e.preventDefault();
          var params = $("#edit-flags form").serializeJSON();

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
  });

  $(".delete-flag").click(function(e) {
    e.preventDefault();
    var flag_id = $(this).attr("flag-id");
    var row = $(this)
      .parent()
      .parent();

    ezq({
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
  });
});
