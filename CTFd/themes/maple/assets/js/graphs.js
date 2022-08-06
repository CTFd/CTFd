import $ from "jquery";
import echarts from "echarts/dist/echarts-en.common";
import dayjs from "dayjs";
import { cumulativeSum, colorHash } from "./utils";

const graph_configs = {
  score_graph: {
    format: (type, id, name, _account_id, responses) => {
      let option = {
        title: {
          left: "center",
          text: "Score over Time",
          textStyle: {
            color: "white",
          },
        },
        tooltip: {
          trigger: "axis",
          axisPointer: {
            type: "cross",
          },
        },
        legend: {
          type: "scroll",
          orient: "horizontal",
          align: "left",
          bottom: 0,
          data: [name],
          textStyle: {
            color: "white",
          },
        },
        toolbox: {
          feature: {
            saveAsImage: {},
          },
        },
        grid: {
          containLabel: true,
        },
        xAxis: [
          {
            type: "category",
            boundaryGap: false,
            data: [],
            textStyle: {
              color: "white",
            },
          },
        ],
        yAxis: [
          {
            type: "value",
          },
        ],
        dataZoom: [
          {
            id: "dataZoomX",
            type: "slider",
            xAxisIndex: [0],
            filterMode: "filter",
            height: 20,
            top: 35,
            fillerColor: "rgba(233, 236, 241, 0.4)",
          },
        ],
        series: [],
        textStyle: {
          fontFamily: "'Press Start 2P'",
          color: "white",
        },
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
        const date = dayjs(total[i].date);
        times.push(date.toDate());
        try {
          scores.push(total[i].challenge.value);
        } catch (e) {
          scores.push(total[i].value);
        }
      }

      times.forEach((time) => {
        option.xAxis[0].data.push(time);
      });

      option.series.push({
        name: window.stats_data.name,
        type: "line",
        label: {
          normal: {
            show: true,
            position: "top",
          },
        },
        areaStyle: {
          normal: {
            color: colorHash(name + id),
          },
        },
        itemStyle: {
          normal: {
            color: colorHash(name + id),
          },
        },
        textStyle: {
          fontFamily: "'Press Start 2P'",
          color: "white",
        },
        data: cumulativeSum(scores),
      });
      return option;
    },
  },

  category_breakdown: {
    format: (type, id, name, account_id, responses) => {
      let option = {
        title: {
          left: "center",
          text: "Category Breakdown",
          textStyle: {
            color: "white",
            fontFamily: "'Press Start 2P'",
          },
        },
        tooltip: {
          trigger: "item",
        },
        toolbox: {
          show: true,
          feature: {
            saveAsImage: {},
          },
        },
        legend: {
          type: "scroll",
          orient: "vertical",
          top: "middle",
          right: 0,
          data: [],
          textStyle: {
            color: "white",
            fontFamily: "'Press Start 2P'",
          },
        },
        series: [
          {
            name: "Category Breakdown",
            type: "pie",
            radius: ["30%", "50%"],
            avoidLabelOverlap: false,
            label: {
              show: false,
              position: "center",
            },
            itemStyle: {
              normal: {
                label: {
                  show: true,
                  formatter: function(data) {
                    return `${data.percent}% (${data.value})`;
                  },
                },
                labelLine: {
                  show: true,
                },
              },
              emphasis: {
                label: {
                  show: true,
                  position: "center",
                  textStyle: {
                    fontWeight: "normal",
                  },
                },
              },
            },
            emphasis: {
              label: {
                show: true,
                fontWeight: "bold",
              },
            },
            labelLine: {
              show: false,
            },
            data: [],
          },
        ],
        textStyle: {
          fontFamily: "'Press Start 2P'",
          color: "white",
        },
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
          itemStyle: { color: colorHash(category) },
        });
      });

      return option;
    },
  },

  solve_percentages: {
    format: (type, id, name, account_id, responses) => {
      const solves_count = responses[0].data.length;
      const fails_count = responses[1].meta.count;
      let option = {
        title: {
          left: "center",
          text: "Solve Percentages",
          textStyle: {
            fontFamily: "'Press Start 2P'",
            color: "white",
          },
        },
        tooltip: {
          trigger: "item",
        },
        toolbox: {
          show: true,
          feature: {
            saveAsImage: {},
          },
        },
        legend: {
          orient: "vertical",
          top: "middle",
          right: 0,
          data: ["Fails", "Solves"],
          textStyle: {
            fontFamily: "'Press Start 2P'",
            color: "white",
          },
        },
        series: [
          {
            name: "Solve Percentages",
            type: "pie",
            radius: ["30%", "50%"],
            avoidLabelOverlap: false,
            label: {
              show: false,
              position: "center",
            },
            itemStyle: {
              normal: {
                label: {
                  show: true,
                  formatter: function(data) {
                    return `${data.name} - ${data.value} (${data.percent}%)`;
                  },
                  textStyle: {
                    fontFamily: "'Press Start 2P'",
                    color: "white",
                  },
                },
                labelLine: {
                  show: true,
                },
              },
              emphasis: {
                label: {
                  show: true,
                  position: "center",
                  textStyle: {
                    fontWeight: "normal",
                    fontFamily: "'Press Start 2P'",
                    color: "white",
                  },
                },
              },
            },
            emphasis: {
              label: {
                show: true,
                fontWeight: "bold",
                textStyle: {
                  fontWeight: "normal",
                  fontFamily: "'Press Start 2P'",
                  color: "white",
                },
              },
            },
            labelLine: {
              show: false,
            },
            data: [
              {
                value: fails_count,
                name: "Fails",
                itemStyle: { color: "rgb(207, 38, 0)" },
              },
              {
                value: solves_count,
                name: "Solves",
                itemStyle: { color: "rgb(0, 209, 64)" },
              },
            ],
          },
        ],
        textStyle: {
          fontFamily: "'Press Start 2P'",
          color: "white",
        },
      };

      return option;
    },
  },
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
  chart.setOption({ textStyle: { fontFamily: "Press Start 2P" } });
}

export function disposeGraph(target) {
  echarts.dispose(document.querySelector(target));
}
