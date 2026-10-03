import { mergeObjects } from "../../objects";
import { ateaGreen, ateaRed } from "./palette";

export function getOption(solves, fails, optionMerge) {
  let option = {
    title: {
      left: "center",
      text: "Solve Percentages",
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
              formatter: function (data) {
                return `${data.name} - ${data.value} (${data.percent}%)`;
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
                fontSize: "14",
                fontWeight: "normal",
              },
            },
          },
        },
        emphasis: {
          label: {
            show: true,
            fontSize: "30",
            fontWeight: "bold",
          },
        },
        labelLine: {
          show: false,
        },
        data: [
          {
            value: fails,
            name: "Fails",
            itemStyle: { color: ateaRed },
          },
          {
            value: solves,
            name: "Solves",
            itemStyle: { color: ateaGreen },
          },
        ],
      },
    ],
  };

  if (optionMerge) {
    option = mergeObjects(option, optionMerge);
  }
  return option;
}
