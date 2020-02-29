import "./main";
import CTFd from "core/CTFd";
import $ from "jquery";
import { htmlEntities } from "core/utils";
import { ezQuery } from "core/ezq";

function deletePage(event) {
  const elem = $(this);
  const name = elem.attr("page-route");
  const page_id = elem.attr("page-id");
  ezQuery({
    title: "Delete " + htmlEntities(name),
    body: "Are you sure you want to delete {0}?".format(
      "<strong>" + htmlEntities(name) + "</strong>"
    ),
    success: function() {
      CTFd.fetch("/api/v1/pages/" + page_id, {
        method: "DELETE"
      })
        .then(function(response) {
          return response.json();
        })
        .then(function(response) {
          if (response.success) {
            elem
              .parent()
              .parent()
              .remove();
          }
        });
    }
  });
}

$(() => {
  $(".delete-page").click(deletePage);
});
