import { cumulativeSum } from "../math";

export function getSpec(description, values) {
  return {
    $schema: "https://vega.github.io/schema/vega-lite/v5.json",
    description: description,
    data: {
      values: values,
    },
    width: "container",
    mark: {
      type: "area",
      line: true,
      point: true,
      // interpolate: "step-after",
      tooltip: { content: "data", nearest: true },
    },
    encoding: {
      x: { field: "time", type: "temporal" },
      y: { field: "score", type: "quantitative" },
    },
  };
}

export function getValues(solves, awards) {
  const times = [];
  let scores = [];
  const solvesData2 = solves.data;
  const awardsData = awards.data;
  const total = solvesData2.concat(awardsData);

  total.sort((a, b) => {
    return new Date(a.date) - new Date(b.date);
  });

  for (let i = 0; i < total.length; i++) {
    // const date = dayjs(total[i].date);
    // times.push(date.toDate());
    const date = total[i].date;
    times.push(date);
    try {
      scores.push(total[i].challenge.value);
    } catch (e) {
      scores.push(total[i].value);
    }
  }

  scores = cumulativeSum(scores);

  let values = [];
  times.forEach((time, index) => {
    // option.xAxis[0].data.push(time);
    values.push({
      time: time,
      score: scores[index],
    });
  });

  return values;
}
