import "./main";
import "core/utils";
import $ from "jquery";
import CTFd from "core/CTFd";
import { ezQuery, ezAlert } from "core/ezq";
import Moment from "moment";
import { htmlEntities } from "core/utils";

function submit(event) {
  event.preventDefault();
  const $form = $(this);
  const params = $form.serializeJSON();

  // Disable button after click
  $form.find("button[type=submit]").attr("disabled", true);

  CTFd.api.post_notification_list({}, params).then(response => {
    $form.find(":input[name=title]").val("");
    $form.find(":input[name=content]").val("");

    // Admin should also see the notification sent out
    setTimeout(function() {
      $form.find("button[type=submit]").attr("disabled", false);
    }, 1000);
    if (!response.success) {
      ezAlert({
        title: "Error",
        body: "Could not send notification. Please try again.",
        button: "OK"
      });
    }

    let date = Moment(response.data.date)
      .local()
      .format("MMMM Do, h:mm:ss A");
    let title = htmlEntities(response.data.title);

    let content = $(`<div class="card bg-light mb-4">
      <button type="button" data-notif-id="${
        response.data.id
      }" class="delete-notification close position-absolute p-3" style="right:0;" data-dismiss="alert" aria-label="Close">
        <span aria-hidden="true">&times;</span>
      </button>
      <div class="card-body">
        <h3 class="card-title">${title}</h3>
        <blockquote class="blockquote mb-0">
          <p>${response.data.content}</p>
          <small class="text-muted"><span data-time="${
            response.data.date
          }">${date}</span></small>
        </blockquote>
      </div>
    </div>`);

    content.find(".delete-notification").click(deleteNotification);
    $("#notifications-list").prepend(content);
  });
}

function deleteNotification(event) {
  event.preventDefault();
  const $elem = $(this);
  const id = $elem.data("notif-id");

  ezQuery({
    title: "Delete Notification",
    body: "Are you sure you want to delete this notification?",
    success: function() {
      CTFd.api.delete_notification({ notificationId: id }).then(response => {
        if (response.success) {
          $elem.parent().remove();
        }
      });
    }
  });
}

$(() => {
  $("#notifications_form").submit(submit);
  $(".delete-notification").click(deleteNotification);
});
