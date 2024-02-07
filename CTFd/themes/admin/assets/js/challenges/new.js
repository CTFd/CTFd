import CTFd from "../compat/CTFd";
import nunjucks from "nunjucks";
import $ from "jquery";
import "../compat/json";

window.challenge = new Object();

function loadChalTemplate(challenge) {
  $.getScript(CTFd.config.urlRoot + challenge.scripts.view, function () {
    $.get(
      CTFd.config.urlRoot + challenge.templates.create,
      function (template_data) {
        const template = nunjucks.compile(template_data);
        $("#create-chal-entry-div").html(
          template.render({
            nonce: CTFd.config.csrfNonce,
            script_root: CTFd.config.urlRoot,
          }),
        );

        $.getScript(
          CTFd.config.urlRoot + challenge.scripts.create,
          function () {
            $("#create-chal-entry-div form").submit(function (event) {
              event.preventDefault();
              const params = $("#create-chal-entry-div form").serializeJSON();
              CTFd.fetch("/api/v1/challenges", {
                method: "POST",
                credentials: "same-origin",
                headers: {
                  Accept: "application/json",
                  "Content-Type": "application/json",
                },
                body: JSON.stringify(params),
              }).then(function (response) {
                if (response.success) {
                  window.location =
                    CTFd.config.urlRoot +
                    "/admin/challenges/" +
                    response.data.id;
                }
              });
            });
          },
        );
      },
    );
  });
}

$.get(CTFd.config.urlRoot + "/api/v1/challenges/types", function (response) {
  $("#create-chals-select").empty();
  const data = response.data;
  const chal_type_amt = Object.keys(data).length;
  if (chal_type_amt > 1) {
    const option = "<option> -- </option>";
    $("#create-chals-select").append(option);
    for (const key in data) {
      const challenge = data[key];
      const option = $("<option/>");
      option.attr("value", challenge.type);
      option.text(challenge.name);
      option.data("meta", challenge);
      $("#create-chals-select").append(option);
    }
    $("#create-chals-select-div").show();
  } else if (chal_type_amt == 1) {
    const key = Object.keys(data)[0];
    $("#create-chals-select").empty();
    loadChalTemplate(data[key]);
  }
});

function createChallenge(_event) {
  const challenge = $(this).find("option:selected").data("meta");
  loadChalTemplate(challenge);
}

$(() => {
  $("#create-chals-select").change(createChallenge);
});
