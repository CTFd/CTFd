import "./main";
import CTFd from "core/CTFd";
import $ from "jquery";
import { ezQuery } from "core/ezq";

function deleteSelectedUsers(event) {
  let userIDs = $("input[data-user-id]:checked").map(function() {
    return $(this).data("user-id");
  });
  let target = userIDs.length === 1 ? "user" : "users";

  ezQuery({
    title: "Delete Users",
    body: `Are you sure you want to delete ${userIDs.length} ${target}?`,
    success: function() {
      const reqs = [];
      for (var userID of userIDs) {
        reqs.push(
          CTFd.fetch(`/api/v1/users/${userID}`, {
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
  $("#users-delete-button").click(deleteSelectedUsers);
});
