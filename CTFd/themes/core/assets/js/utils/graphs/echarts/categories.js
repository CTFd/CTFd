import { colorHash } from "@ctfdio/ctfd-js/ui";
import { mergeObjects } from "../../objects";

export function getOption(solves, optionMerge) {
  let option = {
    title: {
      left: "center",
      text: "Category Breakdown",
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
              formatter: function (data) {
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
        data: [],
      },
    ],
  };
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

  if (optionMerge) {
    option = mergeObjects(option, optionMerge);
  }
  return option;
}
