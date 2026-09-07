import Alpine from "alpinejs";
import dayjs from "dayjs";

import CTFd from "./index";

import { Modal, Tab, Tooltip } from "bootstrap";
import highlight from "./theme/highlight";

function addTargetBlank(html) {
  let dom = new DOMParser();
  let view = dom.parseFromString(html, "text/html");
  let links = view.querySelectorAll('a[href*="://"]');
  links.forEach(link => {
    link.setAttribute("target", "_blank");
  });
  return view.documentElement.outerHTML;
}

window.Alpine = Alpine;

Alpine.store("challenge", {
  data: {
    view: "",
  },
});

Alpine.data("Hint", () => ({
  id: null,
  html: null,

  async showHint(event) {
    if (event.target.open) {
      let response = await CTFd.pages.challenge.loadHint(this.id);
      let hint = response.data;
      if (hint.content) {
        this.html = addTargetBlank(hint.html);
      } else {
        let answer = await CTFd.pages.challenge.displayUnlock(this.id);
        if (answer) {
          let unlock = await CTFd.pages.challenge.loadUnlock(this.id);

          if (unlock.success) {
            let response = await CTFd.pages.challenge.loadHint(this.id);
            let hint = response.data;
            this.html = addTargetBlank(hint.html);
          } else {
            event.target.open = false;
            CTFd._functions.challenge.displayUnlockError(unlock);
          }
        } else {
          event.target.open = false;
        }
      }
    }
  },
}));

Alpine.data("Challenge", () => ({
  id: null,
  next_id: null,
  submission: "",
  tab: null,
  solves: [],
  solution: null,
  solutionLoading: false,
  response: null,
  share_url: null,
  isSubmitting: false,
  submitResult: null,
  showSolvesTab: false,
  showSolutionTab: false,

  async init() {
    highlight();
  },

  getStyles() {
    let styles = {
      "modal-dialog": true,
    };
    try {
      let size = CTFd.config.themeSettings.challenge_window_size;
      switch (size) {
        case "sm":
          styles["modal-sm"] = true;
          break;
        case "lg":
          styles["modal-lg"] = true;
          break;
        case "xl":
          styles["modal-xl"] = true;
          break;
        default:
          break;
      }
    } catch (error) {
      console.log("Error processing challenge_window_size");
      console.log(error);
    }
    return styles;
  },

  async showChallenge() {
    this.showSolvesTab = false;
    this.showSolutionTab = false;
    new Tab(this.$el).show();
  },

  async showSolves() {
    this.solves = await CTFd.pages.challenge.loadSolves(this.id);
    this.solves.forEach(solve => {
      solve.date = dayjs(solve.date).format("MMMM Do, h:mm:ss A");
      return solve;
    });
    new Tab(this.$el).show();
  },

  async toggleSolves() {
    if (!this.showSolvesTab) {
      this.solves = await CTFd.pages.challenge.loadSolves(this.id);
      this.solves.forEach(solve => {
        solve.date = dayjs(solve.date).format("MMMM Do, h:mm:ss A");
        return solve;
      });
      this.showSolutionTab = false;
    }
    this.showSolvesTab = !this.showSolvesTab;
  },

  getSolutionId() {
    let data = Alpine.store("challenge").data;
    return data.solution_id;
  },

  getSolutionState() {
    let data = Alpine.store("challenge").data;
    return data.solution_state;
  },

  setSolutionId(solutionId) {
    Alpine.store("challenge").data.solution_id = solutionId;
  },

  async fetchSolution(solutionId) {
    const response = await CTFd.fetch(`/api/v1/solutions/${solutionId}`, {
      method: "GET",
    });
    const body = await response.json();
    return body.data;
  },

  async loadSolution(solutionId) {
    // Fetch the solution. If the content is already available (visible/admin
    // or previously unlocked) render it directly.
    let solution = await this.fetchSolution(solutionId);
    if (solution && solution.html) {
      this.solution = addTargetBlank(solution.html);
      return;
    }

    // Otherwise the solution is locked. Solutions have no point cost, so we
    // unlock it and then re-fetch the now-visible content.
    const unlockResponse = await CTFd.fetch("/api/v1/unlocks", {
      method: "POST",
      body: JSON.stringify({ target: solutionId, type: "solutions" }),
    });
    const unlock = await unlockResponse.json();
    if (unlock.success) {
      solution = await this.fetchSolution(solutionId);
      this.solution = solution && solution.html ? addTargetBlank(solution.html) : null;
    } else {
      this.solution = null;
    }
  },

  async toggleSolution() {
    if (!this.showSolutionTab) {
      let solutionId = this.getSolutionId();
      if (!solutionId) return;

      if (!this.solution) {
        this.solutionLoading = true;
        try {
          await this.loadSolution(solutionId);
        } finally {
          this.solutionLoading = false;
        }
      }
      this.showSolvesTab = false;
    }
    this.showSolutionTab = !this.showSolutionTab;
  },

  getNextId() {
    let data = Alpine.store("challenge").data;
    return data.next_id;
  },

  async nextChallenge() {
    let modal = Modal.getOrCreateInstance("[x-ref='challengeWindow']");

    modal._element.addEventListener(
      "hidden.bs.modal",
      event => {
        Alpine.nextTick(() => {
          this.$dispatch("load-challenge", this.getNextId());
        });
      },
      { once: true },
    );
    modal.hide();
  },

  async getShareUrl() {
    let body = {
      type: "solve",
      challenge_id: this.id,
    };
    const response = await CTFd.fetch("/api/v1/shares", {
      method: "POST",
      body: JSON.stringify(body),
    });
    const data = await response.json();
    const url = data["data"]["url"];
    this.share_url = url;
  },

  copyShareUrl() {
    navigator.clipboard.writeText(this.share_url);
    let t = Tooltip.getOrCreateInstance(this.$el);
    t.enable();
    t.show();
    setTimeout(() => {
      t.hide();
      t.disable();
    }, 2000);
  },

  async submitChallenge() {
    this.response = await CTFd.pages.challenge.submitChallenge(
      this.id,
      this.submission,
    );

    await this.renderSubmissionResponse();
  },

  async submitChallengeWithEffect() {
    if (!this.submission || this.isSubmitting) return;

    this.isSubmitting = true;
    this.submitResult = null;
    this.response = null;

    try {
      this.response = await CTFd.pages.challenge.submitChallenge(
        this.id,
        this.submission,
      );

      this.isSubmitting = false;

      if (this.response.data.status === "correct") {
        this.submitResult = "correct";
      } else if (this.response.data.status === "already_solved") {
        this.submitResult = "already";
      } else {
        this.submitResult = "incorrect";
      }

      setTimeout(() => {
        this.submitResult = null;
      }, 2000);

      await this.renderSubmissionResponse();
    } catch (error) {
      this.isSubmitting = false;
      this.submitResult = "incorrect";
      setTimeout(() => {
        this.submitResult = null;
      }, 2000);
      console.error("Submit error:", error);
    }
  },

  async renderSubmissionResponse() {
    if (this.response.data.status === "correct") {
      this.submission = "";
    }

    // If the challenge was just solved, an admin-authored "solved"-state
    // solution may now be available. Refresh the solution id so the Solution
    // button appears without needing to reload the challenge.
    if (this.getSolutionId() == null) {
      let state = this.getSolutionState();
      let status = this.response.data.status;
      if (state === "solved" && (status === "correct" || status === "already_solved")) {
        const response = await CTFd.fetch(`/api/v1/challenges/${this.id}/solution`, {
          method: "GET",
        });
        const body = await response.json();
        if (body.success && body.data && body.data.id) {
          this.setSolutionId(body.data.id);
        }
      }
    }

    this.$dispatch("load-challenges");
  },
}));

Alpine.data("ChallengeBoard", () => ({
  loaded: false,
  challenges: [],
  challenge: null,

  async init() {
    this.challenges = await CTFd.pages.challenges.getChallenges();
    this.loaded = true;

    if (window.location.hash) {
      let chalHash = decodeURIComponent(window.location.hash.substring(1));
      let idx = chalHash.lastIndexOf("-");
      if (idx >= 0) {
        let pieces = [chalHash.slice(0, idx), chalHash.slice(idx + 1)];
        let id = pieces[1];
        await this.loadChallenge(id);
      }
    }
  },

  getCategories() {
    const categories = [];

    this.challenges.forEach(challenge => {
      const { category } = challenge;

      if (!categories.includes(category)) {
        categories.push(category);
      }
    });

    try {
      const f = CTFd.config.themeSettings.challenge_category_order;
      if (f && typeof f === "string" && f.trim().startsWith("(")) {
        const getSort = new Function(`"use strict"; return (${f})`);
        categories.sort(getSort());
      }
    } catch (error) {}

    return categories;
  },

  getChallenges(category) {
    let challenges = this.challenges;

    if (category !== null) {
      challenges = this.challenges.filter(challenge => challenge.category === category);
    }

    try {
      const f = CTFd.config.themeSettings.challenge_order;
      if (f && typeof f === "string" && f.trim().startsWith("(")) {
        const getSort = new Function(`"use strict"; return (${f})`);
        challenges.sort(getSort());
      }
    } catch (error) {
      // Challenge order function error silently handled
    }

    return challenges;
  },

  async loadChallenges() {
    this.challenges = await CTFd.pages.challenges.getChallenges();
  },

  async loadChallenge(challengeId) {
    await CTFd.pages.challenge.displayChallenge(challengeId, challenge => {
      challenge.data.view = addTargetBlank(challenge.data.view);
      Alpine.store("challenge").data = challenge.data;

      Alpine.nextTick(() => {
        let modal = Modal.getOrCreateInstance("[x-ref='challengeWindow']");
        modal._element.addEventListener(
          "hidden.bs.modal",
          event => {
            history.replaceState(null, null, " ");
          },
          { once: true },
        );
        modal.show();
        history.replaceState(null, null, `#${challenge.data.name}-${challengeId}`);
      });
    });
  },
}));

Alpine.start();
