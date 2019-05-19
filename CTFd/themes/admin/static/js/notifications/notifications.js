$(document).ready(function() {
  $("#notifications_form").submit(function(e) {
    e.preventDefault();
    var form = $("#notifications_form");
    var params = form.serializeJSON();

    CTFd.fetch("/api/v1/notifications", {
      method: "POST",
      credentials: "same-origin",
      headers: {
        Accept: "application/json",
        "Content-Type": "application/json"
      },
      body: JSON.stringify(params)
    })
      .then(function(response) {
        return response.json();
      })
      .then(function(response) {
        if (response.success) {
          setTimeout(function() {
            window.location.reload();
          }, 3000);
        }
      });
  });

  $(".delete-notification").click(function(e) {
    e.preventDefault();
    var elem = $(this);
    var notif_id = elem.attr("notif-id");

    ezq({
      title: "Delete Notification",
      body: "Are you sure you want to delete this notification?",
      success: function() {
        CTFd.fetch("/api/v1/notifications/" + notif_id, {
          method: "DELETE"
        })
          .then(function(response) {
            return response.json();
          })
          .then(function(response) {
            if (response.success) {
              elem.parent().remove();
            }
          });
      }
    });
  });
});
