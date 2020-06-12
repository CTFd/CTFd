import $ from "jquery";
import echarts from "echarts/dist/echarts-en.common";
import Moment from "moment";
import { cumulativeSum, colorHash } from "./utils";

const graph_configs = {
  score_graph: {
    format: (type, id, name, _account_id, responses) => {
      let option = {
        title: {
          left: "center",
          text: "Score over Time"
        },
        tooltip: {
          trigger: "axis",
          axisPointer: {
            type: "cross"
          }
        },
        legend: {
          type: "scroll",
          orient: "horizontal",
          align: "left",
          bottom: 0,
          data: [name]
        },
        toolbox: {
          feature: {
            saveAsImage: {}
          }
        },
        grid: {
          containLabel: true
        },
        xAxis: [
          {
            type: "category",
            boundaryGap: false,
            data: []
          }
        ],
        yAxis: [
          {
            type: "value"
          }
        ],
        series: []
      };

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

      times.forEach(time => {
        option.xAxis[0].data.push(time);
      });

      option.series.push({
        name: window.stats_data.name,
        type: "line",
        label: {
          normal: {
            show: true,
            position: "top"
          }
        },
        areaStyle: {
          normal: {
            color: colorHash(name + id)
          }
        },
        itemStyle: {
          normal: {
            color: colorHash(name + id)
          }
        },
        data: cumulativeSum(scores)
      });
      return option;
    }
  },

  category_breakdown: {
    format: (type, id, name, account_id, responses) => {
      let option = {
        title: {
          left: "center",
          text: "Category Breakdown"
        },
        tooltip: {
          trigger: "item"
        },
        toolbox: {
          show: true,
          feature: {
            saveAsImage: {}
          }
        },
        legend: {
          orient: "horizontal",
          bottom: 0,
          data: []
        },
        series: [
          {
            name: "Category Breakdown",
            type: "pie",
            radius: ["30%", "50%"],
            avoidLabelOverlap: false,
            label: {
              show: false,
              position: "center"
            },
            itemStyle: {
              normal: {
                label: {
                  show: true,
                  formatter: function(data) {
                    return `${data.name} - ${data.value} (${data.percent}%)`;
                  }
                },
                labelLine: {
                  show: true
                }
              },
              emphasis: {
                label: {
                  show: true,
                  position: "center",
                  textStyle: {
                    fontSize: "14",
                    fontWeight: "normal"
                  }
                }
              }
            },
            emphasis: {
              label: {
                show: true,
                fontSize: "30",
                fontWeight: "bold"
              }
            },
            labelLine: {
              show: false
            },
            data: []
          }
        ]
      };
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

      keys.forEach((category, index) => {
        option.legend.data.push(category);
        option.series[0].data.push({
          value: counts[index],
          name: category,
          itemStyle: { color: colorHash(category) }
        });
      });

      return option;
    }
  },

  solve_percentages: {
    format: (type, id, name, account_id, responses) => {
      const solves_count = responses[0].data.length;
      const fails_count = responses[1].meta.count;
      let option = {
        title: {
          left: "center",
          text: "Solve Percentages"
        },
        tooltip: {
          trigger: "item"
        },
        toolbox: {
          show: true,
          feature: {
            saveAsImage: {}
          }
        },
        legend: {
          orient: "horizontal",
          bottom: 0,
          data: ["Fails", "Solves"]
        },
        series: [
          {
            name: "Solve Percentages",
            type: "pie",
            radius: ["30%", "50%"],
            avoidLabelOverlap: false,
            label: {
              show: false,
              position: "center"
            },
            itemStyle: {
              normal: {
                label: {
                  show: true,
                  formatter: function(data) {
                    return `${data.name} - ${data.value} (${data.percent}%)`;
                  }
                },
                labelLine: {
                  show: true
                }
              },
              emphasis: {
                label: {
                  show: true,
                  position: "center",
                  textStyle: {
                    fontSize: "14",
                    fontWeight: "normal"
                  }
                }
              }
            },
            emphasis: {
              label: {
                show: true,
                fontSize: "30",
                fontWeight: "bold"
              }
            },
            labelLine: {
              show: false
            },
            data: [
              {
                value: fails_count,
                name: "Fails",
                itemStyle: { color: "rgb(207, 38, 0)" }
              },
              {
                value: solves_count,
                name: "Solves",
                itemStyle: { color: "rgb(0, 209, 64)" }
              }
            ]
          }
        ]
      };

      return option;
    }
  }
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
  let chart = echarts.init(document.querySelector(target));
  chart.setOption(cfg.format(type, id, name, account_id, data));
  $(window).on("resize", function() {
    if (chart != null && chart != undefined) {
      chart.resize();
    }
  });
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
  let chart = echarts.init(document.querySelector(target));
  chart.setOption(cfg.format(type, id, name, account_id, data));
}
