function upload_files(form, cb) {
  if (form instanceof jQuery) {
    form = form[0];
  }
  var formData = new FormData(form);
  formData.append("nonce", csrf_nonce);
  var pg = ezpg({
    width: 0,
    title: "Upload Progress"
  });
  $.ajax({
    url: script_root + "/api/v1/files",
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
          pg = ezpg({
            target: pg,
            width: width
          });
        }
      };
      return xhr;
    },
    success: function(data) {
      // Refresh modal
      pg = ezpg({
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
