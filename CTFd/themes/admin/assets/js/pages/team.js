import "./main";
import $ from "jquery";
import CTFd from "core/CTFd";
import { htmlEntities } from "core/utils";
import { ezQuery, ezBadge } from "core/ezq";
import { createGraph, updateGraph } from "core/graphs";

function createTeam(event) {
  event.preventDefault();
  const params = $("#team-info-create-form").serializeJSON(true);

  CTFd.fetch("/api/v1/teams", {
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
        const team_id = response.data.id;
        window.location = CTFd.config.urlRoot + "/admin/teams/" + team_id;
      } else {
        $("#team-info-form > #results").empty();
        Object.keys(response.errors).forEach(function(key, index) {
          $("#team-info-form > #results").append(
            ezBadge({
              type: "error",
              body: response.errors[key]
            })
          );
          const i = $("#team-info-form").find("input[name={0}]".format(key));
          const input = $(i);
          input.addClass("input-filled-invalid");
          input.removeClass("input-filled-valid");
        });
      }
    });
}

function updateTeam(event) {
  event.preventDefault();
  const params = $("#team-info-edit-form").serializeJSON(true);

  CTFd.fetch("/api/v1/teams/" + TEAM_ID, {
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
        $("#team-info-form > #results").empty();
        Object.keys(response.errors).forEach(function(key, index) {
          $("#team-info-form > #results").append(
            ezBadge({
              type: "error",
              body: response.errors[key]
            })
          );
          const i = $("#team-info-form").find("input[name={0}]".format(key));
          const input = $(i);
          input.addClass("input-filled-invalid");
          input.removeClass("input-filled-valid");
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
  $("#team-captain-form").submit(function(e) {
    e.preventDefault();
    const params = $("#team-captain-form").serializeJSON(true);

    CTFd.fetch("/api/v1/teams/" + TEAM_ID, {
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
          Object.keys(response.errors).forEach(function(key, index) {
            $("#team-captain-form > #results").append(
              ezBadge({
                type: "error",
                body: response.errors[key]
              })
            );
            const i = $("#team-captain-form").find(
              "select[name={0}]".format(key)
            );
            const input = $(i);
            input.addClass("input-filled-invalid");
            input.removeClass("input-filled-valid");
          });
        }
      });
  });

  $(".edit-team").click(function(e) {
    $("#team-info-edit-modal").modal("toggle");
  });

  $(".edit-captain").click(function(e) {
    $("#team-captain-modal").modal("toggle");
  });

  $(".award-team").click(function(e) {
    $("#team-award-modal").modal("toggle");
  });

  $("#user-award-form").submit(function(e) {
    e.preventDefault();
    const params = $("#user-award-form").serializeJSON(true);
    params["user_id"] = $("#award-member-input").val();

    $("#user-award-form > #results").empty();

    if (!params["user_id"]) {
      $("#user-award-form > #results").append(
        ezBadge({
          type: "error",
          body: "Please select a team member"
        })
      );
      return;
    }
    params["user_id"] = parseInt(params["user_id"]);

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
  });

  $(".delete-member").click(function(e) {
    e.preventDefault();
    const member_id = $(this).attr("member-id");
    const member_name = $(this).attr("member-name");

    const params = {
      user_id: member_id
    };

    const row = $(this)
      .parent()
      .parent();

    ezQuery({
      title: "Remove Member",
      body: "Are you sure you want to remove {0} from {1}? <br><br><strong>All of their challenges solves, attempts, awards, and unlocked hints will also be deleted!</strong>".format(
        "<strong>" + htmlEntities(member_name) + "</strong>",
        "<strong>" + htmlEntities(TEAM_NAME) + "</strong>"
      ),
      success: function() {
        CTFd.fetch("/api/v1/teams/" + TEAM_ID + "/members", {
          method: "DELETE",
          body: JSON.stringify(params)
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

  $(".delete-team").click(function(e) {
    ezQuery({
      title: "Delete Team",
      body: "Are you sure you want to delete {0}".format(
        "<strong>" + htmlEntities(TEAM_NAME) + "</strong>"
      ),
      success: function() {
        CTFd.fetch("/api/v1/teams/" + TEAM_ID, {
          method: "DELETE"
        })
          .then(function(response) {
            return response.json();
          })
          .then(function(response) {
            if (response.success) {
              window.location = CTFd.config.urlRoot + "/admin/teams";
            }
          });
      }
    });
  });

  $(".delete-submission").click(function(e) {
    e.preventDefault();
    const submission_id = $(this).attr("submission-id");
    const submission_type = $(this).attr("submission-type");
    const submission_challenge = $(this).attr("submission-challenge");

    const body = "<span>Are you sure you want to delete <strong>{0}</strong> submission from <strong>{1}</strong> for <strong>{2}</strong>?</span>".format(
      htmlEntities(submission_type),
      htmlEntities(TEAM_NAME),
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
  });

  $(".delete-award").click(function(e) {
    e.preventDefault();
    const award_id = $(this).attr("award-id");
    const award_name = $(this).attr("award-name");

    const body = "<span>Are you sure you want to delete the <strong>{0}</strong> award from <strong>{1}</strong>?".format(
      htmlEntities(award_name),
      htmlEntities(TEAM_NAME)
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
  });

  $("#team-info-create-form").submit(createTeam);

  $("#team-info-edit-form").submit(updateTeam);

  let type, id, name, account_id;
  ({ type, id, name, account_id } = window.stats_data);

  createGraphs(type, id, name, account_id);
  setInterval(() => {
    updateGraphs(type, id, name, account_id);
  }, 300000);
});
