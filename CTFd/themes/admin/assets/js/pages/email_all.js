import "./main";
import CTFd from "../compat/CTFd";
import $ from "jquery";
import { ezAlert } from "../compat/ezq";

$(() => {
  const form = $("#email-all-form");
  const progressContainer = $("#progress-container");
  const progressBar = $("#email-progress");
  const status = $("#status");

  form.on("submit", async (e) => {
    e.preventDefault();
    const subject = form.find("input[name='subject']").val();
    const body = form.find("textarea[name='body']").val();
    progressContainer.show();

    let users = [];
    let page = 1;
    let total = 0;
    try {
      while (true) {
        const response = await CTFd.api.get_user_list({ page: page });
        const user_list = response.data.data;
        users = users.concat(user_list);
        total = response.data.meta.pagination.total;
        if (user_list.length === 0) {
          break;
        }
        page++;
      }
    } catch (error) {
      console.error("Failed to fetch users:", error);
      ezAlert({
        title: "Error",
        body: "Failed to fetch users. Check the console for details.",
        button: "Close",
      });
      return;
    }

    let sent = 0;
    updateProgress(sent, total);

    // Send at rate of 50 emails at a time, every 10 seconds change later mayb
    while (users.length > 0) {
      const batch = users.splice(0, 50);
      const reqs = batch.map((user) => {
        return CTFd.api
          .post_user_email(user.id, { subject, body })
          .then(() => {
            sent++;
            updateProgress(sent, total);
          })
          .catch((err) => {
            console.error(`Error sending to user ${user.id}:`, err);
          });
      });

      await Promise.all(reqs);

      if (users.length > 0) {
        // Only wait if there are more users to send
        await new Promise((resolve) => setTimeout(resolve, 10000));
      }
    }

    ezAlert({
      title: "Success",
      body: "All emails sent!",
      button: "Close",
    });
  });

  function updateProgress(sent, total) {
    const percent = total > 0 ? (sent / total) * 100 : 0;
    progressBar.css("width", `${percent}%`);
    progressBar.attr("aria-valuenow", sent);
    status.text(`${sent} / ${total} sent`);
  }
});
