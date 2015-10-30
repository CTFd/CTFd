function teamid (){
    loc = window.location.pathname
    return parseInt(loc.substring(loc.lastIndexOf('/')+1, loc.length));
}

function colorhash (x) {
    color = ""
    for (var i = 20; i <= 60; i+=20){
        x += i
        x *= i
        color += x.toString(16)
    };
    return "#" + color.substring(0, 6)
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
    $.get('/solves/'+teamid(), function( data ) {
        solves = $.parseJSON(JSON.stringify(data));
        solves = solves['solves']

        console.log(solves)

        if (solves.length == 0)
            return

        for (var i = 0; i < solves.length; i++) {
            times.push(solves[i].time * 1000)
            scores.push(solves[i].value)
        };
        scores = cumulativesum(scores)

        times.unshift('x1')
        // times.push( Math.round(new Date().getTime()) )

        scores.unshift('data1')
        // scores.push( scores[scores.length-1] )

        console.log(scores)

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
                type: "area-step",
                colors: {
                    data1: colorhash(teamid()),
                },
                labels: true,
                names : {
                    data1: teamname
                }
            },
            axis : {
                x : {
                    tick: {
                        format: function (x) { 
                            return moment(x).local().format('M/D h:mm:ss');
                        }
                    },
                    
                },
                y:{
                    label: {
                        text: 'Score'
                    }
                }
            },
            zoom : {
                enabled: true
            }
        });
    });
}

function keys_percentage_graph(){
    // Solves and Fails pie chart
    $.get('/fails/'+teamid(), function(data){
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
    $.get('/solves/'+teamid(), function(data){
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
                title: "Category Breakdown",
            }
        });
    });
}

category_breakdown_graph()
keys_percentage_graph()
scoregraph()
