import "./main";
import { showMediaLibrary } from "../styles";
import "core/utils";
import $ from "jquery";
import CTFd from "core/CTFd";
import CodeMirror from "codemirror";
import "codemirror/mode/htmlmixed/htmlmixed.js";
import { ezToast } from "core/ezq";

function submit_form() {
  // Save the CodeMirror data to the Textarea
  window.editor.save();
  var params = $("#page-edit").serializeJSON();
  var target = "/api/v1/pages";
  var method = "POST";

  let part = window.location.pathname.split("/").pop();
  if (part !== "new") {
    target += "/" + part;
    method = "PATCH";
  }

  CTFd.fetch(target, {
    method: method,
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
      if (method === "PATCH" && response.success) {
        ezToast({
          title: "Saved",
          body: "Your changes have been saved"
        });
      } else {
        window.location =
          CTFd.config.urlRoot + "/admin/pages/" + response.data.id;
      }
    });
}

function preview_page() {
  window.editor.save(); // Save the CodeMirror data to the Textarea
  $("#page-edit").attr("action", CTFd.config.urlRoot + "/admin/pages/preview");
  $("#page-edit").attr("target", "_blank");
  $("#page-edit").submit();
}

$(() => {
  window.editor = CodeMirror.fromTextArea(
    document.getElementById("admin-pages-editor"),
    {
      lineNumbers: true,
      lineWrapping: true,
      mode: "htmlmixed",
      htmlMode: true
    }
  );

  $("#media-button").click(function(_e) {
    showMediaLibrary(window.editor);
  });

  $("#save-page").click(function(e) {
    e.preventDefault();
    submit_form();
  });

  $(".preview-page").click(function() {
    preview_page();
  });
});
