$(document).ready(function() {
  $(".delete-user").click(function(e) {
    ezq({
      title: "Delete User",
      body: "Are you sure you want to delete {0}".format(
        "<strong>" + htmlentities(USER_NAME) + "</strong>"
      ),
      success: function() {
        CTFd.fetch("/api/v1/users/" + USER_ID, {
          method: "DELETE"
        })
          .then(function(response) {
            return response.json();
          })
          .then(function(response) {
            if (response.success) {
              window.location = script_root + "/admin/users";
            }
          });
      }
    });
  });

  $(".edit-user").click(function(e) {
    $("#user-info-modal").modal("toggle");
  });

  $(".award-user").click(function(e) {
    $("#user-award-modal").modal("toggle");
  });

  $(".email-user").click(function(e) {
    $("#user-email-modal").modal("toggle");
  });

  $("#user-award-form").submit(function(e) {
    e.preventDefault();
    var params = $("#user-award-form").serializeJSON(true);
    params["user_id"] = USER_ID;
    CTFd.fetch("/api/v1/awards", {
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
        if (response.success) {
          window.location.reload();
        } else {
          $("#user-award-form > #results").empty();
          Object.keys(response.errors).forEach(function(key, index) {
            $("#user-award-form > #results").append(
              ezbadge({
                type: "error",
                body: response.errors[key]
              })
            );
            var i = $("#user-award-form").find("input[name={0}]".format(key));
            var input = $(i);
            input.addClass("input-filled-invalid");
            input.removeClass("input-filled-valid");
          });
        }
      });
  });

  $("#user-mail-form").submit(function(e) {
    e.preventDefault();
    var params = $("#user-mail-form").serializeJSON(true);
    CTFd.fetch("/api/v1/users/" + USER_ID + "/email", {
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
        if (response.success) {
          $("#user-mail-form > #results").append(
            ezbadge({
              type: "success",
              body: "E-Mail sent successfully!"
            })
          );
          $("#user-mail-form")
            .find("input[type=text], textarea")
            .val("");
        } else {
          $("#user-mail-form > #results").empty();
          Object.keys(response.errors).forEach(function(key, index) {
            $("#user-mail-form > #results").append(
              ezbadge({
                type: "error",
                body: response.errors[key]
              })
            );
            var i = $("#user-mail-form").find(
              "input[name={0}], textarea[name={0}]".format(key)
            );
            var input = $(i);
            input.addClass("input-filled-invalid");
            input.removeClass("input-filled-valid");
          });
        }
      });
  });

  $(".delete-submission").click(function(e) {
    e.preventDefault();
    var submission_id = $(this).attr("submission-id");
    var submission_type = $(this).attr("submission-type");
    var submission_challenge = $(this).attr("submission-challenge");

    var body = "<span>Are you sure you want to delete <strong>{0}</strong> submission from <strong>{1}</strong> for <strong>{2}</strong>?</span>".format(
      htmlentities(submission_type),
      htmlentities(USER_NAME),
      htmlentities(submission_challenge)
    );

    var row = $(this)
      .parent()
      .parent();

    ezq({
      title: "Delete Submission",
      body: body,
      success: function() {
        CTFd.fetch("/api/v1/submissions/" + submission_id, {
          method: "DELETE",
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
              row.remove();
            }
          });
      }
    });
  });

  $(".delete-award").click(function(e) {
    e.preventDefault();
    var award_id = $(this).attr("award-id");
    var award_name = $(this).attr("award-name");

    var body = "<span>Are you sure you want to delete the <strong>{0}</strong> award from <strong>{1}</strong>?".format(
      htmlentities(award_name),
      htmlentities(USER_NAME)
    );

    var row = $(this)
      .parent()
      .parent();

    ezq({
      title: "Delete Award",
      body: body,
      success: function() {
        CTFd.fetch("/api/v1/awards/" + award_id, {
          method: "DELETE",
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
              row.remove();
            }
          });
      }
    });
  });

  $(".correct-submission").click(function(e) {
    var challenge_id = $(this).attr("challenge-id");
    var challenge_name = $(this).attr("challenge-name");
    var row = $(this)
      .parent()
      .parent();

    var body = "<span>Are you sure you want to mark <strong>{0}</strong> solved for from <strong>{1}</strong>?".format(
      htmlentities(challenge_name),
      htmlentities(USER_NAME)
    );

    var params = {
      provided: "MARKED AS SOLVED BY ADMIN",
      user_id: USER_ID,
      team_id: TEAM_ID,
      challenge_id: challenge_id,
      type: "correct"
    };

    ezq({
      title: "Mark Correct",
      body: body,
      success: function() {
        CTFd.fetch("/api/v1/submissions", {
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
            if (response.success) {
              // TODO: Refresh missing and solves instead of reloading
              row.remove();
              window.location.reload();
            }
          });
      }
    });
  });
});
