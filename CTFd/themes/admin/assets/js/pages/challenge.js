import "./main";
import "core/utils";
import $ from "jquery";
import "bootstrap/js/dist/tab";
import CTFd from "core/CTFd";
import { htmlEntities } from "core/utils";
import { ezQuery, ezAlert, ezToast } from "core/ezq";
import { default as helpers } from "core/helpers";
import { bindMarkdownEditors } from "../styles";
import Vue from "vue/dist/vue.esm.browser";
import CommentBox from "../components/comments/CommentBox.vue";
import FlagList from "../components/flags/FlagList.vue";
import Requirements from "../components/requirements/Requirements.vue";
import TopicsList from "../components/topics/TopicsList.vue";
import TagsList from "../components/tags/TagsList.vue";
import ChallengeFilesList from "../components/files/ChallengeFilesList.vue";
import HintsList from "../components/hints/HintsList.vue";
import NextChallenge from "../components/next/NextChallenge.vue";
import hljs from "highlight.js";

const displayHint = data => {
  ezAlert({
    title: "Hint",
    body: data.html,
    button: "Got it!"
  });
};

const loadHint = id => {
  CTFd.api.get_hint({ hintId: id, preview: true }).then(response => {
    if (response.data.content) {
      displayHint(response.data);
      return;
    }
    // displayUnlock(id);
  });
};

function renderSubmissionResponse(response, cb) {
  var result = response.data;

  var result_message = $("#result-message");
  var result_notification = $("#result-notification");
  var answer_input = $("#submission-input");
  result_notification.removeClass();
  result_message.text(result.message);

  if (result.status === "authentication_required") {
    window.location =
      CTFd.config.urlRoot +
      "/login?next=" +
      CTFd.config.urlRoot +
      window.location.pathname +
      window.location.hash;
    return;
  } else if (result.status === "incorrect") {
    // Incorrect key
    result_notification.addClass(
      "alert alert-danger alert-dismissable text-center"
    );
    result_notification.slideDown();

    answer_input.removeClass("correct");
    answer_input.addClass("wrong");
    setTimeout(function() {
      answer_input.removeClass("wrong");
    }, 3000);
  } else if (result.status === "correct") {
    // Challenge Solved
    result_notification.addClass(
      "alert alert-success alert-dismissable text-center"
    );
    result_notification.slideDown();

    $(".challenge-solves").text(
      parseInt(
        $(".challenge-solves")
          .text()
          .split(" ")[0]
      ) +
        1 +
        " Solves"
    );

    answer_input.val("");
    answer_input.removeClass("wrong");
    answer_input.addClass("correct");
  } else if (result.status === "already_solved") {
    // Challenge already solved
    result_notification.addClass(
      "alert alert-info alert-dismissable text-center"
    );
    result_notification.slideDown();

    answer_input.addClass("correct");
  } else if (result.status === "paused") {
    // CTF is paused
    result_notification.addClass(
      "alert alert-warning alert-dismissable text-center"
    );
    result_notification.slideDown();
  } else if (result.status === "ratelimited") {
    // Keys per minute too high
    result_notification.addClass(
      "alert alert-warning alert-dismissable text-center"
    );
    result_notification.slideDown();

    answer_input.addClass("too-fast");
    setTimeout(function() {
      answer_input.removeClass("too-fast");
    }, 3000);
  }
  setTimeout(function() {
    $(".alert").slideUp();
    $("#challenge-submit").removeClass("disabled-button");
    $("#challenge-submit").prop("disabled", false);
  }, 3000);

  if (cb) {
    cb(result);
  }
}

function loadChalTemplate(challenge) {
  CTFd._internal.challenge = {};
  $.getScript(CTFd.config.urlRoot + challenge.scripts.view, function() {
    let template_data = challenge.create;
    $("#create-chal-entry-div").html(template_data);
    bindMarkdownEditors();

    $.getScript(CTFd.config.urlRoot + challenge.scripts.create, function() {
      $("#create-chal-entry-div form").submit(function(event) {
        event.preventDefault();
        const params = $("#create-chal-entry-div form").serializeJSON();
        CTFd.fetch("/api/v1/challenges", {
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
              $("#challenge-create-options #challenge_id").val(
                response.data.id
              );
              $("#challenge-create-options").modal();
            } else {
              let body = "";
              for (const k in response.errors) {
                body += response.errors[k].join("\n");
                body += "\n";
              }

              ezAlert({
                title: "Error",
                body: body,
                button: "OK"
              });
            }
          });
      });
    });
  });
}

function handleChallengeOptions(event) {
  event.preventDefault();
  var params = $(event.target).serializeJSON(true);
  let flag_params = {
    challenge_id: params.challenge_id,
    content: params.flag || "",
    type: params.flag_type,
    data: params.flag_data ? params.flag_data : ""
  };
  // Define a save_challenge function
  let save_challenge = function() {
    CTFd.fetch("/api/v1/challenges/" + params.challenge_id, {
      method: "PATCH",
      credentials: "same-origin",
      headers: {
        Accept: "application/json",
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        state: params.state
      })
    })
      .then(function(response) {
        return response.json();
      })
      .then(function(data) {
        if (data.success) {
          setTimeout(function() {
            window.location =
              CTFd.config.urlRoot + "/admin/challenges/" + params.challenge_id;
          }, 700);
        }
      });
  };

  Promise.all([
    // Save flag
    new Promise(function(resolve, _reject) {
      if (flag_params.content.length == 0) {
        resolve();
        return;
      }
      CTFd.fetch("/api/v1/flags", {
        method: "POST",
        credentials: "same-origin",
        headers: {
          Accept: "application/json",
          "Content-Type": "application/json"
        },
        body: JSON.stringify(flag_params)
      }).then(function(response) {
        resolve(response.json());
      });
    }),
    // Upload files
    new Promise(function(resolve, _reject) {
      let form = event.target;
      let data = {
        challenge: params.challenge_id,
        type: "challenge"
      };
      let filepath = $(form.elements["file"]).val();
      if (filepath) {
        helpers.files.upload(form, data);
      }
      resolve();
    })
  ]).then(_responses => {
    save_challenge();
  });
}

$(() => {
  $(".preview-challenge").click(function(_e) {
    CTFd._internal.challenge = {};
    $.get(
      CTFd.config.urlRoot + "/api/v1/challenges/" + window.CHALLENGE_ID,
      function(response) {
        // Preview should not show any solves
        var challenge_data = response.data;
        challenge_data["solves"] = null;

        $.getScript(
          CTFd.config.urlRoot + challenge_data.type_data.scripts.view,
          function() {
            const challenge = CTFd._internal.challenge;

            // Inject challenge data into the plugin
            challenge.data = response.data;

            $("#challenge-window").empty();

            // Call preRender function in plugin
            challenge.preRender();

            $("#challenge-window").append(challenge_data.view);

            $("#challenge-window #challenge-input").addClass("form-control");
            $("#challenge-window #challenge-submit").addClass(
              "btn btn-md btn-outline-secondary float-right"
            );

            $(".challenge-solves").hide();
            $(".nav-tabs a").click(function(e) {
              e.preventDefault();
              $(this).tab("show");
            });

            // Handle modal toggling
            $("#challenge-window").on("hide.bs.modal", function(_event) {
              $("#challenge-input").removeClass("wrong");
              $("#challenge-input").removeClass("correct");
              $("#incorrect-key").slideUp();
              $("#correct-key").slideUp();
              $("#already-solved").slideUp();
              $("#too-fast").slideUp();
            });

            $(".load-hint").on("click", function(_event) {
              loadHint($(this).data("hint-id"));
            });

            $("#challenge-submit").click(function(e) {
              e.preventDefault();
              $("#challenge-submit").addClass("disabled-button");
              $("#challenge-submit").prop("disabled", true);
              CTFd._internal.challenge
                .submit(true)
                .then(renderSubmissionResponse);
              // Preview passed as true
            });

            $("#challenge-input").keyup(function(event) {
              if (event.keyCode == 13) {
                $("#challenge-submit").click();
              }
            });

            challenge.postRender();

            $("#challenge-window")
              .find("pre code")
              .each(function(_idx) {
                hljs.highlightBlock(this);
              });

            window.location.replace(
              window.location.href.split("#")[0] + "#preview"
            );

            $("#challenge-window").modal();
          }
        );
      }
    );
  });

  $(".comments-challenge").click(function(_event) {
    $("#challenge-comments-window").modal();
  });

  $(".delete-challenge").click(function(_e) {
    ezQuery({
      title: "Delete Challenge",
      body: "Are you sure you want to delete {0}".format(
        "<strong>" + htmlEntities(window.CHALLENGE_NAME) + "</strong>"
      ),
      success: function() {
        CTFd.fetch("/api/v1/challenges/" + window.CHALLENGE_ID, {
          method: "DELETE"
        })
          .then(function(response) {
            return response.json();
          })
          .then(function(response) {
            if (response.success) {
              window.location = CTFd.config.urlRoot + "/admin/challenges";
            }
          });
      }
    });
  });

  $("#challenge-update-container > form").submit(function(e) {
    e.preventDefault();
    var params = $(e.target).serializeJSON(true);

    CTFd.fetch("/api/v1/challenges/" + window.CHALLENGE_ID + "/flags", {
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
        let update_challenge = function() {
          CTFd.fetch("/api/v1/challenges/" + window.CHALLENGE_ID, {
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
                $(".challenge-state").text(response.data.state);
                switch (response.data.state) {
                  case "visible":
                    $(".challenge-state")
                      .removeClass("badge-danger")
                      .addClass("badge-success");
                    break;
                  case "hidden":
                    $(".challenge-state")
                      .removeClass("badge-success")
                      .addClass("badge-danger");
                    break;
                  default:
                    break;
                }
                ezToast({
                  title: "Success",
                  body: "Your challenge has been updated!"
                });
              } else {
                let body = "";
                for (const k in response.errors) {
                  body += response.errors[k].join("\n");
                  body += "\n";
                }

                ezAlert({
                  title: "Error",
                  body: body,
                  button: "OK"
                });
              }
            });
        };
        // Check if the challenge doesn't have any flags before marking visible
        if (response.data.length === 0 && params.state === "visible") {
          ezQuery({
            title: "Missing Flags",
            body:
              "This challenge does not have any flags meaning it may be unsolveable. Are you sure you'd like to update this challenge?",
            success: update_challenge
          });
        } else {
          update_challenge();
        }
      });
  });

  $("#challenge-create-options form").submit(handleChallengeOptions);

  // Load FlagList component
  if (document.querySelector("#challenge-flags")) {
    const flagList = Vue.extend(FlagList);
    let vueContainer = document.createElement("div");
    document.querySelector("#challenge-flags").appendChild(vueContainer);
    new flagList({
      propsData: { challenge_id: window.CHALLENGE_ID }
    }).$mount(vueContainer);
  }

  // Load TopicsList component
  if (document.querySelector("#challenge-topics")) {
    const topicsList = Vue.extend(TopicsList);
    let vueContainer = document.createElement("div");
    document.querySelector("#challenge-topics").appendChild(vueContainer);
    new topicsList({
      propsData: { challenge_id: window.CHALLENGE_ID }
    }).$mount(vueContainer);
  }

  // Load TagsList component
  if (document.querySelector("#challenge-tags")) {
    const tagList = Vue.extend(TagsList);
    let vueContainer = document.createElement("div");
    document.querySelector("#challenge-tags").appendChild(vueContainer);
    new tagList({
      propsData: { challenge_id: window.CHALLENGE_ID }
    }).$mount(vueContainer);
  }

  // Load Requirements component
  if (document.querySelector("#prerequisite-add-form")) {
    const reqsComponent = Vue.extend(Requirements);
    let vueContainer = document.createElement("div");
    document.querySelector("#prerequisite-add-form").appendChild(vueContainer);
    new reqsComponent({
      propsData: { challenge_id: window.CHALLENGE_ID }
    }).$mount(vueContainer);
  }

  // Load ChallengeFilesList component
  if (document.querySelector("#challenge-files")) {
    const challengeFilesList = Vue.extend(ChallengeFilesList);
    let vueContainer = document.createElement("div");
    document.querySelector("#challenge-files").appendChild(vueContainer);
    new challengeFilesList({
      propsData: { challenge_id: window.CHALLENGE_ID }
    }).$mount(vueContainer);
  }

  // Load HintsList component
  if (document.querySelector("#challenge-hints")) {
    const hintsList = Vue.extend(HintsList);
    let vueContainer = document.createElement("div");
    document.querySelector("#challenge-hints").appendChild(vueContainer);
    new hintsList({
      propsData: { challenge_id: window.CHALLENGE_ID }
    }).$mount(vueContainer);
  }

  // Load Next component
  if (document.querySelector("#next-add-form")) {
    const nextChallenge = Vue.extend(NextChallenge);
    let vueContainer = document.createElement("div");
    document.querySelector("#next-add-form").appendChild(vueContainer);
    new nextChallenge({
      propsData: { challenge_id: window.CHALLENGE_ID }
    }).$mount(vueContainer);
  }

  // Because this JS is shared by a few pages,
  // we should only insert the CommentBox if it's actually in use
  if (document.querySelector("#comment-box")) {
    // Insert CommentBox element
    const commentBox = Vue.extend(CommentBox);
    let vueContainer = document.createElement("div");
    document.querySelector("#comment-box").appendChild(vueContainer);
    new commentBox({
      propsData: { type: "challenge", id: window.CHALLENGE_ID }
    }).$mount(vueContainer);
  }

  $.get(CTFd.config.urlRoot + "/api/v1/challenges/types", function(response) {
    const data = response.data;
    loadChalTemplate(data["standard"]);

    $("#create-chals-select input[name=type]").change(function() {
      let challenge = data[this.value];
      loadChalTemplate(challenge);
    });
  });
});
