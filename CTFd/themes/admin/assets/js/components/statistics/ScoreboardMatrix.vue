<template>
  <div>
    <div v-if="loading" class="text-center py-5">
      <i class="fas fa-circle-notch fa-spin fa-3x fa-fw spinner"></i>
    </div>
    <div v-else-if="error" class="text-center py-5">
      <p class="text-danger">{{ error }}</p>
    </div>
    <div v-else class="mt-3">
      <div class="accordion" id="matrix-filters-accordion">
        <div class="card" style="border-bottom: 1px solid rgba(0, 0, 0, 0.125)">
          <div class="card-header p-0" id="headingFilters">
            <h2 class="mb-0">
              <button
                class="btn btn-link btn-block text-left p-1 text-decoration-none collapsed"
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
                <div class="col-md-3 mb-3 mb-md-0">
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

                <div class="col-md-3 mb-3 mb-md-0">
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

                <div class="col-md-3 mb-3 mb-md-0">
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
                      <option value="position">Position (Default)</option>
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

                <div class="col-md-3">
                  <div class="card p-2 shadow-sm filter-col">
                    <h6>Filter Brackets</h6>
                    <input
                      type="text"
                      class="form-control form-control-sm mb-2"
                      v-model="bracketSearch"
                      placeholder="Search brackets..."
                    />
                    <div class="filter-list">
                      <div
                        v-for="bracket in filteredBracketList"
                        :key="bracket.id"
                        class="px-2 py-1"
                      >
                        <div class="form-check">
                          <input
                            class="form-check-input"
                            type="checkbox"
                            :value="bracket.id"
                            v-model="selectedBracketIds"
                            :id="'bracket-' + bracket.id"
                          />
                          <label
                            class="form-check-label small"
                            :for="'bracket-' + bracket.id"
                          >
                            {{ bracket.name }}
                          </label>
                        </div>
                      </div>
                    </div>
                    <div class="mt-1">
                      <small>
                        <a href="#" @click.prevent="selectAllBrackets"
                          >Select All</a
                        >
                        /
                        <a href="#" @click.prevent="deselectAllBrackets"
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

    <div class="d-flex justify-content-end mb-2">
      <div class="d-flex align-items-center mr-3">
        <div
          style="width: 15px; height: 15px; background-color: #28a745"
          class="mr-1 border"
        ></div>
        <small>Solved</small>
      </div>
      <div class="d-flex align-items-center mr-3">
        <div
          style="width: 15px; height: 15px; background-color: #ffc107"
          class="mr-1 border"
        ></div>
        <small>Attempted</small>
      </div>
      <div class="d-flex align-items-center">
        <div
          style="width: 15px; height: 15px; background-color: #17a2b8"
          class="mr-1 border"
        ></div>
        <small>Opened</small>
      </div>
    </div>

    <div class="matrix-container">
      <table class="table table-striped table-sm mb-0" id="matrix-scoreboard">
        <thead class="thead-dark">
          <tr>
            <th class="sticky-header sticky-col-place text-center">Place</th>
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
            <td class="font-weight-bold sticky-cell sticky-col-place">
              {{ user.place }}
            </td>
            <td
              class="font-weight-bold sticky-cell sticky-col-name"
              :title="user.name"
            >
              <a :href="user.url" class="text-decoration-none">{{
                user.name
              }}</a>
              <span class="badge bg-secondary ml-1 text-white">{{
                user.bracket_name
              }}</span>
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
  </div>
</template>

<script>
import CTFd from "../../compat/CTFd";

export default {
  data() {
    return {
      users: [],
      challenges: [],
      brackets: [],
      loading: true,
      error: null,
      userSearch: "",
      challengeSearch: "",
      categorySearch: "",
      bracketSearch: "",
      selectedUserIds: [],
      selectedChallengeIds: [],
      selectedCategories: [],
      selectedBracketIds: [],
      challengeSort: "position",
      userMode: "",
    };
  },
  created() {
    this.fetchMatrixData();
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
    bracketSearch() {
      this.persistSettings();
    },
    selectedBracketIds() {
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
    filteredBracketList() {
      if (!this.bracketSearch) return this.brackets;
      const lower = this.bracketSearch.toLowerCase();
      return this.brackets.filter((b) => b.name.toLowerCase().includes(lower));
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
        .filter(
          (u) =>
            this.selectedUserIds.includes(u.id) &&
            this.selectedBracketIds.includes(
              u.bracket_id !== null ? u.bracket_id : "no_bracket",
            ),
        )
        .sort((a, b) => a.place - b.place);
    },
    displayChallenges() {
      let filtered = this.challenges.filter(
        (c) =>
          this.selectedChallengeIds.includes(c.id) &&
          this.selectedCategories.includes(c.category),
      );

      return filtered.sort((a, b) => {
        if (this.challengeSort === "position") {
          // position (asc), 0 is last, then value, then name, finally id
          if (a.position === 0 && b.position !== 0) return 1;
          if (b.position === 0 && a.position !== 0) return -1;
          return (
            a.position - b.position ||
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
    fetchMatrixData() {
      this.loading = true;
      this.error = null;
      this.userMode = CTFd.config.userMode;
      CTFd.fetch("/api/v1/statistics/progression/matrix", {
        method: "GET",
        credentials: "same-origin",
        headers: {},
      })
        .then((response) => response.json())
        .then((result) => {
          if (result.success) {
            this.users = result.data.scoreboard;
            this.challenges = result.data.challenges;
            this.brackets = result.data.brackets;
            // Add a "No Bracket" entry if any users have no bracket assigned
            const hasNoBracketUsers = this.users.some(
              (u) => u.bracket_id === null,
            );
            if (hasNoBracketUsers) {
              this.brackets.unshift({
                id: "no_bracket",
                name: "(No Bracket)",
              });
            }
            this.restoreSettings();
          } else {
            this.error = "Failed to load progression data";
          }
        })
        .catch((err) => {
          console.error("Failed to fetch progression data", err);
          this.error = "Failed to load progression data";
        })
        .finally(() => {
          this.loading = false;
        });
    },
    resetFilters() {
      this.userSearch = "";
      this.challengeSearch = "";
      this.categorySearch = "";
      this.bracketSearch = "";
      this.challengeSort = "position";
      this.selectAllUsers();
      this.selectAllChallenges();
      this.selectAllCategories();
      this.selectAllBrackets();
    },
    restoreSettings() {
      const savedSettings = localStorage.getItem(
        "ctfd-scoreboard-matrix-settings",
      );

      if (savedSettings) {
        try {
          const settings = JSON.parse(savedSettings);
          this.userSearch = settings.userSearch || "";
          this.challengeSearch = settings.challengeSearch || "";
          this.categorySearch = settings.categorySearch || "";
          this.challengeSort = settings.challengeSort || "position";
          this.selectedUserIds =
            settings.selectedUserIds || this.users.map((u) => u.id);
          this.selectedChallengeIds =
            settings.selectedChallengeIds || this.challenges.map((c) => c.id);
          this.selectedCategories =
            settings.selectedCategories || this.uniqueCategories;
          this.selectedBracketIds =
            settings.selectedBracketIds || this.brackets.map((b) => b.id);
        } catch (e) {
          console.error("Failed to load scoreboard matrix settings", e);
          this.resetFilters();
        }
      } else {
        this.selectAllUsers();
        this.selectAllChallenges();
        this.selectAllCategories();
        this.selectAllBrackets();
      }
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
        bracketSearch: this.bracketSearch,
        selectedBracketIds: this.selectedBracketIds,
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
    selectAllBrackets() {
      this.selectedBracketIds = this.brackets.map((b) => b.id);
    },
    deselectAllBrackets() {
      this.selectedBracketIds = [];
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
