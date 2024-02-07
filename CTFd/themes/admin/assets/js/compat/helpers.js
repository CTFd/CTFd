import $ from "jquery";
import jQuery from "jquery";
import { default as ezq } from "./ezq";
import { htmlEntities } from "@ctfdio/ctfd-js/utils/html";
import { colorHash } from "./styles";
import { copyToClipboard } from "./ui";

const utils = {
  htmlEntities: htmlEntities,
  colorHash: colorHash,
  copyToClipboard: copyToClipboard,
};

const files = {
  upload: (form, extra_data, cb) => {
    const CTFd = window.CTFd;
    if (form instanceof jQuery) {
      form = form[0];
    }
    var formData = new FormData(form);
    formData.append("nonce", CTFd.config.csrfNonce);
    for (let [key, value] of Object.entries(extra_data)) {
      formData.append(key, value);
    }

    var pg = ezq.ezProgressBar({
      width: 0,
      title: "Upload Progress",
    });
    $.ajax({
      url: CTFd.config.urlRoot + "/api/v1/files",
      data: formData,
      type: "POST",
      cache: false,
      contentType: false,
      processData: false,
      xhr: function () {
        var xhr = $.ajaxSettings.xhr();
        xhr.upload.onprogress = function (e) {
          if (e.lengthComputable) {
            var width = (e.loaded / e.total) * 100;
            pg = ezq.ezProgressBar({
              target: pg,
              width: width,
            });
          }
        };
        return xhr;
      },
      success: function (data) {
        form.reset();
        pg = ezq.ezProgressBar({
          target: pg,
          width: 100,
        });
        setTimeout(function () {
          pg.modal("hide");
        }, 500);

        if (cb) {
          cb(data);
        }
      },
    });
  },
};

const comments = {
  get_comments: (extra_args) => {
    const CTFd = window.CTFd;
    return CTFd.fetch("/api/v1/comments?" + $.param(extra_args), {
      method: "GET",
      credentials: "same-origin",
      headers: {
        Accept: "application/json",
        "Content-Type": "application/json",
      },
    }).then(function (response) {
      return response.json();
    });
  },
  add_comment: (comment, type, extra_args, cb) => {
    const CTFd = window.CTFd;
    let body = {
      content: comment,
      type: type,
      ...extra_args,
    };
    CTFd.fetch("/api/v1/comments", {
      method: "POST",
      credentials: "same-origin",
      headers: {
        Accept: "application/json",
        "Content-Type": "application/json",
      },
      body: JSON.stringify(body),
    })
      .then(function (response) {
        return response.json();
      })
      .then(function (response) {
        if (cb) {
          cb(response);
        }
      });
  },
  delete_comment: (comment_id) => {
    const CTFd = window.CTFd;
    return CTFd.fetch(`/api/v1/comments/${comment_id}`, {
      method: "DELETE",
      credentials: "same-origin",
      headers: {
        Accept: "application/json",
        "Content-Type": "application/json",
      },
    }).then(function (response) {
      return response.json();
    });
  },
};

const helpers = {
  files,
  comments,
  utils,
  ezq,
};

export default helpers;
