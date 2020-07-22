import "./main";
import "core/utils";
import $ from "jquery";
import "bootstrap/js/dist/tab";
import CTFd from "core/CTFd";
import { htmlEntities } from "core/utils";
import { ezQuery, ezAlert, ezToast } from "core/ezq";
import { default as helpers } from "core/helpers";
import { addFile, deleteFile } from "../challenges/files";
import { addTag, deleteTag } from "../challenges/tags";
import { addRequirement, deleteRequirement } from "../challenges/requirements";
import { bindMarkdownEditors } from "../styles";
import {
  showHintModal,
  editHint,
  deleteHint,
  showEditHintModal
} from "../challenges/hints";
import {
  addFlagModal,
  editFlagModal,
  deleteFlag,
  flagTypeSelect
} from "../challenges/flags";

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
    window.challenge = new Object();
    CTFd._internal.challenge = {};
    $.get(
      CTFd.config.urlRoot + "/api/v1/challenges/" + window.CHALLENGE_ID,
      function(response) {
        const challenge = CTFd._internal.challenge;
        var challenge_data = response.data;
        challenge_data["solves"] = null;

        $.getScript(
          CTFd.config.urlRoot + challenge_data.type_data.scripts.view,
          function() {
            $("#challenge-window").empty();

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
            window.location.replace(
              window.location.href.split("#")[0] + "#preview"
            );

            $("#challenge-window").modal();
          }
        );
      }
    );
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

  $("#tags-add-input").keyup(addTag);
  $(".delete-tag").click(deleteTag);

  $("#prerequisite-add-form").submit(addRequirement);
  $(".delete-requirement").click(deleteRequirement);

  $("#file-add-form").submit(addFile);
  $(".delete-file").click(deleteFile);

  $("#hint-add-button").click(showHintModal);
  $(".delete-hint").click(deleteHint);
  $(".edit-hint").click(showEditHintModal);
  $("#hint-edit-form").submit(editHint);

  $("#flag-add-button").click(addFlagModal);
  $(".delete-flag").click(deleteFlag);
  $("#flags-create-select").change(flagTypeSelect);
  $(".edit-flag").click(editFlagModal);

  $.get(CTFd.config.urlRoot + "/api/v1/challenges/types", function(response) {
    const data = response.data;
    loadChalTemplate(data["standard"]);

    $("#create-chals-select input[name=type]").change(function() {
      let challenge = data[this.value];
      loadChalTemplate(challenge);
    });
  });
});
