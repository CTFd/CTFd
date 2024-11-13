import $ from "jquery";
import "../compat/json";
import "../compat/format";
import { ezToast, ezQuery } from "../compat/ezq";
import { htmlEntities } from "@ctfdio/ctfd-js/utils/html";
import CTFd from "../compat/CTFd";
import nunjucks from "nunjucks";

function renderSubmissionResponse(response, cb) {
  const result = response.data;

  const result_message = $("#result-message");
  const result_notification = $("#result-notification");
  const answer_input = $("#submission-input");
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
      "alert alert-danger alert-dismissable text-center",
    );
    result_notification.slideDown();

    answer_input.removeClass("correct");
    answer_input.addClass("wrong");
    setTimeout(function () {
      answer_input.removeClass("wrong");
    }, 3000);
  } else if (result.status === "correct") {
    // Challenge Solved
    result_notification.addClass(
      "alert alert-success alert-dismissable text-center",
    );
    result_notification.slideDown();

    $(".challenge-solves").text(
      parseInt($(".challenge-solves").text().split(" ")[0]) + 1 + " Solves",
    );

    answer_input.val("");
    answer_input.removeClass("wrong");
    answer_input.addClass("correct");
  } else if (result.status === "already_solved") {
    // Challenge already solved
    result_notification.addClass(
      "alert alert-info alert-dismissable text-center",
    );
    result_notification.slideDown();

    answer_input.addClass("correct");
  } else if (result.status === "paused") {
    // CTF is paused
    result_notification.addClass(
      "alert alert-warning alert-dismissable text-center",
    );
    result_notification.slideDown();
  } else if (result.status === "ratelimited") {
    // Keys per minute too high
    result_notification.addClass(
      "alert alert-warning alert-dismissable text-center",
    );
    result_notification.slideDown();

    answer_input.addClass("too-fast");
    setTimeout(function () {
      answer_input.removeClass("too-fast");
    }, 3000);
  }
  setTimeout(function () {
    $(".alert").slideUp();
    $("#submit-key").removeClass("disabled-button");
    $("#submit-key").prop("disabled", false);
  }, 3000);

  if (cb) {
    cb(result);
  }
}

$(() => {
  $(".preview-challenge").click(function (_event) {
    window.challenge = new Object();
    $.get(
      CTFd.config.urlRoot + "/api/v1/challenges/" + window.CHALLENGE_ID,
      function (response) {
        const challenge_data = response.data;
        challenge_data["solves"] = null;

        $.getScript(
          CTFd.config.urlRoot + challenge_data.type_data.scripts.view,
          function () {
            $.get(
              CTFd.config.urlRoot + challenge_data.type_data.templates.view,
              function (template_data) {
                $("#challenge-window").empty();
                const template = nunjucks.compile(template_data);
                window.challenge.data = challenge_data;
                window.challenge.preRender();

                challenge_data["description"] = window.challenge.render(
                  challenge_data["description"],
                );
                challenge_data["script_root"] = CTFd.config.urlRoot;

                $("#challenge-window").append(template.render(challenge_data));

                $(".nav-tabs a").click(function (event) {
                  event.preventDefault();
                  $(this).tab("show");
                });

                // Handle modal toggling
                $("#challenge-window").on("hide.bs.modal", function (_event) {
                  $("#submission-input").removeClass("wrong");
                  $("#submission-input").removeClass("correct");
                  $("#incorrect-key").slideUp();
                  $("#correct-key").slideUp();
                  $("#already-solved").slideUp();
                  $("#too-fast").slideUp();
                });

                $("#submit-key").click(function (event) {
                  event.preventDefault();
                  $("#submit-key").addClass("disabled-button");
                  $("#submit-key").prop("disabled", true);
                  window.challenge.submit(function (data) {
                    renderSubmissionResponse(data);
                  }, true);
                  // Preview passed as true
                });

                $("#submission-input").keyup(function (event) {
                  if (event.keyCode == 13) {
                    $("#submit-key").click();
                  }
                });

                window.challenge.postRender();
                window.location.replace(
                  window.location.href.split("#")[0] + "#preview",
                );

                $("#challenge-window").modal();
              },
            );
          },
        );
      },
    );
  });

  $(".delete-challenge").click(function (_event) {
    ezQuery({
      title: "Delete Challenge",
      body: "Are you sure you want to delete {0}".format(
        "<strong>" + htmlEntities(window.CHALLENGE_NAME) + "</strong>",
      ),
      success: function () {
        CTFd.fetch("/api/v1/challenges/" + window.CHALLENGE_ID, {
          method: "DELETE",
        }).then(function (response) {
          if (response.success) {
            window.location = CTFd.config.urlRoot + "/admin/challenges";
          }
        });
      },
    });
  });

  $("#challenge-update-container > form").submit(function (event) {
    event.preventDefault();
    const params = $(event.target).serializeJSON(true);

    CTFd.fetch("/api/v1/challenges/" + window.CHALLENGE_ID, {
      method: "PATCH",
      credentials: "same-origin",
      headers: {
        Accept: "application/json",
        "Content-Type": "application/json",
      },
      body: JSON.stringify(params),
    }).then(function (data) {
      if (data.success) {
        ezToast({
          title: "Success",
          body: "Your challenge has been updated!",
        });
      }
    });
  });
});
