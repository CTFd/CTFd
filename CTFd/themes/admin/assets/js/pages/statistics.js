import "./main";
import "core/utils";
import CTFd from "core/CTFd";
import $ from "jquery";
import Plotly from "plotly.js-basic-dist";
import { createGraph, updateGraph } from "core/graphs";

const graph_configs = {
  "#solves-graph": {
    layout: annotations => ({
      title: "Solve Counts",
      annotations: annotations,
      xaxis: {
        title: "Challenge Name"
      },
      yaxis: {
        title: "Amount of Solves"
      }
    }),
    fn: () => "CTFd_solves_" + new Date().toISOString().slice(0, 19),
    data: () => CTFd.api.get_challenge_solve_statistics(),
    format: response => {
      const data = response.data;
      const chals = [];
      const counts = [];
      const annotations = [];
      const solves = {};
      for (let c = 0; c < data.length; c++) {
        solves[data[c]["id"]] = {
          name: data[c]["name"],
          solves: data[c]["solves"]
        };
      }

      const solves_order = Object.keys(solves).sort(function(a, b) {
        return solves[b].solves - solves[a].solves;
      });

      $.each(solves_order, function(key, value) {
        chals.push(solves[value].name);
        counts.push(solves[value].solves);
        const result = {
          x: solves[value].name,
          y: solves[value].solves,
          text: solves[value].solves,
          xanchor: "center",
          yanchor: "bottom",
          showarrow: false
        };
        annotations.push(result);
      });

      return [
        {
          type: "bar",
          x: chals,
          y: counts,
          text: counts,
          orientation: "v"
        },
        annotations
      ];
    }
  },

  "#keys-pie-graph": {
    layout: () => ({
      title: "Submission Percentages"
    }),
    fn: () => "CTFd_submissions_" + new Date().toISOString().slice(0, 19),
    data: () => CTFd.api.get_submission_property_counts({ column: "type" }),
    format: response => {
      const data = response.data;
      const solves = data["correct"];
      const fails = data["incorrect"];

      return [
        {
          values: [solves, fails],
          labels: ["Correct", "Incorrect"],
          marker: {
            colors: ["rgb(0, 209, 64)", "rgb(207, 38, 0)"]
          },
          text: ["Solves", "Fails"],
          hole: 0.4,
          type: "pie"
        },
        null
      ];
    }
  },

  "#categories-pie-graph": {
    layout: () => ({
      title: "Category Breakdown"
    }),
    data: () => CTFd.api.get_challenge_property_counts({ column: "category" }),
    fn: () => "CTFd_categories_" + new Date().toISOString().slice(0, 19),
    format: response => {
      const data = response.data;

      const categories = [];
      const count = [];

      for (let category in data) {
        if (data.hasOwnProperty(category)) {
          categories.push(category);
          count.push(data[category]);
        }
      }

      for (let i = 0; i < data.length; i++) {
        categories.push(data[i].category);
        count.push(data[i].count);
      }

      return [
        {
          values: count,
          labels: categories,
          hole: 0.4,
          type: "pie"
        },
        null
      ];
    }
  },

  "#solve-percentages-graph": {
    layout: annotations => ({
      title: "Solve Percentages per Challenge",
      xaxis: {
        title: "Challenge Name"
      },
      yaxis: {
        title: "Percentage of {0} (%)".format(
          CTFd.config.userMode.charAt(0).toUpperCase() +
            CTFd.config.userMode.slice(1)
        ),
        range: [0, 100]
      },
      annotations: annotations
    }),
    data: () => CTFd.api.get_challenge_solve_percentages(),
    fn: () =>
      "CTFd_challenge_percentages_" + new Date().toISOString().slice(0, 19),
    format: response => {
      const data = response.data;

      const names = [];
      const percents = [];

      const annotations = [];

      for (let key in data) {
        names.push(data[key].name);
        percents.push(data[key].percentage * 100);

        const result = {
          x: data[key].name,
          y: data[key].percentage * 100,
          text: Math.round(data[key].percentage * 100) + "%",
          xanchor: "center",
          yanchor: "bottom",
          showarrow: false
        };
        annotations.push(result);
      }

      return [
        {
          type: "bar",
          x: names,
          y: percents,
          orientation: "v"
        },
        annotations
      ];
    }
  }
};

const config = {
  displaylogo: false,
  responsive: true
};

const createGraphs = () => {
  for (let key in graph_configs) {
    const cfg = graph_configs[key];

    const $elem = $(key);
    $elem.empty();
    $elem[0].fn = cfg.fn();

    cfg
      .data()
      .then(cfg.format)
      .then(([data, annotations]) => {
        Plotly.newPlot($elem[0], [data], cfg.layout(annotations), config);
      });
  }
};

function updateGraphs() {
  for (let key in graph_configs) {
    const cfg = graph_configs[key];
    const $elem = $(key);
    cfg
      .data()
      .then(cfg.format)
      .then(([data, annotations]) => {
        // FIXME: Pass annotations
        Plotly.react($elem[0], [data], cfg.layout(annotations), config);
      });
  }
}

$(() => {
  createGraphs();
  setInterval(updateGraphs, 300000);
});
