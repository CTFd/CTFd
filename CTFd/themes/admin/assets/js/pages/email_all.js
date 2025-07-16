import "./main";
import CTFd from "../compat/CTFd";
import $ from "jquery";
import { ezAlert } from "../compat/ezq";

// Configuration
const BATCH_SIZE = 1;
const DELAY_MS = 7000;
const PER_PAGE = 100;
const MAX_PAGES = 100;

$(() => {
  const form = $("#email-all-form");
  const progressContainer = $("#progress-container");
  const progressBar = $("#email-progress");
  const status = $("#status");

  form.on("submit", async (e) => {
    e.preventDefault();

    const subject = form.find("input[name='subject']").val().trim();
    const body = form.find("textarea[name='body']").val().trim();
    const html = form.find("input[name='html']").is(":checked");

    if (subject.length === 0 || body.length === 0) {
      ezAlert({
        title: "Error",
        body: "Subject and body are required.",
        button: "Close",
      });
      return;
    }

    progressContainer.show();
    updateProgress(0, 0);

    let total = 0;
    let sent = 0;
    let failed = [];
    let page = 1;
    let totalPages = 1;

    try {
      for (page = 1; page <= totalPages && page <= MAX_PAGES; page++) {
        const response = await CTFd.api.get_user_list({
          page,
          per_page: PER_PAGE,
        });

        const responseData = response.data || {};
        const user_list = responseData.data || responseData || [];
        const meta = responseData.meta || {};
        const pagination = meta.pagination || {};

        if (page === 1) {
          total = pagination.total || meta.count || user_list.length || 0;
          totalPages = Math.ceil(total / PER_PAGE) || 1;
          updateProgress(0, total);
        }

        if (user_list.length === 0) {
          break;
        }

        let users = [...user_list];
        while (users.length > 0) {
          const batch = users.splice(0, BATCH_SIZE);

          for (const user of batch) {
            const payload = { subject, body };
            if (html) payload.html = true;

            try {
              const emailResponse = await sendEmail(user.id, payload);

              if (emailResponse.success === true) {
                sent++;
              } else {
                failed.push(user.id);
              }
            } catch (err) {
              failed.push(user.id);
            }

            await delay(DELAY_MS);
            updateProgress(sent, total);
          }
        }
      }
    } catch (error) {
      ezAlert({
        title: "Error",
        body: error.message || "Failed to process emails.",
        button: "Close",
      });
      return;
    }

    let alertTitle = "Success";
    let alertBody = `Emails sent to ${sent} / ${total} users.`;
    if (failed.length > 0) {
      alertTitle = "Partial Success";
      alertBody += ` Failed for ${failed.length} users (IDs: ${failed.join(", ")}).`;
    }
    ezAlert({
      title: alertTitle,
      body: alertBody,
      button: "Close",
    });
  });

  // Helpers
  async function sendEmail(userId, payload) {
    const response = await CTFd.fetch(`/api/v1/users/${userId}/email`, {
      method: "POST",
      credentials: "same-origin",
      headers: {
        Accept: "application/json",
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    });

    let result;
    try {
      result = await response.json();
    } catch (parseErr) {
      result = { success: false };
    }

    if (!response.ok) {
      const err = new Error(`HTTP error! Status: ${response.status}`);
      err.status = response.status;
      throw err;
    }
    return result;
  }

  function updateProgress(sent, total) {
    const percent = total > 0 ? (sent / total) * 100 : 0;
    progressBar.css("width", `${percent}%`);
    progressBar.attr("aria-valuenow", sent);
    status.text(`${sent} / ${total} sent`);
  }

  function delay(ms) {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }
});