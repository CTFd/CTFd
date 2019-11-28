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

$(() => {
  $(".tab-next").click(switchTab);

  $("#start-date,#start-time").change(processDateTime("start"));
  $("#end-date,#end-time").change(processDateTime("end"));
});
