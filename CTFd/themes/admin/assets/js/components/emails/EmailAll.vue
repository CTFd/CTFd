<template>
  <div>
    <div v-if="isProcessing" class="alert alert-warning alert-dismissible mb-3" role="alert">
      <i class="fas fa-exclamation-triangle me-2"></i>&nbsp;
      <strong>Email Sending in Progress</strong>
      <br>
      Please do not close this page or disconnect from the internet while emails are being sent. 
      This process may take several minutes to complete.
    </div>

    <form @submit.prevent="handleSubmit">
      <div class="mb-3">
        <label for="body" class="form-label">Email Content</label>
        <textarea
          id="body"
          v-model.trim="body"
          :disabled="isProcessing"
          class="form-control"
          rows="10"
          required
        ></textarea>
      </div>

      <button type="submit" class="btn btn-primary" :disabled="isProcessing">
        {{ isProcessing ? "Sending..." : "Send Emails" }}
      </button>
    </form>

    <div v-if="isProcessing" class="mt-3">
      <div class="progress" style="height: 25px">
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
</template>

<script setup lang="ts">
import { computed, reactive, toRefs, onMounted, onUnmounted } from "vue";
import CTFd from "../../compat/CTFd";
import { ezAlert, ezQuery } from "../../compat/ezq";

// Constants
const DELAY_MS = 5000;
const PER_PAGE = 100;
const MAX_PAGES = 100;
const BATCH_SIZE = 8;

// States
const state = reactive({
  body: "",
  isProcessing: false,
  total: 0,
  sent: 0,
  failed: [] as { id: number; reason: string }[],
});
const { body, isProcessing, total, sent, failed } = toRefs(state);

const progressPercent = computed(() =>
  total.value > 0 ? (sent.value / total.value) * 100 : 0,
);
const statusText = computed(() => `${sent.value} / ${total.value} sent`);

// Beforeunload handler to prevent leaving while emails are sending
const handleBeforeUnload = (event: BeforeUnloadEvent) => {
  if (isProcessing.value) {
    event.preventDefault();
    // Note that this message doesn't actually get shown in the browser
    event.returnValue = "Emails are currently being sent. Are you sure you want to leave?";
    return "Emails are currently being sent. Are you sure you want to leave?";
  }
};

// Setup and cleanup event listeners
onMounted(() => {
  window.addEventListener("beforeunload", handleBeforeUnload);
});

onUnmounted(() => {
  window.removeEventListener("beforeunload", handleBeforeUnload);
});

// Functions
const sleep = (ms: number) => new Promise((r) => setTimeout(r, ms));

async function fetchUsers(page: number) {
  const params = new URLSearchParams({
    page: String(page),
    per_page: String(PER_PAGE),
  });
  const res = await CTFd.fetch(`/api/v1/users?${params}`);
  const json = await res.json();
  return {
    data: json.data ?? [],
    pagination: json.meta?.pagination ?? {},
  };
}

async function sendEmail(userId: number, text: string) {
  const res = await CTFd.fetch(`/api/v1/users/${userId}/email`, {
    method: "POST",
    credentials: "same-origin",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text }),
  });
  
  // Handle rate limiting
  if (res.status === 429) {
    console.log("Rate limit hit (429), waiting for 1 minute...");
    await sleep(60000); // Sleep for 1 minute (60,000ms)
    // Retry the request after rate limit sleep
    const retryRes = await CTFd.fetch(`/api/v1/users/${userId}/email`, {
      method: "POST",
      credentials: "same-origin",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text }),
    });
    try {
      const json = await retryRes.json();
      return json.success === true;
    } catch {
      return false;
    }
  }
  
  try {
    const json = await res.json();
    return json.success === true;
  } catch {
    return false;
  }
}

async function handleSubmit() {
  if (!body.value) return;

  // Show preview and confirmation dialog
  const emailPreview = body.value.length > 200 
    ? body.value.substring(0, 200) + "..." 
    : body.value;
  
  ezQuery({
    title: "Confirm Email Send",
    body: `
      <p>You are about to send the following email to all users:</p>
      <div class="bg-light border-left border-primary border-3" style="padding: 15px; border-width: 3px !important; margin: 10px 0;">
        <pre style="white-space: pre-wrap; margin: 0; font-family: inherit;">${emailPreview}</pre>
      </div>
      <p><strong>Are you sure you want to proceed?</strong></p>
    `,
    success: function () {
      startEmailSending();
    }
  });
}

async function startEmailSending() {
  state.isProcessing = true;
  state.total = 0;
  state.sent = 0;
  state.failed = [];

  try {
    let page = 1;
    let pages = 1;

    while (page <= pages && page <= MAX_PAGES) {
      const { data, pagination } = await fetchUsers(page);
      if (page === 1) {
        state.total = pagination.total ?? 0;
        pages = pagination.pages ?? 1;
      }
      if (!data.length) break;

      // Send emails in batches of BATCH_SIZE
      for (let i = 0; i < data.length; i += BATCH_SIZE) {
        const batch = data.slice(i, i + BATCH_SIZE);
        
        // Send emails in current batch serially
        for (const user of batch) {
          const ok = await sendEmail(user.id, body.value);
          if (ok) state.sent++;
          else state.failed.push({ id: user.id, reason: "Unknown error" });
        }
        
        // Sleep after each batch (except the last one in the page)
        if (i + BATCH_SIZE < data.length) {
          await sleep(DELAY_MS);
        }
      }
      
      page++;
    }
  } catch (e: any) {
    ezAlert({ title: "Fatal Error", body: e.message, button: "Close" });
  } finally {
    let title = "Success";
    let msg = `Finished sending emails. ${sent.value} / ${total.value} sent.`;
    if (failed.value.length) {
      title = "Partial Success";
      msg += `\n\nFailed attempts (${failed.value.length}):`;
      failed.value.forEach((f) => (msg += `\n- User ID ${f.id}: ${f.reason}`));
    }
    ezAlert({ title, body: msg, button: "Close" });
    state.isProcessing = false;
  }
}
</script>
