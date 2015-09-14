//http://stackoverflow.com/a/2648463 - wizardry!
String.prototype.format = String.prototype.f = function() {
    var s = this,
        i = arguments.length;

    while (i--) {
        s = s.replace(new RegExp('\\{' + i + '\\}', 'gm'), arguments[i]);
    }
    return s;
};

function htmlentities(string) {
    return $('<div/>').text(string).html();
}

function updatescores () {
  $.get('/scores', function( data ) {
    teams = $.parseJSON(JSON.stringify(data));
    $('#scoreboard > tbody').empty()
    for (var i = 0; i < teams['teams'].length; i++) {
      row = "<tr><td>{0}</td><td><a href='/team/{1}'>{2}</a></td><td>{3}</td></tr>".format(i+1, teams['teams'][i].id, htmlentities(teams['teams'][i].name), teams['teams'][i].score)
      $('#scoreboard > tbody').append(row)
    };
  });
}

function cumulativesum (arr) {
    var result = arr.concat();
    for (var i = 0; i < arr.length; i++){
        result[i] = arr.slice(0, i + 1).reduce(function(p, i){ return p + i; });
    }
    return result
}

function UTCtoDate(utc){
    var d = new Date(0)
    d.setUTCSeconds(utc)
    return d;
}

function scoregraph () {
    var times = []
    var scores = []
    $.get('/top/10', function( data ) {
        scores = $.parseJSON(JSON.stringify(data));
        scores = scores['scores']
        if (Object.keys(scores).length == 0 ){
            return;
        }
        $('#score-graph').show()
        teams = Object.keys(scores)

        xs_data = {}
        column_data = []
        for (var i = 0; i < teams.length; i++) {
          times = []
          team_scores = []
          for (var x = 0; x < scores[teams[i]].length; x++) {
            times.push(scores[teams[i]][x].time)
            team_scores.push(scores[teams[i]][x].value)
          };
          team_scores = cumulativesum(team_scores)

          times.unshift("x"+i)
          // times.push( Math.round(new Date().getTime()/1000) )

          team_scores.unshift(teams[i])
          // team_scores.push( team_scores[team_scores.length-1] )

              
          xs_data[teams[i]] = "x"+i
          column_data.push(times)
          column_data.push(team_scores)

        };

        var chart = c3.generate({
            bindto: "#score-graph",
            data: {
                xs: xs_data,
                columns: column_data,
                type: "step"
                // labels: true
            },
            axis : {
                x : {
                    tick: {
                        count: 10,
                        format: function (x) { 
                            return moment(x*1000).local().format('LLL');
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

function update(){
  updatescores()
  scoregraph()
}

setInterval(update, 300000); // Update scores every 5 minutes
scoregraph()
