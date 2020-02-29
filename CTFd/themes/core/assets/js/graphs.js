import $ from "jquery";
import Plotly from "plotly.js-basic-dist";
import Moment from "moment";
import { cumulativeSum, colorHash } from "./utils";

const graph_configs = {
  score_graph: {
    layout: {
      title: "Score over Time",
      paper_bgcolor: "rgba(0,0,0,0)",
      plot_bgcolor: "rgba(0,0,0,0)",
      hovermode: "closest",
      xaxis: {
        showgrid: false,
        showspikes: true
      },
      yaxis: {
        showgrid: false,
        showspikes: true
      },
      legend: {
        orientation: "h"
      }
    },
    fn: (type, id, name, account_id) =>
      `CTFd_score_${type}_${name}_${id}_${new Date()
        .toISOString()
        .slice(0, 19)}`,
    format: (type, id, name, account_id, responses) => {
      const times = [];
      const scores = [];
      const solves = responses[0].data;
      const awards = responses[2].data;
      const total = solves.concat(awards);

      total.sort((a, b) => {
        return new Date(a.date) - new Date(b.date);
      });

      for (let i = 0; i < total.length; i++) {
        const date = Moment(total[i].date);
        times.push(date.toDate());
        try {
          scores.push(total[i].challenge.value);
        } catch (e) {
          scores.push(total[i].value);
        }
      }

      return [
        {
          x: times,
          y: cumulativeSum(scores),
          type: "scatter",
          marker: {
            color: colorHash(name + id)
          },
          line: {
            color: colorHash(name + id)
          },
          fill: "tozeroy"
        }
      ];
    }
  },

  category_breakdown: {
    layout: {
      title: "Category Breakdown",
      paper_bgcolor: "rgba(0,0,0,0)",
      plot_bgcolor: "rgba(0,0,0,0)",
      legend: {
        orientation: "v"
      },
      height: "400px"
    },
    fn: (type, id, name, account_id) =>
      `CTFd_submissions_${type}_${name}_${id}_${new Date()
        .toISOString()
        .slice(0, 19)}`,
    format: (type, id, name, account_id, responses) => {
      const solves = responses[0].data;
      const categories = [];

      for (let i = 0; i < solves.length; i++) {
        categories.push(solves[i].challenge.category);
      }

      const keys = categories.filter((elem, pos) => {
        return categories.indexOf(elem) == pos;
      });

      const counts = [];
      for (let i = 0; i < keys.length; i++) {
        let count = 0;
        for (let x = 0; x < categories.length; x++) {
          if (categories[x] == keys[i]) {
            count++;
          }
        }
        counts.push(count);
      }

      return [
        {
          values: counts,
          labels: keys,
          hole: 0.4,
          type: "pie"
        }
      ];
    }
  },

  solve_percentages: {
    layout: {
      title: "Solve Percentages",
      paper_bgcolor: "rgba(0,0,0,0)",
      plot_bgcolor: "rgba(0,0,0,0)",
      legend: {
        orientation: "h"
      },
      height: "400px"
    },
    fn: (type, id, name, account_id) =>
      `CTFd_submissions_${type}_${name}_${id}_${new Date()
        .toISOString()
        .slice(0, 19)}`,
    format: (type, id, name, account_id, responses) => {
      const solves_count = responses[0].data.length;
      const fails_count = responses[1].meta.count;

      return [
        {
          values: [solves_count, fails_count],
          labels: ["Solves", "Fails"],
          marker: {
            colors: ["rgb(0, 209, 64)", "rgb(207, 38, 0)"]
          },
          hole: 0.4,
          type: "pie"
        }
      ];
    }
  }
};

const config = {
  displaylogo: false,
  responsive: true
};

export function createGraph(
  graph_type,
  target,
  data,
  type,
  id,
  name,
  account_id
) {
  const cfg = graph_configs[graph_type];

  const $elem = $(target);
  $elem.empty();
  if ($elem[0] === undefined) {
    console.log("Couldn't find graph target: " + target);
    return;
  }
  $elem[0].fn = cfg.fn(type, id, name, account_id);

  const graph_data = cfg.format(type, id, name, account_id, data);
  Plotly.newPlot($elem[0], graph_data, cfg.layout, config);
}

export function updateGraph(
  graph_type,
  target,
  data,
  type,
  id,
  name,
  account_id
) {
  const cfg = graph_configs[graph_type];

  const $elem = $(target);
  const graph_data = cfg.format(type, id, name, account_id, data);
  Plotly.update($elem[0], graph_data, cfg.layout, config);
}
