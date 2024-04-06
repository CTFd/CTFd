import "./main";
import "../compat/json";
import $ from "jquery";
import CTFd from "../compat/CTFd";
import { ezAlert } from "../compat/ezq";
import Vue from "vue";
import Notification from "../components/notifications/Notification.vue";

const notificationCard = Vue.extend(Notification);

function submit(event) {
  event.preventDefault();
  const $form = $(this);
  const params = $form.serializeJSON();

  // Disable button after click
  $form.find("button[type=submit]").attr("disabled", true);

  CTFd.api.post_notification_list({}, params).then((response) => {
    $form.find(":input[name=title]").val("");
    $form.find(":input[name=content]").val("");

    // Admin should also see the notification sent out
    setTimeout(function () {
      $form.find("button[type=submit]").attr("disabled", false);
    }, 1000);
    if (!response.success) {
      ezAlert({
        title: "Error",
        body: "Could not send notification. Please try again.",
        button: "OK",
      });
    }

    let vueContainer = document.createElement("div");
    $("#notifications-list").prepend(vueContainer);
    new notificationCard({
      propsData: {
        id: response.data.id,
        title: response.data.title,
        content: response.data.content,
        html: response.data.html,
        date: response.data.date,
      },
    }).$mount(vueContainer);
  });
}

function deleteNotification(event) {
  event.preventDefault();
  const $elem = $(this);
  const id = $elem.data("notif-id");

  if (confirm("Are you sure you want to delete this notification?")) {
    CTFd.api.delete_notification({ notificationId: id }).then((response) => {
      if (response.success) {
        $elem.parent().remove();
      }
    });
  }
}

$(() => {
  $("#notifications_form").submit(submit);
  $(".delete-notification").click(deleteNotification);
});
