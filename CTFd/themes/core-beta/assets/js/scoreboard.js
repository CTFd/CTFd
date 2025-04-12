import Alpine from "alpinejs";
import CTFd from "./index";
import { getOption } from "./utils/graphs/echarts/scoreboard";
import { embed } from "./utils/graphs/echarts";
import { io } from "socket.io-client";

window.Alpine = Alpine;
window.CTFd = CTFd;

// Default scoreboard polling interval to every 5 minutes
const scoreboardUpdateInterval = window.scoreboardUpdateInterval || 300000;

// Initialize WebSocket connection
const socket = io('http://127.0.0.1:4000');

// Store a reference to the ECharts instance
let chartInstance = null;

Alpine.data("ScoreboardDetail", () => ({
  data: {},
  show: true,
  activeBracket: null,

  async update() {
    this.data = await CTFd.pages.scoreboard.getScoreboardDetail(10, this.activeBracket);

    let optionMerge = window.scoreboardChartOptions;
    let option = getOption(CTFd.config.userMode, this.data, optionMerge);

    let shouldUpdate = false;

    if (chartInstance) {
      const currentOption = chartInstance.getOption();
      shouldUpdate = !areSeriesEqual(currentOption.series, option.series);
    }

    if (!chartInstance || shouldUpdate) {
      if (chartInstance) {
        chartInstance.dispose()
        chartInstance = null
      }
      chartInstance = embed(this.$refs.scoregraph, option);
    }

    this.show = Object.keys(this.data).length > 0;
  },

  async init() {
    // Establish WebSocket connection
    socket.on('connect', () => {
      console.log('Connected to WebSocket server');
    });

    socket.on('scoreboard_update', async (data) => {
      // console.log('Received scoreboard update:', data);
      this.data = await CTFd.pages.scoreboard.getScoreboardDetail(10, this.activeBracket);

      let optionMerge = window.scoreboardChartOptions;
      let option = getOption(CTFd.config.userMode, this.data, optionMerge);

      let shouldUpdate = false;

      if (chartInstance) {
        const currentOption = chartInstance.getOption();
        shouldUpdate = !areSeriesEqual(currentOption.series, option.series);
      }

      if (!chartInstance || shouldUpdate) {
        if (chartInstance) {
          chartInstance.dispose()
          chartInstance = null
        }
        chartInstance = embed(this.$refs.scoregraph, option);
      }

      this.show = Object.keys(this.data).length > 0;
    });

    socket.on('disconnect', () => {
      console.log('Disconnected from WebSocket server');
    });

    socket.on('error', (error) => {
      console.error('WebSocket error:', error);
    });

    // Initial update
    this.update();

    // Periodic update
    setInterval(() => {
      this.update();
    }, scoreboardUpdateInterval);
  },
}));

Alpine.data("ScoreboardList", () => ({
  standings: [],
  brackets: [],
  activeBracket: null,

  async update() {
    this.brackets = await CTFd.pages.scoreboard.getBrackets(CTFd.config.userMode);
    this.standings = await CTFd.pages.scoreboard.getScoreboard();
  },

  async init() {
    // Watch for bracket changes
    this.$watch("activeBracket", value => {
      this.$dispatch("bracket-change", value);
    });

    socket.on('scoreboard_update', async (data) => {
      // console.log('Received scoreboard update:', data);
      this.standings = await CTFd.pages.scoreboard.getScoreboard();
    });

    // Initial update
    this.update();

    // Periodic update
    setInterval(() => {
      this.update();
    }, scoreboardUpdateInterval);
  },
}));

// Start Alpine
Alpine.start();

function areSeriesEqual(seriesA, seriesB) {
  if (seriesA.length !== seriesB.length) return false;

  for (let i = 0; i < seriesA.length; i++) {
    const a = seriesA[i];
    const b = seriesB[i];

    if (a.name !== b.name) return false;

    const dataA = JSON.stringify(a.data);
    const dataB = JSON.stringify(b.data);
    if (dataA !== dataB) return false;
  }

  return true;
}
