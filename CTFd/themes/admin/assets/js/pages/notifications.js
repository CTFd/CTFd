import "./main";
import "core/utils";
import $ from "jquery";
import CTFd from "core/CTFd";
import { ezQuery } from "core/ezq";

function submit(event) {
  event.preventDefault();
  const $form = $(this);
  const params = $form.serializeJSON();

  CTFd.api.post_notification_list({}, params).then(response => {
    if (response.success) {
      setTimeout(function() {
        window.location.reload();
      }, 3000);
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
