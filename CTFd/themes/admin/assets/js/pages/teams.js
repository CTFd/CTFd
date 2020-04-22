import "./main";
import CTFd from "core/CTFd";
import $ from "jquery";
import { ezQuery } from "core/ezq";


function deleteSelectedTeams(event) {
  let teamIDs = $("input[data-team-id]:checked").map(function() {
    return $(this).data("team-id");
  });
  let target = teamIDs.length === 1 ? "team" : "teams";

  ezQuery({
    title: "Delete Teams",
    body: `Are you sure you want to delete ${teamIDs.length} ${target}?`,
    success: function() {
      const reqs = [];
      for (var teamID of teamIDs) {
        reqs.push(
          CTFd.fetch(`/api/v1/teams/${teamID}`, {
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
  $("#teams-delete-button").click(deleteSelectedTeams);
});