<template>
  <div>
    <div class="row mb-3">
      <div class="col-md-12">
        <!-- Loading State -->
        <div v-if="loading" class="text-center">
          <i class="fas fa-circle-notch fa-spin spinner"></i> Loading ratings...
        </div>

        <!-- Error State -->
        <div v-else-if="error" class="alert alert-danger">
          {{ error }}
        </div>

        <!-- Initial State (before loading) -->
        <div
          v-else-if="!ratings.length && !loading"
          class="text-center text-muted py-4"
        >
          <i class="fa fa-star fa-2x mb-3"></i>
          <p>Loading Ratings</p>
        </div>

        <!-- Ratings Content -->
        <div v-else>
          <!-- No Ratings State -->
          <div v-if="!ratings.length" class="alert alert-info">
            <i class="fa fa-star fa-2x mb-3"></i>
            <strong>No ratings yet</strong> - This challenge has not been rated
            by any users.
          </div>
          <!-- Rating Summary -->
          <div v-if="meta.summary.count > 0" class="mb-3">
            <div class="row">
              <div class="col-md-6 text-center">
                <h5>
                  <strong>
                    Average Rating:
                    {{
                      meta.summary.average
                        ? meta.summary.average.toFixed(2)
                        : "N/A"
                    }}/5
                  </strong>
                </h5>
              </div>
              <div class="col-md-6 text-center">
                <h5>
                  <strong> Total Ratings: {{ meta.summary.count }} </strong>
                </h5>
              </div>
            </div>
          </div>

          <!-- Ratings List -->
          <div class="ratings-list">
            <div v-for="rating in ratings" :key="rating.id" class="mb-2">
              <div class="row border rounded p-3">
                <div class="col-md-8 p-0">
                  <h6 class="mb-1">
                    <a :href="`${urlRoot}/admin/users/${rating.user.id}`">{{
                      rating.user.name
                    }}</a>
                    <span class="text-warning ml-2">{{
                      getStars(rating.value)
                    }}</span>
                    <small class="text-muted">({{ rating.value }}/5)</small>
                  </h6>
                  <p v-if="rating.review">{{ rating.review }}</p>
                </div>
                <div class="col-md-4 text-right p-0">
                  <small class="text-muted">{{
                    toLocalTime(rating.date)
                  }}</small>
                </div>
              </div>
            </div>
          </div>

          <!-- Pagination -->
          <div
            v-if="meta.pagination.pages > 1"
            class="d-flex justify-content-between align-items-center mt-3"
          >
            <!-- Previous button -->
            <button
              v-if="meta.pagination.prev"
              @click="loadPage(meta.pagination.prev)"
              class="btn btn-secondary"
              :disabled="loading"
            >
              <i class="fa fa-arrow-left"></i> Previous
            </button>
            <div v-else></div>

            <!-- Page info -->
            <span class="text-muted">
              Page {{ meta.pagination.page }} of {{ meta.pagination.pages }}
            </span>

            <!-- Next button -->
            <button
              v-if="meta.pagination.next"
              @click="loadPage(meta.pagination.next)"
              class="btn btn-secondary"
              :disabled="loading"
            >
              Next <i class="fa fa-arrow-right"></i>
            </button>
            <div v-else></div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import CTFd from "../../compat/CTFd";
import dayjs from "dayjs";

export default {
  name: "RatingsViewer",
  props: {
    challengeId: {
      type: [String, Number],
      required: true,
    },
  },
  data() {
    return {
      loading: false,
      error: null,
      ratings: [],
      meta: {
        summary: {
          average: null,
          count: 0,
        },
        pagination: {
          page: 1,
          pages: 1,
          prev: null,
          next: null,
          per_page: 50,
          total: 0,
        },
      },
      urlRoot: CTFd.config.urlRoot,
    };
  },
  created() {
    document
      .getElementById("ratings-viewer-load")
      .addEventListener("click", this.onModalShow);
  },
  methods: {
    onModalShow() {
      // This fires when modal is about to be shown
      this.loadRatings();
    },
    async loadRatings(page = 1) {
      this.loading = true;
      this.error = null;

      try {
        const response = await CTFd.fetch(
          `/api/v1/challenges/${this.challengeId}/ratings?page=${page}`,
          {
            method: "GET",
            credentials: "same-origin",
            headers: {
              Accept: "application/json",
              "Content-Type": "application/json",
            },
          },
        );

        const data = await response.json();

        if (data.success) {
          this.ratings = data.data;
          this.meta = data.meta;
        } else {
          this.error = "Failed to load ratings";
          console.error("API Error:", data);
        }
      } catch (err) {
        console.error("Error loading ratings:", err);
        this.error = "Error loading ratings";
      } finally {
        this.loading = false;
      }
    },
    loadPage(page) {
      this.loadRatings(page);
    },
    getStars(value) {
      const filled = "★".repeat(value);
      const empty = "☆".repeat(5 - value);
      return filled + empty;
    },
    toLocalTime(date) {
      return dayjs(date).format("MMMM Do, h:mm:ss A");
    },
  },
};
</script>

<style scoped></style>
