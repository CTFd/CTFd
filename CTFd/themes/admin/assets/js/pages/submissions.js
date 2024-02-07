import "./main";
import CTFd from "../compat/CTFd";
import $ from "jquery";
import { htmlEntities } from "@ctfdio/ctfd-js/utils/html";
import { ezQuery } from "../compat/ezq";
import "../compat/format";

function deleteCorrectSubmission(_event) {
  const key_id = $(this).data("submission-id");
  const $elem = $(this).parent().parent();
  const chal_name = $elem.find(".chal").text().trim();
  const team_name = $elem.find(".team").text().trim();

  const row = $(this).parent().parent();

  ezQuery({
    title: "Delete Submission",
    body: "Are you sure you want to delete correct submission from {0} for challenge {1}".format(
      "<strong>" + htmlEntities(team_name) + "</strong>",
      "<strong>" + htmlEntities(chal_name) + "</strong>",
    ),
    success: function () {
      CTFd.api
        .delete_submission({ submissionId: key_id })
        .then(function (response) {
          if (response.success) {
            row.remove();
          }
        });
    },
  });
}

function deleteSelectedSubmissions(_event) {
  let submissionIDs = $("input[data-submission-id]:checked").map(function () {
    return $(this).data("submission-id");
  });
  let target = submissionIDs.length === 1 ? "submission" : "submissions";

  ezQuery({
    title: "Delete Submissions",
    body: `Are you sure you want to delete ${submissionIDs.length} ${target}?`,
    success: function () {
      const reqs = [];
      for (var subId of submissionIDs) {
        reqs.push(CTFd.api.delete_submission({ submissionId: subId }));
      }
      Promise.all(reqs).then((_responses) => {
        window.location.reload();
      });
    },
  });
}

function correctSubmissions(_event) {
  let submissionIDs = $("input[data-submission-id]:checked").map(function () {
    return $(this).data("submission-id");
  });
  let target = submissionIDs.length === 1 ? "submission" : "submissions";

  ezQuery({
    title: "Correct Submissions",
    body: `Are you sure you want to mark ${submissionIDs.length} ${target} correct?`,
    success: function () {
      const reqs = [];
      for (var subId of submissionIDs) {
        let req = CTFd.fetch(`/api/v1/submissions/${subId}`, {
          method: "PATCH",
          credentials: "same-origin",
          headers: {
            Accept: "application/json",
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ type: "correct" }),
        });
        reqs.push(req);
      }
      Promise.all(reqs).then((_responses) => {
        window.location.reload();
      });
    },
  });
}

function showFlagsToggle(_event) {
  const urlParams = new URLSearchParams(window.location.search);
  if (urlParams.has("full")) {
    urlParams.delete("full");
  } else {
    urlParams.set("full", "true");
  }
  window.location.href = `${window.location.pathname}?${urlParams.toString()}`;
}

function showFlag(event) {
  let target = $(event.currentTarget);
  let eye = target.find("i");
  let flag = target.parent().find("pre");
  if (!flag.hasClass("full-flag")) {
    flag.text(flag.attr("title"));
    flag.addClass("full-flag");
    eye.addClass("fa-eye-slash");
    eye.removeClass("fa-eye");
  } else {
    flag.text(flag.attr("title").substring(0, 42) + "...");
    flag.removeClass("full-flag");
    eye.addClass("fa-eye");
    eye.removeClass("fa-eye-slash");
  }
}

function copyFlag(event) {
  let target = $(event.currentTarget);
  let flag = target.parent().find("pre");
  let text = flag.attr("title");
  navigator.clipboard.writeText(text);

  $(event.currentTarget).tooltip({
    title: "Copied!",
    trigger: "manual",
  });
  $(event.currentTarget).tooltip("show");

  setTimeout(function () {
    $(event.currentTarget).tooltip("hide");
  }, 1500);
}

$(() => {
  $("#show-full-flags-button").click(showFlagsToggle);
  $("#show-short-flags-button").click(showFlagsToggle);
  $(".show-flag").click(showFlag);
  $(".copy-flag").click(copyFlag);
  $("#correct-flags-button").click(correctSubmissions);
  $(".delete-correct-submission").click(deleteCorrectSubmission);
  $("#submission-delete-button").click(deleteSelectedSubmissions);
});
