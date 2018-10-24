function teamid() {
    var loc = window.location.pathname;
    return loc.substring(loc.lastIndexOf('/') + 1, loc.length);
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
    var times = [];
    var scores = [];
    var teamname = $('#team-id').text();
    $.get(script_root + '/api/v1/teams/' + teamid() + '/solves', function (response) {
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
                    color: colorhash(teamname + teamid()),
                },
                line: {
                    color: colorhash(teamname + teamid()),
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
        document.getElementById('score-graph').fn = 'CTFd_score_team_' + teamid() + '_' + (new Date).toISOString().slice(0, 19);
        Plotly.newPlot('score-graph', data, layout);
    });
}

function keys_percentage_graph() {
    var base_url = script_root + '/api/v1/teams/' + teamid();
    $.get(base_url + '/fails', function (fails) {
        $.get(base_url + '/solves', function (solves) {
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
            document.getElementById('keys-pie-graph').fn = 'CTFd_submissions_team_' + teamid() + '_' + (new Date).toISOString().slice(0, 19);
            Plotly.newPlot('keys-pie-graph', graph_data, layout);
        });
    });
}

function category_breakdown_graph() {
    $.get(script_root + '/api/v1/teams/' + teamid() + '/solves', function (response) {
        var solves = response.data;

        var categories = [];
        for (var i = 0; i < solves.length; i++) {
            categories.push(solves[i].challenge.category)
        }

        console.log(categories);

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
        document.getElementById('categories-pie-graph').fn = 'CTFd_categories_team_' + teamid() + '_' + (new Date).toISOString().slice(0, 19);
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


// TODO: None of this works
$(document).ready(function () {
    $('.delete-item').click(function () {
        var elem = $(this).parent().parent();
        var type = elem.attr('class');
        var chal_name = elem.find('.chal').text().trim();
        var team_name = $("#team-id").text();
        var key_id = elem.find('.flag').attr('id');

        if (type == 'chal-solve') {
            var title = 'Delete Solve';
            var description = "<span>Are you sure you want to delete " +
                "<strong>correct</strong> " +
                "submission from " +
                "<strong id='confirm-team-name'></strong> " +
                "for challenge: " +
                "<strong id='confirm-chal-name'></strong>?</span>"


            var description = $($.parseHTML(description));
            description.find('#confirm-team-name').text(team_name);
            description.find('#confirm-chal-name').text(chal_name);
            description = description.html();

            var action = '{{ request.script_root }}/admin/solves/' + key_id + '/delete';
        } else if (type == 'chal-wrong') {
            var title = 'Delete Wrong Key';
            var description = "<span>Are you sure you want to delete " +
                "<strong>incorrect</strong> " +
                "submission from " +
                "<strong id='confirm-team-name'></strong> " +
                "for <strong id='confirm-chal-name'></strong>?</span>";

            var description = $($.parseHTML(description));
            description.find('#confirm-team-name').text(team_name);
            description.find('#confirm-chal-name').text(chal_name);
            description = description.html();

            var action = '{{ request.script_root }}/admin/wrong_keys/' + key_id + '/delete';
        } else if (type == 'award-row') {
            var title = 'Delete Award';
            var award_id = elem.find('.chal').attr('id');
            var description = "<span>Are you sure you want to delete the " +
                "<strong>{0}</strong> award?</span>".format(chal_name);
            var action = '{{ request.script_root }}/admin/awards/{0}/delete'.format(award_id);
        }

        var msg = {
            title: title,
            description: description,
            action: action,
        };

        var td_row = $(this).parent().parent();

        ezq({
            title: title,
            body: description,
            success: function () {
                var route = action;
                $.post(route, {
                    nonce: csrf_nonce,
                }, function (data) {
                    var data = $.parseJSON(JSON.stringify(data));
                    if (data == "1") {
                        td_row.remove();
                    }
                });
            }
        });
    });

    $('.mark-correct').click(function () {
        var elem = $(this).parent().parent();
        var type = elem.attr('class');
        var chal = elem.find('.chal').attr('id');
        var team = window.location.pathname.split('/').pop();

        var chal_name = htmlentities(elem.find('.chal').text().trim());
        var team_name = htmlentities($("#team-id").text());


        var description = $($.parseHTML(description));
        description.find('#confirm-team-name').text(team_name);
        description.find('#confirm-chal-name').text(chal_name);
        description = description.html();

        var action = '{{request.script_root }}/admin/solves/' + team + '/' + chal + '/solve';

        var title = 'Mark ' + chal_name + ' solved for ' + team_name;
        var description = "<span>Are you sure you want to mark " +
            "<strong>{0}</strong> ".format(team_name) +
            "as solved for team " +
            "<strong>{0}</strong>?</span>".format(chal_name);

        var td_row = $(this).parent().parent();

        ezq({
            title: title,
            body: description,
            success: function () {
                var route = script_root + '/admin/solves/' + team + '/' + chal + '/solve';
                $.post(route, {
                    nonce: csrf_nonce,
                }, function (data) {
                    var data = $.parseJSON(JSON.stringify(data));
                    if (data == "1") {
                        td_row.remove();
                    }
                });
            }
        })
    });

    $('#award-create-form').submit(function (e) {
        $.post($(this).attr('action'), $(this).serialize(), function (res) {
            if (res == '1') {
                var award = $('#award-create-form').serializeObject();
                var award_text = '<td class="text-center">{0}</td>'.format(award.name) +
                    '<td class="text-center">{0}</td>'.format(award.description) +
                    '<td class="text-center solve-time">{0}</td>'.format(moment().local().format('MMMM Do, h:mm:ss A')) +
                    '<td class="text-center">{0}</td>'.format(award.value) +
                    '<td class="text-center">{0}</td>'.format(award.category) +
                    '<td class="text-center">{0}</td>'.format('None') +
                    '<td class="text-center"><i class="fas fa-times"></i></td>'
                $('#awards-body').append(award_text);
                $('#create-award-modal').modal('hide');
            }
        })
        e.preventDefault();
    });
});