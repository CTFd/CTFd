var challenges;

function loadchal(id) {
    obj = $.grep(challenges['game'], function (e) {
        return e.id == id;
    })[0];

    updateChalWindow(obj);
}

function loadchalbyname(chalname) {
    obj = $.grep(challenges['game'], function (e) {
      return e.name == chalname;
    })[0];

    updateChalWindow(obj);
}

function updateChalWindow(obj) {
    window.location.hash = obj.name;
    var chal = $('#chal-window');
    chal.find('.chal-name').text(obj.name);
    chal.find('.chal-desc').html(marked(obj.description, {'gfm':true, 'breaks':true}));
    chal.find('.chal-files').empty();
    for (var i = 0; i < obj.files.length; i++) {
        filename = obj.files[i].split('/');
        filename = filename[filename.length - 1];
        $('#chal-window').find('.chal-files').append("<div class='col-md-3 file-button-wrapper'><a class='file-button' href='"+obj.files[i]+"'><label class='challenge-wrapper file-wrapper hide-text'>"+filename+"</label></a></div>")
    }

    var tags = chal.find('.chal-tags');
    tags.empty();
    var tag = "<span class='label label-primary chal-tag'>{0}</span>";
    for (var i = 0; i < obj.tags.length; i++){
        var data = tag.format(obj.tags[i]);
        tags.append($(data));
    }

    chal.find('.chal-value').text(obj.value);
    chal.find('.chal-category').text(obj.category);
    chal.find('#chal-id').val(obj.id);
    var solves = obj.solves == 1 ? " Solve" : " Solves";
    chal.find('.chal-solves').text(obj.solves + solves);
    $('#answer').val("");

    $('pre code').each(function(i, block) {
        hljs.highlightBlock(block);
    });
}

$("#answer-input").keyup(function(event){
    if(event.keyCode == 13){
        $("#submit-key").click();
    }
});


function submitkey(chal, key, nonce) {
    $('#submit-key').addClass("disabled-button");
    $('#submit-key').prop('disabled', true);
    $.post("/chal/" + chal, {
        key: key,
        nonce: nonce
    }, function (data) {
        if (data == -1){
          window.location="/login"
          return
        }
        else if (data == 0){ // Incorrect key
            $("#incorrect-key").slideDown();
            $("#answer-input").addClass("wrong");
            $("#answer-input").removeClass("correct");
            setTimeout(function() {
                $("#answer-input").removeClass("wrong");
            }, 3000);
        }
        else if (data == 1){ // Challenge Solved
            $("#correct-key").slideDown();
            $('.chal-solves').text((parseInt($('.chal-solves').text().split(" ")[0]) + 1 +  " Solves") )
            $("#answer-input").val("");
            $("#answer-input").removeClass("wrong");
            $("#answer-input").addClass("correct");
        }
        else if (data == 2){ // Challenge already solved
            $("#already-solved").slideDown();
            $("#answer-input").addClass("correct");
        }
        else if (data == 3){ // Keys per minute too high
            $("#too-fast").slideDown();
            $("#answer-input").addClass("wrong");
            setTimeout(function() {
                $("#answer-input").removeClass("wrong");
            }, 3000);
        }
        marksolves()
        updatesolves()
        setTimeout(function(){
          $('.alert').slideUp();
          $('#submit-key').removeClass("disabled-button");
          $('#submit-key').prop('disabled', false);
        }, 3000);
    })
}

function marksolves() {
    $.get('/solves', function (data) {
        solves = $.parseJSON(JSON.stringify(data));
        for (var i = solves['solves'].length - 1; i >= 0; i--) {
            id = solves['solves'][i].chalid;
            $('button[value="' + id + '"]').removeClass('theme-background');
            $('button[value="' + id + '"]').addClass('solved-challenge');
        };
        if (window.location.hash.length > 0){
          loadchalbyname(window.location.hash.substring(1))
            $("#chal-window").modal("show");
        }
    });
}

function updatesolves(){
    $.get('/chals/solves', function (data) {
      solves = $.parseJSON(JSON.stringify(data));
      chals = Object.keys(solves);

      for (var i = 0; i < chals.length; i++) {
        obj = $.grep(challenges['game'], function (e) {
            return e.name == chals[i];
        })[0]
        obj.solves = solves[chals[i]]
      };

    });
}

function getsolves(id){
  $.get('/chal/'+id+'/solves', function (data) {
    var teams = data['teams'];
    var box = $('#chal-solves-names');
    box.empty();
    for (var i = 0; i < teams.length; i++) {
      var id = teams[i].id;
      var name = teams[i].name;
      var date = moment(teams[i].date).local().format('LLL');
      box.append('<tr><td><a href="/team/{0}">{1}</td><td>{2}</td></tr>'.format(id, htmlentities(name), date));
    };
  });
}

function loadchals() {

    $.get("/chals", function (data) {
        var categories = [];
        challenges = $.parseJSON(JSON.stringify(data));

        $('#challenges-board').html("");

        for (var i = challenges['game'].length - 1; i >= 0; i--) {
            challenges['game'][i].solves = 0
            if ($.inArray(challenges['game'][i].category, categories) == -1) {
                var category = challenges['game'][i].category;
                categories.push(category);

                var categoryid = category.replace(/ /g,"-").hashCode();
                var categoryrow = $('' +
                    '<div id="{0}-row">'.format(categoryid) +
                        '<div class="category-header col-md-2">' +
                        '</div>' +
                        '<div class="category-challenges col-md-12">' +
                            '<div class="chal-row"></div>' +
                        '</div>' +
                    '</div>');
                categoryrow.find(".category-header").append($("<h3>"+ category +"</h3>"));

                $('#challenges-board').append(categoryrow);
            }
        };

        for (var i = 0; i <= challenges['game'].length - 1; i++) {
            var chalinfo = challenges['game'][i];
            var challenge = chalinfo.category.replace(/ /g,"-").hashCode();
            var chalid = chalinfo.name.replace(/ /g,"-").hashCode();
            var catid = chalinfo.category.replace(/ /g,"-").hashCode();
            var chalwrap = $("<div id='{0}' class='challenge-wrapper col-md-2'></div>".format(chalid));
            var chalbutton = $("<button class='challenge-button trigger theme-background hide-text' value='{0}' data-toggle='modal' data-target='#chal-window'></div>".format(chalinfo.id));
            var chalheader = $("<h5>{0}</h5>".format(chalinfo.name));
            var chalscore = $("<span>{0}</span>".format(chalinfo.value));
            chalbutton.append(chalheader);
            chalbutton.append(chalscore);
            chalwrap.append(chalbutton);

            $("#"+ catid +"-row").find(".category-challenges > .chal-row").append(chalwrap);
        };

        updatesolves();
        marksolves();

        $('.challenge-button').click(function (e) {
            loadchal(this.value);
        });
    });
}

$('#submit-key').click(function (e) {
    submitkey($('#chal-id').val(), $('#answer-input').val(), $('#nonce').val())
});

$('.chal-solves').click(function (e) {
    getsolves($('#chal-id').val())
});

$('#chal-window').on('hide.bs.modal', function (event) {
    $("#answer-input").removeClass("wrong");
    $("#answer-input").removeClass("correct");
    $("#incorrect-key").slideUp();
    $("#correct-key").slideUp();
    $("#already-solved").slideUp();
    $("#too-fast").slideUp();
});

// $.distint(array)
// Unique elements in array
$.extend({
    distinct : function(anArray) {
       var result = [];
       $.each(anArray, function(i,v){
           if ($.inArray(v, result) == -1) result.push(v);
       });
       return result;
    }
});

function colorhash (x) {
    color = ""
    for (var i = 20; i <= 60; i+=20){
        x += i
        x *= i
        color += x.toString(16)
    };
    return "#" + color.substring(0, 6)
}

function update(){
    loadchals()
}

$(function() {
    loadchals();
});

$('.nav-tabs a').click(function (e) {
    e.preventDefault()
    $(this).tab('show')
})

$('.close').click(function() {
    $('.nav-tabs a:first').tab('show')
    window.location.hash = ""
});

setInterval(update, 300000);
