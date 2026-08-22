import Alpine from "alpinejs";
import CTFd from "../index";
import { Modal } from "bootstrap";
import { serializeJSON } from "@ctfdio/ctfd-js/forms";
import { copyToClipboard } from "../utils/clipboard";
import { colorHash } from "@ctfdio/ctfd-js/ui";
import { getOption as getUserScoreOption } from "../utils/graphs/echarts/userscore";
import { embed } from "../utils/graphs/echarts";

window.Alpine = Alpine;
window.CTFd = CTFd;

Alpine.store("inviteToken", "");

Alpine.data("TeamEditModal", () => ({
  success: null,
  error: null,
  initial: null,
  errors: [],

  init() {
    this.initial = serializeJSON(this.$el.querySelector("form"));
  },

  async updateProfile() {
    let data = serializeJSON(this.$el, this.initial, true);

    data.fields = [];

    for (const property in data) {
      if (property.match(/fields\[\d+\]/)) {
        let field = {};
        let id = parseInt(property.slice(7, -1));
        field["field_id"] = id;
        field["value"] = data[property];
        data.fields.push(field);
        delete data[property];
      }
    }

    let response = await CTFd.pages.teams.updateTeamSettings(data);
    if (response.success) {
      this.success = true;
      this.error = false;
      setTimeout(() => {
        this.success = null;
        this.error = null;
      }, 3000);
    } else {
      this.success = false;
      this.error = true;
      Object.keys(response.errors).map(error => {
        const error_msg = response.errors[error];
        this.errors.push(error_msg);
      });
    }
  },
}));

Alpine.data("TeamCaptainModal", () => ({
  success: null,
  error: null,
  errors: [],

  async updateCaptain() {
    let data = serializeJSON(this.$el, null, true);
    let response = await CTFd.pages.teams.updateTeamSettings(data);

    if (response.success) {
      window.location.reload();
    } else {
      this.success = false;
      this.error = true;
      Object.keys(response.errors).map(error => {
        const error_msg = response.errors[error];
        this.errors.push(error_msg);
      });
    }
  },
}));

Alpine.data("TeamInviteModal", () => ({
  copy() {
    copyToClipboard(this.$refs.link);
  },
}));

Alpine.data("TeamDisbandModal", () => ({
  errors: [],

  async disbandTeam() {
    let response = await CTFd.pages.teams.disbandTeam();

    if (response.success) {
      window.location.reload();
    } else {
      this.errors = response.errors[""];
    }
  },
}));

Alpine.data("CaptainMenu", () => ({
  captain: false,

  editTeam() {
    this.teamEditModal = new Modal(document.getElementById("team-edit-modal"));
    this.teamEditModal.show();
  },

  chooseCaptain() {
    this.teamCaptainModal = new Modal(document.getElementById("team-captain-modal"));
    this.teamCaptainModal.show();
  },

  async inviteMembers() {
    const response = await CTFd.pages.teams.getInviteToken();

    if (response.success) {
      const code = response.data.code;
      const url = `${window.location.origin}${CTFd.config.urlRoot}/teams/invite?code=${code}`;

      document.querySelector("#team-invite-modal input[name=link]").value = url;
      this.$store.inviteToken = url;
      this.teamInviteModal = new Modal(document.getElementById("team-invite-modal"));
      this.teamInviteModal.show();
    } else {
      Object.keys(response.errors).map(error => {
        const error_msg = response.errors[error];
        alert(error_msg);
      });
    }
  },

  disbandTeam() {
    this.teamDisbandModal = new Modal(document.getElementById("team-disband-modal"));
    this.teamDisbandModal.show();
  },
}));

Alpine.data("TeamGraphs", () => ({
  solves: null,
  fails: null,
  awards: null,
  solveCount: 0,
  failCount: 0,
  awardCount: 0,

  getSolvePercentage() {
    return ((this.solveCount / (this.solveCount + this.failCount)) * 100).toFixed(2);
  },

  getFailPercentage() {
    return ((this.failCount / (this.solveCount + this.failCount)) * 100).toFixed(2);
  },

  getCategoryBreakdown() {
    const categories = [];
    const breakdown = {};

    this.solves.data.map(solve => {
      categories.push(solve.challenge.category);
    });

    categories.forEach(category => {
      if (category in breakdown) {
        breakdown[category] += 1;
      } else {
        breakdown[category] = 1;
      }
    });

    const data = [];
    for (const property in breakdown) {
      data.push({
        name: property,
        count: breakdown[property],
        percent: (breakdown[property] / categories.length) * 100,
        color: colorHash(property),
      });
    }

    return data;
  },

  async init() {
    this.solves = await CTFd.pages.teams.teamSolves("me");
    this.fails = await CTFd.pages.teams.teamFails("me");
    this.awards = await CTFd.pages.teams.teamAwards("me");

    this.solveCount = this.solves.meta.count;
    this.failCount = this.fails.meta.count;
    this.awardCount = this.awards.meta.count;

    let optionMerge = window.teamScoreGraphChartOptions;

    embed(
      this.$refs.scoregraph,
      getUserScoreOption(
        CTFd.team.id,
        CTFd.team.name,
        this.solves.data,
        this.awards.data,
        optionMerge,
      ),
    );
  },
}));

Alpine.start();
