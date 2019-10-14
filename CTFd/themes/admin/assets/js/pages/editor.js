import "./main";
import "core/utils";
import $ from "jquery";
import CTFd from "core/CTFd";
import { default as helpers } from "core/helpers";
import CodeMirror from "codemirror";
import { ezQuery, ezToast } from "core/ezq";

function get_filetype_icon_class(filename) {
  var mapping = {
    // Image Files
    png: "fa-file-image",
    jpg: "fa-file-image",
    jpeg: "fa-file-image",
    gif: "fa-file-image",
    bmp: "fa-file-image",
    svg: "fa-file-image",

    // Text Files
    txt: "fa-file-alt",

    // Video Files
    mov: "fa-file-video",
    mp4: "fa-file-video",
    wmv: "fa-file-video",
    flv: "fa-file-video",
    mkv: "fa-file-video",
    avi: "fa-file-video",

    // PDF Files
    pdf: "fa-file-pdf",

    // Audio Files
    mp3: "fa-file-sound",
    wav: "fa-file-sound",
    aac: "fa-file-sound",

    // Archive Files
    zip: "fa-file-archive",
    gz: "fa-file-archive",
    tar: "fa-file-archive",
    "7z": "fa-file-archive",
    rar: "fa-file-archive",

    // Code Files
    py: "fa-file-code",
    c: "fa-file-code",
    cpp: "fa-file-code",
    html: "fa-file-code",
    js: "fa-file-code",
    rb: "fa-file-code",
    go: "fa-file-code"
  };

  var ext = filename.split(".").pop();
  return mapping[ext];
}

function get_page_files() {
  return CTFd.fetch("/api/v1/files?type=page", {
    credentials: "same-origin"
  }).then(function(response) {
    return response.json();
  });
}

function show_files(data) {
  var list = $("#media-library-list");
  list.empty();

  for (var i = 0; i < data.length; i++) {
    var f = data[i];
    var fname = f.location.split("/").pop();
    var ext = get_filetype_icon_class(f.location);

    var wrapper = $("<div>").attr("class", "media-item-wrapper");

    var link = $("<a>");
    link.attr("href", "##");

    if (ext === undefined) {
      link.append(
        '<i class="far fa-file" aria-hidden="true"></i> '.format(ext)
      );
    } else {
      link.append('<i class="far {0}" aria-hidden="true"></i> '.format(ext));
    }

    link.append(
      $("<small>")
        .attr("class", "media-item-title")
        .text(fname)
    );

    link.click(function(e) {
      var media_div = $(this).parent();
      var icon = $(this).find("i")[0];
      var f_loc = media_div.attr("data-location");
      var fname = media_div.attr("data-filename");
      var f_id = media_div.attr("data-id");
      $("#media-delete").attr("data-id", f_id);
      $("#media-link").val(f_loc);
      $("#media-filename").html(
        $("<a>")
          .attr("href", f_loc)
          .attr("target", "_blank")
          .text(fname)
      );

      $("#media-icon").empty();
      if ($(icon).hasClass("fa-file-image")) {
        $("#media-icon").append(
          $("<img>")
            .attr("src", f_loc)
            .css({
              "max-width": "100%",
              "max-height": "100%",
              "object-fit": "contain"
            })
        );
      } else {
        // icon is empty so we need to pull outerHTML
        var copy_icon = $(icon).clone();
        $(copy_icon).addClass("fa-4x");
        $("#media-icon").append(copy_icon);
      }
      $("#media-item").show();
    });
    wrapper.append(link);
    wrapper.attr("data-location", CTFd.config.urlRoot + "/files/" + f.location);
    wrapper.attr("data-id", f.id);
    wrapper.attr("data-filename", fname);
    list.append(wrapper);
  }
}

function refresh_files(cb) {
  get_page_files().then(function(response) {
    var data = response.data;
    show_files(data);
    if (cb) {
      cb();
    }
  });
}

function insert_at_cursor(editor, text) {
  var doc = editor.getDoc();
  var cursor = doc.getCursor();
  doc.replaceRange(text, cursor);
}

function submit_form() {
  // Save the CodeMirror data to the Textarea
  window.editor.save();
  var params = $("#page-edit").serializeJSON();
  var target = "/api/v1/pages";
  var method = "POST";

  if (params.id) {
    target += "/" + params.id;
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
  editor.save(); // Save the CodeMirror data to the Textarea
  $("#page-edit").attr("action", CTFd.config.urlRoot + "/admin/pages/preview");
  $("#page-edit").attr("target", "_blank");
  $("#page-edit").submit();
}

function upload_media() {
  helpers.files.upload($("#media-library-upload"), function(data) {
    refresh_files();
  });
}

$(() => {
  window.editor = CodeMirror.fromTextArea(
    document.getElementById("admin-pages-editor"),
    {
      lineNumbers: true,
      lineWrapping: true,
      mode: "xml",
      htmlMode: true
    }
  );

  $("#media-insert").click(function(e) {
    var tag = "";
    try {
      tag = $("#media-icon")
        .children()[0]
        .nodeName.toLowerCase();
    } catch (err) {
      tag = "";
    }
    var link = $("#media-link").val();
    var fname = $("#media-filename").text();
    var entry = null;
    if (tag === "img") {
      entry = "![{0}]({1})".format(fname, link);
    } else {
      entry = "[{0}]({1})".format(fname, link);
    }
    insert_at_cursor(editor, entry);
  });

  $("#media-download").click(function(e) {
    var link = $("#media-link").val();
    window.open(link, "_blank");
  });

  $("#media-delete").click(function(e) {
    var file_id = $(this).attr("data-id");
    ezQuery({
      title: "Delete File?",
      body: "Are you sure you want to delete this file?",
      success: function() {
        CTFd.fetch("/api/v1/files/" + file_id, {
          method: "DELETE",
          credentials: "same-origin",
          headers: {
            Accept: "application/json",
            "Content-Type": "application/json"
          }
        }).then(function(response) {
          if (response.status === 200) {
            response.json().then(function(object) {
              if (object.success) {
                refresh_files();
              }
            });
          }
        });
      }
    });
  });

  $("#save-page").click(function(e) {
    e.preventDefault();
    submit_form();
  });

  $("#media-button").click(function() {
    $("#media-library-list").empty();
    refresh_files(function() {
      $("#media-modal").modal();
    });
  });

  $(".media-upload-button").click(function() {
    upload_media();
  });

  $(".preview-page").click(function() {
    preview_page();
  });
});
