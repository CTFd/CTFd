import "./main";
import "core/utils";
import $ from "jquery";
import "bootstrap/js/dist/tab";
import CTFd from "core/CTFd";
import { htmlEntities } from "core/utils";
import { ezQuery, ezAlert, ezToast } from "core/ezq";
import nunjucks from "nunjucks";
import { default as helpers } from "core/helpers";
import { addFile, deleteFile } from "../challenges/files";
import { addTag, deleteTag } from "../challenges/tags";
import { addRequirement, deleteRequirement } from "../challenges/requirements";
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

const md = CTFd.lib.markdown();

const displayHint = data => {
  ezAlert({
    title: "Hint",
    body: md.render(data.content),
    button: "Got it!"
  });
};

const loadHint = id => {
  CTFd.api.get_hint({ hintId: id, preview: true }).then(response => {
    if (response.data.content) {
      displayHint(response.data);
      return;
    }
    displayUnlock(id);
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
    $("#submit-key").removeClass("disabled-button");
    $("#submit-key").prop("disabled", false);
  }, 3000);

  if (cb) {
    cb(result);
  }
}

function loadChalTemplate(challenge) {
  CTFd._internal.challenge = {};
  $.getScript(CTFd.config.urlRoot + challenge.scripts.view, function() {
    $.get(CTFd.config.urlRoot + challenge.templates.create, function(
      template_data
    ) {
      const template = nunjucks.compile(template_data);
      $("#create-chal-entry-div").html(
        template.render({
          nonce: CTFd.config.csrfNonce,
          script_root: CTFd.config.urlRoot
        })
      );

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
    new Promise(function(resolve, reject) {
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
    new Promise(function(resolve, reject) {
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
  ]).then(responses => {
    save_challenge();
  });
}

function createChallenge(event) {
  const challenge = $(this)
    .find("option:selected")
    .data("meta");
  if (challenge === undefined) {
    $("#create-chal-entry-div").empty();
    return;
  }
  loadChalTemplate(challenge);
}

$(() => {
  $(".preview-challenge").click(function(e) {
    window.challenge = new Object();
    CTFd._internal.challenge = {};
    $.get(CTFd.config.urlRoot + "/api/v1/challenges/" + CHALLENGE_ID, function(
      response
    ) {
      const challenge = CTFd._internal.challenge;
      var challenge_data = response.data;
      challenge_data["solves"] = null;

      $.getScript(
        CTFd.config.urlRoot + challenge_data.type_data.scripts.view,
        function() {
          $.get(
            CTFd.config.urlRoot + challenge_data.type_data.templates.view,
            function(template_data) {
              $("#challenge-window").empty();
              var template = nunjucks.compile(template_data);
              // window.challenge.data = challenge_data;
              // window.challenge.preRender();
              challenge.data = challenge_data;
              challenge.preRender();

              challenge_data["description"] = challenge.render(
                challenge_data["description"]
              );
              challenge_data["script_root"] = CTFd.config.urlRoot;

              $("#challenge-window").append(template.render(challenge_data));

              $(".challenge-solves").click(function(e) {
                getsolves($("#challenge-id").val());
              });
              $(".nav-tabs a").click(function(e) {
                e.preventDefault();
                $(this).tab("show");
              });

              // Handle modal toggling
              $("#challenge-window").on("hide.bs.modal", function(event) {
                $("#submission-input").removeClass("wrong");
                $("#submission-input").removeClass("correct");
                $("#incorrect-key").slideUp();
                $("#correct-key").slideUp();
                $("#already-solved").slideUp();
                $("#too-fast").slideUp();
              });

              $(".load-hint").on("click", function(event) {
                loadHint($(this).data("hint-id"));
              });

              $("#submit-key").click(function(e) {
                e.preventDefault();
                $("#submit-key").addClass("disabled-button");
                $("#submit-key").prop("disabled", true);
                CTFd._internal.challenge
                  .submit(true)
                  .then(renderSubmissionResponse);
                // Preview passed as true
              });

              $("#submission-input").keyup(function(event) {
                if (event.keyCode == 13) {
                  $("#submit-key").click();
                }
              });

              $(".input-field").bind({
                focus: function() {
                  $(this)
                    .parent()
                    .addClass("input--filled");
                  $label = $(this).siblings(".input-label");
                },
                blur: function() {
                  if ($(this).val() === "") {
                    $(this)
                      .parent()
                      .removeClass("input--filled");
                    $label = $(this).siblings(".input-label");
                    $label.removeClass("input--hide");
                  }
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
  });

  $(".delete-challenge").click(function(e) {
    ezQuery({
      title: "Delete Challenge",
      body: "Are you sure you want to delete {0}".format(
        "<strong>" + htmlEntities(CHALLENGE_NAME) + "</strong>"
      ),
      success: function() {
        CTFd.fetch("/api/v1/challenges/" + CHALLENGE_ID, {
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

    CTFd.fetch("/api/v1/challenges/" + CHALLENGE_ID + "/flags", {
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
              "This challenge does not have any flags meaning it is unsolveable. Are you sure you'd like to update this challenge?",
            success: update_challenge
          });
        } else {
          update_challenge();
        }
      });
  });

  $("#challenge-create-options form").submit(handleChallengeOptions);

  $(".nav-tabs a").click(function(e) {
    $(this).tab("show");
    window.location.hash = this.hash;
  });

  if (window.location.hash) {
    let hash = window.location.hash.replace("<>[]'\"", "");
    $('nav a[href="' + hash + '"]').tab("show");
  }

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
    $("#create-chals-select").empty();
    const data = response.data;
    const chal_type_amt = Object.keys(data).length;
    if (chal_type_amt > 1) {
      const option = "<option> -- </option>";
      $("#create-chals-select").append(option);
      for (const key in data) {
        const challenge = data[key];
        const option = $("<option/>");
        option.attr("value", challenge.type);
        option.text(challenge.name);
        option.data("meta", challenge);
        $("#create-chals-select").append(option);
      }
      $("#create-chals-select-div").show();
      $("#create-chals-select").val("standard");
      loadChalTemplate(data["standard"]);
    } else if (chal_type_amt == 1) {
      const key = Object.keys(data)[0];
      $("#create-chals-select").empty();
      loadChalTemplate(data[key]);
    }
  });

  $("#create-chals-select").change(createChallenge);
});
