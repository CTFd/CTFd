<template>
  <div>
    <div class="matrix-container">
      <table class="table table-striped table-sm mb-0" id="matrix-scoreboard">
        <thead class="thead-dark">
          <tr>
            <th class="sticky-header sticky-col-rank text-center">Rank</th>
            <th class="sticky-header sticky-col-name text-center">
              {{ userMode === "teams" ? "Team" : "User" }}
            </th>
            <th class="sticky-header sticky-col-score text-center">Score</th>
            <th
              v-for="challenge in displayChallenges"
              :key="challenge.id"
              class="text-center text-white challenge-col sticky-header"
            >
              <a
                :href="challenge.url"
                class="text-white text-decoration-none"
                target="_blank"
              >
                <div class="challenge-info">
                  {{ challenge.name }}
                  <br />
                  {{ challenge.value }}pt
                </div>
              </a>
            </th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="user in displayUsers" :key="user.id">
            <td class="font-weight-bold sticky-cell sticky-col-rank">
              {{ user.rank }}
            </td>
            <td
              class="font-weight-bold sticky-cell sticky-col-name"
              :title="user.name"
            >
              <a :href="user.url" class="text-decoration-none">{{
                user.name
              }}</a>
            </td>
            <td class="font-weight-bold sticky-cell sticky-col-score">
              {{ user.score }}
            </td>
            <td
              v-for="challenge in displayChallenges"
              :key="challenge.id"
              class="text-center challenge-cell"
              :style="getCellStyle(user, challenge)"
            >
              {{ getCellSymbol(user, challenge) }}
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div class="mt-3">
      <div class="accordion" id="matrix-filters-accordion">
        <div class="card">
          <div class="card-header p-0" id="headingFilters">
            <h2 class="mb-0">
              <button
                class="btn btn-link btn-block text-left p-3 text-decoration-none collapsed"
                type="button"
                data-toggle="collapse"
                data-target="#collapseFilters"
                aria-expanded="false"
                aria-controls="collapseFilters"
              >
                <i class="fas fa-filter mr-2"></i> Filter Matrix Data
              </button>
            </h2>
          </div>

          <div
            id="collapseFilters"
            class="collapse"
            aria-labelledby="headingFilters"
          >
            <div class="card-body bg-light">
              <div
                class="d-flex justify-content-between align-items-center mb-3"
              >
                <h5 class="mb-0">Filters</h5>
                <div>
                  <button
                    class="btn btn-secondary btn-sm"
                    @click="resetFilters"
                  >
                    Reset All
                  </button>
                </div>
              </div>

              <div class="row">
                <div class="col-md-4 mb-3 mb-md-0">
                  <div class="card p-2 shadow-sm filter-col">
                    <h6>
                      Filter {{ userMode === "teams" ? "Teams" : "Users" }}
                    </h6>
                    <input
                      type="text"
                      class="form-control form-control-sm mb-2"
                      v-model="userSearch"
                      :placeholder="
                        'Search ' +
                        (userMode === 'teams' ? 'teams' : 'users') +
                        '...'
                      "
                    />
                    <div class="filter-list">
                      <div
                        v-for="user in filteredUserList"
                        :key="user.id"
                        class="px-2 py-1"
                      >
                        <div class="form-check">
                          <input
                            class="form-check-input"
                            type="checkbox"
                            :value="user.id"
                            v-model="selectedUserIds"
                            :id="'user-' + user.id"
                          />
                          <label
                            class="form-check-label small"
                            :for="'user-' + user.id"
                          >
                            {{ user.name }}
                          </label>
                        </div>
                      </div>
                    </div>
                    <div class="mt-1">
                      <small>
                        <a href="#" @click.prevent="selectAllUsers"
                          >Select All</a
                        >
                        /
                        <a href="#" @click.prevent="deselectAllUsers">None</a>
                      </small>
                    </div>
                  </div>
                </div>

                <div class="col-md-4 mb-3 mb-md-0">
                  <div class="card p-2 shadow-sm filter-col">
                    <h6>Filter Categories</h6>
                    <input
                      type="text"
                      class="form-control form-control-sm mb-2"
                      v-model="categorySearch"
                      placeholder="Search categories..."
                    />
                    <div class="filter-list">
                      <div
                        v-for="cat in filteredCategoryList"
                        :key="cat"
                        class="px-2 py-1"
                      >
                        <div class="form-check">
                          <input
                            class="form-check-input"
                            type="checkbox"
                            :value="cat"
                            v-model="selectedCategories"
                            :id="'cat-' + cat"
                          />
                          <label
                            class="form-check-label small"
                            :for="'cat-' + cat"
                          >
                            {{ cat }}
                          </label>
                        </div>
                      </div>
                    </div>
                    <div class="mt-1">
                      <small>
                        <a href="#" @click.prevent="selectAllCategories"
                          >Select All</a
                        >
                        /
                        <a href="#" @click.prevent="deselectAllCategories"
                          >None</a
                        >
                      </small>
                    </div>
                  </div>
                </div>

                <div class="col-md-4">
                  <div class="card p-2 shadow-sm filter-col">
                    <h6>Filter Challenges</h6>
                    <input
                      type="text"
                      class="form-control form-control-sm mb-2"
                      v-model="challengeSearch"
                      placeholder="Search challenges..."
                    />
                    <label class="mb-0">Sort By</label>
                    <select
                      class="form-control form-control-sm mb-2"
                      v-model="challengeSort"
                    >
                      <option value="weight">Weight (Default)</option>
                      <option value="id">ID (Ascending)</option>
                      <option value="id-desc">ID (Descending)</option>
                      <option value="name-asc">
                        Alphabetical (Ascending: A-Z)
                      </option>
                      <option value="name-desc">
                        Alphabetical (Descending: Z-A)
                      </option>
                      <option value="value-asc">Points (Ascending)</option>
                      <option value="value-desc">Points (Descending)</option>
                    </select>
                    <div class="filter-list">
                      <div
                        v-for="chal in filteredChallengeList"
                        :key="chal.id"
                        class="px-2 py-1"
                      >
                        <div class="form-check">
                          <input
                            class="form-check-input"
                            type="checkbox"
                            :value="chal.id"
                            v-model="selectedChallengeIds"
                            :id="'chal-' + chal.id"
                          />
                          <label
                            class="form-check-label small"
                            :for="'chal-' + chal.id"
                          >
                            {{ chal.name }}
                          </label>
                        </div>
                      </div>
                    </div>
                    <div class="mt-1">
                      <small>
                        <a href="#" @click.prevent="selectAllChallenges"
                          >Select All</a
                        >
                        /
                        <a href="#" @click.prevent="deselectAllChallenges"
                          >None</a
                        >
                      </small>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  props: {
    initialData: {
      type: Array,
      default: () => [],
    },
    challenges: {
      type: Array,
      default: () => [],
    },
    userMode: String,
  },
  data() {
    return {
      users: [],
      userSearch: "",
      challengeSearch: "",
      categorySearch: "",
      selectedUserIds: [],
      selectedChallengeIds: [],
      selectedCategories: [],
      challengeSort: "weight",
    };
  },
  created() {
    this.users = [...this.initialData];
    const savedSettings = localStorage.getItem(
      "ctfd-scoreboard-matrix-settings",
    );

    if (savedSettings) {
      try {
        const settings = JSON.parse(savedSettings);
        this.userSearch = settings.userSearch || "";
        this.challengeSearch = settings.challengeSearch || "";
        this.categorySearch = settings.categorySearch || "";
        this.challengeSort = settings.challengeSort || "weight";
        this.selectedUserIds =
          settings.selectedUserIds || this.users.map((u) => u.id);
        this.selectedChallengeIds =
          settings.selectedChallengeIds || this.challenges.map((c) => c.id);
        this.selectedCategories =
          settings.selectedCategories || this.uniqueCategories;
      } catch (e) {
        console.error("Failed to load scoreboard matrix settings", e);
        this.selectAllUsers();
        this.selectAllChallenges();
        this.selectAllCategories();
      }
    } else {
      this.selectAllUsers();
      this.selectAllChallenges();
      this.selectAllCategories();
    }
  },
  watch: {
    userSearch() {
      this.persistSettings();
    },
    challengeSearch() {
      this.persistSettings();
    },
    categorySearch() {
      this.persistSettings();
    },
    challengeSort() {
      this.persistSettings();
    },
    selectedUserIds() {
      this.persistSettings();
    },
    selectedChallengeIds() {
      this.persistSettings();
    },
    selectedCategories() {
      this.persistSettings();
    },
  },
  computed: {
    filteredUserList() {
      if (!this.userSearch) return this.users;
      const lower = this.userSearch.toLowerCase();
      return this.users.filter((u) => u.name.toLowerCase().includes(lower));
    },
    filteredChallengeList() {
      if (!this.challengeSearch) return this.challenges;
      const lower = this.challengeSearch.toLowerCase();
      return this.challenges.filter((c) =>
        c.name.toLowerCase().includes(lower),
      );
    },
    uniqueCategories() {
      return [...new Set(this.challenges.map((c) => c.category))].sort();
    },
    filteredCategoryList() {
      if (!this.categorySearch) return this.uniqueCategories;
      const lower = this.categorySearch.toLowerCase();
      return this.uniqueCategories.filter((c) =>
        c.toLowerCase().includes(lower),
      );
    },
    displayUsers() {
      return this.users
        .filter((u) => this.selectedUserIds.includes(u.id))
        .sort((a, b) => a.rank - b.rank);
    },
    displayChallenges() {
      let filtered = this.challenges.filter(
        (c) =>
          this.selectedChallengeIds.includes(c.id) &&
          this.selectedCategories.includes(c.category),
      );

      return filtered.sort((a, b) => {
        if (this.challengeSort === "weight") {
          // weight, then value, then alphabetical finally id
          return (
            a.weight - b.weight ||
            a.value - b.value ||
            a.category.localeCompare(b.category) ||
            a.id - b.id
          );
        }
        if (this.challengeSort === "name-asc")
          return a.name.localeCompare(b.name);
        if (this.challengeSort === "name-desc")
          return b.name.localeCompare(a.name);
        if (this.challengeSort === "value-asc") return a.value - b.value;
        if (this.challengeSort === "value-desc") return b.value - a.value;
        if (this.challengeSort === "id-desc") return b.id - a.id;
        return a.id - b.id;
      });
    },
  },
  methods: {
    resetFilters() {
      this.userSearch = "";
      this.challengeSearch = "";
      this.categorySearch = "";
      this.challengeSort = "weight";
      this.selectAllUsers();
      this.selectAllChallenges();
      this.selectAllCategories();
    },
    persistSettings() {
      const settings = {
        userSearch: this.userSearch,
        challengeSearch: this.challengeSearch,
        categorySearch: this.categorySearch,
        challengeSort: this.challengeSort,
        selectedUserIds: this.selectedUserIds,
        selectedChallengeIds: this.selectedChallengeIds,
        selectedCategories: this.selectedCategories,
      };
      localStorage.setItem(
        "ctfd-scoreboard-matrix-settings",
        JSON.stringify(settings),
      );
    },
    selectAllUsers() {
      this.selectedUserIds = this.users.map((u) => u.id);
    },
    deselectAllUsers() {
      this.selectedUserIds = [];
    },
    selectAllChallenges() {
      this.selectedChallengeIds = this.challenges.map((c) => c.id);
    },
    deselectAllChallenges() {
      this.selectedChallengeIds = [];
    },
    selectAllCategories() {
      this.selectedCategories = this.uniqueCategories;
    },
    deselectAllCategories() {
      this.selectedCategories = [];
    },
    getCellStyle(user, challenge) {
      const isSolved = user.solves.includes(challenge.id);
      const isAttempted = user.attempts.includes(challenge.id);
      const isOpened = user.opens.includes(challenge.id);

      if (isSolved) {
        return { backgroundColor: "#28a745", color: "white" };
      } else if (isAttempted) {
        return { backgroundColor: "#ffc107", color: "#212529" };
      } else if (isOpened) {
        return { backgroundColor: "#17a2b8", color: "white" };
      } else {
        return { backgroundColor: "#f8f9fa", color: "#6c757d" };
      }
    },
    getCellSymbol(user, challenge) {
      const isSolved = user.solves.includes(challenge.id);
      if (isSolved) return "✓";
      return "-";
    },
  },
};
</script>
