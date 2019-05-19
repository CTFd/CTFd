$.ajaxSetup({ cache: false });

window.challenge = new Object();

function load_chal_template(challenge) {
  $.getScript(script_root + challenge.scripts.view, function() {
    console.log("loaded renderer");
    $.get(script_root + challenge.templates.create, function(template_data) {
      var template = nunjucks.compile(template_data);
      $("#create-chal-entry-div").html(
        template.render({ nonce: nonce, script_root: script_root })
      );
      $.getScript(script_root + challenge.scripts.create, function() {
        console.log("loaded");
        $("#create-chal-entry-div form").submit(function(e) {
          e.preventDefault();
          var params = $("#create-chal-entry-div form").serializeJSON();
          CTFd.fetch("/api/v1/challenges", {
            method: "POST",
            credentials: "same-origin",
            headers: {
              Accept: "application/json",
              "Content-Type": "application/json"
            },
            body: JSON.stringify(params)
          })
            .then(function(response) {
              return response.json();
            })
            .then(function(response) {
              if (response.success) {
                window.location =
                  script_root + "/admin/challenges/" + response.data.id;
              }
            });
        });
      });
    });
  });
}

$.get(script_root + "/api/v1/challenges/types", function(response) {
  $("#create-chals-select").empty();
  var data = response.data;
  var chal_type_amt = Object.keys(data).length;
  if (chal_type_amt > 1) {
    var option = "<option> -- </option>";
    $("#create-chals-select").append(option);
    for (var key in data) {
      var challenge = data[key];
      var option = $("<option/>");
      option.attr("value", challenge.type);
      option.text(challenge.name);
      option.data("meta", challenge);
      $("#create-chals-select").append(option);
    }
    $("#create-chals-select-div").show();
  } else if (chal_type_amt == 1) {
    var key = Object.keys(data)[0];
    $("#create-chals-select").empty();
    load_chal_template(data[key]);
  }
});
$("#create-chals-select").change(function() {
  var challenge = $(this)
    .find("option:selected")
    .data("meta");
  load_chal_template(challenge);
});
