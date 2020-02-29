import $ from "jquery";
import jQuery from "jquery";
import { default as ezq } from "./ezq";
import { htmlEntities, colorHash, copyToClipboard } from "./utils";

const utils = {
  htmlEntities: htmlEntities,
  colorHash: colorHash,
  copyToClipboard: copyToClipboard
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
      title: "Upload Progress"
    });
    $.ajax({
      url: CTFd.config.urlRoot + "/api/v1/files",
      data: formData,
      type: "POST",
      cache: false,
      contentType: false,
      processData: false,
      xhr: function() {
        var xhr = $.ajaxSettings.xhr();
        xhr.upload.onprogress = function(e) {
          if (e.lengthComputable) {
            var width = (e.loaded / e.total) * 100;
            pg = ezq.ezProgressBar({
              target: pg,
              width: width
            });
          }
        };
        return xhr;
      },
      success: function(data) {
        form.reset();
        pg = ezq.ezProgressBar({
          target: pg,
          width: 100
        });
        setTimeout(function() {
          pg.modal("hide");
        }, 500);

        if (cb) {
          cb(data);
        }
      }
    });
  }
};

const helpers = {
  files,
  utils,
  ezq
};

export default helpers;
