import "./main";
import $ from "jquery";
import CTFd from "../CTFd";

function switchTab(event) {
  event.preventDefault();
  let href = $(event.target).data("href");
  $(`.nav a[href="${href}"]`).tab("show");
}

$(() => {
  $(".tab-next").click(switchTab);
});
