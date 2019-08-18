function solves_graph() {
  $.get(script_root + "/api/v1/statistics/challenges/solves", function(
    response
  ) {
    var data = response.data;
    var res = $.parseJSON(JSON.stringify(data));
    var chals = [];
    var counts = [];
    var colors = [];
    var annotations = [];
    var i = 1;
    var solves = {};
    for (var c = 0; c < res.length; c++) {
      solves[res[c]["id"]] = {
        name: res[c]["name"],
        solves: res[c]["solves"]
      };
    }

    var solves_order = Object.keys(solves).sort(function(a, b) {
      return solves[b].solves - solves[a].solves;
    });

    $.each(solves_order, function(key, value) {
      chals.push(solves[value].name);
      counts.push(solves[value].solves);
      /*colors.push(colorhash(value));*/
      var result = {
        x: solves[value].name,
        y: solves[value].solves,
        text: solves[value].solves,
        xanchor: "center",
        yanchor: "bottom",
        showarrow: false
      };
      annotations.push(result);
    });

    var data = [
      {
        type: "bar",
        x: chals,
        y: counts,
        text: counts,
        orientation: "v"
        /*marker: {
                color: colors
            },*/
      }
    ];

    var layout = {
      title: "Solve Counts",
      annotations: annotations,
      xaxis: {
        title: "Challenge Name"
      },
      yaxis: {
        title: "Amount of Solves"
      }
    };

    $("#solves-graph").empty();
    document.getElementById("solves-graph").fn =
      "CTFd_solves_" + new Date().toISOString().slice(0, 19);
    Plotly.newPlot("solves-graph", data, layout);
  });
}

function keys_percentage_graph() {
  // Solves and Fails pie chart
  $.get(script_root + "/api/v1/statistics/submissions/type", function(
    response
  ) {
    var data = response.data;
    var res = $.parseJSON(JSON.stringify(data));
    var solves = res["correct"];
    var fails = res["incorrect"];

    var data = [
      {
        values: [solves, fails],
        labels: ["Correct", "Incorrect"],
        marker: {
          colors: ["rgb(0, 209, 64)", "rgb(207, 38, 0)"]
        },
        text: ["Solves", "Fails"],
        hole: 0.4,
        type: "pie"
      }
    ];

    var layout = {
      title: "Submission Percentages"
    };

    $("#keys-pie-graph").empty();
    document.getElementById("keys-pie-graph").fn =
      "CTFd_submissions_" + new Date().toISOString().slice(0, 19);
    Plotly.newPlot("keys-pie-graph", data, layout);
  });
}

function category_breakdown_graph() {
  $.get(script_root + "/api/v1/statistics/challenges/category", function(
    response
  ) {
    var data = response.data;
    var res = $.parseJSON(JSON.stringify(data));

    var categories = [];
    var count = [];

    for (var category in res) {
      if (res.hasOwnProperty(category)) {
        categories.push(category);
        count.push(res[category]);
      }
    }

    for (var i = 0; i < res.length; i++) {
      categories.push(res[i].category);
      count.push(res[i].count);
    }

    var data = [
      {
        values: count,
        labels: categories,
        hole: 0.4,
        type: "pie"
      }
    ];

    var layout = {
      title: "Category Breakdown"
    };

    $("#categories-pie-graph").empty();
    document.getElementById("categories-pie-graph").fn =
      "CTFd_categories_" + new Date().toISOString().slice(0, 19);
    Plotly.newPlot("categories-pie-graph", data, layout);
  });
}

function solve_percentages_graph() {
  $.get(
    script_root + "/api/v1/statistics/challenges/solves/percentages",
    function(response) {
      var res = response.data;

      var names = [];
      var percents = [];
      var labels = [];

      var annotations = [];

      for (var key in res) {
        names.push(res[key].name);
        percents.push(res[key].percentage * 100);

        var result = {
          x: res[key].name,
          y: res[key].percentage * 100,
          text: Math.round(res[key].percentage * 100) + "%",
          xanchor: "center",
          yanchor: "bottom",
          showarrow: false
        };
        annotations.push(result);
      }

      var data = [
        {
          type: "bar",
          x: names,
          y: percents,
          orientation: "v"
        }
      ];

      var layout = {
        title: "Solve Percentages per Challenge",
        xaxis: {
          title: "Challenge Name"
        },
        yaxis: {
          title: "Percentage of {0} (%)".format(
            user_mode.charAt(0).toUpperCase() + user_mode.slice(1)
          ),
          range: [0, 100]
        },
        annotations: annotations
      };

      $("#solve-percentages-graph").empty();
      document.getElementById("solve-percentages-graph").fn =
        "CTFd_challenge_percentages_" + new Date().toISOString().slice(0, 19);
      Plotly.newPlot("solve-percentages-graph", data, layout);
    }
  );
}

function update() {
  solves_graph();
  keys_percentage_graph();
  category_breakdown_graph();
  solve_percentages_graph();
}

$(function() {
  update();
  window.onresize = function() {
    console.log("resizing");
    Plotly.Plots.resize(document.getElementById("keys-pie-graph"));
    Plotly.Plots.resize(document.getElementById("categories-pie-graph"));
    Plotly.Plots.resize(document.getElementById("solves-graph"));
    Plotly.Plots.resize(document.getElementById("solve-percentages-graph"));
  };
});

setInterval(update, 300000);
