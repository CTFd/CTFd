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
      const percent = Number((breakdown[property] / categories.length) * 100).toFixed(
        2,
      );

      data.push({
        name: property,
        count: breakdown[property],
        color: colorHash(property),
        percent,
      });
    }

    return data;
  },

  async init() {
    this.solves = await CTFd.pages.users.userSolves("me");
    this.fails = await CTFd.pages.users.userFails("me");
    this.awards = await CTFd.pages.users.userAwards("me");

    this.solveCount = this.solves.meta.count;
    this.failCount = this.fails.meta.count;
    this.awardCount = this.awards.meta.count;

    let optionMerge = window.userScoreGraphChartOptions;

    embed(
      this.$refs.scoregraph,
      getUserScoreOption(
        CTFd.user.id,
        CTFd.user.name,
        this.solves.data,
        this.awards.data,
        optionMerge,
      ),
    );
  },
}));

Alpine.start();
