import "./main";
import $ from "jquery";
import CTFd from "core/CTFd";
import { htmlEntities } from "core/utils";
import { ezQuery, ezBadge } from "core/ezq";
import { createGraph, updateGraph } from "core/graphs";

function createUser(event) {
  event.preventDefault();
  const params = $("#user-info-create-form").serializeJSON(true);

  CTFd.fetch("/api/v1/users", {
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
        const user_id = response.data.id;
        window.location = CTFd.config.urlRoot + "/admin/users/" + user_id;
      } else {
        $("#user-info-create-form > #results").empty();
        Object.keys(response.errors).forEach(function(key, index) {
          $("#user-info-create-form > #results").append(
            ezBadge({
              type: "error",
              body: response.errors[key]
            })
          );
          const i = $("#user-info-form").find("input[name={0}]".format(key));
          const input = $(i);
          input.addClass("input-filled-invalid");
          input.removeClass("input-filled-valid");
        });
      }
    });
}

function updateUser(event) {
  event.preventDefault();
  const params = $("#user-info-edit-form").serializeJSON(true);

  CTFd.fetch("/api/v1/users/" + USER_ID, {
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
        $("#user-info-edit-form > #results").empty();
        Object.keys(response.errors).forEach(function(key, index) {
          $("#user-info-edit-form > #results").append(
            ezBadge({
              type: "error",
              body: response.errors[key]
            })
          );
          const i = $("#user-info-edit-form").find(
            "input[name={0}]".format(key)
          );
          const input = $(i);
          input.addClass("input-filled-invalid");
          input.removeClass("input-filled-valid");
        });
      }
    });
}

function deleteUser(event) {
  event.preventDefault();
  ezQuery({
    title: "Delete User",
    body: "Are you sure you want to delete {0}".format(
      "<strong>" + htmlEntities(USER_NAME) + "</strong>"
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
            window.location = CTFd.config.urlRoot + "/admin/users";
          }
        });
    }
  });
}

function awardUser(event) {
  event.preventDefault();
  const params = $("#user-award-form").serializeJSON(true);
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
            ezBadge({
              type: "error",
              body: response.errors[key]
            })
          );
          const i = $("#user-award-form").find("input[name={0}]".format(key));
          const input = $(i);
          input.addClass("input-filled-invalid");
          input.removeClass("input-filled-valid");
        });
      }
    });
}

function emailUser(event) {
  event.preventDefault();
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
          ezBadge({
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
            ezBadge({
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
}

function deleteUserSubmission(event) {
  event.preventDefault();
  const submission_id = $(this).attr("submission-id");
  const submission_type = $(this).attr("submission-type");
  const submission_challenge = $(this).attr("submission-challenge");

  const body = "<span>Are you sure you want to delete <strong>{0}</strong> submission from <strong>{1}</strong> for <strong>{2}</strong>?</span>".format(
    htmlEntities(submission_type),
    htmlEntities(USER_NAME),
    htmlEntities(submission_challenge)
  );

  const row = $(this)
    .parent()
    .parent();

  ezQuery({
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
}

function deleteUserAward(event) {
  event.preventDefault();
  const award_id = $(this).attr("award-id");
  const award_name = $(this).attr("award-name");

  const body = "<span>Are you sure you want to delete the <strong>{0}</strong> award from <strong>{1}</strong>?".format(
    htmlEntities(award_name),
    htmlEntities(USER_NAME)
  );

  const row = $(this)
    .parent()
    .parent();

  ezQuery({
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
}

function correctUserSubmission(event) {
  event.preventDefault();
  const challenge_id = $(this).attr("challenge-id");
  const challenge_name = $(this).attr("challenge-name");
  const row = $(this)
    .parent()
    .parent();

  const body = "<span>Are you sure you want to mark <strong>{0}</strong> solved for from <strong>{1}</strong>?".format(
    htmlEntities(challenge_name),
    htmlEntities(USER_NAME)
  );

  const params = {
    provided: "MARKED AS SOLVED BY ADMIN",
    user_id: USER_ID,
    team_id: TEAM_ID,
    challenge_id: challenge_id,
    type: "correct"
  };

  ezQuery({
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
}

const api_funcs = {
  team: [
    x => CTFd.api.get_team_solves({ teamId: x }),
    x => CTFd.api.get_team_fails({ teamId: x }),
    x => CTFd.api.get_team_awards({ teamId: x })
  ],
  user: [
    x => CTFd.api.get_user_solves({ userId: x }),
    x => CTFd.api.get_user_fails({ userId: x }),
    x => CTFd.api.get_user_awards({ userId: x })
  ]
};

const createGraphs = (type, id, name, account_id) => {
  let [solves_func, fails_func, awards_func] = api_funcs[type];

  Promise.all([
    solves_func(account_id),
    fails_func(account_id),
    awards_func(account_id)
  ]).then(responses => {
    createGraph(
      "score_graph",
      "#score-graph",
      responses,
      type,
      id,
      name,
      account_id
    );
    createGraph(
      "category_breakdown",
      "#categories-pie-graph",
      responses,
      type,
      id,
      name,
      account_id
    );
    createGraph(
      "solve_percentages",
      "#keys-pie-graph",
      responses,
      type,
      id,
      name,
      account_id
    );
  });
};

const updateGraphs = (type, id, name, account_id) => {
  let [solves_func, fails_func, awards_func] = api_funcs[type];

  Promise.all([
    solves_func(account_id),
    fails_func(account_id),
    awards_func(account_id)
  ]).then(responses => {
    updateGraph(
      "score_graph",
      "#score-graph",
      responses,
      type,
      id,
      name,
      account_id
    );
    updateGraph(
      "category_breakdown",
      "#categories-pie-graph",
      responses,
      type,
      id,
      name,
      account_id
    );
    updateGraph(
      "solve_percentages",
      "#keys-pie-graph",
      responses,
      type,
      id,
      name,
      account_id
    );
  });
};

$(() => {
  $(".delete-user").click(deleteUser);

  $(".edit-user").click(function(event) {
    $("#user-info-modal").modal("toggle");
  });

  $(".award-user").click(function(event) {
    $("#user-award-modal").modal("toggle");
  });

  $(".email-user").click(function(event) {
    $("#user-email-modal").modal("toggle");
  });

  $("#user-mail-form").submit(emailUser);

  $(".delete-submission").click(deleteUserSubmission);
  $(".delete-award").click(deleteUserAward);
  $(".correct-submission").click(correctUserSubmission);

  $("#user-info-create-form").submit(createUser);

  $("#user-info-edit-form").submit(updateUser);
  $("#user-award-form").submit(awardUser);

  let type, id, name, account_id;
  ({ type, id, name, account_id } = window.stats_data);

  createGraphs(type, id, name, account_id);
  setInterval(() => {
    updateGraphs(type, id, name, account_id);
  }, 300000);
});
