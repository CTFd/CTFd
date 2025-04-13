import "./main";
import CTFd from "../compat/CTFd";
import $ from "jquery";
import echarts from "echarts/dist/echarts.common";
import { colorHash } from "../compat/styles";
import io from 'socket.io-client';

// Connect to the Socket.IO server
const socket = io('http://127.0.0.1:4000');

// Connection event handler
socket.on('connect', function () {
  console.log('Connected to the server');
});

// Update text content of an element by ID
function updateTextContent(id, value) {
  const el = document.getElementById(id);
  if (el) el.textContent = value;
}

// Global chart variables
let solvePercentagesChart = null;
let challengeStatsChart = null;
let scoreDistributionChart = null;
let submissionsStatsChart = null;
let categoriesGraphChart = null;
let pointsGraphChart = null;

// Update challenge statistics graph (solves per challenge)
function updateChallengeStatsGraph(data) {
  const el = document.querySelector('#solves-graph');
  if (!el) return;

  // Initialize chart if not already created
  if (!challengeStatsChart) {
    challengeStatsChart = echarts.init(el);

    const option = {
      title: { left: "center", text: "Solve Counts" },
      tooltip: { trigger: "item" },
      toolbox: {
        show: true,
        feature: {
          mark: { show: true },
          dataView: { show: true, readOnly: false },
          magicType: { show: true, type: ["line", "bar"] },
          restore: { show: true },
          saveAsImage: { show: true },
        },
      },
      xAxis: {
        name: "Solve Count",
        nameLocation: "middle",
        type: "value",
      },
      yAxis: {
        name: "Challenge Name",
        nameLocation: "middle",
        nameGap: 60,
        type: "category",
        axisLabel: { interval: 0, rotate: 0 },
        data: []
      },
      series: [
        {
          label: { show: true },
          data: [],
          type: "bar",
          itemStyle: { color: "#1f76b4" },
        },
      ],
    };

    challengeStatsChart.setOption(option);
    // Handle window resize events
    $(window).on("resize", () => challengeStatsChart.resize());
  }

  // Process and update chart data
  if (!Array.isArray(data.data)) return;

  const chals = [];
  const counts = [];

  // Process data and sort by solve count
  const solves = {};
  data.data.forEach(item => {
    solves[item.id] = {
      name: item.name,
      solves: item.solves,
    };
  });

  const solvesOrder = Object.keys(solves).sort((a, b) => solves[b].solves - solves[a].solves);

  solvesOrder.forEach(key => {
    chals.push(solves[key].name);
    counts.push(solves[key].solves);
  });

  challengeStatsChart.setOption({
    yAxis: {
      data: chals,
    },
    series: [{
      data: counts
    }]
  });
}

// Update score distribution graph (teams/users across score brackets)
function updateScoresDistributionGraph(data) {
  const el = document.querySelector('#score-distribution-graph');
  if (!el) return;

  if (!scoreDistributionChart) {
    scoreDistributionChart = echarts.init(el);

    const option = {
      title: {
        left: "center",
        text: "Score Distribution",
      },
      tooltip: {
        trigger: "item",
      },
      toolbox: {
        show: true,
        feature: {
          mark: { show: true },
          dataView: { show: true, readOnly: false },
          magicType: { show: true, type: ["line", "bar"] },
          restore: { show: true },
          saveAsImage: { show: true },
        },
      },
      xAxis: {
        name: "Score Bracket",
        nameGap: 40,
        nameLocation: "middle",
        type: "category",
        data: [],
      },
      yAxis: {
        name: "Number of Teams/Users",
        nameGap: 50,
        nameLocation: "middle",
        type: "value",
      },
      dataZoom: [
        // Configuration for data zoom features
        { show: false, start: 0, end: 100 },
        { type: "inside", show: true, start: 0, end: 100 },
        { fillerColor: "rgba(233, 236, 241, 0.4)", show: true, right: 60, yAxisIndex: 0, width: 20 },
        { type: "slider", fillerColor: "rgba(233, 236, 241, 0.4)", top: 35, height: 20, show: true, start: 0, end: 100 },
      ],
      series: [
        {
          label: { show: true },
          data: [],
          type: "bar",
          itemStyle: { color: "#1f76b4" },
        },
      ],
    };

    scoreDistributionChart.setOption(option);
    $(window).on("resize", () => scoreDistributionChart.resize());
  }

  // Update chart data
  if (!data.data || !data.data.brackets) return;

  const brackets = Object.keys(data.data.brackets).sort((a, b) => a - b);
  const sizes = brackets.map(key => data.data.brackets[key]);

  scoreDistributionChart.setOption({
    xAxis: {
      data: brackets,
    },
    series: [{
      data: sizes
    }]
  });
}

// Update submissions statistics pie chart (correct/incorrect submissions)
function updateSubmissionsStatsGraph(data) {
  const el = document.querySelector('#keys-pie-graph');
  if (!el) return;

  if (!submissionsStatsChart) {
    submissionsStatsChart = echarts.init(el);

    const option = {
      title: { left: "center", text: "Submission Percentages" },
      tooltip: { trigger: "item" },
      toolbox: {
        show: true,
        feature: {
          dataView: { show: true, readOnly: false },
          saveAsImage: {},
        },
      },
      legend: {
        orient: "vertical",
        top: "middle",
        right: 0,
        data: ["Fails", "Solves"],
      },
      series: [
        {
          name: "Submission Percentages",
          type: "pie",
          radius: ["30%", "50%"],
          data: [],
        },
      ],
    };

    submissionsStatsChart.setOption(option);
    $(window).on("resize", () => submissionsStatsChart.resize());
  }

  // Calculate percentages
  const correct = data.data.correct || 0;
  const incorrect = data.data.incorrect || 0;

  submissionsStatsChart.setOption({
    series: [{
      data: [
        { value: incorrect, name: "Fails", itemStyle: { color: "rgb(207, 38, 0)" } },
        { value: correct, name: "Solves", itemStyle: { color: "rgb(0, 209, 64)" } },
      ]
    }]
  });
}

// Update categories distribution pie chart
function updateCategoriesGraph(data) {
  const el = document.querySelector('#categories-pie-graph');
  if (!el) return;

  if (!categoriesGraphChart) {
    categoriesGraphChart = echarts.init(el);

    const option = {
      title: { left: "center", text: "Categories Distribution" },
      tooltip: { trigger: "item" },
      legend: {
        orient: "vertical",
        top: "middle",
        right: 0,
        data: [],
      },
      series: [
        {
          name: "Categories",
          type: "pie",
          radius: ["30%", "50%"],
          data: [],
        },
      ],
    };

    categoriesGraphChart.setOption(option);
    $(window).on("resize", () => categoriesGraphChart.resize());
  }

  // Count challenges per category
  const categoryCounts = {};
  data.data.forEach(item => {
    if (item.category) {
      categoryCounts[item.category] = (categoryCounts[item.category] || 0) + 1;
    }
  });

  const categories = Object.keys(categoryCounts);
  const counts = categories.map(category => categoryCounts[category]);

  categoriesGraphChart.setOption({
    legend: {
      data: categories,
    },
    series: [{
      data: categories.map((category, index) => ({
        value: counts[index],
        name: category,
        itemStyle: { color: colorHash(category) },
      }))
    }]
  });
}

// Update points distribution pie chart
function updatePointsGraph(data) {
  const el = document.querySelector('#points-pie-graph');
  if (!el) return;

  if (!pointsGraphChart) {
    pointsGraphChart = echarts.init(el);

    const option = {
      title: { left: "center", text: "Points Distribution" },
      tooltip: { trigger: "item" },
      legend: {
        orient: "vertical",
        top: "middle",
        right: 0,
        data: [],
      },
      series: [
        {
          name: "Points",
          type: "pie",
          radius: ["30%", "50%"],
          data: [],
        },
      ],
    };

    pointsGraphChart.setOption(option);
    $(window).on("resize", () => pointsGraphChart.resize());
  }

  // Count challenges per point value
  const pointsCounts = {};
  data.data.forEach(item => {
    const points = item.points || item.value;
    pointsCounts[points] = (pointsCounts[points] || 0) + 1;
  });

  const points = Object.keys(pointsCounts);
  const counts = points.map(point => pointsCounts[point]);

  pointsGraphChart.setOption({
    legend: {
      data: points.map(point => `Points: ${point}`),
    },
    series: [{
      data: points.map((point, index) => ({
        value: counts[index],
        name: `Points: ${point}`,
        itemStyle: { color: colorHash(`Points: ${point}`) },
      }))
    }]
  });
}

// Update solve percentages graph (percentage of users/teams who solved each challenge)
function updateSolvePercentagesGraph(data) {
  const el = document.querySelector('#solve-percentages-graph');
  if (!el) return;

  if (!solvePercentagesChart) {
    solvePercentagesChart = echarts.init(el);

    const option = {
      title: {
        left: "center",
        text: "Solve Percentages per Challenge",
      },
      tooltip: {
        trigger: "item",
        formatter: function (data) {
          return `${data.name} - ${(Math.round(data.value * 10) / 10).toFixed(1)}%`;
        },
      },
      toolbox: {
        show: true,
        feature: {
          mark: { show: true },
          dataView: { show: true, readOnly: false },
          magicType: { show: true, type: ["line", "bar"] },
          restore: { show: true },
          saveAsImage: { show: true },
        },
      },
      xAxis: {
        name: "Challenge Name",
        nameGap: 40,
        nameLocation: "middle",
        type: "category",
        data: [],
        axisLabel: {
          interval: 0,
          rotate: 50,
        },
      },
      yAxis: {
        name: `Percentage of ${CTFd.config.userMode.charAt(0).toUpperCase() + CTFd.config.userMode.slice(1)} (%)`,
        nameGap: 50,
        nameLocation: "middle",
        type: "value",
        min: 0,
        max: 100,
      },
      dataZoom: [
        // Configuration for data zoom features
        { show: false, start: 0, end: 100 },
        { type: "inside", show: true, start: 0, end: 100 },
        { fillerColor: "rgba(233, 236, 241, 0.4)", show: true, right: 60, yAxisIndex: 0, width: 20 },
        { type: "slider", fillerColor: "rgba(233, 236, 241, 0.4)", top: 35, height: 20, show: true, start: 0, end: 100 },
      ],
      series: [
        {
          name: "Solved %",
          type: "bar",
          itemStyle: { color: "#1f76b4" },
          data: [],
        }
      ],
    };

    solvePercentagesChart.setOption(option);
    $(window).on("resize", () => solvePercentagesChart.resize());
  }

  // Update chart data
  if (!data.data || !data.data.challenges) return;

  const challenges = data.data.challenges;
  const challengeNames = challenges.map(c => c.name);
  const solvePercentages = challenges.map(c => c.solve_percentage);

  solvePercentagesChart.setOption({
    xAxis: {
      data: challengeNames,
    },
    series: [{
      data: solvePercentages
    }]
  });
}

// Socket.IO event handlers
socket.on('challenge_stats', function (data) {
  updateChallengeStatsGraph(data);
  updateCategoriesGraph(data);
  updatePointsGraph(data);

  const challenges = data.data || [];

  if (challenges.length > 0) {
    // Find most and least solved challenges
    let most = challenges[0];
    let least = challenges[0];

    for (const chal of challenges) {
      if (chal.solves > most.solves) most = chal;
      if (chal.solves < least.solves) least = chal;
    }

    updateTextContent('challenge-count', challenges.length);
    updateTextContent('most-solved', most.name);
    updateTextContent('most-solved-count', most.solves);
    updateTextContent('least-solved', least.name);
    updateTextContent('least-solved-count', least.solves);
  }
});

socket.on('scores_distribution', updateScoresDistributionGraph);
socket.on('submissions_stats', updateSubmissionsStatsGraph);

// Update user statistics
socket.on('users_stats', function (data) {
  updateTextContent('user-count', data.data.registered);
});

// Update team statistics
socket.on('teams_stats', function (data) {
  updateTextContent('team-count', data.data.registered);
});

// Update solve percentages statistics
socket.on('solve_percentages_stats', function (data) {
  updateSolvePercentagesGraph(data);
  updateTextContent('solve-count', data.data.solved);
  updateTextContent('wrong-count', data.data.unsolved);
});

// Request initial data when document is ready
$(document).ready(function () {
  socket.emit('request_initial_data');
});