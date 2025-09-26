import "./main";
import $ from "jquery";
import "../compat/json";
import "bootstrap/js/dist/tab";
import CTFd from "../compat/CTFd";
import { htmlEntities } from "@ctfdio/ctfd-js/utils/html";
import { ezQuery, ezAlert, ezToast } from "../compat/ezq";
import { default as helpers } from "../compat/helpers";
import { bindMarkdownEditors } from "../styles";
import Vue from "vue";
import CommentBox from "../components/comments/CommentBox.vue";
import FlagList from "../components/flags/FlagList.vue";
import Requirements from "../components/requirements/Requirements.vue";
import TopicsList from "../components/topics/TopicsList.vue";
import TagsList from "../components/tags/TagsList.vue";
import ChallengeFilesList from "../components/files/ChallengeFilesList.vue";
import HintsList from "../components/hints/HintsList.vue";
import NextChallenge from "../components/next/NextChallenge.vue";
import SolutionEditor from "../components/solution/SolutionEditor.vue";
import RatingsViewer from "../components/ratings/RatingsViewer.vue";

function loadChalTemplate(challenge) {
  CTFd._internal.challenge = {};
  $.getScript(CTFd.config.urlRoot + challenge.scripts.view, function () {
    let template_data = challenge.create;
    $("#create-chal-entry-div").html(template_data);
    bindMarkdownEditors();

    $.getScript(CTFd.config.urlRoot + challenge.scripts.create, function () {
      $("#create-chal-entry-div form").submit(function (event) {
        event.preventDefault();
        const params = $("#create-chal-entry-div form").serializeJSON();
        CTFd.fetch("/api/v1/challenges", {
          method: "POST",
          credentials: "same-origin",
          headers: {
            Accept: "application/json",
            "Content-Type": "application/json",
          },
          body: JSON.stringify(params),
        })
          .then(function (response) {
            return response.json();
          })
          .then(function (response) {
            if (response.success) {
              $("#challenge-create-options #challenge_id").val(
                response.data.id,
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
                button: "OK",
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
    data: params.flag_data ? params.flag_data : "",
  };
  // Define a save_challenge function
  let save_challenge = function () {
    CTFd.fetch("/api/v1/challenges/" + params.challenge_id, {
      method: "PATCH",
      credentials: "same-origin",
      headers: {
        Accept: "application/json",
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        state: params.state,
      }),
    })
      .then(function (response) {
        return response.json();
      })
      .then(function (data) {
        if (data.success) {
          setTimeout(function () {
            window.location =
              CTFd.config.urlRoot + "/admin/challenges/" + params.challenge_id;
          }, 700);
        }
      });
  };

  Promise.all([
    // Save flag
    new Promise(function (resolve, _reject) {
      if (flag_params.content.length == 0) {
        resolve();
        return;
      }
      CTFd.fetch("/api/v1/flags", {
        method: "POST",
        credentials: "same-origin",
        headers: {
          Accept: "application/json",
          "Content-Type": "application/json",
        },
        body: JSON.stringify(flag_params),
      }).then(function (response) {
        resolve(response.json());
      });
    }),
    // Upload files
    new Promise(function (resolve, _reject) {
      let form = event.target;
      let data = {
        challenge: params.challenge_id,
        type: "challenge",
      };
      let filepath = $(form.elements["file"]).val();
      if (filepath) {
        helpers.files.upload(form, data);
      }
      resolve();
    }),
  ]).then((_responses) => {
    save_challenge();
  });
}

$(() => {
  $(".preview-challenge").click(function (_e) {
    let url = `${CTFd.config.urlRoot}/admin/challenges/preview/${window.CHALLENGE_ID}`;
    $("#challenge-window").html(
      `<iframe src="${url}" height="100%" width="100%" frameBorder=0></iframe>`,
    );
    $("#challenge-modal").modal();
  });

  $(".comments-challenge").click(function (_event) {
    $("#challenge-comments-window").modal();
  });

  $(".ratings-challenge").click(function (_event) {
    $("#challenge-ratings-window").modal();
  });

  $(".delete-challenge").click(function (_e) {
    ezQuery({
      title: "Delete Challenge",
      body: `Are you sure you want to delete <strong>${htmlEntities(
        window.CHALLENGE_NAME,
      )}</strong>`,
      success: function () {
        CTFd.fetch("/api/v1/challenges/" + window.CHALLENGE_ID, {
          method: "DELETE",
        })
          .then(function (response) {
            return response.json();
          })
          .then(function (response) {
            if (response.success) {
              window.location = CTFd.config.urlRoot + "/admin/challenges";
            }
          });
      },
    });
  });

  $("#challenge-update-container > form").submit(function (e) {
    e.preventDefault();
    var params = $(e.target).serializeJSON(true);

    CTFd.fetch("/api/v1/challenges/" + window.CHALLENGE_ID + "/flags", {
      method: "GET",
      credentials: "same-origin",
      headers: {
        Accept: "application/json",
        "Content-Type": "application/json",
      },
    })
      .then(function (response) {
        return response.json();
      })
      .then(function (response) {
        let update_challenge = function () {
          CTFd.fetch("/api/v1/challenges/" + window.CHALLENGE_ID, {
            method: "PATCH",
            credentials: "same-origin",
            headers: {
              Accept: "application/json",
              "Content-Type": "application/json",
            },
            body: JSON.stringify(params),
          })
            .then(function (response) {
              return response.json();
            })
            .then(function (response) {
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
                  body: "Your challenge has been updated!",
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
                  button: "OK",
                });
              }
            });
        };
        // Check if the challenge doesn't have any flags before marking visible
        if (response.data.length === 0 && params.state === "visible") {
          ezQuery({
            title: "Missing Flags",
            body: "This challenge does not have any flags meaning it may be unsolveable. Are you sure you'd like to update this challenge?",
            success: update_challenge,
          });
        } else {
          update_challenge();
        }
      });
  });

  $("#challenge-create-options form").submit(handleChallengeOptions);

  $(".chal-function")
    .change(function () {
      const selectedFunction = $(this).val();
      const initialFormGroup = $(".chal-initial").closest(".form-group");
      const decayFormGroup = $(".chal-decay").closest(".form-group");
      const minimumFormGroup = $(".chal-minimum").closest(".form-group");
      const initialInput = $(".chal-initial");
      const decayInput = $(".chal-decay");
      const minimumInput = $(".chal-minimum");
      const valueInput = $(".chal-value");

      if (selectedFunction === "static") {
        // Save current values to data attributes before clearing them
        if (initialInput.val()) {
          initialInput.data("saved-value", initialInput.val());
        }
        if (decayInput.val()) {
          decayInput.data("saved-value", decayInput.val());
        }
        if (minimumInput.val()) {
          minimumInput.data("saved-value", minimumInput.val());
        }

        // Clear the input values to prevent validation errors on hidden fields
        initialInput.val("");
        decayInput.val("");
        minimumInput.val("");

        // Hide initial, decay, and minimum form groups for static function
        initialFormGroup.hide();
        decayFormGroup.hide();
        minimumFormGroup.hide();

        // Remove name attributes so they won't be included in serializeJSON
        initialInput.removeAttr("name").data("original-name", "initial");
        decayInput.removeAttr("name").data("original-name", "decay");
        minimumInput.removeAttr("name").data("original-name", "minimum");

        // Remove required attribute for static function
        initialInput.removeAttr("required");
        decayInput.removeAttr("required");
        minimumInput.removeAttr("required");

        // Make value input enabled and required for static function
        valueInput.prop("disabled", false).prop("required", true);
      } else if (
        selectedFunction === "linear" ||
        selectedFunction === "logarithmic"
      ) {
        // Show initial, decay, and minimum form groups for linear and logarithmic functions
        initialFormGroup.show();
        decayFormGroup.show();
        minimumFormGroup.show();

        // Restore name attributes so they will be included in serializeJSON
        initialInput.attr(
          "name",
          initialInput.data("original-name") || "initial",
        );
        decayInput.attr("name", decayInput.data("original-name") || "decay");
        minimumInput.attr(
          "name",
          minimumInput.data("original-name") || "minimum",
        );

        // Restore saved values from data attributes
        if (initialInput.data("saved-value")) {
          initialInput.val(initialInput.data("saved-value"));
        }
        if (decayInput.data("saved-value")) {
          decayInput.val(decayInput.data("saved-value"));
        }
        if (minimumInput.data("saved-value")) {
          minimumInput.val(minimumInput.data("saved-value"));
        }

        // Add required attribute for dynamic functions
        initialInput.prop("required", true);
        decayInput.prop("required", true);
        minimumInput.prop("required", true);

        // Make value input disabled and not required for dynamic functions
        valueInput.prop("disabled", true).prop("required", false);
      }
    })
    .trigger("change"); // Trigger change event on page load to set initial state

  // Load FlagList component
  if (document.querySelector("#challenge-flags")) {
    const flagList = Vue.extend(FlagList);
    let vueContainer = document.createElement("div");
    document.querySelector("#challenge-flags").appendChild(vueContainer);
    new flagList({
      propsData: { challenge_id: window.CHALLENGE_ID },
    }).$mount(vueContainer);
  }

  // Load TopicsList component
  if (document.querySelector("#challenge-topics")) {
    const topicsList = Vue.extend(TopicsList);
    let vueContainer = document.createElement("div");
    document.querySelector("#challenge-topics").appendChild(vueContainer);
    new topicsList({
      propsData: { challenge_id: window.CHALLENGE_ID },
    }).$mount(vueContainer);
  }

  // Load TagsList component
  if (document.querySelector("#challenge-tags")) {
    const tagList = Vue.extend(TagsList);
    let vueContainer = document.createElement("div");
    document.querySelector("#challenge-tags").appendChild(vueContainer);
    new tagList({
      propsData: { challenge_id: window.CHALLENGE_ID },
    }).$mount(vueContainer);
  }

  // Load Requirements component
  if (document.querySelector("#prerequisite-add-form")) {
    const reqsComponent = Vue.extend(Requirements);
    let vueContainer = document.createElement("div");
    document.querySelector("#prerequisite-add-form").appendChild(vueContainer);
    new reqsComponent({
      propsData: { challenge_id: window.CHALLENGE_ID },
    }).$mount(vueContainer);
  }

  // Load ChallengeFilesList component
  if (document.querySelector("#challenge-files")) {
    const challengeFilesList = Vue.extend(ChallengeFilesList);
    let vueContainer = document.createElement("div");
    document.querySelector("#challenge-files").appendChild(vueContainer);
    new challengeFilesList({
      propsData: { challenge_id: window.CHALLENGE_ID },
    }).$mount(vueContainer);
  }

  // Load HintsList component
  if (document.querySelector("#challenge-hints")) {
    const hintsList = Vue.extend(HintsList);
    let vueContainer = document.createElement("div");
    document.querySelector("#challenge-hints").appendChild(vueContainer);
    new hintsList({
      propsData: { challenge_id: window.CHALLENGE_ID },
    }).$mount(vueContainer);
  }

  // Load Next component
  if (document.querySelector("#next-add-form")) {
    const nextChallenge = Vue.extend(NextChallenge);
    let vueContainer = document.createElement("div");
    document.querySelector("#next-add-form").appendChild(vueContainer);
    new nextChallenge({
      propsData: { challenge_id: window.CHALLENGE_ID },
    }).$mount(vueContainer);
  }

  // Load SolutionEditor component
  if (document.querySelector("#challenge-solution")) {
    const solutionEditor = Vue.extend(SolutionEditor);
    let vueContainer = document.createElement("div");
    document.querySelector("#challenge-solution").appendChild(vueContainer);
    new solutionEditor({
      propsData: {
        challenge_id: window.CHALLENGE_ID,
      },
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
      propsData: { type: "challenge", id: window.CHALLENGE_ID },
    }).$mount(vueContainer);
  }

  // Load RatingsViewer component
  if (document.querySelector("#ratings-box")) {
    const ratingsViewer = Vue.extend(RatingsViewer);
    let vueContainer = document.createElement("div");
    document.querySelector("#ratings-box").appendChild(vueContainer);
    new ratingsViewer({
      propsData: { challengeId: window.CHALLENGE_ID },
    }).$mount(vueContainer);
  }

  $.get(CTFd.config.urlRoot + "/api/v1/challenges/types", function (response) {
    const data = response.data;
    loadChalTemplate(data["standard"]);

    $("#create-chals-select input[name=type]").change(function () {
      let challenge = data[this.value];
      loadChalTemplate(challenge);
    });
  });
});
