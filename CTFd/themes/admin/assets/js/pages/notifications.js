import "./main";
import "core/utils";
import $ from "jquery";
import CTFd from "core/CTFd";
import { ezQuery, ezAlert } from "core/ezq";

function submit(event) {
  event.preventDefault();
  const $form = $(this);
  const params = $form.serializeJSON();

  // Disable button after click
  $form.find("button[type=submit]").attr("disabled", true);

  CTFd.api.post_notification_list({}, params).then(response => {
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
