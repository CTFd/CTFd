import { _ } from '../../i18n.js';

export function getOption(solves, fails) {
  let option = {
    title: {
      left: "center",
      text: _("Solve Percentages"),
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
      data: [_("Fails"), _("Solves")],
    },
    series: [
      {
        name: _("Solve Percentages"),
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
            name: _("Fails"),
            itemStyle: { color: "rgb(207, 38, 0)" },
          },
          {
            value: solves,
            name: _("Solves"),
            itemStyle: { color: "rgb(0, 209, 64)" },
          },
        ],
      },
    ],
    textStyle: {
      fontFamily: 'sans-serif'
    },
  };
  return option;
}
