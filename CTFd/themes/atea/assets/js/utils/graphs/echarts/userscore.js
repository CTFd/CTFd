import { ateaGreen } from "./palette";
import { cumulativeSum } from "../../math";
import { mergeObjects } from "../../objects";
import dayjs from "dayjs";

export function getOption(id, name, solves, awards, optionMerge) {
  let option = {
    title: {
      left: "center",
      text: "Score over Time",
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
  };

  const times = [];
  const scores = [];
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

  times.forEach(time => {
    option.xAxis[0].data.push(time);
  });

  option.series.push({
    name: name,
    type: "line",
    label: {
      normal: {
        show: true,
        position: "top",
      },
    },
    areaStyle: {
      normal: {
        color: ateaGreen,
      },
    },
    itemStyle: {
      normal: {
        color: ateaGreen,
      },
    },
    data: cumulativeSum(scores),
  });

  if (optionMerge) {
    option = mergeObjects(option, optionMerge);
  }
  return option;
}
