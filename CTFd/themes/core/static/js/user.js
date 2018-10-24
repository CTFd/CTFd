function teamid() {
    return $('#team-id').attr('team-id');
}

function cumulativesum(arr) {
    var result = arr.concat();
    for (var i = 0; i < arr.length; i++) {
        result[i] = arr.slice(0, i + 1).reduce(function (p, i) {
            return p + i;
        });
    }
    return result
}

function scoregraph() {
    // TODO: This graph isn't taking awards into account
    var times = [];
    var scores = [];
    var teamname = $('#team-id').text();
    $.get(script_root + '/api/v1/users/' + user_id + '/solves', function (response) {
        var solves = response.data;

        for (var i = 0; i < solves.length; i++) {
            var date = moment(solves[i].date);
            times.push(date.toDate());
            scores.push(solves[i].challenge.value);
        }

        scores = cumulativesum(scores);

        var data = [
            {
                x: times,
                y: scores,
                type: 'scatter',
                marker: {
                    color: colorhash(teamname + user_id),
                },
                line: {
                    color: colorhash(teamname + user_id),
                }
            }
        ];

        var layout = {
            title: 'Score over Time',
            paper_bgcolor: 'rgba(0,0,0,0)',
            plot_bgcolor: 'rgba(0,0,0,0)',
            hovermode: 'closest',
            xaxis: {
                showgrid: false,
                showspikes: true,
            },
            yaxis: {
                showgrid: false,
                showspikes: true,
            },
            legend: {
                "orientation": "h"
            }
        };

        $('#score-graph').empty();
        document.getElementById('score-graph').fn = 'CTFd_score_user_' + user_id + '_' + (new Date).toISOString().slice(0, 19);
        Plotly.newPlot('score-graph', data, layout);
    });
}

function keys_percentage_graph() {
    // Solves and Fails pie chart
    var base_url = script_root + '/api/v1/users/' + user_id;
    $.get(base_url + '/fails', function (fails) {
        $.get(base_url + '/solves', function(solves) {
            var solves_count = solves.data.length;
            var fails_count = fails.data.length;

            var graph_data = [{
                values: [solves_count, fails_count],
                labels: ['Solves', 'Fails'],
                marker: {
                    colors: [
                        "rgb(0, 209, 64)",
                        "rgb(207, 38, 0)"
                    ]
                },
                hole: .4,
                type: 'pie'
            }];

            var layout = {
                title: 'Solve Percentages',
                paper_bgcolor: 'rgba(0,0,0,0)',
                plot_bgcolor: 'rgba(0,0,0,0)',
                legend: {
                    "orientation": "h"
                }
            };

            $('#keys-pie-graph').empty();
            document.getElementById('keys-pie-graph').fn = 'CTFd_submissions_user_' + user_id + '_' + (new Date).toISOString().slice(0, 19);
            Plotly.newPlot('keys-pie-graph', graph_data, layout);
        });
    });
}

function category_breakdown_graph() {
    $.get(script_root + '/api/v1/users/' + user_id + '/solves', function (response) {
        var solves = response.data;

        var categories = [];
        for (var i = 0; i < solves.length; i++) {
            categories.push(solves[i].challenge.category)
        }

        var keys = categories.filter(function (elem, pos) {
            return categories.indexOf(elem) == pos;
        });

        var counts = [];
        for (var i = 0; i < keys.length; i++) {
            var count = 0;
            for (var x = 0; x < categories.length; x++) {
                if (categories[x] == keys[i]) {
                    count++;
                }
            }
            counts.push(count)
        }

        var data = [{
            values: counts,
            labels: keys,
            hole: .4,
            type: 'pie'
        }];

        var layout = {
            title: 'Category Breakdown',
            paper_bgcolor: 'rgba(0,0,0,0)',
            plot_bgcolor: 'rgba(0,0,0,0)',
            legend: {
                "orientation": "v"
            }
        };

        $('#categories-pie-graph').empty();
        document.getElementById('categories-pie-graph').fn = 'CTFd_categories_team_' + user_id + '_' + (new Date).toISOString().slice(0, 19);
        Plotly.newPlot('categories-pie-graph', data, layout);
    });
}

category_breakdown_graph();
keys_percentage_graph();
scoregraph();

window.onresize = function () {
    Plotly.Plots.resize(document.getElementById('keys-pie-graph'));
    Plotly.Plots.resize(document.getElementById('categories-pie-graph'));
    Plotly.Plots.resize(document.getElementById('score-graph'));
};
