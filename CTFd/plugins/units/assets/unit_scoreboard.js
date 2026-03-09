(function () {
  "use strict";

  var POLL_INTERVAL = 10000;
  var ANIM_DURATION = 800;
  var chart = null;
  var container = document.getElementById("scoreboard");
  var prevData = {};

  // ── View switching ──
  var tabs = document.querySelectorAll(".view-tab");
  var panels = document.querySelectorAll(".view-panel");

  for (var t = 0; t < tabs.length; t++) {
    tabs[t].addEventListener("click", function () {
      for (var i = 0; i < tabs.length; i++) tabs[i].classList.remove("active");
      for (var j = 0; j < panels.length; j++) panels[j].classList.remove("active");
      this.classList.add("active");
      var target = document.getElementById(this.dataset.view + "-view");
      if (target) target.classList.add("active");
      if (this.dataset.view === "chart" && chart) chart.resize();
    });
  }

  // ── Chart view ──
  function fetchChartData() {
    fetch("/api/v1/units/scoreboard/detail")
      .then(function (r) { return r.json(); })
      .then(function (data) { renderChart(data); })
      .catch(function () {});
  }

  // Color palette for lines
  var COLORS = [
    "#d4af37", "#c0c0c0", "#cd7f32", "#4fc3f7", "#81c784",
    "#e57373", "#ba68c8", "#fff176", "#4dd0e1", "#ff8a65",
    "#90caf9", "#f48fb1"
  ];

  function renderChart(places) {
    var chartEl = document.getElementById("score-chart");
    if (!chart) {
      chart = echarts.init(chartEl, null, { renderer: "canvas" });
      window.addEventListener("resize", function () { if (chart) chart.resize(); });
    }

    var keys = Object.keys(places);
    if (keys.length === 0) {
      chart.clear();
      return;
    }

    var legend = [];
    var series = [];

    for (var i = 0; i < keys.length; i++) {
      var unit = places[keys[i]];
      var solves = unit.solves || [];
      var cumulative = [];
      var runningTotal = 0;

      for (var j = 0; j < solves.length; j++) {
        runningTotal += solves[j].value;
        cumulative.push([new Date(solves[j].date), runningTotal]);
      }

      legend.push(unit.name);

      var color = COLORS[i % COLORS.length];

      // Show emblem only on the last data point
      var hasEmblem = !!unit.emblem_url;
      var dataWithSymbols = [];
      for (var k = 0; k < cumulative.length; k++) {
        var isLast = k === cumulative.length - 1;
        var point = {
          value: cumulative[k]
        };
        if (isLast && hasEmblem) {
          point.symbol = "image://" + unit.emblem_url;
          point.symbolSize = 32;
        } else {
          point.symbol = "none";
          point.symbolSize = 0;
        }
        dataWithSymbols.push(point);
      }

      series.push({
        name: unit.name,
        type: "line",
        smooth: true,
        symbol: "none",
        symbolSize: 0,
        lineStyle: { color: color, width: 3 },
        itemStyle: { color: color, borderColor: "#0a0a1a", borderWidth: 2 },
        emphasis: {
          itemStyle: { borderColor: color, borderWidth: 3 },
          lineStyle: { width: 5 }
        },
        data: dataWithSymbols
      });
    }

    var option = {
      backgroundColor: "transparent",
      title: {
        text: "Score Progression",
        left: "center",
        textStyle: { color: "#d4af37", fontSize: 18, fontWeight: 700 }
      },
      tooltip: {
        trigger: "axis",
        backgroundColor: "rgba(20, 20, 40, 0.95)",
        borderColor: "#2a2a4a",
        textStyle: { color: "#e0e0e0" },
        axisPointer: { type: "cross", lineStyle: { color: "#555" } },
        formatter: function (params) {
          if (!params || !params.length) return "";
          var seen = {};
          var lines = [];
          for (var i = 0; i < params.length; i++) {
            var p = params[i];
            if (seen[p.seriesName]) continue;
            seen[p.seriesName] = true;
            lines.push(p.marker + " " + p.seriesName + ": <strong>" + p.value[1].toLocaleString() + "</strong>");
          }
          var date = new Date(params[0].value[0]);
          var header = date.toLocaleString();
          return header + "<br>" + lines.join("<br>");
        }
      },
      legend: {
        type: "scroll",
        bottom: 10,
        textStyle: { color: "#aaa" },
        data: legend
      },
      grid: {
        left: 60,
        right: 50,
        top: 60,
        bottom: 60,
        containLabel: true
      },
      xAxis: {
        type: "time",
        boundaryGap: false,
        axisLine: { lineStyle: { color: "#333" } },
        axisLabel: { color: "#888" },
        splitLine: { lineStyle: { color: "#1a1a2e" } }
      },
      yAxis: {
        type: "value",
        axisLine: { lineStyle: { color: "#333" } },
        axisLabel: { color: "#888" },
        splitLine: { lineStyle: { color: "#1a1a2e" } }
      },
      dataZoom: [
        {
          type: "slider",
          xAxisIndex: 0,
          filterMode: "filter",
          height: 20,
          bottom: 40,
          borderColor: "#333",
          fillerColor: "rgba(212, 175, 55, 0.15)",
          handleStyle: { color: "#d4af37" },
          textStyle: { color: "#888" }
        }
      ],
      series: series
    };

    chart.setOption(option, true);
  }

  // ── Cards view ──
  function fetchScoreboard() {
    fetch("/api/v1/units/scoreboard")
      .then(function (r) { return r.json(); })
      .then(function (data) { renderCards(data); })
      .catch(function () {});
  }

  function renderCards(units) {
    if (!units || units.length === 0) {
      container.innerHTML = '<div class="scoreboard-empty">No units yet</div>';
      prevData = {};
      return;
    }

    var existingRows = {};
    var rows = container.querySelectorAll(".unit-row");
    for (var i = 0; i < rows.length; i++) {
      existingRows[rows[i].dataset.unitId] = rows[i];
    }

    var fragment = document.createDocumentFragment();

    for (var idx = 0; idx < units.length; idx++) {
      var unit = units[idx];
      var existing = existingRows[unit.unit_id];
      var prev = prevData[unit.unit_id];

      if (existing) {
        updateRow(existing, unit, prev);
        fragment.appendChild(existing);
      } else {
        fragment.appendChild(createRow(unit));
      }

      prevData[unit.unit_id] = { score: unit.score, pos: unit.pos };
    }

    for (var uid in existingRows) {
      if (!existingRows[uid].parentNode || existingRows[uid].parentNode === container) {
        var found = false;
        for (var j = 0; j < units.length; j++) {
          if (String(units[j].unit_id) === uid) { found = true; break; }
        }
        if (!found && existingRows[uid].parentNode) {
          existingRows[uid].parentNode.removeChild(existingRows[uid]);
        }
      }
    }

    container.innerHTML = "";
    container.appendChild(fragment);
    checkAutoScroll();
  }

  function createRow(unit) {
    var row = document.createElement("div");
    row.className = "unit-row" + rankClass(unit.pos);
    row.dataset.unitId = unit.unit_id;

    row.innerHTML =
      '<div class="unit-rank">#' + unit.pos + "</div>" +
      emblemHtml(unit) +
      '<div class="unit-info">' +
        '<div class="unit-name">' + escapeHtml(unit.name) + "</div>" +
        '<div class="unit-members">' + unit.member_count + " member" + (unit.member_count !== 1 ? "s" : "") + "</div>" +
      "</div>" +
      '<div class="unit-score" data-score="' + unit.score + '">' + formatScore(unit.score) + "</div>";

    return row;
  }

  function updateRow(row, unit, prev) {
    row.className = "unit-row" + rankClass(unit.pos);

    var rankEl = row.querySelector(".unit-rank");
    rankEl.textContent = "#" + unit.pos;

    var nameEl = row.querySelector(".unit-name");
    nameEl.textContent = unit.name;

    var membersEl = row.querySelector(".unit-members");
    membersEl.textContent = unit.member_count + " member" + (unit.member_count !== 1 ? "s" : "");

    var scoreEl = row.querySelector(".unit-score");
    var oldScore = prev ? prev.score : parseInt(scoreEl.dataset.score, 10) || 0;

    if (oldScore !== unit.score) {
      animateScore(scoreEl, oldScore, unit.score);
      scoreEl.dataset.score = unit.score;
    }
  }

  function animateScore(el, from, to) {
    var start = null;
    var diff = to - from;

    el.classList.remove("score-changed");
    void el.offsetWidth;
    el.classList.add("score-changed");

    function step(ts) {
      if (!start) start = ts;
      var progress = Math.min((ts - start) / ANIM_DURATION, 1);
      var eased = 1 - Math.pow(1 - progress, 3);
      var current = Math.round(from + diff * eased);
      el.textContent = formatScore(current);

      if (progress < 1) {
        requestAnimationFrame(step);
      } else {
        el.textContent = formatScore(to);
      }
    }

    requestAnimationFrame(step);
  }

  function formatScore(n) {
    return n.toLocaleString();
  }

  function rankClass(pos) {
    if (pos === 1) return " rank-1";
    if (pos === 2) return " rank-2";
    if (pos === 3) return " rank-3";
    return "";
  }

  function emblemHtml(unit) {
    if (unit.emblem_url) {
      return '<img class="unit-emblem" src="' + escapeAttr(unit.emblem_url) + '" alt="">';
    }
    return '<div class="unit-emblem-empty">&#9776;</div>';
  }

  function escapeHtml(s) {
    var d = document.createElement("div");
    d.appendChild(document.createTextNode(s));
    return d.innerHTML;
  }

  function escapeAttr(s) {
    return s.replace(/&/g, "&amp;").replace(/"/g, "&quot;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
  }

  function checkAutoScroll() {
    var totalHeight = container.scrollHeight;
    var viewHeight = window.innerHeight;
    if (totalHeight > viewHeight) {
      container.style.setProperty("--scroll-distance", "-" + (totalHeight - viewHeight + 40) + "px");
      container.classList.add("scrolling");
    } else {
      container.classList.remove("scrolling");
    }
  }

  // ── Initial load + polling ──
  fetchChartData();
  fetchScoreboard();
  setInterval(function () {
    fetchChartData();
    fetchScoreboard();
  }, POLL_INTERVAL);
})();
