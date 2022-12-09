import Alpine from "alpinejs";
import CTFd from "../index";
import { colorHash } from "@ctfdio/ctfd-js/ui";
import { getOption as getUserScoreOption } from "../utils/graphs/echarts/userscore";
import { embed } from "../utils/graphs/echarts";

window.Alpine = Alpine;

Alpine.data("UserGraphs", () => ({
  solves: null,
  fails: null,
  awards: null,
  solveCount: 0,
  failCount: 0,
  awardCount: 0,

  getSolvePercentage() {
    let percent = (this.solveCount / (this.solveCount + this.failCount)) * 100;
    return Math.round(percent);
  },

  getFailPercentage() {
    let percent = (this.failCount / (this.solveCount + this.failCount)) * 100;
    return Math.round(percent);
  },

  getCategoryBreakdown() {
    let categories = [];
    let breakdown = {};

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

    let data = [];
    for (const property in breakdown) {
      let percent_result = Number((breakdown[property] / categories.length) * 100);
      data.push({
        name: property,
        count: breakdown[property],
        percent: percent_result.toFixed(2),
        color: colorHash(property),
      });
    }

    return data;
  },

  async init() {
    this.solves = await CTFd.pages.users.userSolves(window.USER.id);
    this.fails = await CTFd.pages.users.userFails(window.USER.id);
    this.awards = await CTFd.pages.users.userAwards(window.USER.id);

    this.solveCount = this.solves.meta.count;
    this.failCount = this.fails.meta.count;
    this.awardCount = this.awards.meta.count;

    let userScoreOption = getUserScoreOption(
      window.USER.id,
      window.USER.name,
      this.solves.data,
      this.awards.data
    );
    embed(this.$refs.scoregraph, userScoreOption);
  },
}));

Alpine.start();
