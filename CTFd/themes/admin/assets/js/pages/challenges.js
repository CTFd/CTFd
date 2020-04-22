import "./main";
import CTFd from "core/CTFd";
import $ from "jquery";
import { ezQuery } from "core/ezq";

function deleteSelectedChallenges(event){
  let challengeIDs = $("input[data-challenge-id]:checked").map(function() {
    return $(this).data("challenge-id");
  });
  let target = challengeIDs.length === 1 ? "challenge" : "challenges";

  ezQuery({
    title: "Delete Challenges",
    body: `Are you sure you want to delete ${challengeIDs.length} ${target}?`,
    success: function() {
      const reqs = [];
      for (var chalID of challengeIDs) {
        reqs.push(
          CTFd.fetch(`/api/v1/challenges/${chalID}`, {
            method: "DELETE"
          })
        );
      }
      Promise.all(reqs).then(responses => {
        window.location.reload();
      });
    }
  });
}

$(() => {
  $("#challenges-delete-button").click(deleteSelectedChallenges);
});

