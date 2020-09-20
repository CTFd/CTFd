import "./main";
import $ from "jquery";
import CTFd from "core/CTFd";
import { htmlEntities } from "core/utils";
import { ezQuery, ezBadge } from "core/ezq";
import { createGraph, updateGraph } from "core/graphs";
import Vue from "vue/dist/vue.esm.browser";
import CommentBox from "../components/comments/CommentBox.vue";

function createUser(event) {
  event.preventDefault();
  const params = $("#user-info-create-form").serializeJSON(true);

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

  // Move the notify value into a GET param
  let url = "/api/v1/users";
  let notify = params.notify;
  if (notify === true) {
    url = `${url}?notify=true`;
  }
  delete params.notify;

  CTFd.fetch(url, {
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
        Object.keys(response.errors).forEach(function(key, _index) {
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

  CTFd.fetch("/api/v1/users/" + window.USER_ID, {
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
        Object.keys(response.errors).forEach(function(key, _index) {
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
      "<strong>" + htmlEntities(window.USER_NAME) + "</strong>"
    ),
    success: function() {
      CTFd.fetch("/api/v1/users/" + window.USER_ID, {
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
  params["user_id"] = window.USER_ID;

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
}

function emailUser(event) {
  event.preventDefault();
  var params = $("#user-mail-form").serializeJSON(true);
  CTFd.fetch("/api/v1/users/" + window.USER_ID + "/email", {
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
        Object.keys(response.errors).forEach(function(key, _index) {
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
    } ${target} correct for ${htmlEntities(window.USER_NAME)}?`,
    success: function() {
      const reqs = [];
      for (var challengeID of challengeIDs) {
        let params = {
          provided: "MARKED AS SOLVED BY ADMIN",
          user_id: window.USER_ID,
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

  $(".edit-user").click(function(_event) {
    $("#user-info-modal").modal("toggle");
  });

  $(".award-user").click(function(_event) {
    $("#user-award-modal").modal("toggle");
  });

  $(".email-user").click(function(_event) {
    $("#user-email-modal").modal("toggle");
  });

  $(".addresses-user").click(function(_event) {
    $("#user-addresses-modal").modal("toggle");
  });

  $("#user-mail-form").submit(emailUser);

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

  $("#user-info-create-form").submit(createUser);

  $("#user-info-edit-form").submit(updateUser);
  $("#user-award-form").submit(awardUser);

  // Insert CommentBox element
  const commentBox = Vue.extend(CommentBox);
  let vueContainer = document.createElement("div");
  document.querySelector("#comment-box").appendChild(vueContainer);
  new commentBox({
    propsData: { type: "user", id: window.USER_ID }
  }).$mount(vueContainer);

  let type, id, name, account_id;
  ({ type, id, name, account_id } = window.stats_data);

  let intervalId;
  $("#user-statistics-modal").on("shown.bs.modal", function(_e) {
    createGraphs(type, id, name, account_id);
    intervalId = setInterval(() => {
      updateGraphs(type, id, name, account_id);
    }, 300000);
  });

  $("#user-statistics-modal").on("hidden.bs.modal", function(_e) {
    clearInterval(intervalId);
  });

  $(".statistics-user").click(function(_event) {
    $("#user-statistics-modal").modal("toggle");
  });
});
