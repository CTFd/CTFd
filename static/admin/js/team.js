function teamid (){
    loc = window.location.pathname
    return loc.substring(loc.lastIndexOf('/')+1, loc.length);
}


function cumulativesum (arr) {
    var result = arr.concat();
    for (var i = 0; i < arr.length; i++){
        result[i] = arr.slice(0, i + 1).reduce(function(p, i){ return p + i; });
    }
    return result
}

function scoregraph () {
    var times = []
    var scores = []
    var teamname = $('#team-id').text()
    $.get('/admin/solves/'+teamid(), function( data ) {
        solves = $.parseJSON(JSON.stringify(data));
        solves = solves['solves']

        if (solves.length == 0)
            return

        for (var i = 0; i < solves.length; i++) {
            times.push(solves[i].time * 1000)
            scores.push(solves[i].value)
        };
        scores = cumulativesum(scores)

        times.unshift('x1')
        times.push( Math.round(new Date().getTime()) )

        scores.unshift('data1')
        scores.push( scores[scores.length-1] )

        var chart = c3.generate({
            bindto: "#score-graph",
            data: {
                xs: {
                    "data1": 'x1',
                },
                columns: [
                    times,
                    scores,
                ],
                type: "area",
                labels: true,
                names : {
                    data1: teamname
                }
            },
            axis : {
                x : {
                    tick: {
                        format: function (x) { 
                            return moment(x).local().format('LLL');
                        }
                    },
                    
                },
                y:{
                    label: {
                        text: 'Score'
                    }
                }
            }
        });
    });
}

function adjust_times () {
    $.each($(".solve-time"), function(i, e){
        $(e).text( moment(parseInt(e.innerText)).local().format('LLL') ) 
    })
    $(".solve-time").css('color', "#222")
}


function keys_percentage_graph(){
    // Solves and Fails pie chart
    $.get('/admin/fails/'+teamid(), function(data){
        res = $.parseJSON(JSON.stringify(data));
        solves = res['solves']
        fails = res['fails']
        total = solves+fails

        if (total == 0)
            return

        var chart = c3.generate({
            bindto: '#keys-pie-graph',
            data: {
                columns: [
                    ['Solves', solves],
                    ['Fails', fails],
                ],
                type : 'donut'
            },
            color: {
                    pattern: ["#00D140", "#CF2600"]
            },
            donut: {
                title: "Solves vs Fails",
            }
        });
    });
}

function category_breakdown_graph(){
    $.get('/admin/solves/'+teamid(), function(data){
        solves = $.parseJSON(JSON.stringify(data));
        solves = solves['solves']

        if (solves.length == 0)
            return

        categories = []
        for (var i = 0; i < solves.length; i++) {
            categories.push(solves[i].category)
        };

        keys = categories.filter(function(elem, pos) {
            return categories.indexOf(elem) == pos;
        })

        data = []
        for (var i = 0; i < keys.length; i++) {
            temp = []
            count = 0
            for (var x = 0; x < categories.length; x++) {
                if (categories[x] == keys[i]){
                    count++
                }
            };
            temp.push(keys[i])
            temp.push(count)
            data.push(temp)
        };

        var chart = c3.generate({
            bindto: '#categories-pie-graph',
            data: {
                columns: data,
                type : 'donut',
                labels: true
            },
            donut: {
                title: "Category Breakdown"
            }
        });
    });
}

category_breakdown_graph()
keys_percentage_graph()
adjust_times()
scoregraph()