import "./main";
import CTFd from "../compat/CTFd";
import $ from "jquery";
import { ezAlert } from "../compat/ezq";

// Configurable constants for batching and rate limiting
const BATCH_SIZE = 50;
const DELAY_MS = 10000;
const PER_PAGE = 100; // Adjust based on API limits; CTFd defaults vary

$(() => {
  const form = $("#email-all-form");
  const progressContainer = $("#progress-container");
  const progressBar = $("#email-progress");
  const status = $("#status");

  form.on("submit", async (e) => {
    e.preventDefault(); // Prevent native form submit to avoid unintended POST requests

    const subject = form.find("input[name='subject']").val();
    const body = form.find("textarea[name='body']").val();
    const html = form.find("input[name='html']").is(":checked");

    progressContainer.show();
    updateProgress(0, 0);

    let total = 0;
    let sent = 0;
    let failed = [];
    let page = 1;
    let totalPages = 1; // Initialize to 1; will update from meta

    try {
      // Loop over pages using pagination metadata for safety (avoids while(true))
      do {
        // Fetch users for the current page (admin-only API)
        const response = await CTFd.api.get("/api/v1/users", {
          params: { page, per_page: PER_PAGE },
        });
        const data = response.data || {};
        const meta = data.meta || {};
        const user_list = data.data || [];

        // Update total and totalPages on first fetch
        if (page === 1) {
          total = meta.pagination ? meta.pagination.total : user_list.length;
          totalPages = meta.pagination ? meta.pagination.pages : 1;
          updateProgress(0, total);
        }

        // If no users on this page, break early (safety net)
        if (user_list.length === 0) {
          break;
        }

        // Process users in batches to respect rate limits
        let users = [...user_list];
        while (users.length > 0) {
          const batch = users.splice(0, BATCH_SIZE);

          // Send batch concurrently but await all
          const reqs = batch.map((user) =>
            sendEmail(user.id, { subject, body, html })
              .then(() => sent++)
              .catch((err) => {
                console.error(`Error sending to user ${user.id}:`, err);
                if (err.response && err.response.status === 403) {
                  throw new Error("Permission denied: Admin access required.");
                }
                failed.push(user.id);
              })
          );

          await Promise.all(reqs);
          updateProgress(sent, total);

          // Delay only if there are more batches on this page
          if (users.length > 0) {
            await delay(DELAY_MS);
          }
        }

        page++;
      } while (page <= totalPages);
    } catch (error) {
      console.error("Failed to fetch users or send emails:", error);
      ezAlert({
        title: "Error",
        body: error.message || "Failed to process emails. Check console for details (e.g., permissions or API issues).",
        button: "Close",
      });
      return;
    }

    // Display final status with partial failure handling
    let alertTitle = "Success";
    let alertBody = `Emails sent to ${sent} / ${total} users.`;
    if (failed.length > 0) {
      alertTitle = "Partial Success";
      alertBody += ` Failed for ${failed.length} users (IDs: ${failed.join(", ")}). Check console.`;
    }
    ezAlert({
      title: alertTitle,
      body: alertBody,
      button: "Close",
    });
  });

  // Helper function to send email to a single user (using CTFd.api)
  function sendEmail(userId, payload) {
    return CTFd.api.post(`/api/v1/users/${userId}/email`, { data: payload });
  }

  // Helper function for progress update
  function updateProgress(sent, total) {
    const percent = total > 0 ? (sent / total) * 100 : 0;
    progressBar.css("width", `${percent}%`);
    progressBar.attr("aria-valuenow", sent);
    status.text(`${sent} / ${total} sent`);
  }

  // Helper function for async delay
  function delay(ms) {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }
});