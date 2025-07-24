<template>
  <div>
    <div class="jumbotron">
      <div class="container">
        <h1>Email All</h1>
      </div>
    </div>

    <div class="container">
      <div class="row">
        <div class="col-md-12">
          <form @submit.prevent="handleSubmit">
            <div class="form-group">
              <label for="body">Email Content</label>
              <textarea
                id="body"
                class="form-control"
                rows="10"
                v-model="body"
                :disabled="isProcessing"
                required
              ></textarea>
            </div>

            <button
              type="submit"
              class="btn btn-primary"
              :disabled="isProcessing"
            >
              {{ isProcessing ? "Sending..." : "Send Emails" }}
            </button>
          </form>

          <div v-if="isProcessing" class="mt-3">
            <div class="progress">
              <div
                class="progress-bar"
                role="progressbar"
                :style="{ width: progressPercent + '%' }"
                :aria-valuenow="sent"
                aria-valuemin="0"
                :aria-valuemax="total"
              ></div>
            </div>
            <p class="mt-1 text-center">{{ statusText }}</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import CTFd from "../../compat/CTFd";
import { ezAlert } from "../../compat/ezq";

const DELAY_MS = 2000;
const PER_PAGE = 100;
const MAX_PAGES = 100;

export default {
  name: "EmailAll",
  data() {
    return {
      body: "",
      isProcessing: false,
      total: 0,
      sent: 0,
      failed: [],
    };
  },
  computed: {
    progressPercent() {
      return this.total > 0 ? (this.sent / this.total) * 100 : 0;
    },
    statusText() {
      return `${this.sent} / ${this.total} sent`;
    },
  },
  methods: {
    delay(ms) {
      return new Promise((resolve) => setTimeout(resolve, ms));
    },

    async sendEmail(userId, payload) {
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

      return result;
    },

    async handleSubmit() {
      if (this.body.trim().length === 0) {
        return ezAlert({
          title: "Error",
          body: "Email content is required.",
          button: "Close",
        });
      }

      this.isProcessing = true;
      this.total = 0;
      this.sent = 0;
      this.failed = [];

      try {
        let currentPage = 1;
        let totalPages = 1;

        while (currentPage <= totalPages && currentPage <= MAX_PAGES) {
          const params = new URLSearchParams({
            page: currentPage,
            per_page: PER_PAGE,
          });

          const rawResponse = await CTFd.fetch(
            `/api/v1/users?${params.toString()}`,
          );
          const response = await rawResponse.json();

          const user_list = response.data || [];
          const meta = response.meta || {};
          const pagination = meta.pagination || {};

          if (currentPage === 1) {
            this.total = pagination.total || 0;
            totalPages = pagination.pages || 1;
          }

          if (user_list.length === 0) break;

          for (const user of user_list) {
            const emailResponse = await this.sendEmail(user.id, {
              text: this.body,
            });

            if (emailResponse.success === true) {
              this.sent++;
            } else {
              this.failed.push({
                id: user.id,
                reason: emailResponse.errors
                  ? Object.values(emailResponse.errors).flat().join(", ")
                  : "Unknown error",
              });
            }
            await this.delay(DELAY_MS);
          }
          currentPage++;
        }
      } catch (error) {
        ezAlert({
          title: "Fatal Error",
          body: error.message || "Failed to process emails.",
          button: "Close",
        });
      } finally {
        let alertTitle = "Success";
        let alertBody = `Finished sending emails. ${this.sent} / ${this.total} sent.`;
        if (this.failed.length > 0) {
          alertTitle = "Partial Success";
          alertBody += `\n\nFailed attempts (${this.failed.length}):`;
          this.failed.forEach(
            (f) => (alertBody += `\n- User ID ${f.id}: ${f.reason}`),
          );
        }
        ezAlert({ title: alertTitle, body: alertBody, button: "Close" });
        this.isProcessing = false;
      }
    },
  },
};
</script>

<style scoped>
.progress {
  height: 25px;
}
.progress-bar {
  transition: width 0.2s ease-in-out;
}
</style>
