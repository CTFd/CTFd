import "./main";
import "core/utils";
import "bootstrap/js/dist/tab";
import Moment from "moment-timezone";
import moment from "moment-timezone";
import CTFd from "core/CTFd";
import { default as helpers } from "core/helpers";
import $ from "jquery";
import { ezQuery, ezProgressBar, ezAlert } from "core/ezq";
import CodeMirror from "codemirror";
import "codemirror/mode/htmlmixed/htmlmixed.js";

function loadTimestamp(place, timestamp) {
  if (typeof timestamp == "string") {
    timestamp = parseInt(timestamp, 10);
  }
  const m = Moment(timestamp * 1000);
  $("#" + place + "-month").val(m.month() + 1); // Months are zero indexed (http://momentjs.com/docs/#/get-set/month/)
  $("#" + place + "-day").val(m.date());
  $("#" + place + "-year").val(m.year());
  $("#" + place + "-hour").val(m.hour());
  $("#" + place + "-minute").val(m.minute());
  loadDateValues(place);
}

function loadDateValues(place) {
  const month = $("#" + place + "-month").val();
  const day = $("#" + place + "-day").val();
  const year = $("#" + place + "-year").val();
  const hour = $("#" + place + "-hour").val();
  const minute = $("#" + place + "-minute").val();
  const timezone = $("#" + place + "-timezone").val();

  const utc = convertDateToMoment(month, day, year, hour, minute);
  if (isNaN(utc.unix())) {
    $("#" + place).val("");
    $("#" + place + "-local").val("");
    $("#" + place + "-zonetime").val("");
  } else {
    $("#" + place).val(utc.unix());
    $("#" + place + "-local").val(
      utc.local().format("dddd, MMMM Do YYYY, h:mm:ss a zz")
    );
    $("#" + place + "-zonetime").val(
      utc.tz(timezone).format("dddd, MMMM Do YYYY, h:mm:ss a zz")
    );
  }
}

function convertDateToMoment(month, day, year, hour, minute) {
  let month_num = month.toString();
  if (month_num.length == 1) {
    month_num = "0" + month_num;
  }

  let day_str = day.toString();
  if (day_str.length == 1) {
    day_str = "0" + day_str;
  }

  let hour_str = hour.toString();
  if (hour_str.length == 1) {
    hour_str = "0" + hour_str;
  }

  let min_str = minute.toString();
  if (min_str.length == 1) {
    min_str = "0" + min_str;
  }

  // 2013-02-08 24:00
  const date_string =
    year.toString() +
    "-" +
    month_num +
    "-" +
    day_str +
    " " +
    hour_str +
    ":" +
    min_str +
    ":00";
  return Moment(date_string, Moment.ISO_8601);
}

function updateConfigs(event) {
  event.preventDefault();
  const obj = $(this).serializeJSON();
  const params = {};

  if (obj.mail_useauth === false) {
    obj.mail_username = null;
    obj.mail_password = null;
  } else {
    if (obj.mail_username === "") {
      delete obj.mail_username;
    }
    if (obj.mail_password === "") {
      delete obj.mail_password;
    }
  }

  Object.keys(obj).forEach(function(x) {
    if (obj[x] === "true") {
      params[x] = true;
    } else if (obj[x] === "false") {
      params[x] = false;
    } else {
      params[x] = obj[x];
    }
  });

  CTFd.api.patch_config_list({}, params).then(_response => {
    window.location.reload();
  });
}

function uploadLogo(event) {
  event.preventDefault();
  let form = event.target;
  helpers.files.upload(form, {}, function(response) {
    const f = response.data[0];
    const params = {
      value: f.location
    };
    CTFd.fetch("/api/v1/configs/ctf_logo", {
      method: "PATCH",
      body: JSON.stringify(params)
    })
      .then(function(response) {
        return response.json();
      })
      .then(function(response) {
        if (response.success) {
          window.location.reload();
        } else {
          ezAlert({
            title: "Error!",
            body: "Logo uploading failed!",
            button: "Okay"
          });
        }
      });
  });
}

function removeLogo() {
  ezQuery({
    title: "Remove logo",
    body: "Are you sure you'd like to remove the CTF logo?",
    success: function() {
      const params = {
        value: null
      };
      CTFd.api
        .patch_config({ configKey: "ctf_logo" }, params)
        .then(_response => {
          window.location.reload();
        });
    }
  });
}

function importConfig(event) {
  event.preventDefault();
  let import_file = document.getElementById("import-file").files[0];

  let form_data = new FormData();
  form_data.append("backup", import_file);
  form_data.append("nonce", CTFd.config.csrfNonce);

  let pg = ezProgressBar({
    width: 0,
    title: "Upload Progress"
  });

  $.ajax({
    url: CTFd.config.urlRoot + "/admin/import",
    type: "POST",
    data: form_data,
    processData: false,
    contentType: false,
    statusCode: {
      500: function(resp) {
        alert(resp.responseText);
      }
    },
    xhr: function() {
      let xhr = $.ajaxSettings.xhr();
      xhr.upload.onprogress = function(e) {
        if (e.lengthComputable) {
          let width = (e.loaded / e.total) * 100;
          pg = ezProgressBar({
            target: pg,
            width: width
          });
        }
      };
      return xhr;
    },
    success: function(_data) {
      pg = ezProgressBar({
        target: pg,
        width: 100
      });
      setTimeout(function() {
        pg.modal("hide");
      }, 500);
      setTimeout(function() {
        window.location.reload();
      }, 700);
    }
  });
}

function exportConfig(event) {
  event.preventDefault();
  window.location.href = $(this).attr("href");
}

function insertTimezones(target) {
  let current = $("<option>").text(moment.tz.guess());
  $(target).append(current);
  let tz_names = moment.tz.names();
  for (let i = 0; i < tz_names.length; i++) {
    let tz = $("<option>").text(tz_names[i]);
    $(target).append(tz);
  }
}

$(() => {
  const theme_header_editor = CodeMirror.fromTextArea(
    document.getElementById("theme-header"),
    {
      lineNumbers: true,
      lineWrapping: true,
      mode: "htmlmixed",
      htmlMode: true
    }
  );

  const theme_footer_editor = CodeMirror.fromTextArea(
    document.getElementById("theme-footer"),
    {
      lineNumbers: true,
      lineWrapping: true,
      mode: "htmlmixed",
      htmlMode: true
    }
  );

  const theme_settings_editor = CodeMirror.fromTextArea(
    document.getElementById("theme-settings"),
    {
      lineNumbers: true,
      lineWrapping: true,
      mode: { name: "javascript", json: true }
    }
  );

  // Handle refreshing codemirror when switching tabs.
  // Better than the autorefresh approach b/c there's no flicker
  $("a[href='#theme']").on("shown.bs.tab", function(_e) {
    theme_header_editor.refresh();
    theme_footer_editor.refresh();
    theme_settings_editor.refresh();
  });

  $("#theme-settings-modal form").submit(function(e) {
    e.preventDefault();
    theme_settings_editor
      .getDoc()
      .setValue(JSON.stringify($(this).serializeJSON(), null, 2));
    $("#theme-settings-modal").modal("hide");
  });

  $("#theme-settings-button").click(function() {
    let form = $("#theme-settings-modal form");
    let data;

    // Ignore invalid JSON data
    try {
      data = JSON.parse(theme_settings_editor.getValue());
    } catch (e) {
      data = {};
    }

    $.each(data, function(key, value) {
      var ctrl = form.find(`[name='${key}']`);
      switch (ctrl.prop("type")) {
        case "radio":
        case "checkbox":
          ctrl.each(function() {
            if ($(this).attr("value") == value) {
              $(this).attr("checked", value);
            }
          });
          break;
        default:
          ctrl.val(value);
      }
    });
    $("#theme-settings-modal").modal();
  });

  insertTimezones($("#start-timezone"));
  insertTimezones($("#end-timezone"));
  insertTimezones($("#freeze-timezone"));

  $(".config-section > form:not(.form-upload)").submit(updateConfigs);
  $("#logo-upload").submit(uploadLogo);
  $("#remove-logo").click(removeLogo);
  $("#export-button").click(exportConfig);
  $("#import-button").click(importConfig);
  $("#config-color-update").click(function() {
    const hex_code = $("#config-color-picker").val();
    const user_css = theme_header_editor.getValue();
    let new_css;
    if (user_css.length) {
      let css_vars = `theme-color: ${hex_code};`;
      new_css = user_css.replace(/theme-color: (.*);/, css_vars);
    } else {
      new_css =
        `<style id="theme-color">\n` +
        `:root {--theme-color: ${hex_code};}\n` +
        `.navbar{background-color: var(--theme-color) !important;}\n` +
        `.jumbotron{background-color: var(--theme-color) !important;}\n` +
        `</style>\n`;
    }
    theme_header_editor.getDoc().setValue(new_css);
  });

  $(".start-date").change(function() {
    loadDateValues("start");
  });
  $(".end-date").change(function() {
    loadDateValues("end");
  });
  $(".freeze-date").change(function() {
    loadDateValues("freeze");
  });

  const start = $("#start").val();
  const end = $("#end").val();
  const freeze = $("#freeze").val();

  if (start) {
    loadTimestamp("start", start);
  }
  if (end) {
    loadTimestamp("end", end);
  }
  if (freeze) {
    loadTimestamp("freeze", freeze);
  }

  // Toggle username and password based on stored value
  $("#mail_useauth")
    .change(function() {
      $("#mail_username_password").toggle(this.checked);
    })
    .change();
});
