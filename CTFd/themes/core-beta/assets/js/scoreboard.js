import Alpine from "alpinejs";
import CTFd from "./index";
import { getOption } from "./utils/graphs/echarts/scoreboard";
import { embed } from "./utils/graphs/echarts";
import { io } from "socket.io-client";

// Make Alpine and CTFd available globally
window.Alpine = Alpine;
window.CTFd = CTFd;

// Default scoreboard polling interval to every 5 minutes
const scoreboardUpdateInterval = window.scoreboardUpdateInterval || 300000;

// Initialize WebSocket connection
const socket = io('http://127.0.0.1:4000');

// Store a reference to the ECharts instance
let chartInstance = null;

// Alpine.js component for detailed scoreboard visualization
Alpine.data("ScoreboardDetail", () => ({
  data: {},  // Scoreboard data
  show: true,  // Flag to control visibility
  activeBracket: null,  // Currently active bracket

  async update() {
    // Fetch scoreboard data with the current bracket filter
    this.data = await CTFd.pages.scoreboard.getScoreboardDetail(10, this.activeBracket);

    // Generate chart options based on data and user mode
    let optionMerge = window.scoreboardChartOptions;
    let option = getOption(CTFd.config.userMode, this.data, optionMerge);

    // Determine if chart needs to be updated
    let shouldUpdate = false;

    if (chartInstance) {
      const currentOption = chartInstance.getOption();
      shouldUpdate = !areSeriesEqual(currentOption.series, option.series);
    }

    // Update or initialize the chart
    if (!chartInstance || shouldUpdate) {
      if (chartInstance) {
        chartInstance.dispose();  // Dispose of existing chart
        chartInstance = null;
      }
      chartInstance = embed(this.$refs.scoregraph, option);  // Create new chart
    }

    // Update visibility based on data availability
    this.show = Object.keys(this.data).length > 0;
  },

  async init() {
    // Establish WebSocket connection
    socket.on('connect', () => {
      console.log('Connected to WebSocket server');
    });

    // Handle real-time scoreboard updates
    socket.on('scoreboard_update', async (data) => {
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
          chartInstance.dispose();
          chartInstance = null;
        }
        chartInstance = embed(this.$refs.scoregraph, option);
      }

      this.show = Object.keys(this.data).length > 0;
    });

    // Handle WebSocket disconnection
    socket.on('disconnect', () => {
      console.log('Disconnected from WebSocket server');
    });

    // Handle WebSocket errors
    socket.on('error', (error) => {
      console.error('WebSocket error:', error);
    });

    // Initial data fetch and chart initialization
    this.update();

    // Periodic data refresh
    setInterval(() => {
      this.update();
    }, scoreboardUpdateInterval);
  },
}));

// Alpine.js component for scoreboard list
Alpine.data("ScoreboardList", () => ({
  standings: [],  // Current standings data
  brackets: [],  // Available brackets
  activeBracket: null,  // Currently active bracket

  async update() {
    // Fetch brackets and standings data
    this.brackets = await CTFd.pages.scoreboard.getBrackets(CTFd.config.userMode);
    this.standings = await CTFd.pages.scoreboard.getScoreboard();
  },

  async init() {
    // Watch for bracket changes and dispatch events
    this.$watch("activeBracket", value => {
      this.$dispatch("bracket-change", value);
    });

    // Handle real-time scoreboard updates
    socket.on('scoreboard_update', async (data) => {
      this.standings = await CTFd.pages.scoreboard.getScoreboard();
    });

    // Initial data fetch
    this.update();

    // Periodic data refresh
    setInterval(() => {
      this.update();
    }, scoreboardUpdateInterval);
  },
}));

// Start Alpine.js
Alpine.start();

// Utility function to compare chart series data
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