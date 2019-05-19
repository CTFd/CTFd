function toggle_account(elem) {
  var btn = $(elem);
  var teamId = btn.attr("team-id");
  var state = btn.attr("state");
  var hidden = undefined;
  if (state == "visible") {
    hidden = true;
  } else if (state == "hidden") {
    hidden = false;
  }

  var params = {
    hidden: hidden
  };

  CTFd.fetch("/api/v1/" + user_mode + "/" + teamId, {
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
        if (hidden) {
          btn.attr("state", "hidden");
          btn.addClass("btn-danger").removeClass("btn-success");
          btn.text("Hidden");
        } else {
          btn.attr("state", "visible");
          btn.addClass("btn-success").removeClass("btn-danger");
          btn.text("Visible");
        }
      }
    });
}
