$(document).ready(function() {
  $("#prerequisite-add-form").submit(function(e) {
    e.preventDefault();
    var requirements = $("#prerequisite-add-form").serializeJSON();
    CHALLENGE_REQUIREMENTS.prerequisites.push(
      parseInt(requirements["prerequisite"])
    );

    var params = {
      requirements: CHALLENGE_REQUIREMENTS
    };

    CTFd.fetch("/api/v1/challenges/" + CHALLENGE_ID, {
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
      .then(function(data) {
        if (data.success) {
          // TODO: Make this refresh requirements
          window.location.reload();
        }
      });
  });

  $(".delete-requirement").click(function(e) {
    var challenge_id = $(this).attr("challenge-id");
    var row = $(this)
      .parent()
      .parent();

    CHALLENGE_REQUIREMENTS.prerequisites.pop(challenge_id);

    var params = {
      requirements: CHALLENGE_REQUIREMENTS
    };

    CTFd.fetch("/api/v1/challenges/" + CHALLENGE_ID, {
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
      .then(function(data) {
        if (data.success) {
          row.remove();
        }
      });
  });
});
