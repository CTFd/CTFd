import "./main";
import $ from "jquery";
import Moment from "moment-timezone";
import moment from "moment-timezone";
import CTFd from "../CTFd";

function switchTab(event) {
  event.preventDefault();

  // Handle tab validation
  let valid_tab = true;
  $(event.target)
    .closest("[role=tabpanel]")
    .find("input,textarea")
    .each(function(i, e) {
      $e = $(e);
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
  let date_picker = $(`#${datetime}-date`);
  let time_picker = $(`#${datetime}-time`);
  return function(event) {
    let unix_time = Moment(
      `${date_picker.val()} ${time_picker.val()}`,
      "YYYY-MM-DD HH:mm"
    )
      .utc()
      .format("X");
    $(`#${datetime}-preview`).val(unix_time);
  };
}

function mlcSetup(event) {
  let params = {
    ctf_name: $("#ctf_name").val(),
    ctf_type: "jeopardy",
    ctf_description: $("#ctf_description").val(),
    ctf_user_mode: $("#user_mode").val(),
    event_url: window.location.origin + CTFd.config.urlRoot,
    redirect_url:
      window.location.origin + CTFd.config.urlRoot + "/setup/integrations",
    start: $("#start-preview").val(),
    end: $("#end-preview").val(),
    platform: "CTFd"
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
  $("#integration-mlc").click(mlcSetup);

  $("#start-date,#start-time").change(processDateTime("start"));
  $("#end-date,#end-time").change(processDateTime("end"));

  window.addEventListener("storage", function(event) {
    if (event.key == "integrations" && event.newValue) {
      let integration = JSON.parse(event.newValue);
      if (integration["name"] == "mlc") {
        $("#integration-mlc")
          .text("Already Configured")
          .attr("disabled", true);
        window.focus();
        localStorage.removeItem('integrations');
      }
    }
  });
});
