import "./main";
import CTFd from "../compat/CTFd";
import $ from "jquery";
import echarts from "echarts/dist/echarts.common";
import { colorHash } from "../compat/styles";
import io from 'socket.io-client';

const socket = io('http://127.0.0.1:4000');

socket.on('connect', function () {
  console.log('Conectado al servidor');
});

function updateChallengeStatsGraph(data) {
  if (!Array.isArray(data.data)) return;
  const el = document.querySelector('#solves-graph');
  if (!el) return;
  const chart = echarts.init(el);

  const chals = [];
  const counts = [];

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
      data: chals,
      axisLabel: { interval: 0, rotate: 0 },
    },
    dataZoom: [
      { show: false, start: 0, end: 100 },
      { type: "inside", yAxisIndex: 0, show: true, width: 20 },
      {
        fillerColor: "rgba(233, 236, 241, 0.4)",
        show: true,
        yAxisIndex: 0,
        width: 20,
      },
    ],
    series: [
      {
        label: { show: true },
        data: counts,
        type: "bar",
        itemStyle: { color: "#1f76b4" },
      },
    ],
  };

  chart.setOption(option);
  $(window).on("resize", () => chart.resize());
}

function updateScoresDistributionGraph(data) {
  if (!data.data || !data.data.brackets) return;
  const el = document.querySelector('#score-distribution-graph');
  if (!el) return;
  const chart = echarts.init(el);

  const brackets = Object.keys(data.data.brackets).sort((a, b) => a - b);
  const sizes = brackets.map(key => data.data.brackets[key]);

  const option = {
    title: { left: "center", text: "Score Distribution" },
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
      name: "Score Bracket",
      nameGap: 40,
      nameLocation: "middle",
      type: "category",
      data: brackets.map(key => `${key - (data.bracket_size || 0)} - ${key}`),
    },
    yAxis: {
      name: `Number of ${CTFd.config.userMode.charAt(0).toUpperCase() + CTFd.config.userMode.slice(1)}`,
      nameGap: 50,
      nameLocation: "middle",
      type: "value",
    },
    series: [
      {
        label: { show: true },
        data: sizes,
        type: "bar",
        itemStyle: { color: "#1f76b4" },
      },
    ],
  };

  chart.setOption(option);
}

function updateSubmissionsStatsGraph(data) {
  console.log(data);
  const el = document.querySelector('#keys-pie-graph');
  if (!el) return;
  const chart = echarts.init(el);

  const correct = data.data.correct || 0;
  const incorrect = data.data.incorrect || 0;
  const total = correct + incorrect;

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
        avoidLabelOverlap: false,
        label: { show: false, position: "center" },
        itemStyle: {
          normal: {
            label: {
              show: true,
              formatter: function (data) {
                const value = data.data.value || 0;
                const percent = total > 0 ? (value / total) * 100 : 0;
                return `${data.data.name} (${value})\n${percent.toFixed(1)}%`;
              },
            },
            labelLine: { show: true },
          },
          emphasis: {
            label: {
              show: true,
              position: "center",
              textStyle: { fontSize: "14", fontWeight: "normal" },
            },
          },
        },
        emphasis: { label: { show: true, fontSize: "30", fontWeight: "bold" } },
        labelLine: { show: false },
        data: [
          { value: incorrect, name: "Fails", itemStyle: { color: "rgb(207, 38, 0)" } },
          { value: correct, name: "Solves", itemStyle: { color: "rgb(0, 209, 64)" } },
        ],
      },
    ],
  };

  chart.setOption(option);
}

function updateCategoriesGraph(data) {
  const el = document.querySelector('#categories-pie-graph');
  if (!el) return;
  const chart = echarts.init(el);

  const categoryCounts = {};
  data.data.forEach(item => {
    if (item.category) {
      categoryCounts[item.category] = (categoryCounts[item.category] || 0) + 1;
    }
  });

  const categories = Object.keys(categoryCounts);
  const counts = categories.map(category => categoryCounts[category]);

  const option = {
    title: { left: "center", text: "Categories Distribution" },
    tooltip: { trigger: "item" },
    legend: {
      orient: "vertical",
      top: "middle",
      right: 0,
      data: categories,
    },
    series: [
      {
        name: "Categories",
        type: "pie",
        radius: ["30%", "50%"],
        data: categories.map((category, index) => ({
          value: counts[index],
          name: category,
          itemStyle: { color: colorHash(category) },
        })),
      },
    ],
  };

  chart.setOption(option);
}

function updatePointsGraph(data) {
  const el = document.querySelector('#points-pie-graph');
  if (!el) return;
  const chart = echarts.init(el);

  const pointsCounts = {};
  data.data.forEach(item => {
    const points = item.points || item.value;
    pointsCounts[points] = (pointsCounts[points] || 0) + 1;
  });

  const points = Object.keys(pointsCounts);
  const counts = points.map(point => pointsCounts[point]);

  const option = {
    title: { left: "center", text: "Points Distribution" },
    tooltip: { trigger: "item" },
    legend: {
      orient: "vertical",
      top: "middle",
      right: 0,
      data: points.map(point => `Points: ${point}`),
    },
    series: [
      {
        name: "Points",
        type: "pie",
        radius: ["30%", "50%"],
        data: points.map((point, index) => ({
          value: counts[index],
          name: `Points: ${point}`,
          itemStyle: { color: colorHash(`Points: ${point}`) },
        })),
      },
    ],
  };

  chart.setOption(option);
}

function updateSolvePercentagesGraph(data) {
  const el = document.querySelector('#solve-percentages-graph');
  if (!el) return;
  const chart = echarts.init(el);
  const option = {
    title: { left: "center", text: "Solve Percentages" },
    tooltip: { trigger: "item" },
    series: [
      {
        name: "Solve Percentages",
        type: "pie",
        radius: ["30%", "50%"],
        data: [
          { value: data.data.solved, name: "Solved", itemStyle: { color: "rgb(0, 209, 64)" } },
          { value: data.data.unsolved, name: "Unsolved", itemStyle: { color: "rgb(207, 38, 0)" } },
        ],
      },
    ],
  };

  chart.setOption(option);
}

socket.on('challenge_stats', function (data) {
  updateChallengeStatsGraph(data);
  updateCategoriesGraph(data);
  updatePointsGraph(data);
});
socket.on('scores_distribution', updateScoresDistributionGraph);
socket.on('submissions_stats', updateSubmissionsStatsGraph);
socket.on('solve_percentages_stats', updateSolvePercentagesGraph);

$(document).ready(function () {
  socket.emit('request_initial_data');
});
