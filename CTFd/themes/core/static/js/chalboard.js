var challenges;
var user_solves = [];
var templates = {};

window.challenge = new Object();

function loadchal(id) {
    var obj = $.grep(challenges['game'], function (e) {
        return e.id == id;
    })[0];

    updateChalWindow(obj);
}

function loadchalbyname(chalname) {
    var obj = $.grep(challenges['game'], function (e) {
      return e.name == chalname;
    })[0];

    updateChalWindow(obj);
}

function updateChalWindow(obj) {
    $.get(script_root + "/chals/" + obj.id, function(challenge_data){
        $.getScript(script_root + obj.script, function(){
            $.get(script_root + obj.template, function (template_data) {
                $('#chal-window').empty();

                var template = nunjucks.compile(template_data);

                var solves = obj.solves == 1 ? " Solve" : " Solves";
                var solves = obj.solves + solves;

                var nonce = $('#nonce').val();

                window.challenge.data = challenge_data;

                window.challenge.preRender();

                challenge_data['description'] = window.challenge.render(challenge_data['description']);
                challenge_data['script_root'] = script_root;
                challenge_data['solves'] = solves;

                $('#chal-window').append(template.render(challenge_data));

                $('.chal-solves').click(function (e) {
                    getsolves($('#chal-id').val())
                });
                $('.nav-tabs a').click(function (e) {
                    e.preventDefault();
                    $(this).tab('show')
                });

                // Handle modal toggling
                $('#chal-window').on('hide.bs.modal', function (event) {
                    $("#answer-input").removeClass("wrong");
                    $("#answer-input").removeClass("correct");
                    $("#incorrect-key").slideUp();
                    $("#correct-key").slideUp();
                    $("#already-solved").slideUp();
                    $("#too-fast").slideUp();
                });

                $('#submit-key').click(function (e) {
                    e.preventDefault();
                    $('#submit-key').addClass("disabled-button");
                    $('#submit-key').prop('disabled', true);
                    window.challenge.submit(function (data) {
                        renderSubmissionResponse(data)
                    });
                });

                $("#answer-input").keyup(function (event) {
                    if (event.keyCode == 13) {
                        $("#submit-key").click();
                    }
                });

                $(".input-field").bind({
                    focus: function () {
                        $(this).parent().addClass('input--filled');
                        $label = $(this).siblings(".input-label");
                    },
                    blur: function () {
                        if ($(this).val() === '') {
                            $(this).parent().removeClass('input--filled');
                            $label = $(this).siblings(".input-label");
                            $label.removeClass('input--hide');
                        }
                    }
                });

                window.challenge.postRender();

                window.location.replace(window.location.href.split('#')[0] + '#' + obj.name);
                $('#chal-window').modal();
            });
        });
    });
}

$("#answer-input").keyup(function(event){
    if(event.keyCode == 13){
        $("#submit-key").click();
    }
});


function renderSubmissionResponse(data, cb){
    var result = $.parseJSON(JSON.stringify(data));

    var result_message = $('#result-message');
    var result_notification = $('#result-notification');
    var answer_input = $("#answer-input");
    result_notification.removeClass();
    result_message.text(result.message);

    if (result.status == -1) {
        window.location = script_root + "/login?next=" + script_root + window.location.pathname + window.location.hash
        return
    }
    else if (result.status == 0) { // Incorrect key
        result_notification.addClass('alert alert-danger alert-dismissable text-center');
        result_notification.slideDown();

        answer_input.removeClass("correct");
        answer_input.addClass("wrong");
        setTimeout(function () {
            answer_input.removeClass("wrong");
        }, 3000);
    }
    else if (result.status == 1) { // Challenge Solved
        result_notification.addClass('alert alert-success alert-dismissable text-center');
        result_notification.slideDown();

        $('.chal-solves').text((parseInt($('.chal-solves').text().split(" ")[0]) + 1 + " Solves"));

        answer_input.val("");
        answer_input.removeClass("wrong");
        answer_input.addClass("correct");
    }
    else if (result.status == 2) { // Challenge already solved
        result_notification.addClass('alert alert-info alert-dismissable text-center');
        result_notification.slideDown();

        answer_input.addClass("correct");
    }
    else if (result.status == 3) { // Keys per minute too high
        result_notification.addClass('alert alert-warning alert-dismissable text-center');
        result_notification.slideDown();

        answer_input.addClass("too-fast");
        setTimeout(function () {
            answer_input.removeClass("too-fast");
        }, 3000);
    }
    marksolves();
    updatesolves();
    setTimeout(function () {
        $('.alert').slideUp();
        $('#submit-key').removeClass("disabled-button");
        $('#submit-key').prop('disabled', false);
    }, 3000);

    if (cb) {
        cb(result);
    }
}

function marksolves(cb) {
    $.get(script_root + '/solves', function (data) {
        var solves = $.parseJSON(JSON.stringify(data));
        for (var i = solves['solves'].length - 1; i >= 0; i--) {
            var id = solves['solves'][i].chalid;
            var btn = $('button[value="' + id + '"]');
            btn.addClass('solved-challenge');
            btn.prepend("<i class='fas fa-check corner-button-check'></i>")
        }
        if (cb) {
            cb();
        }
    });
}

function load_user_solves(cb){
    $.get(script_root + '/solves', function (data) {
        var solves = $.parseJSON(JSON.stringify(data));

        for (var i = solves['solves'].length - 1; i >= 0; i--) {
            var chal_id = solves['solves'][i].chalid;
            user_solves.push(chal_id);

        }
        if (cb) {
            cb();
        }
    });
}

function updatesolves(cb){
    $.get(script_root + '/chals/solves', function (data) {
        var solves = $.parseJSON(JSON.stringify(data));
        var chalids = Object.keys(solves);

        for (var i = 0; i < chalids.length; i++) {
            for (var z = 0; z < challenges['game'].length; z++) {
                var obj = challenges['game'][z];
                var solve_cnt = solves[chalids[i]];
                if (obj.id == chalids[i]){
                    if (solve_cnt) {
                        obj.solves = solve_cnt;
                    } else {
                        obj.solves = 0;
                    }
                }
            }
        };
        if (cb) {
            cb();
        }
    });
}

function getsolves(id){
  $.get(script_root + '/chal/'+id+'/solves', function (data) {
    var teams = data['teams'];
    $('.chal-solves').text((parseInt(teams.length) + " Solves"));
    var box = $('#chal-solves-names');
    box.empty();
    for (var i = 0; i < teams.length; i++) {
      var id = teams[i].id;
      var name = teams[i].name;
      var date = moment(teams[i].date).local().fromNow();
      box.append('<tr><td><a href="team/{0}">{1}</td><td>{2}</td></tr>'.format(id, htmlentities(name), date));
    };
  });
}

function loadchals(cb) {
    $.get(script_root + "/chals", function (data) {
        var categories = [];
        challenges = $.parseJSON(JSON.stringify(data));

        $('#challenges-board').empty();

        for (var i = challenges['game'].length - 1; i >= 0; i--) {
            challenges['game'][i].solves = 0;
            if ($.inArray(challenges['game'][i].category, categories) == -1) {
                var category = challenges['game'][i].category;
                categories.push(category);

                var categoryid = category.replace(/ /g,"-").hashCode();
                var categoryrow = $('' +
                    '<div id="{0}-row" class="pt-5">'.format(categoryid) +
                        '<div class="category-header col-md-12 mb-3">' +
                        '</div>' +
                        '<div class="category-challenges col-md-12">' +
                            '<div class="challenges-row col-md-12"></div>' +
                        '</div>' +
                    '</div>');
                categoryrow.find(".category-header").append($("<h3>"+ category +"</h3>"));

                $('#challenges-board').append(categoryrow);
            }
        }

        for (var i = 0; i <= challenges['game'].length - 1; i++) {
            var chalinfo = challenges['game'][i];
            var challenge = chalinfo.category.replace(/ /g,"-").hashCode();
            var chalid = chalinfo.name.replace(/ /g,"-").hashCode();
            var catid = chalinfo.category.replace(/ /g,"-").hashCode();
            var chalwrap = $("<div id='{0}' class='col-md-3 d-inline-block'></div>".format(chalid));

            if (user_solves.indexOf(chalinfo.id) == -1){
                var chalbutton = $("<button class='btn btn-dark challenge-button w-100 text-truncate pt-3 pb-3 mb-2' value='{0}'></button>".format(chalinfo.id));
            } else {
                var chalbutton = $("<button class='btn btn-dark challenge-button solved-challenge w-100 text-truncate pt-3 pb-3 mb-2' value='{0}'><i class='fas fa-check corner-button-check'></i></button>".format(chalinfo.id));
            }

            var chalheader = $("<p>{0}</p>".format(chalinfo.name));
            var chalscore = $("<span>{0}</span>".format(chalinfo.value));
            for (var j = 0; j < chalinfo.tags.length; j++) {
                var tag = 'tag-' + chalinfo.tags[j].replace(/ /g, '-');
                chalwrap.addClass(tag);
            }

            chalbutton.append(chalheader);
            chalbutton.append(chalscore);
            chalwrap.append(chalbutton);

            $("#"+ catid +"-row").find(".category-challenges > .challenges-row").append(chalwrap);
        };

        // marksolves();

        $('.challenge-button').click(function (e) {
            loadchal(this.value);
        });

        if (cb){
            cb();
        }
    });
}

function loadhint(hintid){
    var md = window.markdownit({
        html: true,
    });
    ezq({
        title: "Unlock Hint?",
        body: "Are you sure you want to open this hint?",
        success: function(){
            $.post(script_root + "/hints/" + hintid, {'nonce': $('#nonce').val()}, function (data) {
                if (data.errors) {
                    ezal({
                        title: "Error!",
                        body: data.errors,
                        button: "Okay"
                    });
                } else {

                    ezal({
                        title: "Hint",
                        body: md.render(data.hint),
                        button: "Got it!"
                    });
                }
            });
        }
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

var load_location_hash = function () {
    if (window.location.hash.length > 0) {
        loadchalbyname(decodeURIComponent(window.location.hash.substring(1)));
    }
};

function update(cb){
    load_user_solves(function () { // Load the user's solved challenge ids
        loadchals(function () { //  Load the full list of challenges
            updatesolves(cb); // Load the counts of all challenge solves and then load the location hash specified challenge
        });
    });
}

$(function() {
    update(function(){
        load_location_hash();
    });
});

$('.nav-tabs a').click(function (e) {
    e.preventDefault();
    $(this).tab('show')
})

$('#chal-window').on('hidden.bs.modal', function() {
    $('.nav-tabs a:first').tab('show');
    history.replaceState('', document.title, window.location.pathname);
});

setInterval(update, 300000);
