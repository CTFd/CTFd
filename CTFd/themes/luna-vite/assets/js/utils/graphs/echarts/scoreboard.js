import { colorHash } from "@ctfdio/ctfd-js/ui";
import dayjs from "dayjs";
import { _ } from '../../i18n.js';

export function cumulativeSum(arr) {
  let result = [...arr];
  for (let i = 0; i < arr.length; i++) {
    result[i] = arr.slice(0, i + 1).reduce(function (p, i) {
      return p + i;
    });
  }
  // console.log("cumulativeSumArr", arr);
  // console.log("cumulativeSumResult", result);
  return result;
}

export function getOption(mode, places) {
  let option = {
    title: {
      left: "center",
      text: (mode === "teams" ? _("Top 10 Teams") : _("Top 10 Users")),
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
      bottom: 35,
      data: [],
    },
    toolbox: {
      feature: {
        dataZoom: {
          yAxisIndex: "none",
        },
        saveAsImage: {},
      },
    },
    grid: {
      containLabel: true,
    },
    xAxis: [
      {
        type: "time",
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
    textStyle: {
      fontFamily: 'sans-serif'
    },
  };

  const teams = Object.keys(places);
  for (let i = 0; i < teams.length; i++) {
    const team_score = [];
    const times = [];
    for (let j = 0; j < places[teams[i]]["solves"].length; j++) {
      team_score.push(places[teams[i]]["solves"][j].value);
      const date = dayjs(places[teams[i]]["solves"][j].date);
      times.push(date.toDate());
    }

    // console.log("team_score", team_score);
    const total_scores = cumulativeSum(team_score);
    // console.log("total_scores", total_scores);
    let scores = times.map(function (e, i) {
      return [e, total_scores[i]];
    });
    // console.log("scores", scores);

    option.legend.data.push(places[teams[i]]["name"]);

    const data = {
      name: places[teams[i]]["name"],
      type: "line",
      label: {
        normal: {
          position: "top",
        },
      },
      itemStyle: {
        normal: {
          color: colorHash(places[teams[i]]["name"] + places[teams[i]]["id"]),
        },
      },
      data: scores,
    };
    option.series.push(data);
  }

  return option;
}
