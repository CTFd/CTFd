function hint(id) {
  return CTFd.fetch("/api/v1/hints/" + id + "?preview=true", {
    method: "GET",
    credentials: "same-origin",
    headers: {
      Accept: "application/json",
      "Content-Type": "application/json"
    }
  }).then(function(response) {
    return response.json();
  });
}

function loadhint(hintid) {
  var md = window.markdownit({
    html: true,
    linkify: true
  });

  hint(hintid).then(function(response) {
    if (response.data.content) {
      ezal({
        title: "Hint",
        body: md.render(response.data.content),
        button: "Got it!"
      });
    } else {
      ezal({
        title: "Error",
        body: "Error loading hint!",
        button: "OK"
      });
    }
  });
}

$(document).ready(function() {
  $("#hint-add-button").click(function(e) {
    $("#hint-edit-modal form")
      .find("input, textarea")
      .val("");

    // Markdown Preview
    $("#new-hint-edit").on("shown.bs.tab", function(event) {
      console.log(event.target.hash);
      if (event.target.hash == "#hint-preview") {
        console.log(event.target.hash);
        var renderer = window.markdownit({
          html: true,
          linkify: true
        });
        var editor_value = $("#hint-write textarea").val();
        $(event.target.hash).html(renderer.render(editor_value));
      }
    });

    $("#hint-edit-modal").modal();
  });

  $(".delete-hint").click(function(e) {
    e.preventDefault();
    var hint_id = $(this).attr("hint-id");
    var row = $(this)
      .parent()
      .parent();
    ezq({
      title: "Delete Hint",
      body: "Are you sure you want to delete this hint?",
      success: function() {
        CTFd.fetch("/api/v1/hints/" + hint_id, {
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

  $(".edit-hint").click(function(e) {
    e.preventDefault();
    var hint_id = $(this).attr("hint-id");

    CTFd.fetch("/api/v1/hints/" + hint_id + "?preview=true", {
      method: "GET",
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
          $("#hint-edit-form input[name=content],textarea[name=content]").val(
            response.data.content
          );
          $("#hint-edit-form input[name=cost]").val(response.data.cost);
          $("#hint-edit-form input[name=id]").val(response.data.id);

          // Markdown Preview
          $("#new-hint-edit").on("shown.bs.tab", function(event) {
            console.log(event.target.hash);
            if (event.target.hash == "#hint-preview") {
              console.log(event.target.hash);
              var renderer = new markdownit({
                html: true,
                linkify: true
              });
              var editor_value = $("#hint-write textarea").val();
              $(event.target.hash).html(renderer.render(editor_value));
            }
          });

          $("#hint-edit-modal").modal();
        }
      });
  });

  $("#hint-edit-form").submit(function(e) {
    e.preventDefault();
    var params = $(this).serializeJSON(true);
    params["challenge"] = CHALLENGE_ID;

    var method = "POST";
    var url = "/api/v1/hints";
    if (params.id) {
      method = "PATCH";
      url = "/api/v1/hints/" + params.id;
    }
    CTFd.fetch(url, {
      method: method,
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
          // TODO: Refresh hints on submit.
          window.location.reload();
        }
      });
  });
});
