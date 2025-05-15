import "./main";
import { showMediaLibrary } from "../styles";
import $ from "jquery";
import CTFd from "../compat/CTFd";
import "../compat/json";
import CodeMirror from "codemirror";
import "codemirror/mode/htmlmixed/htmlmixed.js";
import { ezAlert, ezToast } from "../compat/ezq";
import * as Vue from "vue";
import CommentBox from "../components/comments/CommentBox.vue";

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

  // Patch link_target to be null when empty string
  if (params["link_target"] === "") {
    params["link_target"] = null;
  }

  CTFd.fetch(target, {
    method: method,
    credentials: "same-origin",
    headers: {
      Accept: "application/json",
      "Content-Type": "application/json",
    },
    body: JSON.stringify(params),
  })
    .then(function (response) {
      return response.json();
    })
    .then(function (response) {
      // Show errors reported by API
      if (response.success === false) {
        let body = "";
        for (const k in response.errors) {
          body += response.errors[k].join("\n");
          body += "\n";
        }

        ezAlert({
          title: "Error",
          body: body,
          button: "OK",
        });
        return;
      }

      if (method === "PATCH" && response.success) {
        ezToast({
          title: "Saved",
          body: "Your changes have been saved",
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
      htmlMode: true,
    },
  );

  $("#media-button").click(function (_e) {
    showMediaLibrary(window.editor);
  });

  $("#save-page").click(function (e) {
    e.preventDefault();
    submit_form();
  });

  $(".preview-page").click(function () {
    preview_page();
  });

  // Insert CommentBox element
  if (window.PAGE_ID) {
    let vueContainer = document.createElement("div");
    document.querySelector("#comment-box").appendChild(vueContainer);

    Vue.createApp({
      render: () => Vue.h(CommentBox, {
        type: "page",
        id: window.PAGE_ID
      })
    }).mount(vueContainer);
  }
});
