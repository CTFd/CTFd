import "./main";
import $ from "jquery";
import { ezQuery } from "core/ezq";

function reset(event) {
  event.preventDefault();
  ezQuery({
    title: "Reset CTF?",
    body: "Are you sure you want to reset your CTFd instance?",
    success: function() {
      $("#reset-ctf-form")
        .off("submit")
        .submit();
    }
  });
}

$(() => {
  $("#reset-ctf-form").submit(reset);
});
