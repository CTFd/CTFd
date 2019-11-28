import "./main";
import $ from "jquery";
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

$(() => {
  $(".tab-next").click(switchTab);
});
