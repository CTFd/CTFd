<template>
  <div>
    <div class="jumbotron">
      <h1>Email All</h1>
    </div>

    <div class="container">
      <div class="row">
        <div class="col-md-12">
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

            <button
              type="submit"
              class="btn btn-primary"
              :disabled="isProcessing"
            >
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
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, reactive, toRefs } from "vue";
import CTFd from "../../compat/CTFd";
import { ezAlert } from "../../compat/ezq";

// Constants
const DELAY_MS = 60000;
const PER_PAGE = 100;
const MAX_PAGES = 100;
const CONCURRENCY = 10;

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
  try {
    const json = await res.json();
    return json.success === true;
  } catch {
    return false;
  }
}

async function semaphore<T>(
  tasks: (() => Promise<T>)[],
  limit: number,
): Promise<T[]> {
  const results: T[] = [];
  let idx = 0;

  async function runNext(): Promise<void> {
    if (idx >= tasks.length) return;
    const current = idx++;
    const task = tasks[current];
    results[current] = await task();
    await runNext();
  }

  await Promise.all(Array.from({ length: limit }, runNext));
  return results;
}

async function handleSubmit() {
  if (!body.value) return;

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

      const tasks = data.map((user: any) => async () => {
        const ok = await sendEmail(user.id, body.value);
        if (ok) state.sent++;
        else state.failed.push({ id: user.id, reason: "Unknown error" });
        await sleep(DELAY_MS);
      });

      await semaphore(tasks, CONCURRENCY);
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
