import "./main";
import $ from "jquery";
import dayjs from "dayjs";
import CTFd from "../CTFd";

function switchTab(event) {
  event.preventDefault();

  // Handle tab validation
  let valid_tab = true;
  $(event.target)
    .closest("[role=tabpanel]")
    .find("input,textarea")
    .each(function(i, e) {
      let $e = $(e);
      let status = e.checkValidity();
      if (status === false) {
        $e.removeClass("input-filled-valid");
        $e.addClass("input-filled-invalid");
        valid_tab = false;
      }
    });

  if (valid_tab == false) {
    return;
  }

  let href = $(event.target).data("href");
  $(`.nav a[href="${href}"]`).tab("show");
}

function processDateTime(datetime) {
  return function(_event) {
    let date_picker = $(`#${datetime}-date`);
    let time_picker = $(`#${datetime}-time`);
    let unix_time = dayjs(
      `${date_picker.val()} ${time_picker.val()}`,
      "YYYY-MM-DD HH:mm"
    ).unix();

    if (isNaN(unix_time)) {
      $(`#${datetime}-preview`).val("");
    } else {
      $(`#${datetime}-preview`).val(unix_time);
    }
  };
}

function mlcSetup(_event) {
  let params = {
    name: $("#ctf_name").val(),
    type: "jeopardy",
    description: $("#ctf_description").val(),
    user_mode: $("#user_mode").val(),
    event_url: window.location.origin + CTFd.config.urlRoot,
    redirect_url: window.location.origin + CTFd.config.urlRoot + "/redirect",
    integration_setup_url:
      window.location.origin + CTFd.config.urlRoot + "/setup/integrations",
    start: $("#start-preview").val(),
    end: $("#end-preview").val(),
    platform: "CTFd",
    state: window.STATE
  };

  const ret = [];
  for (let p in params) {
    ret.push(encodeURIComponent(p) + "=" + encodeURIComponent(params[p]));
  }
  window.open(
    "https://www.majorleaguecyber.org/events/new?" + ret.join("&"),
    "_blank"
  );
}

$(() => {
  $(".tab-next").click(switchTab);
  $("input").on("keypress", function(e) {
    // Hook Enter button
    if (e.keyCode == 13) {
      e.preventDefault();
      $(e.target)
        .closest(".tab-pane")
        .find("button[data-href]")
        .click();
    }
  });

  $("#integration-mlc").click(mlcSetup);

  $("#start-date,#start-time").change(processDateTime("start"));
  $("#end-date,#end-time").change(processDateTime("end"));

  $("#config-color-picker").on("input", function(_e) {
    $("#config-color-input").val($(this).val());
  });

  $("#config-color-reset").click(function() {
    $("#config-color-input").val("");
    $("#config-color-picker").val("");
  });

  window.addEventListener("storage", function(event) {
    if (event.key == "integrations" && event.newValue) {
      let integration = JSON.parse(event.newValue);
      if (integration["name"] == "mlc") {
        $("#integration-mlc")
          .text("Already Configured")
          .attr("disabled", true);
        window.focus();
        localStorage.removeItem("integrations");
      }
    }
  });

  $("#setup-form").submit(function(e) {
    if ($("#newsletter-checkbox").prop("checked")) {
      let email = $(e.target)
        .find("input[name=email]")
        .val();

      $.ajax({
        type: "POST",
        url:
          "https://ctfd.us15.list-manage.com/subscribe/post-json?u=6c7fa6feeced52775aec9d015&id=dd1484208e&c=?",
        data: {
          EMAIL: email,
          subscribe: "Subscribe",
          b_6c7fa6feeced52775aec9d015_dd1484208e: ""
        },
        dataType: "jsonp",
        contentType: "application/json; charset=utf-8"
      });
    }
  });
});
