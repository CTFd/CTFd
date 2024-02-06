import Alpine from "alpinejs";
import CTFd from "./index";
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

Alpine.data("ScoreboardList", () => ({
  standings: null,
  brackets: [],
  activeBracket: null,

  async init() {
    let response = await CTFd.fetch(`/api/v1/brackets?type=${CTFd.config.userMode}`, {
      method: "GET",
    });
    const body = await response.json();
    this.brackets = body["data"];
    this.full_standings = this.standings = await CTFd.pages.scoreboard.getScoreboard();
  },
}));

Alpine.start();
