$(document).ready(function() {
  $("#file-add-form").submit(function(e) {
    e.preventDefault();
    var formData = new FormData(e.target);
    formData.append("nonce", csrf_nonce);
    formData.append("challenge", CHALLENGE_ID);
    formData.append("type", "challenge");
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
        // TODO: Refresh files on submit
        e.target.reset();

        // Refresh modal
        pg = ezpg({
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
  });

  $(".delete-file").click(function(e) {
    var file_id = $(this).attr("file-id");
    var row = $(this)
      .parent()
      .parent();
    ezq({
      title: "Delete Files",
      body: "Are you sure you want to delete this file?",
      success: function() {
        CTFd.fetch("/api/v1/files/" + file_id, {
          method: "DELETE"
        })
          .then(function(response) {
            return response.json();
          })
          .then(function(response) {
            if (response.success) {
              row.remove();
            }
          });
      }
    });
  });
});
