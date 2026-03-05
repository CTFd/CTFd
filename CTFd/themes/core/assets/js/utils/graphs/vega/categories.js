export function getSpec(description, values) {
  return {
    $schema: "https://vega.github.io/schema/vega-lite/v5.json",
    description: description,
    data: {
      values: values,
    },
    width: "container",

    layer: [
      {
        params: [
          {
            name: "category",
            select: {
              type: "point",
              fields: ["category"],
            },
            bind: "legend",
          },
        ],
        mark: {
          type: "arc",
          innerRadius: 50,
          outerRadius: 95,
          stroke: "#fff",
        },
        encoding: {
          opacity: {
            condition: {
              param: "category",
              value: 1,
            },
            value: 0.2,
          },
        },
      },
      {
        mark: {
          type: "text",
          radius: 105,
        },
        encoding: {
          text: {
            field: "value",
            type: "quantitative",
          },
        },
      },
    ],
    encoding: {
      theta: {
        field: "value",
        type: "quantitative",
        stack: true,
      },
      color: {
        field: "category",
        type: "nominal",
        // scale: {
        //   domain: ["Solves", "Fails"],
        //   range: ["#00d13f", "#cf2600"],
        // },
        legend: {
          orient: "bottom",
        },
      },
    },
  };
}

export function getValues(solves) {
  const solvesData = solves.data;
  const categories = [];

  for (let i = 0; i < solvesData.length; i++) {
    categories.push(solvesData[i].challenge.category);
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

  let values = [];

  keys.forEach((category, index) => {
    values.push({
      category: category,
      value: counts[index],
    });
  });

  return values;
}
