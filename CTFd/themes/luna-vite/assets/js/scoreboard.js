import Alpine from "alpinejs";
import CTFd from "./base";
import { getOption } from "./utils/graphs/echarts/scoreboard";
import { embed } from "./utils/graphs/echarts";

window.Alpine = Alpine;
window.CTFd = CTFd;

Alpine.data("ScoreboardDetail", () => ({
  data: null,

  async init() {
    this.data = await CTFd.pages.scoreboard.getScoreboardDetail(10);

    let option = getOption(CTFd.config.userMode, this.data);
    embed(this.$refs.scoregraph, option);
  },
}));

Alpine.start();

(() => {
  if (window.init.userId != null) {
    document.querySelectorAll(`[data-user-id="${window.init.userId}"]`).forEach(n => n.classList.add("active"));
  }
  if (window.init.teamId != null) {
    document.querySelectorAll(`[data-team-id="${window.init.teamId}"]`).forEach(n => n.classList.add("active"));
  }
})();