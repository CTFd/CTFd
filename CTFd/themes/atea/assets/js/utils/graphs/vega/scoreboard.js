import { cumulativeSum } from "../math";

export function getSpec(description, values) {
  let spec = {
    $schema: "https://vega.github.io/schema/vega-lite/v5.json",
    description: description,
    data: { values: values },
    mark: "line",
    width: "container",
    encoding: {
      x: { field: "date", type: "temporal" },
      y: { field: "score", type: "quantitative" },
      color: {
        field: "name",
        type: "nominal",
        legend: {
          orient: "bottom",
        },
      },
    },
  };
  return spec;
}

export function getValues(scoreboardDetail) {
  const teams = Object.keys(scoreboardDetail);
  let values = [];

  for (let i = 0; i < teams.length; i++) {
    const team = scoreboardDetail[teams[i]];
    const team_score = [];
    const times = [];
    for (let j = 0; j < team["solves"].length; j++) {
      team_score.push(team["solves"][j].value);
      times.push(team["solves"][j].date);
      // const date = dayjs(team["solves"][j].date);
      // times.push(date.toDate());
    }

    const total_scores = cumulativeSum(team_score);
    const team_name = team["name"];
    let scores = times.map(function (e, i) {
      return {
        name: team_name,
        score: total_scores[i],
        date: e,
      };
    });
    values = values.concat(scores);
  }

  return values;
}
