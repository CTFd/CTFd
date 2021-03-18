import "./main";
import $ from "jquery";
import CTFd from "core/CTFd";
import { htmlEntities } from "core/utils";
import { ezAlert, ezQuery, ezBadge } from "core/ezq";
import { createGraph, updateGraph } from "core/graphs";
import Vue from "vue/dist/vue.esm.browser";
import CommentBox from "../components/comments/CommentBox.vue";
import UserAddForm from "../components/teams/UserAddForm.vue";
import { copyToClipboard } from "../../../../core/assets/js/utils";

function createTeam(event) {
  event.preventDefault();
  const params = $("#team-info-create-form").serializeJSON(true);

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
        $("#team-info-create-form > #results").empty();
        Object.keys(response.errors).forEach(function(key, _index) {
          $("#team-info-create-form > #results").append(
            ezBadge({
              type: "error",
              body: response.errors[key]
            })
          );
          const i = $("#team-info-create-form").find(
            "input[name={0}]".format(key)
          );
          const input = $(i);
          input.addClass("input-filled-invalid");
          input.removeClass("input-filled-valid");
        });
      }
    });
}

function updateTeam(event) {
  event.preventDefault();
  let params = $("#team-info-edit-form").serializeJSON(true);

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

  CTFd.fetch("/api/v1/teams/" + window.TEAM_ID, {
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
        Object.keys(response.errors).forEach(function(key, _index) {
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

function deleteSelectedSubmissions(event, target) {
  let submissions;
  let type;
  let title;
  switch (target) {
    case "solves":
      submissions = $("input[data-submission-type=correct]:checked");
      type = "solve";
      title = "Solves";
      break;
    case "fails":
      submissions = $("input[data-submission-type=incorrect]:checked");
      type = "fail";
      title = "Fails";
      break;
    default:
      break;
  }

  let submissionIDs = submissions.map(function() {
    return $(this).data("submission-id");
  });
  let target_string = submissionIDs.length === 1 ? type : type + "s";

  ezQuery({
    title: `Delete ${title}`,
    body: `Are you sure you want to delete ${
      submissionIDs.length
    } ${target_string}?`,
    success: function() {
      const reqs = [];
      for (var subId of submissionIDs) {
        reqs.push(CTFd.api.delete_submission({ submissionId: subId }));
      }
      Promise.all(reqs).then(_responses => {
        window.location.reload();
      });
    }
  });
}

function deleteSelectedAwards(_event) {
  let awardIDs = $("input[data-award-id]:checked").map(function() {
    return $(this).data("award-id");
  });
  let target = awardIDs.length === 1 ? "award" : "awards";

  ezQuery({
    title: `Delete Awards`,
    body: `Are you sure you want to delete ${awardIDs.length} ${target}?`,
    success: function() {
      const reqs = [];
      for (var awardID of awardIDs) {
        let req = CTFd.fetch("/api/v1/awards/" + awardID, {
          method: "DELETE",
          credentials: "same-origin",
          headers: {
            Accept: "application/json",
            "Content-Type": "application/json"
          }
        });
        reqs.push(req);
      }
      Promise.all(reqs).then(_responses => {
        window.location.reload();
      });
    }
  });
}

function solveSelectedMissingChallenges(event) {
  event.preventDefault();
  let challengeIDs = $("input[data-missing-challenge-id]:checked").map(
    function() {
      return $(this).data("missing-challenge-id");
    }
  );
  let target = challengeIDs.length === 1 ? "challenge" : "challenges";

  ezQuery({
    title: `Mark Correct`,
    body: `Are you sure you want to mark ${
      challengeIDs.length
    } ${target} correct for ${htmlEntities(window.TEAM_NAME)}?`,
    success: function() {
      ezAlert({
        title: `User Attribution`,
        body: `
        Which user on ${htmlEntities(window.TEAM_NAME)} solved these challenges?
        <div class="pb-3" id="query-team-member-solve">
        ${$("#team-member-select").html()}
        </div>
        `,
        button: "Mark Correct",
        success: function() {
          const USER_ID = $("#query-team-member-solve > select").val();
          const reqs = [];
          for (var challengeID of challengeIDs) {
            let params = {
              provided: "MARKED AS SOLVED BY ADMIN",
              user_id: USER_ID,
              team_id: window.TEAM_ID,
              challenge_id: challengeID,
              type: "correct"
            };

            let req = CTFd.fetch("/api/v1/submissions", {
              method: "POST",
              credentials: "same-origin",
              headers: {
                Accept: "application/json",
                "Content-Type": "application/json"
              },
              body: JSON.stringify(params)
            });
            reqs.push(req);
          }
          Promise.all(reqs).then(_responses => {
            window.location.reload();
          });
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
  $("#team-captain-form").submit(function(e) {
    e.preventDefault();
    const params = $("#team-captain-form").serializeJSON(true);

    CTFd.fetch("/api/v1/teams/" + window.TEAM_ID, {
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

  $(".edit-team").click(function(_e) {
    $("#team-info-edit-modal").modal("toggle");
  });

  $(".invite-team").click(function(_e) {
    CTFd.fetch(`/api/v1/teams/${window.TEAM_ID}/members`, {
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
          $("#team-invite-modal").modal("toggle");
        }
      });
  });

  $("#team-invite-link-copy").click(function(e) {
    copyToClipboard(e, "#team-invite-link");
  });

  $(".members-team").click(function(_e) {
    $("#team-add-modal").modal("toggle");
  });

  $(".edit-captain").click(function(_e) {
    $("#team-captain-modal").modal("toggle");
  });

  $(".award-team").click(function(_e) {
    $("#team-award-modal").modal("toggle");
  });

  $(".addresses-team").click(function(_event) {
    $("#team-addresses-modal").modal("toggle");
  });

  $("#user-award-form").submit(function(e) {
    e.preventDefault();
    const params = $("#user-award-form").serializeJSON(true);
    params["user_id"] = $("#award-member-input").val();
    params["team_id"] = window.TEAM_ID;

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
          Object.keys(response.errors).forEach(function(key, _index) {
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
      body: "Are you sure you want to remove {0} from {1}? <br><br><strong>All of their challenge solves, attempts, awards, and unlocked hints will also be deleted!</strong>".format(
        "<strong>" + htmlEntities(member_name) + "</strong>",
        "<strong>" + htmlEntities(window.TEAM_NAME) + "</strong>"
      ),
      success: function() {
        CTFd.fetch("/api/v1/teams/" + window.TEAM_ID + "/members", {
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

  $(".delete-team").click(function(_e) {
    ezQuery({
      title: "Delete Team",
      body: "Are you sure you want to delete {0}".format(
        "<strong>" + htmlEntities(window.TEAM_NAME) + "</strong>"
      ),
      success: function() {
        CTFd.fetch("/api/v1/teams/" + window.TEAM_ID, {
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

  $("#solves-delete-button").click(function(e) {
    deleteSelectedSubmissions(e, "solves");
  });

  $("#fails-delete-button").click(function(e) {
    deleteSelectedSubmissions(e, "fails");
  });

  $("#awards-delete-button").click(function(e) {
    deleteSelectedAwards(e);
  });

  $("#missing-solve-button").click(function(e) {
    solveSelectedMissingChallenges(e);
  });

  $("#team-info-create-form").submit(createTeam);

  $("#team-info-edit-form").submit(updateTeam);

  // Insert CommentBox element
  const commentBox = Vue.extend(CommentBox);
  let vueContainer = document.createElement("div");
  document.querySelector("#comment-box").appendChild(vueContainer);
  new commentBox({
    propsData: { type: "team", id: window.TEAM_ID }
  }).$mount(vueContainer);

  // Insert team member addition form
  const userAddForm = Vue.extend(UserAddForm);
  let memberFormContainer = document.createElement("div");
  document
    .querySelector("#team-add-modal .modal-body")
    .appendChild(memberFormContainer);
  new userAddForm({
    propsData: { team_id: window.TEAM_ID }
  }).$mount(memberFormContainer);

  let type, id, name, account_id;
  ({ type, id, name, account_id } = window.stats_data);

  let intervalId;
  $("#team-statistics-modal").on("shown.bs.modal", function(_e) {
    createGraphs(type, id, name, account_id);
    intervalId = setInterval(() => {
      updateGraphs(type, id, name, account_id);
    }, 300000);
  });

  $("#team-statistics-modal").on("hidden.bs.modal", function(_e) {
    clearInterval(intervalId);
  });

  $(".statistics-team").click(function(_event) {
    $("#team-statistics-modal").modal("toggle");
  });
});
