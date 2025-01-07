import Alpine from "alpinejs";
import CTFd from "./base";
import { colorHash } from "@ctfdio/ctfd-js/ui";
import { getOption as getUserScoreOption } from "./utils/graphs/echarts/userscore";
import { embed } from "./utils/graphs/echarts/index";

window.Alpine = Alpine;

Alpine.data("UserGraphs", () => ({
  solves: {data: []},
  fails: {data: []},
  awards: {data: []},
  solveCount: 0,
  failCount: 0,
  awardCount: 0,

  getSolvePercentage(){
    let percent = (this.solveCount / (this.solveCount + this.failCount)) * 100;
    return Math.round(percent);
  },

  getFailPercentage(){
    let percent = (this.failCount / (this.solveCount + this.failCount)) * 100;
    return Math.round(percent);
  },

  getCategoryBreakdown(){
    let categories = [];
    let breakdown = {};

    this.solves.data.map((solve) => {
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
      data.push({
        "name": property,
        "count": breakdown[property],
        "percent": (breakdown[property] / categories.length) * 100,
        "color": colorHash(property),
      });
    }

    // console.log("getCategoryBreakdown Data", data);
    return data;
  },

  async init() {
    const userIdAlias = window.USER ? window.USER.id : "me";
    this.solves = await CTFd.pages.users.userSolves(userIdAlias);
    this.fails = await CTFd.pages.users.userFails(userIdAlias);
    this.awards = await CTFd.pages.users.userAwards(userIdAlias);
    
    this.solveCount = this.solves.meta.count;
    this.failCount = this.fails.meta.count;
    this.awardCount = this.awards.meta.count;
    
    console.log(this.solves.data);
    
    const user = window.USER || CTFd.user;
    let userScoreOption = getUserScoreOption(
      user.id,
      user.name,
      this.solves.data,
      this.awards.data
    );

    if (this.$refs.scoregraph) {
      embed(this.$refs.scoregraph, userScoreOption);
    }
  },
}));

Alpine.start();
